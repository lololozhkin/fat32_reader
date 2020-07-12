import struct
from ATTR import ATTR
from EntryType import EntryType


class Entry:
    def __init__(self, entry):
        if not isinstance(entry, bytes) or len(entry) != 32:
            raise ValueError("not entry is given")

        self.entry = entry
        self.attributes = int(entry[11])

        high_word = struct.unpack("<H", entry[20:22])[0]
        low_word = struct.unpack("<H", entry[26:28])[0]
        self.first_cluster = (high_word << 2) + low_word

    def __str__(self):
        return f"{'long entry' if self.is_long_entry else self.alias_name}"

    def __getitem__(self, item):
        return self.entry.__getitem__(item)

    @property
    def is_free(self):
        return int(self.entry[0]) in (0xE5, 0x00)

    @property
    def is_long_entry(self):
        return (int(self.attributes) & ATTR.LONG_NAME_MASK) == ATTR.LONG_NAME and \
               int(self.entry[0]) not in (0x00, 0xE5)

    @property
    def long_dir_order(self):
        if self.is_long_entry:
            return int(self.entry[0])
        else:
            raise ValueError("short directory entries doesn't have LDIR_Ord")

    @property
    def alias_name(self):
        if not self.is_long_entry:
            return str(self.entry[:11])
        else:
            raise ValueError("long directory entries doesn't have short name")

    @property
    def short_type(self):
        if not self.is_long_entry:
            masked_attr = self.attributes & (ATTR.DIRECTORY | ATTR.VOLUME_ID)
            if masked_attr == 0x00:
                return EntryType.File
            elif masked_attr == ATTR.DIRECTORY:
                return EntryType.Directory
            elif masked_attr == ATTR.VOLUME_ID:
                return EntryType.Volume
            else:
                return EntryType.Invalid
        else:
            raise ValueError("long directory entries doesn't have short name")


def main():
    pass


if __name__ == '__main__':
    main()
