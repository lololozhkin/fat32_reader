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
    return '/'.join(edited_path)


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
            description='list information about the files '
                        '(the current directory by default)',
            usage='ls [OPTIONS] [DIRECTORY]')
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
            return

        print()
        for file in self._fat_worker.get_all_files_in_dir(
                self._current_directory_cluster):
            if file.name in ('.', '..') and not args.all:
                continue
            if args.l:
                print(file.__str__()[:-len(file.name)], end=' ')
            if file.is_directory:
                print(Fore.LIGHTMAGENTA_EX + file.name)
            elif file.is_file:
                print(Fore.BLUE + file.name)
            print(Style.RESET_ALL, end='')
        print()

    def pwd(self, params=None):
        print()
        print(Fore.LIGHTCYAN_EX + self.current_dir + Style.RESET_ALL)
        print()

    def cd(self, params=None):
        if params is None:
            params = '/'

        if not isinstance(params, str):
            raise TypeError("parameters have to be in string form")

        if params.count(' ') > 0:
            raise ValueError("Too many parameters")

        if params.startswith('./'):
            params = params[2:]

        dirs_order = list(filter(lambda x: x != '', params.split('/')))
        cur_dir_index = 0
        cur_dir_first_cluster = self._fat_worker.root_cluster \
            if params.startswith('/') \
            else self._current_directory_cluster

        if len(dirs_order) == 0:
            self._current_directory = '/'
            self._current_directory_cluster = self._fat_worker.root_cluster
            return

        while True:
            files = self._fat_worker.get_all_files_in_dir(
                cur_dir_first_cluster)
            for file in files:
                if (file.is_directory
                        and file.name == dirs_order[cur_dir_index]):
                    cur_dir_index += 1
                    cur_dir_first_cluster = file.first_cluster
                    if cur_dir_first_cluster == 0:
                        cur_dir_first_cluster = self._fat_worker.root_cluster
                    break
            else:
                print()
                print(f"{Fore.RED}No such directory{Style.RESET_ALL} {params}")
                print()
                return
            if cur_dir_index == len(dirs_order):
                if params.startswith('/'):
                    self._current_directory = params
                else:
                    self._current_directory = os.path.join(self.current_dir,
                                                           params)
                self._current_directory = normalize_path(
                    self._current_directory)
                self._current_directory_cluster = cur_dir_first_cluster
                break

    def exit(self, params):
        self._fat_worker.image.close()
        return False

    def tree(self, params=None):
        pass
