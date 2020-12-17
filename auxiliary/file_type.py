import enum


class FileType(enum.Enum):
    Directory = 0
    File = 1
    Volume = 2
    Invalid = 3
