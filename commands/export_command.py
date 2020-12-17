from .command import Command
from auxiliary.parsers import Parsers


class ExportCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.export_parser(file=self.cli.out)

    def execute(self, params=''):
        try:
            params = self.split_with_quotes(params)
            args = self.parser.parse_args(params)
        except ValueError:
            return

        try:
            self.cli.file_system.export(args.disk_path, args.img_path)
        except FileNotFoundError as e:
            if e.args[0].endswith('image'):
                self.cli.print_error(
                    "There isn't such file or directory on image",
                    end=' '
                )
                self.cli.print(args.img_path)
            else:
                self.cli.print_error(
                    "There isn't such file or directory on your computer",
                    end=' '
                )
                self.cli.print(args.disk_path)
            return
        except PermissionError:
            self.cli.print_error('Permission error')
            return

        self.cli.print('Done')
