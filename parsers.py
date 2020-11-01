import argparse


class Parsers:
    @staticmethod
    def ls_parser():
        parser = argparse.ArgumentParser(
            prog='ls',
            description='list information about the files '
                        '(the current directory by default)'
        )
        parser.add_argument('-l',
                            action='store_true',
                            help='use a long format')

        parser.add_argument('-a', '--all',
                            action='store_true',
                            help='do not ignore hidden files')

        parser.add_argument('path',
                            default='./',
                            metavar='path',
                            nargs='?',
                            help='directory, that has to be shown')

        return parser

    @staticmethod
    def pwd_parser():
        parser = argparse.ArgumentParser(
            prog='pwd',
            description='print working directory'
        )

        return parser

    @staticmethod
    def cd_parser():
        parser = argparse.ArgumentParser(
            prog='cd',
            description='changes current directory',
        )

        parser.add_argument('path', default='/', help='new path')

        return parser

    @staticmethod
    def export_parser():
        parser = argparse.ArgumentParser(
            prog='export',
            description='exports file from the image to a disk'
        )
        parser.add_argument('img_path',
                            type=str,
                            help='path in the image of disk'
                            )
        parser.add_argument('disk_path',
                            type=str,
                            help='path of the file in your computer'
                            )

        return parser

    @staticmethod
    def main_parser():
        parser = argparse.ArgumentParser(
            description="Program to view directories and files of FAT32 image"
        )
        parser.add_argument('file',
                            help='Path to image')

        parser.add_argument('-i', '--scan-intersection',
                            action='store_true',
                            help='scan for intersected cluster '
                                 'chains before work')

        parser.add_argument('-l', '--scan-lost',
                            action='store_true',
                            help='scan for lost clusters before work')

        parser.add_argument('-s', '--scan',
                            action='store_true',
                            help='scan image for problems before work')

        parser.add_argument('-r', '--resolve',
                            action='store_true',
                            help='resolve all solvable problems of image')

        return parser
