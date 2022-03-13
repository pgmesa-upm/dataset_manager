
import os
import json
import copy
import datetime as dt
from math import isnan
from pathlib import Path
from subprocess import run, PIPE
import dateutil.parser as dateparser

import pandas as pd
from upm_oct_dataset_utils.dataset_classes import RawDataset, StudyDate, DatasetAccessError

raw_ds_path = Path("D:/study_datasets/raw_dataset/").resolve()
raw_ds = RawDataset(raw_ds_path)
execution_path = Path(__file__).resolve().parent
excel_path = execution_path/"./eyes_data.xlsx"

dest_dir_name = 'extra-info'

date_format = "%d-%m-%Y"

base_schema = {
    "OD": {
        "visual-acuity": None,
        "diopters":{
            "myopia-hypermetropia": None,
            "astigmatism": None
        }
    },
    "OS": {
        "visual-acuity": None,
        "diopters":{
            "myopia-hypermetropia": None,
            "astigmatism": None
        }
    }
}

commands = {
    'process': "Process excel info into raw-dataset. quiet mode (add -q), override (add -o), ask for each (add -a)",
    'open': "Open excel file",
    'exit': 'Exit from the program'
}

global_flags = {
    '-h': "shows command help",
}

def eyes_data_shell():
    print("\n + Eye Data Processor (ctrl-c to exit):\n")
    print(f" => Excel Path: '{excel_path}'")
    print_help()
    print("\n -  Enter command: ")
    exit_var = False
    while not exit_var:
        try:
            command_line = str(input("/eyes-data> ")).split(" ")
            # Filtramos los argumentos no validos
            command_line = [arg for arg in command_line if arg != ""]
            if len(command_line) == 0: continue
            command = command_line.pop(0)
            if command in global_flags:
                flag = command
                if flag == '-h': print_help()
            elif command in commands:
                if command == "process":
                    o = False; a = False; q = False
                    if '-o' in command_line: o = True; command_line.remove('-o')
                    if '-a' in command_line: a = True; command_line.remove('-a')
                    if '-q' in command_line: q = True; command_line.remove('-q')
                    process_excel(override=o, ask_for_each=a, quiet=q)
                elif command == "open":
                    open_excel()
                elif command == "exit":
                    print("[%] Exiting...")
                    exit_var = True
            else:
                print(f"[!] '{command}' command doesn't exist in the program")
        except Exception as err:
            print(f"[!] '{err}'")

def print_help():
    print("[?] Commands:")
    for command, info in commands.items():
        print(f"     => '{command}': {info}")
        
    print("[?] Global Flags:")
    for gflag, info in global_flags.items():
        print(f"     => '{gflag}': {info}") 

def isempty(elem:any) -> bool:
    is_nan = False
    try: is_nan = isnan(elem)
    except: pass
    return elem == "" or elem is None or is_nan

def open_excel():
    process = run(f'start excel "{excel_path}"', cwd=os.getcwd(), shell=True, stdout=PIPE, stderr=PIPE)
    if process.returncode == 0:
        print("[%] Abriendo excel...")
    else:
        print("[!] No se pudo abrir el excel")

def process_eye_data(od_d:str, os_d:str, va:str) -> dict:
    schema = copy.deepcopy(base_schema)
    have_va = True
    if isempty(va):
        have_va = False
    else:
        od_va, os_va = va.replace("'", "").split("/")
        od_va = float(od_va); os_va = float(os_va)
    for eye in schema:
        eye_dict = schema[eye]
        if eye == "OD":
            var = od_d
            if have_va:
                va_var = od_va
        else: 
            var = os_d
            if have_va:
                va_var = os_va
        if have_va:
            eye_dict["visual-acuity"] = va_var
        if isempty(var): continue 
        m_h, astg = var.replace("'", "").split("/")
        m_h = float(m_h); astg = float(astg)
        eye_dict["diopters"]["myopia-hypermetropia"] = m_h
        eye_dict["diopters"]["astigmatism"] = astg
    return schema

def process_excel(override:bool=False, ask_for_each:bool=False, quiet:bool=False):
    
    if not os.path.exists(raw_ds_path):
        print(f"[!] Invalid RawDataset path, hard disk plugged in? -> '{raw_ds_path}'")
        return
    
    def log(*msgs):
        if not quiet:
            print(*msgs)
            
    print("[%] Processing excel...")
    excel = pd.ExcelFile(excel_path)
    sheet_names = excel.sheet_names
    for sheet_name in sheet_names:
        log(f"+ '{sheet_name.upper()}' GROUP:")
        sheet:pd.DataFrame = excel.parse(sheet_name, parse_dates=False)
        excel_dict = sheet.to_dict('list')
        pnums = excel_dict['PATIENT_NUM']
        std_dates = excel_dict['STUDY_DATE']
        od_diop = excel_dict['OD_DIOPTERS']
        os_diop = excel_dict['OS_DIOPTERS']
        vas = excel_dict['VISUAL_ACUITY']
        for pnum, std_date, od_d, os_d, va in zip(pnums, std_dates, od_diop, os_diop, vas):
            if isempty(std_date): continue
            if type(std_date) is dt.datetime:
                date = dateparser.parse(str(std_date).split(" ")[0])
                std_date = str(date.strftime(date_format))
            if "/" in std_date:
                day, month, year = std_date.split("/")
            else:
                day, month, year = std_date.split("-")
            std_date = StudyDate(int(day), int(month), int(year))
            try:
                study_dir = raw_ds.get_study_dir(sheet_name, pnum, std_date)
                study_path = raw_ds.get_dir_path(group=sheet_name, patient_num=pnum, study=study_dir)
            except DatasetAccessError as err:
                print(err)
                continue
            dest_dir_path = study_path/dest_dir_name
            try:
                os.remove(dest_dir_path/'eye-data.json')
            except: pass
            dest_fname = (f"patient-{pnum}"+"_"+std_date.as_str(year_first=True)+"_"+"eyes"+".json")
            dest_fpath = dest_dir_path/dest_fname
            if os.path.exists(dest_fpath):
                if not override:
                    # log(f"[%] '{dest_fname}' already exists, NOT overriding")
                    continue
                else:
                    log(f"[%] '{dest_fname}' already exists, OVERRIDING...")
            eye_info = process_eye_data(od_d, os_d, va)
            log(f" => Patient {pnum} | '{study_dir}' ")
            if ask_for_each:
                log(json.dumps(eye_info, indent=4))
                log(f"+ Se creará '{dest_fname}' en '{dest_dir_path}' con la información mostrada arriba")
                answer = str(input("-> ¿Quieres realizar la operación? (y/n): "))
                if answer.lower() != 'y':
                    log("[!] Operation cancelled")
                    continue
            if not os.path.exists(dest_dir_path):
                os.mkdir(dest_dir_path)
            with open(dest_fpath, 'w') as file:
                json.dump(eye_info, file, indent=4)
            log("[%] Completed!")
        log("[%] Group finished")
    print(f"--- Finished, excel has been processed ---")