from amitools.vamos.libstructs import FileLockStruct, FileHandleStruct
from amitools.vamos.atypes import AmigaType, AmigaTypeDef


@AmigaTypeDef(FileLockStruct)
class FileLock(AmigaType):
    pass


@AmigaTypeDef(FileHandleStruct)
class FileHandle(AmigaType):
    pass
