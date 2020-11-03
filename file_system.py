from fat_worker import FatWorker
import os
import colorama
from collections import defaultdict


def normalize_path(path):
    path = path.split('/')
    edited_path = []
    for directory in path:
        if directory == '.':
            continue
        if directory == '..':
            if len(edited_path):
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
        path, file = self._try_get_path_and_file(self._current_directory)
        file.path = path
        return path

    def ls(self, directory='./'):
        try:
            dir_path, file = self._try_get_path_and_file(directory)
            cluster = file.first_cluster
        except ValueError:
            raise FileNotFoundError("No such directory")

        files = list(self._fat_worker.get_all_files_in_dir(cluster))
        dir_path = '' if dir_path == '/' else dir_path
        for file in files:
            file.path = '/'.join((dir_path, file.name))

        return files

    def cd(self, directory='./'):
        try:
            path, file = self._try_get_path_and_file(directory)
            cluster = file.first_cluster
            file.path = path
            self._current_directory = path
            self._current_directory_cluster = cluster
        except ValueError:
            raise FileNotFoundError(
                f"there isn't such directory {directory}")

    def exit(self):
        self._fat_worker.close()

    def export(self, disk_path, img_path):
        cur_dir = self._current_directory \
            if self._current_directory != '/' \
            else ''

        img_path = normalize_path(cur_dir + normalize_path(img_path))

        try:
            _, file = self._try_get_path_and_file(img_path, True)
        except ValueError:
            raise FileNotFoundError("No such file on disk image")

        try:
            if os.path.isdir(disk_path):
                disk_path = os.path.join(disk_path, file.name)

            open(disk_path, 'wb').close()
            with open(disk_path, 'wb') as f:
                for data in self._fat_worker.get_file_data(file):
                    f.write(data)

        except FileNotFoundError:
            raise FileNotFoundError('No such file on your computer')
        except PermissionError:
            raise PermissionError("Permission error")

    def tree(self, params=None):
        pass

    def walk(self, start_path='/'):
        path, file = self._try_get_path_and_file(start_path)
        path = '' if path == '/' else path
        yield from self._walk(file.first_cluster, path)

    def scan_and_resolve_lost_clusters(self):
        lost_clusters = self._scan_for_lost_cluster_chains()
        if lost_clusters is not None:
            frac = (len(lost_clusters) / self._fat_worker.total_clusters) * 100
            resolve = yield f'Some clusters are lost: \n\n' \
                            f'{frac:.3f}% of sectors are lost'
            if resolve:
                yield 'Restore lost clusters...'
                for cluster in lost_clusters:
                    yield f'restoring cluster {hex(cluster)}'
                    self._fat_worker.write_to_fat(cluster, b'\x00' * 4)
                yield 'Done'
        else:
            res = yield 'Everything is ok'

    def scan_for_intersected_chains(self):
        graph = defaultdict(list)
        reversed_graph = defaultdict(list)
        for file in self.walk('/'):
            chain = list(
                self._fat_worker.get_cluster_chain(file.first_cluster))
            for from_cluster, to_cluster in zip(chain[:-1], chain[1:]):
                graph[from_cluster].append(to_cluster)
                reversed_graph[to_cluster].append(from_cluster)

        res = list(self._find_clusters_before_intersections(reversed_graph))
        if len(res):
            return f'Some cluster-chains are intersected'
        else:
            return f'Everything is ok'

    def _find_clusters_before_intersections(self, reversed_graph):
        intersections = filter(
            lambda x: len(x[1]) > 1, reversed_graph.items())
        return (vertices for _, vertices in intersections)

    def _walk(self, dir_cluster, dir_path):
        return map(lambda x: x[0],
                   self._walk_with_depth(dir_cluster, dir_path))

    def _walk_with_depth(self, dir_cluster, dir_path, depth=0):
        if dir_cluster == self._fat_worker.root_cluster:
            yield self._fat_worker.root_dir_file, 0

        files = self._fat_worker.get_all_files_in_dir(dir_cluster)
        for file in files:
            file.path = '/'.join((dir_path, file.name))

            if file.is_file:
                yield file, depth
            elif file.name not in ('..', '.'):
                yield file, depth
                yield from self._walk_with_depth(file.first_cluster,
                                                 file.path,
                                                 depth + 1)

    def _scan_for_lost_cluster_chains(self):
        true_non_free_clusters = set(
            self._get_all_non_free_clusters())
        fat_non_free_clusters = set(
            self._fat_worker.get_non_free_fat_clusters())

        if len(fat_non_free_clusters) > len(true_non_free_clusters):
            return fat_non_free_clusters.difference(true_non_free_clusters)

    def _get_all_non_free_clusters(self):
        all_files = self.walk('/')
        for file in all_files:
            yield from self._fat_worker.get_cluster_chain(file.first_cluster)

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
                raise ValueError("No such directory")

            if cur_dir_index == len(dirs_order):
                if path.startswith('/'):
                    cur_dir = path
                else:
                    cur_dir = os.path.join(self.current_dir, path)
                cur_dir = normalize_path(cur_dir)
                return cur_dir, cur_file
