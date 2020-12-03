from .command import Command
from parsers import Parsers


class CdCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.cd_parser(file=self.cli.out)

    def execute(self, params=''):
        try:
            params = self.split_with_quotes(params)
            args = self.parser.parse_args(params)
        except ValueError:
            return

        directory = args.path
        try:
            self.cli.file_system.cd(directory)
        except FileNotFoundError:
            self.cli.print_error(f"There isn't such directory")
