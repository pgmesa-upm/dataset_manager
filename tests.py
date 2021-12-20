
import json
from PIL import Image
import os
from process_raw_dataset import process_image2D3D, study_hard_disk_path, process_cube
from modules.visualization_lib import show_image, animate_volume
from modules.dataset_classes import RawDataset, DatasetAccessError
from modules.oct_processing_lib import Cube

raw_dataset_path = "D:/study_datasets/raw_dataset"

raw_dataset = RawDataset(raw_dataset_path)

def compare():
    if not os.path.exists(study_hard_disk_path):
        print("ERROR: The study hard disk is not connected to the computer")
        exit(1)
    datas = []; titles = []
    for i in range(2):
        eye = 'left' if i==0 else 'right'
        search_params = dict(
            group='control', patient_num=3,
            data_type='OCTA', zone='macula', eye=eye
        )
        search_params2 = dict(
            group='control', patient_num=3,
            data_type='OCTA', zone='optic-nerve', eye=eye
        )
        data_type = search_params["data_type"]
        try:
            data_path = raw_dataset.get_data_paths(**search_params)
            data_path2 = raw_dataset.get_data_paths(**search_params2)
        except DatasetAccessError as err:
            print("ERROR:", err)
            exit(1)
        print(" + Accediendo al disco duro...")
        data = process_image2D3D(data_path, data_type, search_params["zone"], resize=True, timeit=True)
        data2 = process_image2D3D(data_path2, data_type, search_params2["zone"], resize=True, timeit=True)
        datas.append(data); datas.append(data2)
        titles.append(f'macula_{eye}'); titles.append(f'optic-nerve_{eye}')
    if data_type == 'OCTA':
        show_image(datas, colorbar=True, title=titles, cmap='gray', multi=True, subplot_size=(2,2))
    elif data_type == 'OCT':
        animate_volume(data, colorbar=True, title=data_type)
    elif data_type == 'RETINOGRAPHY':
        show_image(data, title=data_type)
        
def test():
    data_type = 'OCTA'
    search_params = dict(
        group='ms', patient_num=1,
        data_type=data_type, eye='left', zone='optic-nerve'
    )
    try:
        data_path = raw_dataset.get_data_paths(**search_params)
    except DatasetAccessError as err:
        print(f'ERROR: {err}'); exit(1)
    print(" + Processing data")
    if data_type == 'OCT':
        data = process_image2D3D(data_path, data_type=data_type, zone=search_params["zone"], resize=True)
        animate_volume(data)
    elif data_type == 'OCTA':
        data = process_image2D3D(data_path, data_type=data_type, zone=search_params["zone"], resize=True)
        show_image(data, cmap='gray')
        # data = process_cube(data_path, modality=data_type, zone=search_params["zone"]).rotate_face(axe='x').as_nparray()
        # animate_volume(data)
    elif data_type == 'retinography':
        data = process_image2D3D(data_path, data_type=data_type, zone=search_params["zone"])
        show_image(data)

# ----------------------------------------------------------------
excel_file_cp = 'patients_data_cp.xlsx'
excel_salt = b'n\xb0\xf7\x15?-\x1d\xa5\xfa}\xbe\x90XP$\x95\xef\xea\xb4\xe5\xa10\xc5z'

def encrypt_xlsx(file_path, pw:str=None):
    import deprecated.encryption_lib as cripto
    passed_pw = False if pw is None else True
    print(f"\n + Encrypting '{file_path}'")
    if not passed_pw:
        pw = str(input(" -> Enter a password: "))
    if pw == "":
        print(" + ERROR: password field cannot be empty\n")
        return
    if not passed_pw:
        confirmed_pw = str(input(" -> Repeat the password: "))
    if passed_pw or pw == confirmed_pw:
        key = cripto.derive_password(pw, excel_salt)
        cripto.encrypt_file(file_path, key)
        print(" + SUCCESS: File encrypted\n")
    else:
        print(" + ERROR: The passwords don't match\n")
    
def decrypt_xlsx(file_path:str, pw:str=None):
    import deprecated.encryption_lib as cripto
    print(f"\n + Decrypting '{file_path}'")
    try:
        if pw is None:
            pw = str(input(" -> Introduce the password: "))
        key = cripto.derive_password(pw, excel_salt)
        cripto.decrypt_file(file_path, key)
        print(" + SUCCESS: File decrypted\n")
    except cripto.InvalidToken:
        print(" + ERROR: password is incorrect\n")

# ----------------------------------------------------------------
if __name__ == "__main__":
    # decrypt_xlsx(excel_file_cp)
    # test()
    # compare()
    # data = raw_dataset.get_data_paths(group='sclerosis', patient_num=15)
    # print(json.dumps(data, indent=4))
    raw_dataset.show_info(only_missing_info=True)
    

   