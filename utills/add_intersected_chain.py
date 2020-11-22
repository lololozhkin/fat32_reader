from fat_worker import FatWorker
from file_system import FileSystem
import random


def main():
    worker = FatWorker('../test_files/intersected_chains.img')
    fs = FileSystem(worker)
    _, war_and_piece = fs._try_get_path_and_file('/war_and_piece.txt', True)
    _, jpg = fs._try_get_path_and_file('/dir/lol.jpg', True)
    war_clusters = list(worker.get_cluster_chain(war_and_piece.first_cluster))
    jpg_clusters = list(worker.get_cluster_chain(jpg.first_cluster))
    jpg_tail = random.randint(0, len(jpg_clusters))
    war_tail = random.randint(0, len(war_clusters))
    worker.write_to_fat(jpg_clusters[jpg_tail], war_clusters[war_tail])


if __name__ == '__main__':
    main()
