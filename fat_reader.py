#!/usr/bin/env python3

from fat_worker import FatWorker
from file_system import FileSystem
from CLI import CLI
import colorama
from colorama import Fore, Style
from parsers import Parsers
import readline


def main():
    colorama.init()
    parser = Parsers.main_parser()
    args = parser.parse_args()
    file = args.file

    try:
        fs = FileSystem(FatWorker(file))
    except PermissionError:
        print('Not able to read image because of Permission Error.')
        print('Good bye')
        return 0

    cli = CLI(fs)

    while True:
        try:
            command = input(f'{Fore.LIGHTCYAN_EX}{fs.current_dir}'
                            f'{Fore.BLUE}${Style.RESET_ALL}: ')
            if len(command) == 0:
                continue
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
            cli.execute_command(util, params)
        except OSError as e:
            print('Critical Error occurred:', e)
            fs.exit()
            print('Good bye')
            break


if __name__ == '__main__':
    main()
