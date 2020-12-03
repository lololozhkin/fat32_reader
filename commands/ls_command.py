from .command import Command
from parsers import Parsers


class LsCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.ls_parser(file=self.cli.out)

    def execute(self, params=''):
        params = self.split_with_quotes(params)
        try:
            args = self.parser.parse_args(params)
        except ValueError:
            return

        try:
            files = self.cli.file_system.ls(args.path)
        except FileNotFoundError:
            self.cli.print_error(f'No such directory {args.path}')
            return

        for file in files:
            if file.name.startswith('.') and not args.all:
                continue
            if args.l:
                self.cli.print(str(file)[:-len(file.name)], end=' ')
            if file.is_directory:
                self.cli.print_with_color(file.name, self.cli.dir_color)
            elif file.is_file:
                self.cli.print_with_color(file.name, self.cli.file_color)
