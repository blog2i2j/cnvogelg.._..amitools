from amitools.vamos.libstructs import TaskStruct
from amitools.vamos.atypes import (
    AmigaTypeWithName,
    AmigaTypeDef,
    BitFieldType,
    BitField,
    EnumType,
    Enum,
    CString,
)
from .node import NodeType


@BitFieldType
class TaskFlags(BitField):
    TF_PROCTIME = 1 << 0
    TF_ETASK = 1 << 3
    TF_STACKCHK = 1 << 4
    TF_EXCEPT = 1 << 5
    TF_SWITCH = 1 << 6
    TF_LAUNCH = 1 << 7


@EnumType
class TaskState(Enum):
    TS_INVALID = 0
    TS_ADDED = 1
    TS_RUN = 2
    TS_READY = 3
    TS_WAIT = 4
    TS_EXCEPT = 5
    TS_REMOVED = 6


@AmigaTypeDef(TaskStruct, wrap={"Flags": TaskFlags, "State": TaskState})
class Task(AmigaTypeWithName):
    def setup(self, pri=0, flags=0, nt=NodeType.NT_TASK):
        node = self.get_node()
        node.set_type(nt)
        node.set_pri(pri)

        self.set_flags(flags)
        self.set_state(TaskState.TS_INVALID)
        self.mem_entry.new_list(NodeType.NT_MEMORY)

    def set_name(self, val):
        self.get_node().set_name(val)

    def get_name(self, ptr=False):
        return self.get_node().get_name(ptr)
