import re
from enum import Enum

class ReadType(Enum):
    """Enum of all reader OrderTypes"""
    MATCH = 1
    EXACT = 2

class WriteType(Enum):
    """Enum of all Writer OrderTypes"""
    WITH = 1
    REPLACE = 2
    R_APPEND = 3
    F_APPEND = 4

class CopyType(Enum):
    """Enum of all Copy OrderTypes"""
    HARD = 1
    SOFT = 2
    MODIFY = 3

class IdentifierType(Enum):
    """Enum of all identifier OrderTypes"""
    READER = 1
    WRITER = 2
    FROM = 3
    EXCLUDING = 4

class CaseType(Enum):
    """Enum of all Casing OrderTypes"""
    KEEP = 1
    IGNORE = 2
    CAMEL = 3

class OrderType(Enum):
    READER = 1
    WRITER = 2
    COPY = 3
    IDN = 4
    CASE = 5

OrderType.Read = ReadType
OrderType.Write = WriteType
OrderType.Copy = CopyType
OrderType.Idn = IdentifierType
OrderType.Case = CaseType

class CommandReader:
    TOKEN_PATTERN = r'"[^"]*"|\S+'

    EXIT_CMD = "exit"
    FULL_CLEAR_CMD = "clear_res"
    CLEAR_CMD = "clear"

    ARG_TYPES = {
        "match": ReadType.MATCH,
        "exact": ReadType.EXACT,

        "excluding": IdentifierType.EXCLUDING,
        "from": IdentifierType.FROM,

        "with": WriteType.WITH,
        "replace": WriteType.REPLACE,
        "r_append": WriteType.R_APPEND,
        "f_append": WriteType.F_APPEND,

        "!keep_case": CaseType.KEEP,
        "!ignore_case": CaseType.IGNORE,
        "!camel_case": CaseType.CAMEL,

        "~h_copy": CopyType.HARD,
        "~modify": CopyType.MODIFY,
        "~s_copy": CopyType.SOFT
    }

    def __init__(self, commands: list[str]):
        """Tokenizes & verifies commands given to terminal"""
        self.__args = commands
        self.__instructions = { OrderType.IDN: {}}
        self.__identifier_queue: list[IdentifierType] = []

        self.set_instructions()


    @staticmethod
    def is_name(potential_name: str) -> bool:
        """Used for checking if a name identifier token is provided"""
        if(len(potential_name) <= 2): return False

        if(potential_name[0] == '"' and potential_name[-1] == '"'): return True
            
        return False


    @staticmethod
    def is_range(potential_range: str) -> bool:
        """Used for checking if a range identifier token is provided"""

        if(potential_range[0] == "(" and potential_range[-1] == ")"): return True
        
        return False


    @staticmethod
    def get_range_nums(range_token: str) -> list[int, int]:
        """grabs ranges for FROM identifier, returns [start, end]"""

        numbers = re.findall(r'\d+', range_token)
        numbers = [int(num) for num in numbers]

        if(len(numbers) != 2):
            raise ValueError(
                "CommandReader get_rane_nums() was given an invalid amount of range values provided for FROM, received: " 
                + len(numbers))

        return numbers


    def handle_identifier(self, idn: str) -> None:
        """handles identifier queue status & allocation of identifiers with corresponding type"""

        if(len(idn) < 3):
            raise ValueError("CommandReader handle_identifier() found an identifier with not enough characters.\n"
                + "[identifier: " + idn + "]\n"
                + "make sure identifiers have a starting and ending quotation, with all characters inbetween")

        if(self.__identifier_queue == 0):
            raise ValueError("CommandReader handle_identifier() found an identifier but did not know where to place it\n"
                + "\t[identifier: " + idn + "]\n"
                + "make sure your identifiers have an identifier type (readers, writers, from, excluding) before writing them")

        if(idn[0] != '"' or idn[-1] != '"'):
            raise ValueError("CommandReader handle_identifier found an identifier lacking proper quotations.\n" 
                + "\t[identifier: " + idn + "]\n"
                + "make sure all identifiers have leading and trailing quotations, with all characters inbetween")

        self.__instructions[OrderType.IDN][self.__identifier_queue[0]] = idn[1 : -1] #to remove quotations from checks
        self.__identifier_queue.pop(0)


    def set_instructions(self):
        """Reads through the args list and updates the instructions dictionary"""

        for arg in self.__args:
            arg_type = CommandReader.ARG_TYPES.get(arg)

            if(arg_type):
                match arg_type:
                    case ReadType():
                        self.__instructions[OrderType.READER] = arg_type
                        self.__identifier_queue.append(OrderType.READER)

                    case WriteType():
                        self.__instructions[OrderType.WRITER] = arg_type
                        self.__identifier_queue.append(OrderType.WRITER)

                    case CopyType():
                        self.__instructions[OrderType.COPY] = arg_type

                        if(arg_type == CopyType.SOFT):
                            self.__identifier_queue.append(OrderType.COPY)

                    case IdentifierType():
                        self.__identifier_queue.append(arg_type)

                    case CaseType():
                        self.__instructions[OrderType.CASE] = arg_type

            elif(CommandReader.is_name(arg)):
                self.handle_identifier(arg)

            elif(CommandReader.is_range(arg)):
                if(self.__identifier_queue[0] == IdentifierType.EXCLUDING):
                    self.__instructions[OrderType.IDN][IdentifierType.EXCLUDING] = CommandReader.get_range_nums(arg)
                    self.__identifier_queue.pop(0)
                else:
                    self.__instructions[OrderType.IDN][IdentifierType.FROM] = CommandReader.get_range_nums(arg)
                    self.__identifier_queue.pop(0)

            else:
                raise ValueError("CommandReader set_instructions() detected an unexpected token, only use the token types specified"
                    + " or ensure text specifications use \" before and after (ex: \"text\")\n"
                    + "\t[token interpereted: " + arg + "]")


    def get_instructions(self):
        return self.__instructions