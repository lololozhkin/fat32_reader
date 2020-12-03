from .command import Command
from parsers import Parsers


class ScanCommand(Command):
    def __init__(self, cli):
        super().__init__(cli)
        self.parser = Parsers.scan_parser(file=self.cli.out)

    def execute(self, params=''):
        if params == '':
            self.cli.print(self.parser.format_usage())
            return

        try:
            params = self.split_with_quotes(params)
            args = self.parser.parse_args(params)
        except ValueError:
            return

        if args.command_name == 'lost':
            if args.directory is not None:
                restore_args = {'restore': True, 'directory': args.directory}
            else:
                restore_args = {}

            for res in self._scan_restore_lost_clusters(**restore_args):
                self.cli.print(res)
        else:
            for res in self._scan_resolve_intersected_chains(args.resolve):
                self.cli.print(res)

    def _scan_restore_lost_clusters(self, restore=False, directory=None):
        yield 'Scanning for lost clusters...'
        res = self.cli.file_system.scan_and_recover_lost_cluster_chains(
            restore,
            directory
        )
        frac = next(res)
        yield 'Scan finished'
        yield frac
        try:
            yield from res
        except StopIteration:
            pass

    def _scan_resolve_intersected_chains(self, resolve=False):
        yield 'Scanning for intersected chains...'
        res = self.cli.file_system.scan_and_resolve_intersected_chains(resolve)
        next_out = next(res)
        yield 'Scan finished'
        yield next_out
        try:
            yield from res
        except StopIteration:
            pass
