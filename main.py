import argparse
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

    args = parser.parse_args(
        "./test_files/bad_image.img -s".split())
    # args = parser.parse_args('/dev/sdc1'.split())
    # args = parser.parse_args()

    args.scan_intersection |= args.scan
    args.scan_lost |= args.scan

    file = args.file
    try:
        fs = FileSystem(FatWorker(file))
    except PermissionError:
        print('Not able to read image because of Permission Error.')
        print('Good bye')
        return 0

    cli = CLI(fs)
    if args.scan_intersection or args.scan_lost:
        for ans in cli.scan(args.scan_intersection, args.scan_lost):
            print(ans)

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
        except OSError as e:
            print('Critical Error occurred:', e)
            fs.exit()
            print('Good bye')
            break


if __name__ == '__main__':
    main()
