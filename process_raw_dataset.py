
import os
import sys
import json
# -- Python version check ---
dig1, dig2 = sys.version.split('.')[:2]
req_d1, req_d2 = 3, 9
if req_d1 > int(dig1) or req_d2 > int(dig2):
    print(f"ERROR: The python version must be {req_d1}.{req_d2} or higher")
    exit(1)
# ---------------------------
import time
import logging
from typing import Union
from pathlib import Path

import numpy as np
from PIL import Image
import tiffile as tiff

import modules.oct_processing_lib as raw
from modules.oct_processing_lib import Cube
from modules.xml_processing_lib import process_xmlscans
from modules.dataset_classes import RawDataset, CleanDataset, DatasetAccessError


study_hard_disk_path = "D:/"
study_dir_name = "study_datasets"
clean_dataset_path = study_hard_disk_path+f"{study_dir_name}/clean_dataset"
raw_dataset_path = study_hard_disk_path+f"{study_dir_name}/raw_dataset"
clean_dataset = CleanDataset(clean_dataset_path)
raw_dataset = RawDataset(raw_dataset_path)

axial_resolution = 5 # Micras
transversal_resolution = 15 # Micras
transv_axial_ratio = transversal_resolution/axial_resolution
width_scale_factor = transv_axial_ratio/2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OVERRIDE = False

def main():
    process_raw_dataset(
        group='control', patient_nums=[1,2,3,4,5,6,7,8,9,10,11,21]
    )

def process_raw_dataset(group:str=None, patient_nums:Union[int, list[int]]=None, 
                        data_types:Union[str, list[str]]=None, zone:str=None, eye:str=None):
    if not os.path.exists(study_hard_disk_path):
        logger.error(" The study hard disk is not connected to the computer")
        exit(1)
    logger.info(" ----------- Procesing raw_dataset into clean_dataset -----------")
    logger.info(f" -> Raw Dataset Path => '{raw_dataset_path}'")
    logger.info(f" -> Clean Dataset Path => '{clean_dataset_path}'")
    raw_data_paths = raw_dataset.get_data_paths(
        group=group, patient_num=patient_nums, data_type=data_types, zone=zone, eye=eye
    )
    for grp in raw_dataset.groups:
        if group is not None and grp != group: continue
        logger.info(f" => {grp.upper()} GROUP")
        # vemos que pacientes hay que procesar
        if patient_nums is None: pat_iterable = range(1, raw_dataset.get_num_patients(grp)+1)
        elif type(patient_nums) is list: pat_iterable = patient_nums
        elif type(patient_nums) is int: pat_iterable = [patient_nums]
        # iteramos
        for p_num in pat_iterable:
            patient = f'patient-{p_num}'
            logger.info(f"  + Processing '{patient}' data")
            clean_dataset.create_patient(grp, patient_num=p_num)
            # Vemos que data types hay que procesar
            if type(data_types) is str: data_types = [data_types]
            elif data_types is None: data_types = raw_dataset.data_types   
            # iteramos
            for dtype in data_types:
                dtype_data:dict = raw_data_paths[grp][patient][dtype]
                clean_path = clean_dataset.get_dir_path(group=grp, patient_num=p_num, data_type=dtype)
                if bool(dtype_data):
                    if dtype == 'OCT' or dtype == 'OCTA':
                        for zone, zone_info in raw_dataset.zones.items():
                            if zone in dtype_data:
                                zone_data = dtype_data[zone]
                                for eye, eye_conv in raw_dataset.eyes.items():
                                    if eye in zone_data:
                                        path = Path(zone_data[eye])
                                        raw_file_info = raw_dataset.split_file_name(path.name, dtype)
                                        adq_date = raw_file_info['adquisition_date']
                                        adq_name = zone_info['adquisitions_name']
                                        file_name = patient+"_"+adq_name[dtype]+"_"+adq_date+"_"+eye_conv+'.tif'
                                        file_path = clean_path/file_name
                                        if not OVERRIDE and os.path.exists(file_path):
                                            logger.info(f"      -> (.tif) '{dtype}_{zone}_{eye}' already exists")
                                            continue
                                        data = process_image2D3D(path, data_type=dtype, zone=zone, resize=True)
                                        msg = f"      -> saving raw (.img) '{dtype}_{zone}_{eye}' as tiff (.tif)"
                                        if OVERRIDE and os.path.exists(file_path):
                                            msg += " (overriding)"
                                        logger.info(msg)
                                        tiff.imwrite(file_path, data)              
                    elif dtype == 'retinography':
                        for eye, eye_conv in raw_dataset.eyes.items():
                            if eye in dtype_data:
                                # Copiamos el fichero en el mismo formato pero con otro nombre
                                path = Path(dtype_data[eye])
                                raw_file_info = raw_dataset.split_file_name(path.name, dtype)
                                adq_name = raw_file_info['adquisition_date']
                                file_name = patient+"_"+dtype+"_"+adq_name+"_"+eye_conv+".jpg"
                                file_path = clean_path/file_name
                                if not OVERRIDE and os.path.exists(file_path):
                                    logger.info(f"      -> (.jpg) '{dtype}_{eye}' already exists")
                                    continue
                                data = process_image2D3D(path, data_type=dtype, zone=zone, resize=True)
                                msg = f"      -> saving (.jpg) '{dtype}_{eye}'"
                                if OVERRIDE and os.path.exists(file_path):
                                    msg += " (overriding)"
                                logger.info(msg)
                                Image.fromarray(data).save(file_path, format='jpeg')           
                    elif dtype == 'XML':
                        file_name = f'{patient}_analysis.json'
                        file_path = clean_path/file_name
                        if not OVERRIDE and os.path.exists(file_path):
                            logger.info(f"      -> '{file_name}' already exists")
                            continue
                        scans = {}
                        for xml_path, xml_scans in dtype_data.items():
                            logger.debug(f"{xml_path}\n{xml_scans}")
                            processed_xml:dict = process_xmlscans(xml_path, xml_scans)
                            scans.update(processed_xml)
                        msg = f"      -> saving '{file_name}'"
                        if OVERRIDE and os.path.exists(file_path):
                            msg += " (overriding)"
                        logger.info(msg)
                        with open(file_path, 'w') as file:
                            json.dump(scans, file, indent=4)
                            
    logger.info(" ------------------ End, Raw Dataset processed ------------------")
    
