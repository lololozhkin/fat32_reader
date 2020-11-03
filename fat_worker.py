import struct
from entry import Entry
from file import File
from ATTR import ATTR


class FatWorker:
    EOC = 0x0FFFFFFF
    EOF = 0x0FFFFFF8
    BAD_CLUSTER = 0x0FFFFFF7
    LAST_LONG_ENTRY_MASK = 0x40

    def __init__(self, path):
        self.image = open(path, 'rb+')

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

    @property
    def root_dir_file(self):
        return File(name='/',
                    attributes=ATTR.DIRECTORY,
                    first_cluster=self.root_cluster
                    )

    @property
    def total_clusters(self):
        return self.bytes_per_sector * self.fats_z32 >> 2

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
        while cur_cluster != FatWorker.EOC and cur_cluster < FatWorker.EOF:
            for i in range(
                    (self.sectors_per_cluster * self.bytes_per_sector) >> 5):
                entry = self.get_entry_for_dir(cur_cluster, i)
                if int(entry[0]) == 0x00:
                    break
                if int(entry[0]) == 0xE5:
                    continue
                yield Entry(entry)

            cur_cluster = self.get_next_cluster(cur_cluster)

    def get_all_files_in_dir(self, dir_first_cluster):
        yield from self.get_files_from_entries(
            self.get_all_entries_of_dir(dir_first_cluster))

    def get_files_from_entries(self, entries_iterable):
        for cur_entry in entries_iterable:
            file = File(fat_worker=self)
            if cur_entry.is_long_entry:
                long_entry_parts = [cur_entry]
                short_entry = None
                for entry_part in entries_iterable:
                    if entry_part.is_short_entry:
                        short_entry = entry_part
                        break
                    long_entry_parts.append(entry_part)

                file.name = FatWorker._generate_long_name(long_entry_parts)
                file.attributes = short_entry.attributes
                (file.time, file.date) = (short_entry.time, short_entry.date)
                file.first_cluster = short_entry.first_cluster
                file.file_size = short_entry.file_size
                file.alias = short_entry.alias_name
            else:
                file.name = file.alias = cur_entry.alias_name
                file.alias = cur_entry.alias_name
                file.attributes = cur_entry.attributes
                (file.time, file.date) = (cur_entry.time, cur_entry.date)
                file.first_cluster = cur_entry.first_cluster
                file.file_size = cur_entry.file_size

            yield file

    def get_cluster_chain(self, first_cluster):
        cur_cluster = first_cluster
        while True:
            yield cur_cluster
            cur_cluster = self.get_next_cluster(cur_cluster)
            if cur_cluster == self.EOC or cur_cluster >= self.EOF:
                break

    def get_all_sectors_of_file(self, first_cluster):
        for cluster in self.get_cluster_chain(first_cluster):
            first_sector = self.get_first_sector_of_cluster(cluster)
            for i in range(self.sectors_per_cluster):
                self.image.seek((first_sector + i) * self.bytes_per_sector)
                yield self.image.read(self.bytes_per_sector)

    def get_non_free_fat_clusters(self):
        clusters_num = (self.fats_z32 * self.bytes_per_sector) >> 2
        for cluster in range(2, clusters_num):
            if self.get_next_cluster(cluster) != 0:
                yield cluster

    def get_file_data(self, file):
        first_cluster = file.first_cluster
        size = file.file_size
        for sector in self.get_all_sectors_of_file(first_cluster):
            if size >= self.bytes_per_sector:
                size -= self.bytes_per_sector
                yield sector
            else:
                yield sector[:size]
                break

    def write_to_fat(self, cluster_num: int, value: bytes):
        sector, offset = self.get_fat_sector_and_offset(cluster_num)
        self.image.seek(sector * self.bytes_per_sector + offset)
        self.image.write(value)
        self.image.flush()

    def close(self):
        self.image.close()

    @staticmethod
    def _generate_long_name(entries: list):
        name = b''.join(
            reversed(list(
                map(lambda entry: entry.long_entry_letters, entries)
                )
            )
        )
        return name.decode('utf-16')
