from .file_type import FileType
from .ATTR import ATTR
import struct


def get_bit_slice_of_word(word, begin, end):
    return ((word << (15 - end)) & 0xFFFF) >> (15 - end + begin)


class File:
    def __init__(self, name=None,
                 attributes=None,
                 time=None,
                 date=None,
                 file_size=None,
                 first_cluster=None,
                 alias=None,
                 fat_worker=None,
                 path=None):
        self._name = name
        self._attributes = attributes
        self._time = time
        self._date = date
        self._file_size = file_size
        self._first_cluster = first_cluster
        self._alias = alias
        self._fat_worker = fat_worker
        self._path = path

    def __str__(self):
        return f"{self.type.name[0].lower()} " \
               f"{self.date} {self.time} " \
               f"{str(self.file_size).rjust(10, ' ')}b " \
               f"{self.name}"

    def data(self):
        yield from self._fat_worker.get_file_data(self)

    @property
    def name(self):
        name = self._name.replace(chr(0xFFFF), '')
        name = name.replace(chr(0), '')
        return name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes = value

    @property
    def time(self):
        int_time = struct.unpack("<H", self._time)[0]
        seconds = 2 * get_bit_slice_of_word(int_time, 0, 4)
        minutes = get_bit_slice_of_word(int_time, 5, 10)
        hours = get_bit_slice_of_word(int_time, 11, 15)

        return f'{str(hours).rjust(2, "0")}:' \
               f'{str(minutes).rjust(2, "0")}:' \
               f'{str(seconds).rjust(2, "0")}'

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def date(self):
        int_date = struct.unpack("<H", self._date)[0]
        day = get_bit_slice_of_word(int_date, 0, 4)
        month = get_bit_slice_of_word(int_date, 5, 8)
        year = 1980 + get_bit_slice_of_word(int_date, 9, 15)
        return f'{str(day).rjust(2, "0")}.{str(month).rjust(2, "0")}.{year}'

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def file_size(self):
        return self._file_size

    @file_size.setter
    def file_size(self, value):
        self._file_size = value

    @property
    def first_cluster(self):
        return self._first_cluster

    @first_cluster.setter
    def first_cluster(self, value):
        self._first_cluster = value

    @property
    def alias(self):
        return self._alias

    @alias.setter
    def alias(self, value):
        self._alias = value

    @property
    def type(self):
        masked_attr = self.attributes & (ATTR.DIRECTORY | ATTR.VOLUME_ID)
        if masked_attr == 0x00:
            return FileType.File
        elif masked_attr == ATTR.DIRECTORY:
            return FileType.Directory
        elif masked_attr == ATTR.VOLUME_ID:
            return FileType.Volume
        else:
            return FileType.Invalid

    @property
    def is_directory(self):
        return self.type == FileType.Directory

    @property
    def is_file(self):
        return self.type == FileType.File

    @property
    def is_volume(self):
        return self.type == FileType.Volume

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path