# ----------------------------------------------
def process_image2D3D(data_path:str, data_type:str, zone:str, resize:bool=False, timeit:bool=False) -> np.array:
    t0 = time.time()
    if data_type == 'retinography':
        data = np.array(Image.open(data_path, formats=['jpeg']))
    elif data_type == 'OCT':
        if zone == 'macula':
            resize_t = (int(width_scale_factor*1024), 1024) if resize else None
        else:
            resize_t = (512, 1024) if resize else None
        data = process_cube(
            data_path, data_type, zone, 
            resize=resize_t
        ).as_nparray()
    elif data_type == 'OCTA':
        data = process_cube(
            data_path, data_type, zone, 
            resize=(int(width_scale_factor*1024), 1024) if resize else None
        ).rotate_face(axe='x').resize_slices((350,350)).project().as_nparray()
    else:
        print(f"DATA_ERROR: '{data_type}' is not a valid data type")
        exit(1)
        
    if timeit:
        tf = time.time()
        print(f" + Time spent processing = {round(tf-t0, 2)} seg")
    
    return data

def process_cube(data_path:str, modality:str, zone:str, resize:tuple[int,int]=None) -> Cube:
    if modality == 'OCT':
        if zone == 'macula':
            cube = raw.process_oct(
                data_path, 
                width_pixels=256, # Num A-Scans/2
                height_pixels=1024, # Samples of every A-Scan (always 1024 samples) (2 mm of depth in the tissue)
                num_images=128, # Num B-Scans
                vertical_flip=True,
                resize=resize
            )
        elif zone == 'optic-nerve':
            cube = raw.process_oct(
                data_path, 
                width_pixels=100,
                height_pixels=1024,
                num_images=200,
                vertical_flip=True,
                resize=resize
            )
        else:
            print(f"DATA_ERROR: '{zone}' is not a valid zone")
            exit(1)
    elif modality == 'OCTA':
        if zone == 'macula' or zone == 'optic-nerve':
            cube = raw.process_oct(
                data_path, 
                width_pixels=175,
                height_pixels=1024,
                num_images=350,
                vertical_flip=True,
                resize=resize
            )
        else:
            print(f"DATA_ERROR: '{zone}' is not a valid zone")
            exit(1)
    
    return cube

# ----------------------------------------------
if "__main__" == __name__:
    main()