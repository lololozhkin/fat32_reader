import argparse
from FatWorker import FatWorker


def main():
    parser = argparse.ArgumentParser(
        description="Program to view directories and files of FAT32 image")
    parser.add_argument('--file', default='/home/lololozhkin/img_test/test.img')

    args = parser.parse_args()
    file = args.file
    fat_worker = FatWorker(file)
    # print(fat_worker.num_fats)
    # print(fat_worker.fats_z32)
    # print(hex(fat_worker.read_value_at_fat(*fat_worker.get_fat_sector_number_and_entry_offset(fat_worker.root_cluster))))
    # print(fat_worker.get_first_cluster_of_this_entry(fat_worker.first_sector_of_root_cluster))
    for entry in fat_worker.get_all_entries_of_dir(fat_worker.root_cluster):
        print(entry)


if __name__ == '__main__':
    main()
