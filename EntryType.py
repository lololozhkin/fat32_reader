import enum


class EntryType(enum.Enum):
    Directory = 0
    File = 1
    Volume = 2
    Invalid = 3
