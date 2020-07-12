from FileType import FileType
from ATTR import ATTR
#       b     e
# 1001000100010001


def get_bit_slice_of_word(word, begin, end):
    return (word << (begin - 1)) >> (15 + begin - end)


class File:
    def __init__(self, name=None,
                 attributes=None,
                 time=None,
                 date=None,
                 file_size=None,
                 first_cluster=None,
                 alias=None):
        self._name = name
        self._attributes = attributes
        self._time = time
        self._date = date
        self._file_size = file_size
        self._first_cluster = first_cluster
        self._alias = alias

    def __str__(self):
        return f"{self.type.name[0].lower()} " \
               f"{bin(self.attributes)[2:].rjust(8, '0')} " \
               f"{self.date} {self.time} " \
               f"{self.file_size}b " \
               f"{self.name}"

    @property
    def name(self):
        return self._name.rstrip(chr(0xFFFF))

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
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def date(self):
        int_date = int(self._date)
        day = (int_date << (16 - 4)) >> (16 - 4)
        month = (int_date << (16 - 8)) >> (16 - 8 + 5)
        return self._date

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
