class ATTR:
    READ_ONLY = 0x01
    HIDDEN = 0x02
    SYSTEM = 0x04
    VOLUME_ID = 0x08
    DIRECTORY = 0x10
    ARCHIVE = 0x20
    LONG_NAME = (READ_ONLY |
                 HIDDEN |
                 SYSTEM |
                 VOLUME_ID)
    LONG_NAME_MASK = LONG_NAME | DIRECTORY | ARCHIVE
