
import sys

from process_raw_dataset import process_raw_dataset, raw_dataset, clean_dataset

commands = {
    'raw': "Shows raw dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s)",
    'clean': "Shows clean dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s)",
    'check': "Shows the difference between the 2 datasets. Is usefull to see if there is available data to process",
    'process': "Processes the entire raw dataset (add -o to override existing clean files)"
}

def main():
    print_help()
    print(" -  Enter command: ")
    valid_command = False
    while not valid_command:
        command_line = str(input("> ")).split(" ")
        command = command_line[0]
        print(command_line, command)
        if command in commands:
            valid_command = True
            if command == 'raw':
                # Info del raw_dataset
                if len(command_line) > 1:
                    # 2 posibles modos, toda la info, solo la sobrante, solo el summary
                    mode = command_line[1]
                    if mode == '-m':
                        raw_dataset.show_info(only_missing_info=True)
                    elif mode == '-s':
                        raw_dataset.show_info(only_summary=True)
                    else:
                        print(f"[!] '{mode}' is not a valid mode")
                        valid_command = False
                else:
                    raw_dataset.show_info()
            elif command == 'clean':
                # Info del raw_dataset
                if len(command_line) > 1:
                    # 2 posibles modos, toda la info, solo la sobrante, solo el summary
                    if mode == '-m':
                        clean_dataset.show_info(only_missing_info=True)
                    elif mode == '-s':
                        clean_dataset.show_info(only_summary=True)
                    else:
                        print(f"[!] '{mode}' is not a valid mode")
                        valid_command = False
                else:
                    clean_dataset.show_info()
            elif command == "check":
                print("[!] Not implemented yet")
                valid_command = False
                ...
            elif command == "process":
                # process_raw_dataset()
                print("[!] Not implemented yet")
                valid_command = False
                ...
        else:
            print(f"[!] '{command}' command doesn't exist in the program")
    args = sys.argv; args.pop(0)
        
            
def print_help():
    print("[?] Commands:")
    for command, info in commands.items():
        print(f"     - {command}: {info}")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[!] Exit")
        exit(1)
    except Exception as err:
        print(f"[!] Unexpected Error: {err}")
        input("-> Press Enter to exit")
        exit(1)