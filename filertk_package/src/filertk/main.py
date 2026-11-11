import re 
import sys

from colorama import Fore, Style

from pathlib import Path 

from .file_manager import FileManager 
from .command_reader import CommandReader

INSTRUCTIONS = """fileformatter cmdlet: 
    SPECIAL: 
        exit: exit program early 
        clear_res: clears results file
        clear "file.ext": deletes file from results/

    READ TYPES: 
        match "text": find words that contain the text 
        exact "text": words that only meet the exact input 
        excluding "text" or (num): do not include items of the exact syntax or line number (use for match or from) 
        from (start-end): only modify lines specified 

    WRITE TYPES: 
        with "text": removes only the text that matches with new text 
        replace "text": replaces matches with new text 
        r_append "text": appends text to the end of the matches
        f_append "text": appends text to the front of the matches

    CASING TYPES:
        !keep_case: finds read matches ignoring casing and writes to the same casing style as the replacing text
        !ignore_case: finds read matches ignoring casing, writes each match the same as write casing specified
        !camel_case: with the exact casing of the write provided, it is utilized on all camel cased matches, otherwise fully lowercased/uppercased

    FILE COPY TYPES:
        ~h_copy: creates a copy of the same file name in results folder [defaulted to this]
        ~modify: modified the original file (a backup is creates in results/) 
        ~s_copy "name": creates a copy of the same file with a custom name 

    Writing Commands: 
        simply combine the commands you want in no necessary order, for example: 
            from (1-10) excluding "var_name2" match "var_name" with "new_name" ~h_copy 
"""

def full_res_clear() -> None:
    """Clears every file inside of the results folder"""

    to_delete = [] 

    for file_path in FileManager.RESULTS_DIR.iterdir(): 
        print("\trequested delete: ", file_path) 
        to_delete.append(file_path) 

    validate = input("Are you sure you want to delete all these files? [Y/N]: ").strip() 

    if(validate.lower() == "y"): 
        for file in to_delete: 
            file.unlink(missing_ok=True) 
            print('\t' + str(file) + " deleted successfuly") 
        print(f"{Fore.GREEN}All files in results deleted!{Style.RESET_ALL}") 
    else: 
        print(f"{Fore.GREEN}clear_res was canceled{Style.RESET_ALL}") 


def specify_res_clear(args: list[str]) -> None:
    """Analyzes the tokenized input provided to allocate the file name specified"""

    if(len(args) < 2): 
        print(f"{Fore.YELLOW}filertk clear command was used, but could not find a file identifier{Style.RESET_ALL}")
        return

    if(len(args) > 2):
        print(f"{Fore.YELLOW}filertk clear command was used with too many identifiers; only provide the clear command, and the file name inside the reuslts folder{Style.RESET_ALL}")
        return
    
    file_idn = args[0] if args[0] != CommandReader.CLEAR_CMD else args[1]
    if(not CommandReader.is_name(file_idn)):
        print(f"{Fore.YELLOW}file identifier requires quotations around to ensure it's properly retrieved, make sure there is double quotes both at the front and end of your file's name{Style.RESET_ALL}")

    else:
        to_clear: Path = FileManager.RESULTS_DIR / file_idn[1 : -1]

        if(to_clear.exists):
            to_clear.unlink(missing_ok=True)
            print(f"{Fore.GREEN}{to_clear} successfully deleted{Style.RESET_ALL}")

        else:
            print(f"{Fore.YELLOW}{to_clear} file was not found; are you sure you typed it correctly?{Style.RESET_ALL}")
    return


def read_input(instructions: str, expect_file_dir=False) -> str: 
    user_input = input(instructions)
    result: list[str] = re.findall(CommandReader.TOKEN_PATTERN, user_input)

    if(CommandReader.EXIT_CMD in result):
        print("exit called, closing filertk...")
        sys.exit()

    if(CommandReader.FULL_CLEAR_CMD in result):
        full_res_clear()
        return

    if(CommandReader.CLEAR_CMD in result):
        specify_res_clear(result)
        return

    if(expect_file_dir): 
        if(CommandReader.is_name(user_input)):
            return user_input[1 : -1]
        return user_input
    
    return result


def main(): 
    print(INSTRUCTIONS) 

    user_input: str
    file_path: Path

    while(True):
        user_input = read_input("Enter a file directory: ", expect_file_dir=True)

        if(user_input):
            file_path = Path(user_input)
            if(file_path.exists()): break
        else:
            continue

        print(f"{Fore.YELLOW}\nInvalid file path provided! Make sure your file path is correct\n" 
            + f"\t[provided path: {file_path}{Style.RESET_ALL}]") 

    print("path", file_path, "accepted") 

    args: list[str] | bool = None
    while(not args):
        args = read_input("Enter command instructions:$// ")

    reader = CommandReader(args) 
    manager = FileManager(file_path, reader) 

if __name__ == "__main__": 
    main() 