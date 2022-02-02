
from colorama import Fore

class Printer():

    prefix: str

    def __init__(self, bot_name=''):
        self.prefix = f' ** [{bot_name}] '
        
    def title(self, message):
        prefix = f'\n ***** '
        suffix = f' ***** '
        print(Fore.BLUE + prefix + message + suffix)

    def info(self, message):
        print(self.prefix + message)

    def r_info(self, message):
        print(self.prefix + message, end='\r')

    def r_warn(self, message):
        print(Fore.YELLOW + self.prefix + message, end='\r')

    def error(self, message):
        print(Fore.RED + self.prefix + message)