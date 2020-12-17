from .command import Command
from auxiliary.parsers import Parsers


class CatCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.cat_parser(file=self.cli.out)

    def execute(self, params=''):
        try:
            params = self.split_with_quotes(params)
            args = self.parser.parse_args(params)
        except ValueError:
            return

        try:
            for data in self.cli.file_system.get_file_data_by_path(args.path):
                self.cli.print(data.decode(errors='replace'), end='')
            self.cli.print()
        except FileNotFoundError:
            self.cli.print_error("There isn't such file on image", end=' ')
            self.cli.print(args.path)
