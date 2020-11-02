from entry import Entry
from fat_worker import FatWorker
from CLI import CLI
from unittest import TestCase
from file_system import FileSystem
from download_samples import download_samples
import shutil
import os

from file_type import FileType


class TestCLI(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        download_samples()
        pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('test_files')
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

    def test_CLI_HelpDoesntHaveOutput(self):
        self.assertEqual(self.eng_cli.ls('--help'), [])
        self.assertEqual(self.eng_cli.pwd('--help'), [])
        self.assertEqual(list(self.eng_cli.scan('--help')), [])
        self.assertEqual(self.eng_cli.cd('--help'), [])
        self.assertEqual(self.eng_cli.export('--help'), [])

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

    def test_cd_WIthNonExistingPath(self):
        self.assertEqual(self.eng_cli.cd('non_existing_dir'),
                         ["There isn't such directory"])

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

    def test_export_WithNonExistingFile(self):
        self.assertEqual(
            self.eng_cli.export('non_existing_file.aba test_files'),
            ["There isn't such file on image non_existing_file.aba"]
        )

    def test_export_WithoutExistingDirectoryOnComputer(self):
        self.assertEqual(
            self.eng_cli.export('file0 non_existing_directory/file.aba'),
            ["There isn't such file on your computer"
             " non_existing_directory/file.aba"]
        )

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


class InnerTests(TestCase):
    def test_entry_LongNameFromShortEntry(self):
        entry = b'A       PY  \x00\x8a\x83\xa5]QaQ\x00' \
                b'\x00\x83\xa5]Q\xbd(\xa0\x00\x00\x00'
        entry = Entry(entry)
        self.assertTrue(entry.is_short_entry)
        self.assertRaises(ValueError, lambda: entry.long_dir_order)
        self.assertRaises(ValueError, lambda: entry.long_entry_letters)

    def test_entry_ShortAttributesFromLongEntry(self):
        entry = b'\x01w\x00a\x00r\x00_\x00a\x00\x0f' \
                b'\x00Mn\x00d\x00_\x00p\x00i\x00e\x00\x00\x00c\x00e\x00'
        entry = Entry(entry)
        self.assertTrue(entry.is_long_entry)
        self.assertRaises(ValueError, lambda: entry.alias_name)
        self.assertRaises(ValueError, lambda: entry.file_size)
        self.assertRaises(ValueError, lambda: entry.short_type)

    def test_entry_LongEntryLetters(self):
        entry = b'\x01w\x00a\x00r\x00_\x00a\x00\x0f' \
                b'\x00Mn\x00d\x00_\x00p\x00i\x00e\x00\x00\x00c\x00e\x00'
        entry = Entry(entry)
        self.assertEqual(
            entry.long_entry_letters.decode('utf-16'),
            'war_and_piece'
        )

    def test_entry_NotEntryIsGiven(self):
        self.assertRaises(ValueError, lambda: Entry(b'abacaba'))

    def test_entry_LongEntryTestStr(self):
        entry = b'\x01w\x00a\x00r\x00_\x00a\x00\x0f' \
                b'\x00Mn\x00d\x00_\x00p\x00i\x00e\x00\x00\x00c\x00e\x00'
        entry = Entry(entry)
        self.assertEqual(str(entry), 'long entry, war_and_piece')

    def test_entry_ShortEntryTestStr(self):
        entry = b'A       PY  \x00\x8a\x83\xa5]QaQ\x00' \
                b'\x00\x83\xa5]Q\xbd(\xa0\x00\x00\x00'
        entry = Entry(entry)
        self.assertEqual(str(entry), 'A.PY')

    def test_entry_EntryIsFree(self):
        entry = b'\x00' * 32
        entry = Entry(entry)
        self.assertTrue(entry.is_free)

    def test_entry_ShortTypeOfEntry(self):
        entry = b'A       PY  \x00\x8a\x83\xa5]QaQ\x00' \
                b'\x00\x83\xa5]Q\xbd(\xa0\x00\x00\x00'
        entry = Entry(entry)
        self.assertEqual(entry.short_type, FileType.File)

        entry = b'DIR        \x10\x00G\xfbMPQPQ\x00\x00' \
                b'\xfbMPQ\x03\x00\x00\x00\x00\x00'
        entry = Entry(entry)
        self.assertEqual(entry.short_type, FileType.Directory)

        entry = b'\xff' * 32
        entry = Entry(entry)
        self.assertEqual(entry.short_type, FileType.Invalid)
