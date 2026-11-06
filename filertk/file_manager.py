from pathlib import Path
import shutil
from command_reader import CommandReader, OrderType

class DataFormatter:
    """Used for cleaner and easier access of individual lines and words inside said lines"""

    def __init__(self, line_number=0, words=""):
        self.line_number = line_number
        self.words: list[str] = words.split()
        self.indenter = words[ : len(words) - len(words.lstrip())] if not words.isspace() else ""

    def insert_word(self, word: str, cpos=0):
        self.words.append(word)

class WordMatches:
    """Used for cleaner and easier access of individual matches"""

    def __init__(self, word: str, line_number=0, cpos=0):
        self.word = word
        self.line_number = line_number
        self.cpos = cpos
    

class FileManager:
    """Reviews tokenized instructions and documents changes to file"""

    def __init__(self, original: Path, commands: CommandReader):
        self.__path = original
        self.__commands = commands.get_instructions()

        self.__original_data: list[DataFormatter] = []
        self.read_original()

        self.__matches: list[WordMatches] = []
        self.__instance_changes_ctr = 0

        self.interperit_matcher(self.__commands.get(OrderType.READER))
        self.interperit_writer(self.__commands.get(OrderType.WRITER))
        self.write_to_file()


    def __get_word_index(self, word: str) -> int:
        """returns index of match if found inside of word"""
        search: str = self.__commands[OrderType.IDN][OrderType.READER]
        
        case_rule = self.__commands.get(OrderType.CASE)
        if(case_rule == OrderType.Case.KEEP or case_rule == OrderType.Case.READ_IGNORE): 
            return word.lower().find(search.lower())

        return word.find(search)
    

    def __with_formatter(self, word: str):
        """returns the modified word under the with formatting context"""

        replacement = ""
        index = self.__get_word_index(word)
        to_insert = self.__commands[OrderType.IDN][OrderType.WRITER]

        if(index > -1):
            replacement = word[0 : index] + to_insert + word[index + len(self.__commands[OrderType.IDN][OrderType.READER]) : ]
            self.__instance_changes_ctr += 1

            return replacement


    def __replace_formatter(self, word: str):
        """returns the modified word under the replace formatting context"""

        index = self.__get_word_index(word)
        to_insert = self.__commands[OrderType.IDN][OrderType.WRITER]

        if(index > -1):
            self.__instance_changes_ctr += 1
            return to_insert


    def __append_formatter(self, word: str):
        """returns the modified word under the append formatting context"""

        replacement = ""
        index = self.__get_word_index(word)
        to_insert = self.__commands[OrderType.IDN][OrderType.WRITER]

        if(index > -1):
            word_end = index + len(word)

            if(self.__commands.get(OrderType.Write.R_APPEND)):
                replacement = word[0 : word_end] + to_insert + word[(word_end + len(to_insert)) : ]
            else:
                replacement = word[0 : index] + to_insert + word[index + len(to_insert) : ]

            self.__instance_changes_ctr += 1
            return replacement


    def __update_write_casing(self, match: WordMatches) -> WordMatches:
        """Updates the casing of writer to properly replace text off of KEEP request, returns match inserted (no changes)"""
        
        idn: str = self.__commands[OrderType.IDN]
        original_word: str = self.__original_data[match.line_number - 1].words[match.cpos]

        new_writer_word = idn[OrderType.WRITER]

        if(original_word.upper() == original_word): #picks up on capitalizations automatically
            idn[OrderType.WRITER] = new_writer_word.upper()
            return match

        for i in range(min(len(original_word), len(idn[OrderType.WRITER]))):
            writer_char = new_writer_word[i]
            original_char = original_word[i]
            
            if(original_char.isalpha() and writer_char.isalpha()):
                if(original_char.isupper()):
                    new_writer_word =  new_writer_word[ : i] + writer_char.upper() + new_writer_word[i + 1: ]
                else:
                    new_writer_word = new_writer_word[ : i] + writer_char.lower() + new_writer_word[i + 1: ]

        idn[OrderType.WRITER] = new_writer_word
        return match
          


    def __create_backup(self) -> Path:
        """used for creating backup files of original file"""

        backup_path = Path("results/" + self.__path.stem + "_backup" + self.__path.suffix)
        shutil.copy2(self.__path, backup_path)

        return backup_path

    
    def read_original(self):
        """reads thorugh the original file provided"""
        line_num = 0

        with open(self.__path, 'r') as file:
            for line in file:
                line_num += 1
                self.__original_data.append(DataFormatter(line_num, line))


    def interperit_matcher(self, match_type: OrderType.Read):
        """scans file for matches based off of match type specifier to be modified later"""

        validator = lambda arg: False

        range_based = self.__commands[OrderType.IDN].get(OrderType.Idn.FROM)
        excluding = self.__commands[OrderType.IDN].get(OrderType.Idn.EXCLUDING)
        case_rule = self.__commands.get(OrderType.CASE)

        excluding_handler = lambda _, __: False
        if(isinstance(excluding, str)):
            excluding_handler = lambda arg, _: excluding == arg #range arg in unwated in word exclude

        elif(isinstance(excluding, list)):
            excluding_handler = lambda _, arg: arg < excluding[0] or arg > excluding[1] #word arg is unwanted in range exclude

        match(match_type):
            case(OrderType.Read.MATCH):
                if(case_rule == OrderType.Case.KEEP or case_rule == OrderType.Case.READ_IGNORE):
                    validator = lambda word: (self.__commands[OrderType.IDN][OrderType.READER].lower() in word.lower())

                else:
                    validator = lambda word: (self.__commands[OrderType.IDN][OrderType.READER] in word)

            case(OrderType.Read.EXACT):
                if(case_rule == OrderType.Case.KEEP or case_rule == OrderType.Case.READ_IGNORE):
                    validator = lambda word: (self.__commands[OrderType.IDN][OrderType.READER].lower() == word.lower())

                else:
                    validator = lambda word: (self.__commands[OrderType.IDN][OrderType.READER] == word)

        for data in self.__original_data:
            for word_pos in range(len(data.words)):
                word = data.words[word_pos]

                if(range_based and (data.line_number >= range_based[0] or data.line_number <= range_based[1])):
                    break

                if(excluding_handler(word, data.line_number)):
                    continue
                
                if(validator(word)): 
                    self.__matches.append(WordMatches(word, data.line_number, word_pos))


    def interperit_writer(self, write_type: OrderType.WRITER):
        """modifies matches found in file to specified write type"""

        formatter = None
        match(write_type):
            case OrderType.Write.WITH:
                formatter = lambda match: self.__with_formatter(match.word)

            case OrderType.Write.REPLACE:
                formatter = lambda match: self.__replace_formatter(match.word)

            case OrderType.Write.APPEND:
                formatter = lambda match: self.__append_formatter(match.word)

        handler = formatter
        if(self.__commands.get(OrderType.CASE) == OrderType.Case.KEEP):
            if(len(self.__commands[OrderType.IDN][OrderType.WRITER]) != len(self.__commands[OrderType.IDN][OrderType.READER])):
                print("WARNING: !casing_kp [keep casing to match] request was made, but reader and writer identifiers differ in size.\n" \
                + "\tResults may not be as expected due to size mismatch.")

            handler = lambda match: formatter(self.__update_write_casing(match))

        for match in self.__matches:
            self.__original_data[match.line_number - 1].words[match.cpos] = handler(match)

        print(self.__instance_changes_ctr, "instance changes made in file", self.__path)
            

    def write_to_file(self):
        """takes all data collected & modified from original file & writes it into instructed file"""

        file_mode = self.__commands.get(OrderType.COPY)
        file_path: Path

        if(not file_mode):
            print("WARNING: FileManager write_to_file() detected no copy command from command list.\n"
                + "\tFileManager write_to_file() is defaulting to hard copy [~h_copy]")
            
            file_mode = OrderType.Copy.HARD

        match(file_mode):
            case OrderType.Copy.HARD:
                file_path = "results/" + self.__path.name

            case OrderType.Copy.SOFT:
                requested_name = self.__commands[OrderType.IDN].get(OrderType.COPY)

                if(not requested_name):
                    raise ValueError("FileManager write_to_file() was provided with ~s_copy() but recieved no identifier for file name; did you specify one?\n"
                        + "\t~s_copy requires a name for the file, make sure you wrote one!")
                file_path = "results/" + requested_name

            case OrderType.Copy.MODIFY:
                file_path = self.__path
                backup = self.__create_backup()

                print("~modify copy type created a backup file at:", backup)

        with open(file_path, 'w') as file:
            for data in self.__original_data:
                file.write(data.indenter)
                
                for word in data.words:
                    file.write(word + ' ')
                file.write('\n')