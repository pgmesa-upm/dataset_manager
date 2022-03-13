
import sys
# -- Python version check ---
dig1, dig2 = sys.version.split('.')[:2]
req_d1, req_d2 = 3, 9
print(f"Detected python version: {dig1}.{dig2}")
print(f"Required python version: {req_d1}.{req_d2} or higher")
if req_d1 > int(dig1) or req_d2 > int(dig2):
    print(f"ERROR: The python version must be {req_d1}.{req_d2} or higher")
    exit(1)
# ---------------------------

try:
    from extra_data.eyes_data.main import eyes_data_shell
    from dataset_manager import process_raw_dataset, raw_dataset, clean_dataset, compare_datasets, StudyDate
except ModuleNotFoundError as err:
    print("[!] ERROR: No se han instalado todas las dependencias del programa",
          f"\n -> ERROR_MSG: {err}",
          "\n -> Introduce 'pip install -r requirements.txt', a ser posible en un entorno virtual aislado")
    exit(1)

commands = {
    'raw': "Shows raw dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s)",
    'clean': "Shows clean dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s)",
    'check': ("Shows the difference between the 2 datasets. Is usefull to see if there is available data to process "+ 
                "(add -a to show all info)"),
    'process': "Processes the entire raw dataset (add -o to override existing clean files)",
    'eyes': "Activates eyes-data shell",
    'exit': 'Exits from the program'
}

global_flags = {
    '-h': "shows command help",
    '-hq': "shows information about how to use specific queries in a command"
}

def main():
    print("\n + DATASET MANAGER (ctrl-c to exit):\n")
    print_help()
    print("\n -  Enter command: ")
    exit_var = False
    while not exit_var:
        try:
            command_line = str(input("> ")).split(" ")
            # Filtramos los argumentos no validos
            command_line = [arg for arg in command_line if arg != ""]
            if len(command_line) == 0: continue
            command = command_line.pop(0)
            if command in global_flags:
                flag = command
                if flag == '-h': print_help()
                elif flag == "-hq": show_how_to_query()
            elif command in commands:
                if command == 'raw' or command == "clean":
                    if command == "raw": dataset = raw_dataset
                    else: dataset = clean_dataset
                    m = False; s = False
                    # 2 posibles modos, toda la info, solo la sobrante, solo el summary
                    if '-m' in command_line: m = True; command_line.remove('-m')
                    elif '-s' in command_line: s = True; command_line.remove('-s')
                    queries = process_queries(command_line)
                    dataset.show_info(**queries, only_missing_info=m, only_summary=s)
                elif command == "check":
                    a = False
                    if '-a' in command_line: a = True; command_line.remove('-a')
                    queries = process_queries(command_line)
                    compare_datasets(**queries, all_info=a)
                elif command == "process":
                    o = False
                    if '-o' in command_line: o = True; command_line.remove('-o')
                    queries = process_queries(command_line)
                    process_raw_dataset(**queries, OVERRIDE=o)
                elif command == "eyes":
                    eyes_data_shell()
                elif command == "exit":
                    print("[%] Exiting...")
                    exit_var = True
            else:
                print(f"[!] '{command}' command doesn't exist in the program")
        except Exception as err:
            print(f"[!] '{err}'")

def process_queries(cmd_line:list) -> dict:
    queries = dict(
        group=[], patient_num=[], study=[],data_type=[]
    )
    qflags ={
        '-g=':"group", '-p=':"patient_num", '-s=':"study", '-d=':"data_type"
    }
    for arg in cmd_line:
        flag = arg[:3]; query = arg[3:]
        if flag in qflags.keys():
            splitted = query.split(",")
            key = qflags[flag]
            for sp in splitted:
                if sp == '': continue
                val = sp
                if '-s=' == flag:
                    try: val = int(sp)
                    except:
                        val = StudyDate.from_str(sp)              
                if '-p=' == flag:
                    if "-" in sp: 
                        low, high = sp.split("-")
                        low = int(low); high = int(high)
                        val = [i for i in range(low, high+1) if i not in queries[key]]
                        queries[key] += val
                        continue
                    else:
                        val = int(sp)
                if val not in queries[key]:
                    queries[key].append(val)      
        else:
            raise Exception(f"'{arg}' has an incorrect flag '{flag}'")
        
    for key, val in queries.items():
        if len(val) == 0:
            val = None
        # if len(val) == 1:
        #     val = val[0]
        queries[key] = val
        
    return queries
    
def show_how_to_query():
    info = """
    [?] How to make queries (always use ',' for enums without ' ' after it):
    - 3 options (only in those commands which support it):
    1. '-g=' - Choose one or more groups. Ex: -g=control,MS,NMO
    2. '-p=' - Choose one or more patients (ranges are supported: 1-5,4,12-16). Ex: -p=1-5,8,9 -> [1,2,3,4,5,8,9]
    4. '-s=' - Choose one or more studies. Ex: -s=1,2 or -s=12-10-2021,13-4-2022
    3. '-d=' - Choose one or more data types. Ex: -d=OCT,retinography,XML
    
    *INFO: For acronyms use upper case, otherwise the query will fail.
        - If nothing is specified, all options are processed
    """
    print(info)
        
def print_help():
    print("[?] Commands:")
    for command, info in commands.items():
        print(f"     => '{command}': {info}")
        
    print("[?] Global Flags:")
    for gflag, info in global_flags.items():
        print(f"     => '{gflag}': {info}")
    print("[%] *INFO: commands 'raw', 'clean', 'check' and 'process' admits specific queries (-hq to know more)")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[!] Exit")
        exit(1)
    except Exception as err:
        print(f"[!] Unexpected error: '{err}'")
        input("-> Press enter to exit")