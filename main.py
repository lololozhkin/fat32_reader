import argparse
from FatWorker import FatWorker


def main():
    parser = argparse.ArgumentParser(
        description="Program to view directories and files of FAT32 image")
    parser.add_argument('--file', default='/home/lololozhkin/img_test/test.img')

    args = parser.parse_args()
    file = args.file
    fat_worker = FatWorker(file)
    print('/$', end=' ')


if __name__ == '__main__':
    main()
