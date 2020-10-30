from FatWorker import FatWorker
import random
import sys


def main():
    path = sys.argv[1]
    worker = FatWorker(path)
    with open(path, 'rb+') as f:
        for cluster in range(2, worker.fats_z32 * worker.bytes_per_sector >> 2):
            if worker.get_next_cluster(cluster) == 0:
                if random.randint(1, 10) <= 7:
                    sec, off = worker.get_fat_sector_and_offset(cluster)
                    f.seek(sec * worker.bytes_per_sector + off)
                    f.write(random.randint(2, 2**30).to_bytes(4, 'little'))


if __name__ == '__main__':
    main()
