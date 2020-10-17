import argparse
from FatWorker import FatWorker
from FileSystem import FileSystem
from CLI import CLI
import colorama
from colorama import Fore, Style
import readline


def main():
    colorama.init()
    parser = argparse.ArgumentParser(
        description="Program to view directories and files of FAT32 image"
    )
    parser.add_argument('file',
                        help='Path to image')

    args = parser.parse_args()
    file = args.file
    fs = FileSystem(FatWorker(file))
    cli = CLI(fs)

    utils = {
        'cd': cli.cd,
        'pwd': cli.pwd,
        'ls': cli.ls,
        'export': cli.export,
    }

    while True:
        try:
            command = input(f'{Fore.LIGHTCYAN_EX}{fs.current_dir}'
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

        if util == 'exit':
            print('Good bye')
            fs.exit()
            break

        try:
            res = utils[util](params)
            for item in res:
                print(item)

        except KeyError:
            print(f"{Fore.RED}Command not found '{util}'{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
