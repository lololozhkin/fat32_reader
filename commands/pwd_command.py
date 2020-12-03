from .command import Command
from parsers import Parsers


class PwdCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.pwd_parser(file=self.cli.out)

    def execute(self, params=''):
        if params is not None:
            try:
                params = self.split_with_quotes(params)
                args = self.parser.parse_args(params)
            except ValueError:
                return

        current_dir = self.cli.file_system.current_dir
        self.cli.print_with_color(current_dir, self.cli.dir_color)
