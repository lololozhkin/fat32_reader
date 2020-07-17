from FatWorker import FatWorker
import os
import colorama
from colorama import Fore, Style
import argparse


def normalize_path(path):
    path = path.split('/')
    edited_path = []
    for directory in path:
        if directory == '.':
            continue
        if directory == '..':
            edited_path.pop(-1)
        else:
            edited_path.append(directory)
    normalized_path = '/'.join(edited_path)
    if normalized_path.endswith('/'):
        normalized_path = normalized_path[:-1]
    return normalized_path


class CLI:
    def __init__(self, fat_worker: FatWorker):
        self._fat_worker = fat_worker
        self._current_directory = '/'
        self._current_directory_cluster = fat_worker.root_cluster
        colorama.init()

    @property
    def current_dir(self):
        if self._current_directory.startswith('/'):
            return self._current_directory
        else:
            return f'/{self._current_directory}'

    def ls(self, params=None):
        parser = argparse.ArgumentParser(
            prog='ls',
            description='list information about the files '
                        '(the current directory by default)'
        )
        parser.add_argument('-l',
                            action='store_true',
                            help='use a long format')

        parser.add_argument('-a', '--all',
                            action='store_true',
                            help='do not ignore hidden files')

        parser.add_argument('path',
                            metavar='path',
                            nargs='?',
                            help='directory, that has to be shown')

        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return True

        cluster = self._current_directory_cluster
        if args.path is not None:
            try:
                _, cluster = self._try_get_first_cluster_and_path(args.path)
            except ValueError:
                print(f"\n{Fore.RED}No such a directory "
                      f"{Style.RESET_ALL}{args.path}\n")
                return True

        print()
        for file in self._fat_worker.get_all_files_in_dir(cluster):
            if file.name in ('.', '..') and not args.all:
                continue
            if args.l:
                print(file.__str__()[:-len(file.name)], end=' ')
            if file.is_directory:
                print(Fore.BLUE + file.name)
            elif file.is_file:
                print(Fore.LIGHTYELLOW_EX + file.name)
            print(Style.RESET_ALL, end='')
        print()
        return True

    def pwd(self, args=None):
        print(f'\n{Fore.LIGHTCYAN_EX}{self.current_dir}{Style.RESET_ALL}\n')
        return True

    def cd(self, args=None):
        parser = argparse.ArgumentParser(
            prog='cd',
            description='changes current directory',
        )

        parser.add_argument('path', default='/', help='new path')
        try:
            args = parser.parse_args(args.split())
        except SystemExit:
            return True

        args = args.path
        try:
            path, cluster = self._try_get_first_cluster_and_path(args)
            self._current_directory = path
            self._current_directory_cluster = cluster
        except ValueError:
            print(f"\n{Fore.RED}No such a directory {Style.RESET_ALL}{args}\n")
        return True

    def exit(self, params=None):
        self._fat_worker.image.close()
        return False

    def export(self, params=None):
        parser = argparse.ArgumentParser(
            prog='export',
            description='exports file from the image to a disk'
        )
        parser.add_argument('img_path',
                            type=str,
                            help='path in the image of disk'
                            )
        parser.add_argument('disk_path',
                            type=str,
                            help='path of the file in your computer'
                                 ' to copy data from image to it'
                            )
        try:
            args = parser.parse_args(params.split())
        except SystemExit:
            return True

        (disk_path, img_path) = (normalize_path(path)
                                 for path in (args.disk_path, args.img_path))
        try:
            _, file_cluster = self._try_get_first_cluster_and_path(img_path,
                                                                   True)
        except ValueError:
            print(f"\n{Fore.RED}No such a file on disk image "
                  f"{Style.RESET_ALL}{img_path}\n")
            return True

        try:
            with open(disk_path, 'wb') as f:
                for sector in self._fat_worker.get_all_sectors_of_file(
                        file_cluster):
                    f.write(sector)
        except FileNotFoundError:
            print(f"\n{Fore.RED}No such file on your computer "
                  f"{Style.RESET_ALL}{disk_path}\n")
        except PermissionError:
            print(f"\n{Fore.RED}Permission error for file "
                  f"{Style.RESET_ALL}{disk_path}\n")
        return True

    def tree(self, params=None):
        pass

    def _try_get_first_cluster_and_path(self, path, is_file=False):
        dirs_order = list(filter(lambda x: x != '', path.split('/')))
        cur_dir_index = 0
        cur_dir_first_cluster = self._fat_worker.root_cluster \
            if path.startswith('/') \
            else self._current_directory_cluster

        if len(dirs_order) == 0:
            return '/', self._fat_worker.root_cluster

        while True:
            files = self._fat_worker.get_all_files_in_dir(
                cur_dir_first_cluster)
            for file in files:
                legal_path = (file.is_directory
                              or (file.is_file
                                  and cur_dir_index == len(dirs_order) - 1
                                  and is_file))
                if legal_path and file.name == dirs_order[cur_dir_index]:
                    cur_dir_index += 1
                    cur_dir_first_cluster = file.first_cluster
                    if cur_dir_first_cluster == 0:
                        cur_dir_first_cluster = self._fat_worker.root_cluster
                    break
            else:
                raise ValueError("No such a directory")

            if cur_dir_index == len(dirs_order):
                if path.startswith('/'):
                    cur_dir = path
                else:
                    cur_dir = os.path.join(self.current_dir, path)
                cur_dir = normalize_path(cur_dir)
                return cur_dir, cur_dir_first_cluster
