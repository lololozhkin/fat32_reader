from io import StringIO
import sys
import functools
from FatWorker import FatWorker
from CLI import CLI
from colorama import Style, Fore
import colorama
import itertools
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


class TestCLI:
    colorama.init()
    fat_worker = FatWorker('test.img')

    def test_ls_without_params(self):
        cli = CLI(self.fat_worker)
        test_ls = get_all_std_output(cli.ls)

        output = get_set_from_ls_out(test_ls(''))

        correct_set = set((f'dir{i}' for i in range(5)))
        correct_set.update({f'file{i}' for i in range(5)})

        assert output == correct_set

    def test_ls_with_path(self):
        cli = CLI(self.fat_worker)
        test_ls = get_all_std_output(cli.ls)

        output = get_set_from_ls_out(test_ls('/dir0/'))

        correct_set = {'dir1', 'some_script.py'}

        assert output == correct_set

        output = remove_control_sequences(test_ls('abacaba')).replace('\n', '')
        correct_output = 'No such a directory abacaba'
        assert output == correct_output

    def test_ls_with_all_flag(self):
        cli = CLI(self.fat_worker)
        test_ls = get_all_std_output(cli.ls)

        output = get_set_from_ls_out(test_ls('-a /dir0/'))

        correct_set = {'dir1', 'some_script.py', '..', '.'}

        assert output == correct_set

    def test_cd_with_abs_path(self):
        cli = CLI(self.fat_worker)
        cli.cd('/dir0/')
        assert cli.current_dir == '/dir0'

        cli.cd('/dir0/dir1')
        assert cli.current_dir == '/dir0/dir1'

    def test_cd_with_relative_path(self):
        cli = CLI(self.fat_worker)
        cli.cd('dir0')
        assert cli.current_dir == '/dir0'

        cli.cd('./dir1')
        assert cli.current_dir == '/dir0/dir1'

        cli.cd('../../dir1')
        assert cli.current_dir == '/dir1'

        cli.cd('./././')
        assert cli.current_dir == '/dir1'

    class TestFatWorker:
        colorama.init()
        fat_worker = FatWorker('test.img')

        def test_(self):
            pass
