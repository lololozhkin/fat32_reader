from .command import Command
from parsers import Parsers


class HelpCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.help_parser(file=self.cli.out)

    def execute(self, params=''):
        try:
            params = self.split_with_quotes(params)
            args = self.parser.parse_args(params)
        except ValueError:
            return

        if args.command is None:
            for name, command in self.cli.commands.items():
                self.cli.print(f'{name}:')
                command(self.cli).help()
                self.cli.print('--------------------------------')
        else:
            command = args.command
            if command in self.cli.commands:
                self.cli.commands[command](self.cli).help()
            else:
                self.cli.print_error('Command not found')
