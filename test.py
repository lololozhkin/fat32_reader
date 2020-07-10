import argparse
import struct


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='An utility for watching directories and files')
    parser.add_argument('--file', help='use this flag to chose fat32 image')

    args = parser.parse_args()
    file = args.file

    with open(file, 'rb') as image:
        image.seek(11)
        bytes_per_sector = struct.unpack("<H", image.read(2))[0]

        sectors_per_cluster = struct.unpack('<B', image.read(1))[0]

        reserved_sectors = struct.unpack("<H", image.read(2))[0]

        num_fats = struct.unpack('<B', image.read(1))[0]

        image.seek(36)
        fats_z32 = struct.unpack('<I', image.read(4))[0]

        image.seek(44)
        root_cluster = struct.unpack('<I', image.read(4))[0]

        first_data_sector = reserved_sectors + (num_fats * fats_z32)

        first_sector_of_root_cluster = ((root_cluster - 2) * sectors_per_cluster) + first_data_sector
        image.seek(first_sector_of_root_cluster * 512)
        print(image.read(150))

        print(bytes_per_sector)
        print(sectors_per_cluster)
        print(reserved_sectors)
        print(num_fats)
        print(fats_z32)
        print(root_cluster)
        print(first_data_sector)

