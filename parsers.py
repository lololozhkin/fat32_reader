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
            prog='fat32-reader',
            description="Program to view directories and files of FAT32 image"
        )
        parser.add_argument('file',
                            help='Path to image')

        return parser

    @staticmethod
    def scan_parser():
        parser = argparse.ArgumentParser(
            prog='scan',
            description='scanning disk for errors like intersected '
                        'or lost clusterchains'
        )

        sub_parser = parser.add_subparsers(
            dest='command_name',
            help='choose type of errors to be scanned'
        )

        lost_parser = sub_parser.add_parser('lost',
                                            help='scan for lost clusterchains')
        lost_parser.add_argument('-d', '--directory',
                                 type=str,
                                 help='choose directory to save lost files')

        intersect_parser = sub_parser.add_parser('intersected',
                                                 help='scan for intersected '
                                                      'clusterchains')
        intersect_parser.add_argument('-r', '--resolve',
                                      action='store_true',
                                      help='use this flag to resolve problems '
                                           'with intersected clusterchains')

        return parser

    @staticmethod
    def cat_parser():
        parser = argparse.ArgumentParser(
            description='Shows file data in a text format to standard output'
        )
        parser.add_argument('path',
                            type=str,
                            help='Path to file to show')

        parser.add_argument('-r', '--resolve',
                            action='store_true',
                            help='resolve all errors occurred')

        return parser

    @staticmethod
    def xxd_parser():
        parser = argparse.ArgumentParser(
            description='Shows file data in binary format to standard output'
        )
        parser.add_argument('path',
                            type=str,
                            help='Path to file to show')

        return parser

