import argparse
from FatWorker import FatWorker
from CLI import CLI
import colorama
from colorama import Fore, Style


def main():
    colorama.init()
    parser = argparse.ArgumentParser(
        description="Program to view directories and files of FAT32 image"
    )
    parser.add_argument('file',
                        default='/home/lololozhkin/img_test/test.img')

    args = parser.parse_args()
    file = args.file
    fat_worker = FatWorker(file)
    cli = CLI(fat_worker)

    utils = {
        'cd': cli.cd,
        'pwd': cli.pwd,
        'ls': cli.ls,
        'exit': cli.exit,
        'export': cli.export
    }

    while True:
        try:
            command = input(f'{Fore.LIGHTCYAN_EX}{cli.current_dir}'
                            f'{Fore.BLUE}${Style.RESET_ALL}: ')

            command = ' '.join(command.split(' '))
        except UnicodeDecodeError as e:
            print(e.__doc__,
                  e.reason,
                  e.args[1][e.start:e.end],
                  f'at position {e.start}.')
            continue
        command = command.replace('\n', '')
        util = command.split()[0]
        params = command[len(util) + 1:]

        try:
            res = utils[util](params)
            print(Style.RESET_ALL, end='')
            if not res:
                break
        except KeyError:
            print(f"{Fore.RED}Command not found '{util}'{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
