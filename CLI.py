from file_system import FileSystem
from colorama import Fore, Style
from parsers import Parsers


class CLI:
    def __init__(self, file_system: FileSystem, testing=False):
        self.file_system = file_system
        self._testing = testing

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
            return []

        try:
            files = self.file_system.ls(args.path)
        except FileNotFoundError as e:
            return [f'{self.err_color}No such directory {args.path}']

        response = []
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
            response.append(cur_response)

        return response

    def pwd(self, params=None):
        parser = Parsers.pwd_parser()
        if params is not None:
            try:
                args = parser.parse_args(params.split())
            except SystemExit:
                return []

        current_dir = self.file_system.current_dir
        return [f'{self.dir_color}{current_dir}{self.reset_all}']

    def cd(self, params=None):
        parser = Parsers.cd_parser()
        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return []

        directory = args.path
        try:
            self.file_system.cd(directory)
        except FileNotFoundError:
            return [
                f"{self.err_color}There isn't such directory{self.reset_all}"
            ]
        return []

    def export(self, params=None):
        parser = Parsers.export_parser()

        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return []

        try:
            self.file_system.export(args.disk_path, args.img_path)
        except FileNotFoundError as e:
            if e.args[0].endswith('image'):
                return [f"{self.err_color}there isn't such file on image "
                        f"{self.reset_all}{args.img_path}"]
            else:
                return [f"{self.err_color}"
                        f"There isn't such file on your computer"
                        f"{self.reset_all}{args.disk_path}"]
        except PermissionError as e:
            return [f"{self.err_color}Permission error{self.reset_all}"]

        return ["Done"]

    def scan(self, intersection, lost):
        if lost:
            yield from self._scan_for_lost_clusters()
        if intersection:
            yield from self._scan_for_intersected_chains()

    @staticmethod
    def help(params=None):
        ans = '\n'.join(['ls: shows directories and files',
                         'pwd: prints current directory',
                         'export: exports file from image to your computer',
                         'cd: changes current directory',
                         '',
                         'for more information type command --help'])
        return [ans]

    def _scan_for_lost_clusters(self):
        yield 'Scanning for lost clusters...'
        res = self.file_system.scan_lost_clusters()
        yield 'Scan finished'
        yield res
        yield '\n'

    def _scan_for_intersected_chains(self):
        yield 'Scanning for intersected chains...'
        res = self.file_system.scan_for_intersected_chains()
        yield 'Scan finished'
        yield res
        yield '\n'
