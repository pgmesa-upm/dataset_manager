
from process_raw_dataset import process_raw_dataset, raw_dataset, clean_dataset

commands = {
    'raw': "Shows raw dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s). Admits specific queries",
    'clean': "Shows clean dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s). Admits specific queries",
    'check': "Shows the difference between the 2 datasets. Is usefull to see if there is available data to process",
    'process': "Processes the entire raw dataset (add -o to override existing clean files)"
}

global_flags = {
    '-h': "shows command help",
    '-hq': "shows information about how to use specific queries in a command"
}

def main():
    print(" + DATASET MANAGER (ctrl-c to exit):")
    print_help()
    print(" -  Enter command: ")
    while True:
        try:
            command_line = str(input("> ")).split(" ")
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
                    print(queries)
                    dataset.show_info(**queries, only_missing_info=m, only_summary=s)
                elif command == "check":
                    print("[!] Not implemented yet")
                    ...
                elif command == "process":
                    # process_raw_dataset()
                    print("[!] Not implemented yet")
                    ...
            else:
                if command != '':
                    print(f"[!] '{command}' command doesn't exist in the program")
        except Exception as err:
            print(f"[!] '{err}'")

def process_queries(cmd_line:list) -> dict:
    queries = dict(
        group=[], patient_num=[], data_types=[]
    )
    qflags ={
        '-g=':"group", '-p=':"patient_num", '-d=':"data_types"
    }
    for arg in cmd_line:
        flag = arg[:3]; query = arg[3:]
        if flag in qflags.keys():
            splitted = query.split(",")
            key = qflags[flag]
            print(splitted)
            for sp in splitted:
                val = sp
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
        elif len(val) == 1:
            val = val[0]
        queries[key] = val
        
    return queries
    
def show_how_to_query():
    info = """
    [?] How to make queries (always use ',' for enums without ' ' after it):
    - 3 options (only in those commands which support it):
    1. '-g=' - Choose one or more groups. Ex: -g=control,MS,NMO
    2. '-p=' - Choose one or more patients (ranges are supported: 1-5,4,12-16). Ex: -p=1-5,8,9 -> [1,2,3,4,5,8,9]
    3. '-d=' - Choose one or more data types. Ex: -g=OCT,retinography,XML
    
    *INFO: For acronyms use upper case, otherwise the query will fail.
    """
    print(info)
        
def print_help():
    print("[?] Commands:")
    for command, info in commands.items():
        print(f"     => '{command}': {info}")
        
    print("[?] Global Commands:")
    for gflag, info in global_flags.items():
        print(f"     => '{gflag}': {info}")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[!] Exit")
        exit(1)