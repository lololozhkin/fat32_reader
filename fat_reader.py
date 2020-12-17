#!/usr/bin/env python3

import colorama
import sys

from auxiliary.fat_worker import FatWorker
from auxiliary.file_system import FileSystem
from auxiliary.CLI import CLI
from colorama import Fore, Style
from auxiliary.parsers import Parsers


def main():
    colorama.init()
    parser = Parsers.main_parser()
    args = parser.parse_args()
    file = args.file

    try:
        fs = FileSystem(FatWorker(file))
    except PermissionError:
        print(
            'Not able to read image because of Permission Error.',
            file=sys.stderr
        )
        print('Good bye')
        return 1
    except IsADirectoryError as e:
        print(e, file=sys.stderr)
        return 5
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 6

    cli = CLI(fs)

    try:
        while True:
            try:
                command = input(
                    f'{Fore.LIGHTCYAN_EX}{fs.current_dir}'
                    f'{Fore.BLUE}${Style.RESET_ALL}: '
                )
                if len(command) == 0:
                    continue
                command = ' '.join(command.split(' '))
            except UnicodeDecodeError as e:
                print(
                    e.__doc__,
                    e.reason,
                    e.args[1][e.start:e.end],
                    f'at position {e.start}.'
                )
                continue
            except EOFError:
                fs.exit()
                print('\nGood bye')
                break

            command = command.replace('\n', '')
            util = command.split()[0]
            params = command[len(util) + 1:]

            if util == 'exit':
                print('Good bye')
                fs.exit()
                break

            try:
                cli.execute_command(util, params)
            except (FileNotFoundError, PermissionError) as e:
                print(e)
                continue
            except OSError as e:
                print('Critical Error occurred:', e, file=sys.stderr)
                fs.exit()
                print('Good bye', file=sys.stderr)
                return 2

    except KeyboardInterrupt as e:
        fs.exit()
        print(e, file=sys.stderr)
        return 3

    return 0


if __name__ == '__main__':
    sys.exit(main())
