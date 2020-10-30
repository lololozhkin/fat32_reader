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

    parser.add_argument('-i', '--scan-intersection',
                        action='store_true',
                        help='scan for intersected cluster chains before work')

    parser.add_argument('-l', '--scan-lost',
                        action='store_true',
                        help='scan for lost clusters before work')

    parser.add_argument('-s', '--scan',
                        action='store_true',
                        help='scan image for problems before work')

    parser.add_argument('-r', '--resolve',
                        action='store_true',
                        help='resolve all solvable problems of image')

    # args = parser.parse_args(
    #     "./test_files/bad_image.img".split())
    args = parser.parse_args('/dev/sdc1'.split())
    # args = parser.parse_args()
    file = args.file
    try:
        fs = FileSystem(FatWorker(file))
    except PermissionError:
        print('Not able to read image because of Permission Error.')
        print('Good bye')
        return 0

    cli = CLI(fs)

    print(fs.scan_lost_clusters())
    print(fs.scan_for_intersected_chains())

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
