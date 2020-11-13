import sys

from file_system import FileSystem
from colorama import Fore, Style
from parsers import Parsers


class CLI:
    def __init__(self, file_system: FileSystem, testing=False, out=sys.stdout):
        self.file_system = file_system
        self._testing = testing
        self.out = out


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

    def ls(self, params=None):
        parser = Parsers.ls_parser()

        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return

        try:
            files = self.file_system.ls(args.path)
        except FileNotFoundError as e:
            print(
                f'{self.err_color}No such directory {args.path}',
                file=self.out
            )
            return

        for file in files:
            if file.name.startswith('.') and not args.all:
                continue
            cur_response = ""
            if args.l:
                cur_response += f'{str(file)[:-len(file.name)]} '
            if file.is_directory:
                cur_response += f'{self.dir_color}{file.name}'
            elif file.is_file:
                cur_response += f'{self.file_color}{file.name}'
            cur_response += self.reset_all

            print(cur_response, file=self.out)

    def pwd(self, params=None):
        parser = Parsers.pwd_parser()
        if params is not None:
            try:
                args = parser.parse_args(params.split())
            except SystemExit:
                return

        current_dir = self.file_system.current_dir
        print(f'{self.dir_color}{current_dir}{self.reset_all}', file=self.out)

    def cd(self, params=None):
        parser = Parsers.cd_parser()
        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return

        directory = args.path
        try:
            self.file_system.cd(directory)
        except FileNotFoundError:
            print(
                f"{self.err_color}There isn't such directory{self.reset_all}",
                file=self.out
            )

    def export(self, params=None):
        parser = Parsers.export_parser()

        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return

        try:
            self.file_system.export(args.disk_path, args.img_path)
        except FileNotFoundError as e:
            if e.args[0].endswith('image'):
                print(
                    f"{self.err_color}There isn't such file on image "
                    f"{self.reset_all}{args.img_path}",
                    file=self.out
                )
            else:
                print(
                    f"{self.err_color}"
                    f"There isn't such file on your computer "
                    f"{self.reset_all}{args.disk_path}",
                    file=self.out
                )
            return
        except PermissionError as e:
            print(
                f"{self.err_color}Permission error{self.reset_all}",
                file=self.out
            )
            return

        print("Done", file=self.out)

    def scan(self, params=None):
        parser = Parsers.scan_parser()

        if params == '':
            print(parser.format_usage(), file=self.out)
            return

        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return

        if args.command_name == 'lost':
            if args.directory is not None:
                restore_args = {'restore': True, 'directory': args.directory}
            else:
                restore_args = {}

            for res in self._scan_restore_lost_clusters(**restore_args):
                print(res, file=self.out)
        else:
            for res in self._scan_for_intersected_chains():
                print(res, file=self.out)

    def help(self, params=None):
        ans = '\n'.join(['ls: shows directories and files',
                         'pwd: prints current directory',
                         'export: exports file from image to your computer',
                         'cd: changes current directory',
                         '',
                         'for more information type *command* --help'])
        print(ans, file=self.out)

    def cat(self, params=None):
        parser = Parsers.cat_parser()
        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return

        for data in self.file_system.cat(args.path):
            data: bytes
            print(data.decode(errors='ignore'), file=self.out, end='')
        print(file=self.out)

    def _scan_restore_lost_clusters(self, restore=False, directory=None):
        yield 'Scanning for lost clusters...'
        res = self.file_system.scan_and_recover_lost_cluster_chains(
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

    def _scan_for_intersected_chains(self):
        yield 'Scanning for intersected chains...'
        res = self.file_system.scan_for_intersected_chains()
        yield 'Scan finished'
        yield res
