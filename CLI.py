from FatWorker import FatWorker


class CLI:
    def __init__(self, fat_worker: FatWorker):
        self._fat_worker = fat_worker
        self._current_directory = '/'
        self._current_directory_cluster = fat_worker.root_cluster

    @property
    def current_dir(self):
        return self._current_directory

    def ls(self, params=None):
        pass

    def pwd(self, params=None):
        print(self._current_directory)

    def cd(self, params=None):
        if params is None:
            params = '/'

        params: str
        if not isinstance(params, str):
            raise TypeError("parameters have to be in string form")

        if params.count(' ') > 0:
            raise ValueError("Too many parameters")

        is_absolute = params.startswith('/')
        if params.startswith('/'):
            dirs_order = list(filter(lambda x: x != '', params.split('/')))
            cur_dir_index = 0
            cur_dir_first_cluster = self._fat_worker.root_cluster
            while True:
                files = self._fat_worker.get_all_files_in_dir(
                    cur_dir_first_cluster)
                for file in files:
                    if (file.is_directory
                            and file.name == dirs_order[cur_dir_index]):
                        cur_dir_index += 1
                        cur_dir_first_cluster = file.first_cluster
                        break
                else:
                    print(f"No such directory {params}")
                    return
                if cur_dir_index == len(dirs_order):
                    self._current_directory = params
                    self._current_directory_cluster = cur_dir_first_cluster
                    break






    def tree(self, params=None):
        pass
