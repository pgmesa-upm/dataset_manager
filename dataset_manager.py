
# Built-in modules
import os
import sys
import json
import time
import shutil
import logging
from typing import Union
from pathlib import Path
from copy import deepcopy

# -- External dependencies (pip)
import numpy as np
from PIL import Image
import tiffile as tiff
# pgmesa public PyPI package
import upm_oct_dataset_utils.oct_processing_lib as raw
from upm_oct_dataset_utils.oct_processing_lib import Cube
from upm_oct_dataset_utils.xml_processing_lib import process_xmlscans
from upm_oct_dataset_utils.dataset_classes import (
    RawDataset, CleanDataset, DatasetAccessError, StudyDate
)
import upm_oct_dataset_utils.dataset_classes as ds

from extra_data.main import dest_dir_name

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

def process_raw_dataset(group:Union[str,list[str]]=None, patient_num:Union[int, list[int]]=None, study:Union[int,StudyDate,list[int],list[StudyDate]]=None,
                        data_type:Union[str, list[str]]=None, zone:str=None, eye:str=None, OVERRIDE=False):
    if not os.path.exists(study_hard_disk_path):
        logger.error(f" The study hard disk is not connected to the computer '{study_hard_disk_path}'")
        return
    logger.info(" ----------- Procesing raw_dataset into clean_dataset -----------")
    logger.info(f" -> Raw Dataset Path => '{raw_dataset_path}'")
    logger.info(f" -> Clean Dataset Path => '{clean_dataset_path}'")
    raw_data_paths = raw_dataset.get_data_paths(
        group=group, patient_num=patient_num, study=study, data_type=data_type, zone=zone, eye=eye
    )
    for grp in raw_dataset.groups:
        if group is not None:
            if type(group) == str and grp != group: continue
            elif type(group) == list and grp not in group: continue
        logger.info(f" => {grp.upper()} GROUP")
        # vemos que pacientes hay que procesar
        if patient_num is None: pat_iterable = raw_dataset.get_patients(grp, as_int=True)
        elif type(patient_num) is list: pat_iterable = patient_num
        elif type(patient_num) is int: pat_iterable = [patient_num]
        # iteramos
        for p_num in pat_iterable:
            patient = f'patient-{p_num}'
            logger.info(f"  + Processing '{patient}' data")
            clean_dataset.create_patient(grp, patient_num=p_num)
            # Patient info si existe un XML
            xml_path = None
            studies_dict = raw_data_paths[grp][patient]
            for std_info in studies_dict.values():
                try:
                    xml_path = list(std_info[ds.XML].keys())[0]
                    break
                except: pass
            if xml_path is not None:
                xml_path = Path(xml_path).resolve()
                raw_file_info = raw_dataset.split_file_name(xml_path.name, ds.XML)
                birth_year = raw_file_info['birth_year_date'][:4]
                sex = raw_file_info['sex']
                p_dir_path = clean_dataset.get_dir_path(group=grp, patient_num=p_num)
                with open(p_dir_path/f'{patient}.json', 'w') as file:
                    json.dump({"SEX":sex, "BIRTH_YEAR": birth_year}, file, indent=4)    
            # Vemos los estudios a procesar
            studies = raw_dataset.get_studies(grp, p_num, study=study)
            for std in studies:
                std_date = raw_dataset.get_studydir_date(std).as_str(year_first=True)
                clean_std = "study_"+std_date
                logger.info(f"   -'{clean_std}'")
                clean_dataset.create_study(grp, p_num, clean_std)
                # Copiamos la extra info al directorio clean
                study_dir_path = raw_dataset.get_dir_path(group=grp, patient_num=p_num, study=std)
                clean_study_dir_path = clean_dataset.get_dir_path(group=grp, patient_num=p_num, study=clean_std)
                extra_info_path = study_dir_path/dest_dir_name
                if os.path.exists(extra_info_path):
                    l = os.listdir(extra_info_path)
                    for f in l:
                        logger.info(f"      -> copying '{f}'...")
                        shutil.copy(extra_info_path/f, clean_study_dir_path)
                # Vemos que data types hay que procesar
                if type(data_type) is str: data_type = [data_type]
                elif data_type is None: data_type = raw_dataset.data_types   
                # iteramos
                for dtype in data_type:
                    dtype_data:dict = raw_data_paths[grp][patient][std][dtype]
                    clean_path = clean_dataset.get_dir_path(group=grp, patient_num=p_num, study=clean_std, data_type=dtype)
                    if not os.path.exists(clean_path): os.mkdir(clean_path)
                    if bool(dtype_data):
                        if dtype == ds.OCT or dtype == ds.OCTA:
                            for zone, zone_info in raw_dataset.zones.items():
                                if zone in dtype_data:
                                    zone_data = dtype_data[zone]
                                    for eye, eye_conv in raw_dataset.eyes.items():
                                        if eye in zone_data:
                                            path = Path(zone_data[eye])
                                            raw_file_info = raw_dataset.split_file_name(path.name, dtype)
                                            adq_date = raw_file_info['adquisition_date']
                                            adq_hour = raw_file_info['hour']
                                            adq_name = zone_info['adquisitions_name']
                                            file_name = patient+"_"+adq_name[dtype]+"_"+adq_date+"_"+adq_hour+"_"+eye_conv+'.tif'
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
                        elif dtype == ds.RET:
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
                        elif dtype == ds.XML:
                            file_name = f'{patient}_{std_date}_analysis.json'
                            file_path = clean_path/file_name
                            if not OVERRIDE and os.path.exists(file_path):
                                logger.info(f"      -> '{file_name}' already exists")
                                continue
                            scans = {}
                            for xml_path, xml_scans in dtype_data.items():
                                if len(xml_scans) == 0: continue
                                logger.debug(f"{xml_path}\n{xml_scans}")
                                std_date_obj = StudyDate.from_str(std_date, sep='-', year_first=True)
                                processed_xml:dict = process_xmlscans(xml_path, std_date_obj, xml_scans)
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
    if data_type == ds.RET:
        data = np.array(Image.open(data_path, formats=['jpeg']))
    elif data_type == ds.OCT:
        if zone == ds.MACULA:
            resize_t = (int(width_scale_factor*1024), 1024) if resize else None
        else:
            resize_t = (512, 1024) if resize else None
        data = process_cube(
            data_path, data_type, zone, 
            resize=resize_t
        ).as_nparray()
    elif data_type == ds.OCTA:
        data = process_cube(
            data_path, data_type, zone, 
            resize=(int(width_scale_factor*1024), 1024) if resize else None
        ).rotate_face(axe='x').resize_slices((350,350)).project().as_nparray()
    else:
        raise Exception(f"DATA_ERROR: '{data_type}' is not a valid data type")
        
    if timeit:
        tf = time.time()
        print(f" + Time spent processing = {round(tf-t0, 2)} seg")
    
    return data

