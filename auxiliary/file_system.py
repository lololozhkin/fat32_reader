import itertools
import os
import colorama
from typing import Union, Iterable
from .fat_worker import FatWorker
from .file import File


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


def get_not_taken_index(directory):
    existing_files = os.listdir(directory)
    lost_files_dirs_indexes = []
    for file in existing_files:
        path = os.path.join(directory, file)

        if (os.path.isdir(path)
                and file.startswith('lost_files')
                and file[len('lost_files'):].isdigit()):
            lost_files_dirs_indexes.append(int(file[len('lost_files'):]))

    if len(lost_files_dirs_indexes) > 0:
        indexes = list(sorted(lost_files_dirs_indexes))
        indexes.append(indexes[-1] + 2)
        needed_ind = -1
        for cur, nxt in zip(indexes[:-1], indexes[1:]):
            if nxt - cur > 1:
                needed_ind = cur + 1
                break
    else:
        needed_ind = 0

    return needed_ind


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
                f"there isn't such directory {directory}"
            )

    def exit(self):
        self._fat_worker.close()

    def export(self, disk_path, img_path):
        cur_dir = self._current_directory \
            if self._current_directory != '/' \
            else ''

        img_path = normalize_path(cur_dir + normalize_path(img_path))

        try:
            path, file = self._try_get_path_and_file(img_path, True)
        except ValueError:
            raise FileNotFoundError("No such file on disk image")

        if file.is_directory:
            name = file.name if file.name != '/' else 'fat_image_files/'
            disk_path = os.path.join(disk_path, name)
            os.makedirs(disk_path, exist_ok=True)

            for file in self.walk(path):
                if file.is_file:
                    disk_file_path = disk_path + file.path[len(path):]
                    open(disk_file_path, 'wb').close()
                    with open(disk_file_path, 'wb') as f:
                        for data in file.data():
                            f.write(data)
                elif file.is_directory:
                    disk_dir_path = disk_path + file.path[len(path):]
                    os.makedirs(disk_dir_path, exist_ok=True)
            return

        try:
            if os.path.isdir(disk_path):
                disk_path = os.path.join(disk_path, file.name)

            open(disk_path, 'wb').close()
            with open(disk_path, 'wb') as f:
                for data in file.data():
                    f.write(data)

        except FileNotFoundError:
            raise FileNotFoundError('There is not such file on your computer')

    def get_file_data_by_path(self, file_path):
        try:
            _, file = self._try_get_path_and_file(file_path, is_file=True)
            if not file.is_file:
                raise ValueError
        except ValueError:
            raise FileNotFoundError('There is not such file on image')

        yield from file.data()

    def walk(self, start_path='/') -> Iterable[Union[File, int]]:
        path, file = self._try_get_path_and_file(start_path)
        path = '' if path == '/' else path
        yield from self._walk(file.first_cluster, path)

    def scan_and_recover_lost_cluster_chains(
            self,
            recover=False,
            directory=''
    ):
        result = self._scan_for_lost_cluster_chains()
        if result is not None:
            real_chains, fat_chains = result
            real_non_free_clusters = set(
                itertools.chain(*(chain_ for chain_ in real_chains))
            )
            fat_non_free_clusters = set(
                itertools.chain(*(chain_ for chain_ in fat_chains))
            )
            lost_clusters = len(
                fat_non_free_clusters.difference(real_non_free_clusters)
            )

            frac = (lost_clusters / self._fat_worker.total_clusters) * 100
            yield f'Some clusters are lost: \n\n' \
                  f'{frac:.3f}% of sectors are lost'

            if recover:
                yield f'Recovering lost files into {directory} ...'
                lost_chains = fat_chains.difference(real_chains)
                self._recover_lost_files(
                    lost_chains,
                    real_non_free_clusters,
                    directory
                )
                yield 'Recovering completed'
        else:
            yield 'Everything is ok'
            return

    def scan_and_resolve_intersected_chains(self, resolve=False):
        used = set()
        for file in self.walk('/'):
            for cl in self._fat_worker.get_cluster_chain(file.first_cluster):
                if cl in used:
                    yield 'Some cluster-chains are intersected'
                    if not resolve:
                        return

                    yield 'Copying clusterchains...'
                    self._resolve_intersected_chains()
                    yield 'Copying ended'
                    return
                used.add(cl)

        yield f'Everything is ok'

    def _resolve_intersected_chains(self):
        used = set()
        free_clusters = self._fat_worker.get_free_clusters()
        for file in self.walk('/'):
            prev_cluster = -1
            for cl in self._fat_worker.get_cluster_chain(file.first_cluster):
                if cl not in used:
                    used.add(cl)
                    prev_cluster = cl
                    continue
                chain_tail = list(self._fat_worker.get_cluster_chain(cl))
                copy_clusters = []
                for free_cluster in free_clusters:
                    copy_clusters.append(free_cluster)
                    if len(copy_clusters) == len(chain_tail):
                        break
                else:
                    raise ValueError(
                        "You dont have free space enough to "
                        "copy all intersected chains"
                    )

                self._copy_clusters(chain_tail, copy_clusters)
                if prev_cluster != -1:
                    self._fat_worker.write_to_fat(
                        prev_cluster,
                        copy_clusters[0]
                    )
                    break

    def _copy_clusters(self, from_clusters, to_clusters):
        if len(from_clusters) > len(to_clusters):
            raise ValueError(
                'Not enough clusters to place the copy'
            )
        prev_copy_cluster = -1
        for from_cl, to_cl in zip(from_clusters, to_clusters):
            data = self._fat_worker.read_cluster(from_cl)
            self._fat_worker.write_data_to_cluster(
                to_cl,
                data
            )

            if prev_copy_cluster != -1:
                self._fat_worker.write_to_fat(prev_copy_cluster, to_cl)

            prev_copy_cluster = to_cl

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

    def _recover_lost_files(
            self,
            lost_cluster_chains: set,
            not_lost_clusters: set,
            directory='.'
    ):
        dir_index = get_not_taken_index(directory)
        dir_name = 'lost_files' + str(dir_index)
        dir_path = os.path.join(directory, dir_name)

        os.mkdir(dir_path)
        for ind, chain in enumerate(lost_cluster_chains):
            number = str(ind).rjust(5, '0')
            file_name = f'file{number}'
            with open(os.path.join(dir_path, file_name), 'wb') as f:
                for cluster in chain:
                    f.write(self._fat_worker.read_cluster(cluster))
                    if cluster in not_lost_clusters or cluster in (0, 1):
                        continue
                    self._fat_worker.write_to_fat(cluster, 0)

    def _scan_for_lost_cluster_chains(self):
        real_cluster_chains = set(self._get_all_cluster_chains())
        fat_cluster_chains = set(self._get_cluster_chains_from_fat_table())

        if len(fat_cluster_chains) > len(real_cluster_chains):
            return real_cluster_chains, fat_cluster_chains

    def _get_all_cluster_chains(self):
        all_files = self.walk('/')
        for file in all_files:
            yield tuple(self._fat_worker.get_cluster_chain(file.first_cluster))

    def _get_cluster_chains_from_fat_table(self):
        top_sorted_clusters = self._get_top_sorted_clusters_from_fat_table()
        used_clusters = set()
        cluster_chains = []
        for cluster in top_sorted_clusters:
            if cluster in used_clusters:
                continue

            cluster_chain = []
            for cluster_ in self._fat_worker.get_cluster_chain(cluster):
                used_clusters.add(cluster_)
                cluster_chain.append(cluster_)

            cluster_chains.append(tuple(cluster_chain))

        return cluster_chains

    def _get_top_sorted_clusters_from_fat_table(self):
        used_clusters = set()
        top_sorted = []
        for cluster in self._fat_worker.get_non_free_fat_clusters():
            if cluster in used_clusters:
                continue

            chain_from_current_cluster = []
            for cluster_ in self._fat_worker.get_cluster_chain(cluster):
                if cluster_ in used_clusters:
                    break
                used_clusters.add(cluster_)
                chain_from_current_cluster.append(cluster_)

            top_sorted.extend(reversed(chain_from_current_cluster))

        return reversed(top_sorted)

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
                cur_dir_first_cluster
            )
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
