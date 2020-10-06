from FileSystem import FileSystem
from colorama import Fore, Style
from Parsers import Parsers


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
        return '' if self._testing else self.reset_all

    def ls(self, params=None):
        parser = Parsers.ls_parser()

        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return True

        try:
            files = self.file_system.ls(args.path)
        except FileNotFoundError as e:
            return [f'{self.err_color}No such a directory {args.path}']

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
                return True

        current_dir = self.file_system.current_dir
        return [f'{self.dir_color}{current_dir}{self.reset_all}']

    def cd(self, params=None):
        parser = Parsers.cd_parser()
        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            pass

        directory = args.path
        try:
            self.file_system.cd(directory)
        except FileNotFoundError:
            return [
                f"{self.err_color}There isn't such a directory{self.reset_all}"
            ]
        return []

    def export(self, params=None):
        parser = Parsers.export_parser()

        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return True

        try:
            self.file_system.export(args.disk_path, args.img_path)
        except FileNotFoundError as e:
            if e.args[0].endswith('image'):
                return f"{self.err_color}there isn't such a file on image" \
                       f"{self.reset_all}{args.img_path}"
            else:
                return f"{self.err_color}There isn't such a file on your computer" \
                       f"{self.reset_all}{args.disk_path}"
        except PermissionError as e:
            return f"{self.err_color}Permission error{self.reset_all}"
