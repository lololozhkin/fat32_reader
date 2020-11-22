import struct
from ATTR import ATTR
from file_type import FileType


class Entry:
    def __init__(self, entry):
        if not isinstance(entry, bytes) or len(entry) != 32:
            raise ValueError("not entry is given")

        self.entry = entry
        self.attributes = int(entry[11])

        high_word = struct.unpack("<H", entry[20:22])[0]
        low_word = struct.unpack("<H", entry[26:28])[0]
        self.first_cluster = (high_word << 16) | low_word

    def __str__(self):
        if self.is_long_entry:
            decoded_letters = self.long_entry_letters.decode(
                "utf-16",
                errors="replace"
            )
            return f'long entry, {decoded_letters}'
        else:
            return self.alias_name

    def __getitem__(self, item):
        return self.entry.__getitem__(item)

    @property
    def is_free(self):
        return int(self.entry[0]) in (0xE5, 0x00)

    @property
    def is_long_entry(self):
        return ((int(self.attributes) & ATTR.LONG_NAME_MASK) == ATTR.LONG_NAME
                and int(self.entry[0]) not in (0x00, 0xE5))

    @property
    def is_short_entry(self):
        return not self.is_long_entry

    @property
    def long_dir_order(self):
        if self.is_long_entry:
            return int(self.entry[0])
        else:
            raise ValueError("short directory entries doesn't have LDIR_Ord")

    @property
    def alias_name(self):
        if not self.is_long_entry:
            alias = self.entry[:11].decode(encoding='ascii', errors='replace')
            ext = alias[-3:]
            name = alias[:-3].rstrip(' ')
            if name in ('.', '..') or ext == '   ':
                return name
            return f'{name}.{ext}'.rstrip(' ')
        else:
            raise ValueError("long directory entries doesn't have short name")

    @property
    def date(self):
        return self.entry[24:26]

    @property
    def time(self):
        return self.entry[22:24]

    @property
    def long_entry_letters(self):
        if self.is_short_entry:
            raise ValueError("short entries doesn't have such a field")

        name1 = self.entry[1:11]
        name2 = self.entry[14:26]
        name3 = self.entry[28:32]

        letters = name1 + name2 + name3
        return letters

    @property
    def short_type(self):
        if self.is_short_entry:
            masked_attr = self.attributes & (ATTR.DIRECTORY | ATTR.VOLUME_ID)
            if masked_attr == 0x00:
                return FileType.File
            elif masked_attr == ATTR.DIRECTORY:
                return FileType.Directory
            elif masked_attr == ATTR.VOLUME_ID:
                return FileType.Volume
            else:
                return FileType.Invalid
        else:
            raise ValueError("long directory entries doesn't have short name")

    @property
    def file_size(self):
        if self.is_long_entry:
            raise ValueError("long entries doesn't have such a field")

        return struct.unpack("<I", self.entry[28:32])[0]
