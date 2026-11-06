import re 
import sys 
from pathlib import Path 

from file_manager import FileManager 
from command_reader import CommandReader 

INSTRUCTIONS = """fileformatter cmdlet: 
    SPECIAL: 
        exit: exit program early 
        clear_res: clears results file 

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
        !case_ign: ignores the casing inside the file, only writes the kind provided [defaulted to this]
        !case_kp: finds read matches ignoring casing and writes to the same casing style as the replacing text
        !r_case_ign: only finds read matches ignoring casing, writes each match the same as write casing specified

    FILE COPY TYPES:
        ~h_copy: creates a copy of the same file name in results folder [defaulted to this]
        ~modify: modified the original file (a backup is creates in results/) 
        ~s_copy "name": creates a copy of the same file with a custom name 

    Writing Commands: 
        simply combine the commands you want in no necessary order, for example: 
            from (1-10) excluding "var_name2" match "var_name" with "new_name" ~h_copy 
"""

def read_input(instructions: str) -> str: 
    EXIT = r'(?<!["\'])exit(?!["\'])' 
    FULL_CLEAR = r'(?<!["\'])clear_res(?!["\'])' 

    result = input(instructions) 

    if( bool(re.search(EXIT, result.lower())) ): 
        print("exit called on program, closing...") 
        sys.exit() 

    if( bool(re.search(FULL_CLEAR, result.lower())) ): 
        parent_dir = Path(__file__).resolve().parent 
        results_dir = Path(str(parent_dir) + "/results") 

        to_delete = [] 

        for file_path in results_dir.iterdir(): 
            print("\trequested delete: ", file_path) 
            to_delete.append(file_path) 

        validate = input("Are you sure you want to delete all these files? [Y/N]: ").strip() 

        if(validate.lower() == "y"): 
            for file in to_delete: 
                file.unlink(missing_ok=True) 
                print('\t' + str(file) + " deleted successfuly") 
            print("All files in results deleted!") 
        else: 
            print("clear_res was canceled") 

        print("closing program (after clearing res, program will always reset)") 
        sys.exit() 

    return result 


def main(): 
    print(INSTRUCTIONS) 

    file_path = Path(read_input("Enter a file directory: ").strip('"')) 

    while(not file_path.exists()): 
        print("\nInvalid file path provided! Make sure your file path is correct\n" 
            + "\t[provided path: " + str(file_path) + "]") 

        file_path = Path(read_input("Enter a file directory: ").strip('"'))

    print("path '" + str(file_path) + "' accepted") 

    reader = CommandReader(read_input("Enter command instructions:$// ")) 
    manager = FileManager(file_path, reader) 

if __name__ == "__main__": 
    main() 