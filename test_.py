from FatWorker import FatWorker
from CLI import CLI
from unittest import TestCase
from FileSystem import FileSystem
from download_samples import download_samples
import shutil


class TestCLI(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # download_samples()
        pass

    @classmethod
    def tearDownClass(cls):
        # shutil.rmtree('test_files')
        pass

    def setUp(self):
        self.file_system = FileSystem(
            FatWorker('test_files/simple_image_only_eng_letters.img'))
        self.cli = CLI(self.file_system, True)

    def tearDown(self):
        self.file_system.exit()

    def test_ls_WithoutParams(self):
        ls_set = {file for file in self.cli.ls('')}

        correct_set = set((f'dir{i}' for i in range(5)))
        correct_set.update({f'file{i}' for i in range(5)})
        correct_set.update({'efi'})

        self.assertSetEqual(ls_set, correct_set)

    def test_ls_WithParams_ExistedPath(self):
        output = set(self.cli.ls('/dir0/'))
        correct_set = {'dir1', 'some_script.py'}
        self.assertSetEqual(correct_set, output)

    def test_ls_WithParams_NonExistingPath(self):
        output = self.cli.ls('abacaba')
        correct_output = ['No such a directory abacaba']
        self.assertEqual(correct_output, output)

    def test_ls_WithFlags_AllFlag(self):
        output = set(self.cli.ls('-a /dir0/'))
        correct_set = {'dir1', 'some_script.py', '..', '.'}

        self.assertSetEqual(output, correct_set)

    def test_cd_WithAbsPath(self):
        self.cli.cd('/dir0/')
        self.assertEqual(self.cli.pwd(), ['/dir0'])

    def test_cd_WithAbsPath_NotOneDirectory(self):
        self.cli.cd('/dir0/dir1')
        self.assertEqual(self.cli.pwd(''), ['/dir0/dir1'])

    def test_cd_WithRelativePath(self):
        self.cli.cd('dir0')
        self.assertEqual(self.cli.pwd(), ['/dir0'])

    def test_cd_WIthRelativePath_WithDots(self):
        self.cli.cd('./dir1')
        self.assertEqual(self.cli.pwd(), ['/dir1'])

    def test_cd_WithRelativePath_WithTwoDots(self):
        self.cli.cd('../../dir1')
        self.assertEqual(self.cli.pwd(), ['/dir1'])

    def test_cd_WithRelativePath_WithNotOneDot(self):
        self.cli.cd('./././dir1')
        self.assertEqual(self.cli.pwd(), ['/dir1'])
