import sys

from auxiliary.file_system import FileSystem

from commands import (
    CatCommand, CdCommand, ExportCommand, HelpCommand,
    LsCommand, PwdCommand, ScanCommand, XxdCommand
)

from colorama import Fore, Style


class CLI:
    def __init__(self, file_system: FileSystem, testing=False, out=sys.stdout):
        self.file_system = file_system
        self._testing = testing
        self.out = out
        self.commands = {
            'cat': CatCommand,
            'cd': CdCommand,
            'export': ExportCommand,
            'ls': LsCommand,
            'pwd': PwdCommand,
            'scan': ScanCommand,
            'xxd': XxdCommand,
            'help': HelpCommand
        }

    def execute_command(self, command, params=''):
        if command not in self.commands:
            self.print_error("Command not found")
            return
        to_execute = self.commands[command](self)
        to_execute.execute(params)

    @property
    def dir_color(self):
        return '' if self._testing else Fore.LIGHTCYAN_EX

    @property
    def file_color(self):
        return '' if self._testing else Fore.LIGHTYELLOW_EX

    @property
    def err_color(self):
        return '' if self._testing else Fore.RED

    @property
    def reset_all(self):
        return '' if self._testing else Style.RESET_ALL

    def print(self, data='', sep=' ', end='\n'):
        print(data, file=self.out, sep=sep, end=end)

    def print_with_color(self, data, color, sep=' ', end='\n'):
        data = f'{color}{data}{self.reset_all}'
        self.print(data, sep, end)

    def print_error(self, data='', sep=' ', end='\n'):
        self.print_with_color(data, self.err_color, sep, end)
