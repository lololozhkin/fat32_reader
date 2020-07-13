import struct
from Entry import Entry
from File import File


class FatWorker:
    EOC = 0x0FFFFFFF
    LAST_LONG_ENTRY_MASK = 0x40

    def __init__(self, path: str):
        self.image = open(path, 'rb')

        self.image.seek(11)
        self.bytes_per_sector = struct.unpack("<H", self.image.read(2))[0]

        self.sectors_per_cluster = struct.unpack('<B', self.image.read(1))[0]

        self.reserved_sectors = struct.unpack("<H", self.image.read(2))[0]

        self.num_fats = struct.unpack('<B', self.image.read(1))[0]

        self.image.seek(36)
        self.fats_z32 = struct.unpack('<I', self.image.read(4))[0]

        self.image.seek(44)
        self.root_cluster = struct.unpack('<I', self.image.read(4))[0]

        self.first_data_sector = (self.reserved_sectors +
                                  (self.num_fats * self.fats_z32))

        self.image.seek(self.first_data_sector * self.bytes_per_sector)

    def get_first_sector_of_cluster(self, cluster):
        return (((cluster - 2) * self.sectors_per_cluster)
                + self.first_data_sector)

    def get_fat_sector_and_offset(self, cluster):
        fat_offset = cluster * 4
        sector_number = self.reserved_sectors + (
                fat_offset // self.bytes_per_sector)
        entry_offset = fat_offset % self.bytes_per_sector

        return sector_number, entry_offset

    def get_next_cluster(self, cluster):
        fat_sec_num, offset = self.get_fat_sector_and_offset(cluster)

        self.image.seek(fat_sec_num * self.bytes_per_sector + offset)

        return struct.unpack("<I", self.image.read(4))[0] & 0x0fffffff

    def get_entry_for_dir(self, dir_cluster, entry_num):
        self.image.seek(self.get_first_sector_of_cluster(
            dir_cluster) * self.bytes_per_sector
                        + entry_num * 32)
        return self.image.read(32)

    def get_all_entries_of_dir(self, dir_first_cluster):
        cur_cluster = dir_first_cluster
        while cur_cluster != FatWorker.EOC:
            for i in range(
                    (self.sectors_per_cluster * self.bytes_per_sector) // 32):
                entry = self.get_entry_for_dir(cur_cluster, i)
                if int(entry[0]) == 0x00:
                    break
                if int(entry[0]) == 0xE5:
                    continue
                yield Entry(entry)

            cur_cluster = self.get_next_cluster(cur_cluster)

    def get_all_files_in_dir(self, dir_first_cluster):
        yield from FatWorker.get_files_from_entries(
            self.get_all_entries_of_dir(dir_first_cluster))

    @staticmethod
    def get_files_from_entries(entries_iterable):
        for cur_entry in entries_iterable:
            cur_entry: Entry
            if cur_entry.is_long_entry:
                long_entry_parts = [cur_entry]
                short_entry = None
                for entry_part in entries_iterable:
                    entry_part: Entry
                    if entry_part.is_short_entry:
                        short_entry = entry_part
                        break
                    long_entry_parts.append(entry_part)

                file = File()
                file.name = FatWorker._generate_long_name(long_entry_parts)
                file.attributes = short_entry.attributes
                file.time = short_entry.time
                file.date = short_entry.date
                file.first_cluster = short_entry.first_cluster
                file.file_size = short_entry.file_size
                file.alias = short_entry.alias_name
                yield file

    @staticmethod
    def _generate_long_name(entries: list):
        name = ''.join(
            reversed(
                list(
                    map(lambda entry: entry.long_entry_letters,
                        entries)
                )
            )
        )
        return name
