from FatWorker import FatWorker
from CLI import CLI
from unittest import TestCase
from FileSystem import FileSystem


class TestCLI(TestCase):
    def setUp(self):
        self.file_system = FileSystem(
            FatWorker('test_files/simple_image_only_eng_letters.img'))

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
        fat_worker = FatWorker('test.img')

        def test_(self):
            pass
