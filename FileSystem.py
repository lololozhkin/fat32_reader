from FatWorker import FatWorker
import os
import colorama
from colorama import Fore, Style
import argparse


DIR_COLOR = Fore.LIGHTCYAN_EX
FILE_COLOR = Fore.LIGHTYELLOW_EX
ERR_COLOR = Fore.RED


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
    if not normalized_path.startswith('/'):
        normalized_path = '/' + normalized_path
    return normalized_path


class FileSystem:
    def __init__(self, fat_worker: FatWorker):
        self._fat_worker = fat_worker
        self._current_directory = '/'
        self._current_directory_cluster = fat_worker.root_cluster
        colorama.init()

    @property
    def current_dir(self):
        return self._try_get_path_and_file(self._current_directory)[0]

    def ls(self, directory='./'):
        try:
            _, file = self._try_get_path_and_file(directory)
            cluster = file.first_cluster
        except ValueError:
            raise FileNotFoundError("No such a directory")

        return self._fat_worker.get_all_files_in_dir(cluster)

    def cd(self, directory='./'):
        try:
            path, file = self._try_get_path_and_file(directory)
            cluster = file.first_cluster
            self._current_directory = path
            self._current_directory_cluster = cluster
        except ValueError:
            raise FileNotFoundError(
                f"there isn't such a directory {directory}")
        return True

    def exit(self, params=None):
        self._fat_worker.image.close()
        return False

    def export(self, disk_path, img_path):
        disk_path = normalize_path(disk_path)
        img_path = normalize_path(self._current_directory
                                  + normalize_path(img_path))

        try:
            _, file = self._try_get_path_and_file(img_path, True)
        except ValueError:
            raise FileNotFoundError("No such a file on disk image")

        try:
            open(disk_path, 'wb').close()
            with open(disk_path, 'wb') as f:
                for data in self._fat_worker.get_file_data(file):
                    f.write(data)
        except FileNotFoundError:
            raise FileNotFoundError('No such a file on your computer')
        except PermissionError:
            raise PermissionError("Permission error")
        return True

    def tree(self, params=None):
        pass

    def _try_get_path_and_file(self, path, is_file=False):
        if not path.startswith('/'):
            path = normalize_path(os.path.join(self._current_directory, path))

        dirs_order = list(filter(lambda x: x != '', path.split('/')))
        cur_dir_index = 0
        cur_dir_first_cluster = self._fat_worker.root_cluster \
            if path.startswith('/') \
            else self._current_directory_cluster

        if len(dirs_order) == 0:
            return '/', self._fat_worker.root_dir_file

        cur_file = None
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
                    cur_file = file
                    if cur_dir_first_cluster == 0:
                        cur_dir_first_cluster = self._fat_worker.root_cluster
                        cur_file = self._fat_worker.root_dir_file
                    break
            else:
                raise ValueError("No such a directory")

            if cur_dir_index == len(dirs_order):
                if path.startswith('/'):
                    cur_dir = path
                else:
                    cur_dir = os.path.join(self.current_dir, path)
                cur_dir = normalize_path(cur_dir)
                return cur_dir, cur_file
