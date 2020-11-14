import io

from entry import Entry
from fat_worker import FatWorker
from CLI import CLI, format_block
from unittest import TestCase
from file_system import FileSystem
from download_samples import download_samples
import shutil
import os

from file_type import FileType


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
        self.out = io.StringIO()
        self.eng_fs = FileSystem(
            FatWorker('test_files/simple_image_only_eng_letters.img'))
        self.eng_cli = CLI(self.eng_fs, True, self.out)

        self.rus_fs = FileSystem(
            FatWorker('test_files/russian_and_english_letters.img')
        )
        self.rus_cli = CLI(self.rus_fs, True, self.out)

        self.bad_fs = FileSystem(
            FatWorker('test_files/beated_image.img')
        )
        self.bad_cli = CLI(self.bad_fs, True, self.out)

    def tearDown(self):
        self.eng_fs.exit()
        self.rus_fs.exit()
        self.bad_fs.exit()

    def test_ls_WithoutParams(self):
        self.eng_cli.ls('')
        ls_set = set(self.out.getvalue().split('\n'))
        ls_set.remove('')

        correct_set = set((f'dir{i}' for i in range(5)))
        correct_set.update({f'file{i}' for i in range(5)})
        correct_set.update({'efi'})

        self.assertSetEqual(ls_set, correct_set)

    def test_ls_WithParams_ExistedPath(self):
        self.eng_cli.ls('/dir0/')
        output = set(self.out.getvalue().split('\n'))
        output.remove('')
        correct_set = {'dir1', 'some_script.py'}
        self.assertSetEqual(correct_set, output)

    def test_ls_WithParams_NonExistingPath(self):
        self.eng_cli.ls('abacaba')
        output = self.out.getvalue()
        correct_output = 'No such directory abacaba\n'
        self.assertEqual(correct_output, output)

    def test_ls_WithFlags_AllFlag(self):
        self.eng_cli.ls('-a /dir0/')
        output = set(self.out.getvalue().split('\n'))
        output.remove('')
        correct_set = {'dir1', 'some_script.py', '..', '.'}

        self.assertSetEqual(output, correct_set)

    def test_CLI_HelpDoesntHaveOutput(self):
        self.eng_cli.ls('--help')
        self.eng_cli.pwd('--help')
        self.eng_cli.scan('--help')
        self.eng_cli.cd('--help')
        self.eng_cli.export('--help')

        self.assertEqual(self.out.getvalue(), '')

    def test_cd_WithAbsPath(self):
        self.eng_cli.cd('/dir0/')
        self.eng_cli.pwd()
        last_dir = self.out.getvalue().split('\n')[-2]
        self.assertEqual(last_dir, '/dir0')

    def test_cd_WithAbsPath_NotOneDirectory(self):
        self.eng_cli.cd('/dir0/dir1')
        self.eng_cli.pwd()
        last_dir = self.out.getvalue().split('\n')[-2]
        self.assertEqual(last_dir, '/dir0/dir1')

    def test_cd_WithRelativePath(self):
        self.eng_cli.cd('dir0')
        self.eng_cli.pwd()
        last_dir = self.out.getvalue().split('\n')[-2]
        self.assertEqual(last_dir, '/dir0')

    def test_cd_WIthRelativePath_WithDots(self):
        self.eng_cli.cd('./dir1')
        self.eng_cli.pwd()
        last_dir = self.out.getvalue().split('\n')[-2]
        self.assertEqual(last_dir, '/dir1')

    def test_cd_WithRelativePath_WithTwoDots(self):
        self.eng_cli.cd('../../dir1')
        self.eng_cli.pwd()
        last_dir = self.out.getvalue().split('\n')[-2]
        self.assertEqual(last_dir, '/dir1')

    def test_cd_WithRelativePath_WithNotOneDot(self):
        self.eng_cli.cd('./././dir1')
        self.eng_cli.pwd()
        last_dir = self.out.getvalue().split('\n')[-2]
        self.assertEqual(last_dir, '/dir1')

    def test_cd_WIthNonExistingPath(self):
        self.eng_cli.cd('non_existing_dir')
        self.assertEqual(
            self.out.getvalue(),
            "There isn't such directory\n"
        )

    def test_ls_WithRussianLetters_without_params(self):
        self.rus_cli.ls('')
        out = set(self.out.getvalue().split('\n'))
        out.remove('')
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
        self.rus_cli.ls('русская')
        out = set(self.out.getvalue().split('\n'))
        out.remove('')
        correct_set = {
            'eng_file.txt',
            'рус_eng.file',
            'русский_файл.ру'
        }

        self.assertSetEqual(out, correct_set)

    def test_cd_WithRussianLetters(self):
        self.rus_cli.cd('русская')
        self.rus_cli.pwd()
        self.assertEqual(self.out.getvalue().split('\n')[-2], '/русская')

        self.rus_cli.cd('../очень_длинное_название_русской_папки')
        self.rus_cli.pwd()
        self.assertEqual(
            self.out.getvalue().split('\n')[-2],
            '/очень_длинное_название_русской_папки'
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
        self.eng_cli.export('non_existing_file.aba test_files')
        self.assertEqual(
            self.out.getvalue(),
            "There isn't such file on image non_existing_file.aba\n"
        )

    def test_export_WithoutExistingDirectoryOnComputer(self):
        self.eng_cli.export('file0 non_existing_directory/file.aba')
        self.assertEqual(
            self.out.getvalue(),
            "There isn't such file on your computer"
            " non_existing_directory/file.aba\n"
        )

    def test_cat_WithExistingFile(self):
        self.eng_cli.cat('file0')
        out = self.out.getvalue()
        self.assertEqual(
            out,
            'python is the best programming language ever\n\n'
        )

    def test_cat_WithNonExistingFile(self):
        self.eng_cli.cat('aa')
        out = self.out.getvalue()
        self.assertEqual(out, "There isn't such file on image aa\n")

    def test_cat_WithDirectory(self):
        self.eng_cli.cat('dir0')
        out = self.out.getvalue()
        self.assertEqual(out, "There isn't such file on image dir0\n")

    def test_xxd_FormatBlock_SimpleSample(self):
        data = b'abcdefghijklmnop'
        formatted_data = format_block(0, data)
        num = '00000000'
        byte_presentation = '6162 6364 6566 6768 696a 6b6c 6d6e 6f70'
        ascii_presentation = 'abcdefghijklmnop'
        self.assertEqual(
            formatted_data,
            f'{num}: {byte_presentation} {ascii_presentation}'
        )

    def test_xxd_FormatBlock_LessBytes(self):
        data = b'abc'
        formatted_data = format_block(0, data)
        num = '00000000'
        byte_presentation = '6162 63'.ljust(39, ' ')
        ascii_presentation = 'abc'
        self.assertEqual(
            formatted_data,
            f'{num}: {byte_presentation} {ascii_presentation}'
        )

    def test_xxd_XxdSimpleTest(self):
        self.eng_cli.xxd('file1')
        out = self.out.getvalue()
        num = '00000000'
        bytes_presentation = '736f 6d65 5f74 6578 740a'.ljust(39, ' ')
        ascii_presentation = 'some_text.'
        self.assertEqual(
            out,
            f'{num}: {bytes_presentation} {ascii_presentation}\n'
        )

    def test_scan_NormalImage_WithoutLostClusters(self):
        self.eng_cli.scan('lost')
        result = self.out.getvalue().split('\n')[-2]
        self.assertEqual(result, 'Everything is ok')

    def test_scan_NormalImage_WithoutIntersectedSectors(self):
        self.eng_cli.scan('intersected')
        result = self.out.getvalue().split('\n')[-2]
        self.assertEqual(result, 'Everything is ok')

    def test_scan_NotNormalImage_WithLostSectors(self):
        self.bad_cli.scan('lost')
        result = self.out.getvalue()
        self.assertNotEqual('Everything is ok', result)
        self.assertTrue('Some clusters are lost' in result)

    def test_scan_NotNormalImage_WithLostSectorsButWithoutIntersections(self):
        self.bad_cli.scan('intersected')
        result = self.out.getvalue().split('\n')[-2]
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
