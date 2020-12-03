from abc import ABC, abstractmethod
import re


class Command(ABC):
    split_regexp = re.compile(r'\'[^\']*\'|\"[^\"]*\"|[^ ]+')

    def __init__(self, cli):
        self.cli = cli

    @staticmethod
    def split_with_quotes(params: str):
        params = re.findall(Command.split_regexp, params)
        s = ''
        return [param.strip('\'\"') for param in params]

    @abstractmethod
    def execute(self, params=''):
        pass

    def help(self):
        self.cli.print(self.parser.format_help())