def process_cube(data_path:str, modality:str, zone:str, resize:tuple[int,int]=None) -> Cube:
    if modality == ds.OCT:
        if zone == ds.MACULA:
            cube = raw.process_oct(
                data_path, 
                width_pixels=256, # Num A-Scans/2
                height_pixels=1024, # Samples of every A-Scan (always 1024 samples) (2 mm of depth in the tissue)
                num_images=128, # Num B-Scans
                vertical_flip=True,
                resize=resize
            )
        elif zone == ds.OPTIC_DISC:
            cube = raw.process_oct(
                data_path, 
                width_pixels=100,
                height_pixels=1024,
                num_images=200,
                vertical_flip=True,
                resize=resize
            )
        else:
            raise Exception(f"DATA_ERROR: '{zone}' is not a valid zone")
    elif modality == ds.OCTA:
        if zone == ds.MACULA or zone == ds.OPTIC_DISC:
            cube = raw.process_oct(
                data_path, 
                width_pixels=175,
                height_pixels=1024,
                num_images=350,
                vertical_flip=True,
                resize=resize
            )
        else:
            raise Exception(f"DATA_ERROR: '{zone}' is not a valid zone")
    
    return cube

def compare_datasets(group:Union[str, list[str]]=None, patient_num:Union[int, list[int]]=None, study:Union[int,StudyDate,list[int],list[StudyDate]]=None,
                       data_type:Union[str, list[str]]=None, zone:str=None, eye:str=None, all_info=False):
    # Hallamos los datos no procesados
    available_info = raw_dataset.get_data_paths(
        group=group, patient_num=patient_num, study=study, data_type=data_type, zone=zone, eye=eye,
    )
    without_paths = raw_dataset.get_data_paths(
        group=group, patient_num=patient_num, study=study, data_type=data_type, zone=zone, eye=eye,
        _withoutpaths=True
    )
    processed_info = clean_dataset.get_data_paths()
    not_processed = {}
    for group, agroup_info in available_info.items():
        if not bool(agroup_info): continue
        if group not in processed_info:
            not_processed[group] = without_paths[group]
        else:
            pgroup_info = processed_info[group]
            not_processed[group] = {}
            for patient, apatient_info in agroup_info.items():
                if not bool(apatient_info): continue
                if patient not in pgroup_info:
                    not_processed[group][patient] = deepcopy(without_paths[group][patient])
                    for std, std_info in without_paths[group][patient].items():
                        if not bool(std_info):
                            not_processed[group][patient].pop(std)
                    if len(not_processed[group][patient]) == 0:
                        not_processed[group].pop(patient)
                else:
                    ppatient_info = pgroup_info[patient]
                    not_processed[group][patient] = {}
                    for std, astudy_info in apatient_info.items():
                        std_date = raw_dataset.get_studydir_date(std).as_str(year_first=True)
                        clean_std = "study_"+std_date
                        if not bool(astudy_info): continue
                        if clean_std not in ppatient_info:
                            not_processed[group][patient][std] = without_paths[group][patient][std]
                        else:
                            pstudy_info = ppatient_info[clean_std]
                            not_processed[group][patient][std] = {}
                            for dtype, adtype_info in astudy_info.items():
                                if not bool(adtype_info): continue
                                if dtype not in pstudy_info:
                                    not_processed[group][patient][std][dtype] = without_paths[group][patient][std][dtype]
                                else:
                                    if dtype == ds.OCTA or dtype == ds.OCT:
                                        pzones_info = pstudy_info[dtype]
                                        not_processed[group][patient][std][dtype] = {}
                                        for zone, azone_info in adtype_info.items():
                                            if not bool(azone_info): continue
                                            if zone not in pzones_info:
                                                not_processed[group][patient][std][dtype][zone] = without_paths[group][patient][std][dtype][zone]
                                            else:
                                                peyes_info = pzones_info[zone]
                                                not_processed[group][patient][std][dtype][zone] = []
                                                for eye, aeye_info in azone_info.items():
                                                    if eye not in peyes_info:
                                                        not_processed[group][patient][std][dtype][zone].append(eye)
                                                if len(not_processed[group][patient][std][dtype][zone]) == 0:
                                                    not_processed[group][patient][std][dtype].pop(zone)
                                    elif dtype == ds.RET:
                                        peyes_info = pstudy_info[dtype]
                                        not_processed[group][patient][std][dtype] = []
                                        for eye, aeye_info in adtype_info.items():
                                            if eye not in peyes_info:
                                                not_processed[group][patient][std][dtype].append(eye)    
                                    elif dtype == ds.XML:
                                        not_processed[group][patient][std][dtype] = []
                                        list_ = list(pstudy_info[dtype].values())
                                        if len(list_) > 0: 
                                            pscans = list_[0]
                                            for xmlpath, scans in adtype_info.items():
                                                npscans = [scan for scan in scans if scan not in pscans]
                                                not_processed[group][patient][std][dtype] += npscans
                                    if len(not_processed[group][patient][std][dtype]) == 0:
                                        not_processed[group][patient][std].pop(dtype)
                            if len(not_processed[group][patient][std]) == 0:
                                not_processed[group][patient].pop(std)
                    if len(not_processed[group][patient]) == 0:
                        not_processed[group].pop(patient)
            if len(not_processed[group]) == 0:
                not_processed.pop(group)
    # print(json.dumps(not_processed, indent=4))
    # Mostramos la información no procesada
    print(" => AVAILABLE DATA TO PROCESS:")
    if len(not_processed) == 0:
        print("     [%] There is no data to process")
        return
    for group, group_info in not_processed.items():
        if not bool(group_info): continue
        print(f" + '{group.upper()}' GROUP")
        for patient, patient_info in group_info.items():
            if not bool(patient_info): continue
            print(f" - '{patient}' has data to process")
            if all_info:
                str_info = json.dumps(patient_info, indent=4)
                tab = "     "; str_info = str_info.replace('\n', '\n'+tab)
                print(tab+str_info)