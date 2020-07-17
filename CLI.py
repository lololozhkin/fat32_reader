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
            return True

        print()
        for file in self._fat_worker.get_all_files_in_dir(
                self._current_directory_cluster):
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

    def pwd(self):
        print()
        print(Fore.LIGHTCYAN_EX + self.current_dir + Style.RESET_ALL)
        print()
        return True

    def cd(self, args=None):
        parser = argparse.ArgumentParser(
            description='changes current directory',
            usage='cd PATH')

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

    def exit(self, params):
        self._fat_worker.image.close()
        return False

    def tree(self, params=None):
        pass

    def _try_get_first_cluster_and_path(self, path):
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
                if (file.is_directory
                        and file.name == dirs_order[cur_dir_index]):
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
