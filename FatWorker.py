import argparse
import struct


class FatWorker:
    def __init__(self, path: str):
        with open(path, 'rb') as image:
            image.seek(11)
            self.bytes_per_sector = struct.unpack("<H", image.read(2))[0]

            self.sectors_per_cluster = struct.unpack('<B', image.read(1))[0]

            self.reserved_sectors = struct.unpack("<H", image.read(2))[0]

            self.num_fats = struct.unpack('<B', image.read(1))[0]

            image.seek(36)
            self.fats_z32 = struct.unpack('<I', image.read(4))[0]

            image.seek(44)
            self.root_cluster = struct.unpack('<I', image.read(4))[0]

            self.first_data_sector = self.reserved_sectors + (self.num_fats * self.fats_z32)

            self.first_sector_of_root_cluster = self.get_first_sector_of_cluster(self.root_cluster)

    def get_first_sector_of_cluster(self, n):
        return ((n - 2) * self.sectors_per_cluster) + self.first_data_sector
