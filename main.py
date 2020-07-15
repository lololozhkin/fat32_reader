import argparse
from FatWorker import FatWorker
from CLI import CLI
import colorama
from colorama import Fore, Style


def main():
    colorama.init()
    parser = argparse.ArgumentParser(
        description="Program to view directories and files of FAT32 image")
    parser.add_argument('file',
                        default='/home/lololozhkin/img_test/test.img')

    args = parser.parse_args(['/home/lololozhkin/img_test/test.img'])
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
        print(f'{Fore.LIGHTCYAN_EX}{cli.current_dir}'
              f'{Fore.BLUE}${Style.RESET_ALL}:', end=' ')
        command = ' '.join(input().split(' '))
        command = command.replace('\n', '')
        util = command.split()[0]
        params = command[len(util) + 1:]

        try:
            res = utils[util].__call__(params)
            if res is False:
                break
        except KeyError:
            print()
            print(f"Command not found '{util}'")
            print()
    # for file in fat_worker.get_all_files_in_dir(fat_worker.root_cluster):
    #     print(file)


if __name__ == '__main__':
    main()
