from io import StringIO
import sys
import functools
from FatWorker import FatWorker
from FileSystem import FileSystem
from CLI import CLI
from unittest import TestCase
import colorama
import re


regex = r'\x1b\[(?:\d{1,2})m'


def get_all_std_output(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        stdout = sys.stdout

        all_output = StringIO()
        sys.stdout = all_output

        func(*args, **kwargs)

        sys.stdout = stdout
        return all_output.getvalue()
    return wrapper


def remove_control_sequences(string):
    return re.sub(regex, '', string)


def get_set_from_ls_out(ls_out):
    output = set(remove_control_sequences(ls_out).split('\n'))
    output.discard('')
    return output


class TestCLI(TestCase):
    colorama.init()

    def setUp(self):
        self.file_system = FileSystem(FatWorker('test.img'))

    def test_ls_without_params(self):
        cli = CLI(self.file_system, True)
        ls_set = {file for file in cli.ls('')}

        correct_set = set((f'dir{i}' for i in range(5)))
        correct_set.update({f'file{i}' for i in range(5)})
        correct_set.update({'efi'})

        self.assertSetEqual(ls_set, correct_set)

    def test_ls_with_path(self):
        cli = CLI(self.file_system, True)

        output = set(cli.ls('/dir0/'))

        correct_set = {'dir1', 'some_script.py'}

        self.assertSetEqual(correct_set, output)

        output = cli.ls('abacaba')
        correct_output = ['No such a directory abacaba']
        self.assertEqual(correct_output, output)

    def test_ls_with_all_flag(self):
        cli = CLI(self.file_system, True)

        output = set(cli.ls('-a /dir0/'))

        correct_set = {'dir1', 'some_script.py', '..', '.'}

        self.assertSetEqual(output, correct_set)

    def test_cd_with_abs_path(self):
        cli = CLI(self.file_system, True)
        cli.cd('/dir0/')
        self.assertEqual(cli.pwd(), ['/dir0'])

        cli.cd('/dir0/dir1')
        self.assertEqual(cli.pwd(''), ['/dir0/dir1'])

    def test_cd_with_relative_path(self):
        cli = CLI(self.file_system, True)
        cli.cd('dir0')
        self.assertEqual(cli.pwd(), ['/dir0'])

        cli.cd('./dir1')
        self.assertEqual(cli.pwd(), ['/dir0/dir1'])

        cli.cd('../../dir1')
        self.assertEqual(cli.pwd(), ['/dir1'])

        cli.cd('./././')
        self.assertEqual(cli.pwd(), ['/dir1'])

    class TestFatWorker:
        colorama.init()
        fat_worker = FatWorker('test.img')

        def test_(self):
            pass
