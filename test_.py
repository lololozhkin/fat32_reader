from fat_worker import FatWorker
from CLI import CLI
from unittest import TestCase
from file_system import FileSystem
from download_samples import download_samples
import shutil
import os


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
        self.eng_fs = FileSystem(
            FatWorker('test_files/simple_image_only_eng_letters.img'))
        self.eng_cli = CLI(self.eng_fs, True)

        self.rus_fs = FileSystem(
            FatWorker('test_files/russian_and_english_letters.img')
        )
        self.rus_cli = CLI(self.rus_fs, True)

        self.bad_fs = FileSystem(
            FatWorker('test_files/beated_image.img')
        )
        self.bad_cli = CLI(self.bad_fs, True)

    def tearDown(self):
        self.eng_fs.exit()
        self.rus_fs.exit()
        self.bad_fs.exit()

    def test_ls_WithoutParams(self):
        ls_set = {file for file in self.eng_cli.ls('')}

        correct_set = set((f'dir{i}' for i in range(5)))
        correct_set.update({f'file{i}' for i in range(5)})
        correct_set.update({'efi'})

        self.assertSetEqual(ls_set, correct_set)

    def test_ls_WithParams_ExistedPath(self):
        output = set(self.eng_cli.ls('/dir0/'))
        correct_set = {'dir1', 'some_script.py'}
        self.assertSetEqual(correct_set, output)

    def test_ls_WithParams_NonExistingPath(self):
        output = self.eng_cli.ls('abacaba')
        correct_output = ['No such directory abacaba']
        self.assertEqual(correct_output, output)

    def test_ls_WithFlags_AllFlag(self):
        output = set(self.eng_cli.ls('-a /dir0/'))
        correct_set = {'dir1', 'some_script.py', '..', '.'}

        self.assertSetEqual(output, correct_set)

    def test_cd_WithAbsPath(self):
        self.eng_cli.cd('/dir0/')
        self.assertEqual(self.eng_cli.pwd(), ['/dir0'])

    def test_cd_WithAbsPath_NotOneDirectory(self):
        self.eng_cli.cd('/dir0/dir1')
        self.assertEqual(self.eng_cli.pwd(''), ['/dir0/dir1'])

    def test_cd_WithRelativePath(self):
        self.eng_cli.cd('dir0')
        self.assertEqual(self.eng_cli.pwd(), ['/dir0'])

    def test_cd_WIthRelativePath_WithDots(self):
        self.eng_cli.cd('./dir1')
        self.assertEqual(self.eng_cli.pwd(), ['/dir1'])

    def test_cd_WithRelativePath_WithTwoDots(self):
        self.eng_cli.cd('../../dir1')
        self.assertEqual(self.eng_cli.pwd(), ['/dir1'])

    def test_cd_WithRelativePath_WithNotOneDot(self):
        self.eng_cli.cd('./././dir1')
        self.assertEqual(self.eng_cli.pwd(), ['/dir1'])

    def test_ls_WithRussianLetters_without_params(self):
        out = set(self.rus_cli.ls(''))
        correct_set = {
            'eng',
            'русская',
            'long_english_directory',
            'папка',
            'очень_длинное_название_русской_папки',
            'eng.txt',
            'рус.рус',
            'рус.txt'
        }
        self.assertSetEqual(out, correct_set)

    def test_ls_WithRussianLetters_WithRussianArgument(self):
        out = set(self.rus_cli.ls('русская'))
        correct_set = {
            'eng_file.txt',
            'рус_eng.file',
            'русский_файл.ру'
        }

        self.assertSetEqual(out, correct_set)

    def test_cd_WithRussianLetters(self):
        self.rus_cli.cd('русская')
        self.assertEqual(self.rus_cli.pwd(), ['/русская'])

        self.rus_cli.cd('../очень_длинное_название_русской_папки')
        self.assertEqual(
            self.rus_cli.pwd(),
            ['/очень_длинное_название_русской_папки']
        )

    def test_export_WithFileTarget(self):
        self.eng_cli.export('file0 test_files/file0_test.txt')
        with open('test_files/file0_test.txt', 'r') as f:
            text = f.read()

        self.assertEqual(
            text,
            'python is the best programming language ever\n'
        )

        os.remove('test_files/file0_test.txt')

    def test_export_WithDirectoryTarget(self):
        self.eng_cli.export('file0 test_files')
        self.assertTrue(os.path.isfile('test_files/file0'))
        with open('test_files/file0', 'r') as f:
            text = f.read()

        self.assertEqual(
            text,
            'python is the best programming language ever\n'
        )

        os.remove('test_files/file0')

    def test_scan_NormalImage_WithoutLostSectors(self):
        result = self.eng_fs.scan_lost_clusters()
        self.assertEqual(result, 'Everything is ok')

    def test_scan_NormalImage_WithoutIntersectedSectors(self):
        result = self.eng_fs.scan_for_intersected_chains()
        self.assertEqual(result, 'Everything is ok')

    def test_scan_NotNormalImage_WithLostSectors(self):
        result = self.bad_fs.scan_lost_clusters()
        self.assertNotEqual('Everything is ok', result)
        self.assertTrue('Some clusters are lost' in result)

    def test_scan_NotNormalImage_WithLostSectorsButWithoutIntersections(self):
        result = self.bad_fs.scan_for_intersected_chains()
        self.assertEqual(result, 'Everything is ok')
