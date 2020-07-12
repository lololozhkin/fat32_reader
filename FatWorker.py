import struct
from Entry import Entry


class FatWorker:
    EOC = 0x0ffffff8
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

        self.first_data_sector = self.reserved_sectors + (self.num_fats * self.fats_z32)

        self.first_sector_of_root_cluster = self.get_first_sector_of_cluster(self.root_cluster)

        self.image.seek(self.first_data_sector * self.bytes_per_sector)

    def get_first_sector_of_cluster(self, cluster):
        return ((cluster - 2) * self.sectors_per_cluster) + self.first_data_sector

    def get_fat_sector_and_offset(self, cluster):
        fat_offset = cluster * 4
        sector_number = self.reserved_sectors + (fat_offset // self.bytes_per_sector)
        entry_offset = fat_offset % self.bytes_per_sector

        return sector_number, entry_offset

    def get_next_cluster(self, cluster):
        fat_sec_num, offset = self.get_fat_sector_and_offset(cluster)

        self.image.seek(fat_sec_num * self.bytes_per_sector + offset)

        return struct.unpack("<I", self.image.read(4))[0] & 0x0fffffff

    def get_entry_for_dir(self, dir_cluster, entry_num):
        self.image.seek(self.get_first_sector_of_cluster(dir_cluster) * self.bytes_per_sector
                        + entry_num * 32)
        return self.image.read(32)

    def get_all_entries_of_dir(self, dir_first_cluster):
        cur_cluster = dir_first_cluster
        while cur_cluster != FatWorker.EOC:
            for i in range((self.sectors_per_cluster * self.bytes_per_sector) >> 5):
                entry = self.get_entry_for_dir(cur_cluster, i)
                if int(entry[0]) in (0x00, 0xE5):
                    break
                yield Entry(entry)

            cur_cluster = self.get_next_cluster(dir_first_cluster)

