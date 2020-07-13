import argparse
from FatWorker import FatWorker
from CLI import CLI


def main():
    parser = argparse.ArgumentParser(
        description="Program to view directories and files of FAT32 image")
    parser.add_argument('--file',
                        default='/home/lololozhkin/img_test/test.img')

    args = parser.parse_args()
    file = args.file
    fat_worker = FatWorker(file)
    cli = CLI(fat_worker)

    utils = {
        'cd': cli.cd,
        'pwd': cli.pwd,
        'ls': cli.ls,
        'exit': cli.exit
    }

    while True:
        print(f'{cli.current_dir}$:', end=' ')
        command = ' '.join(input().split(' '))
        command = command.replace('\n', '')
        util = command.split()[0]
        params = command[len(util) + 1:]

        res = utils[util](params)
        if res is False:
            break

    # for file in fat_worker.get_all_files_in_dir(fat_worker.root_cluster):
    #     print(file)




if __name__ == '__main__':
    main()
