from amitools.vamos.libstructs import TaskStruct, NodeType, TaskState
from amitools.vamos.astructs import AmigaClassDef


@AmigaClassDef
class Task(TaskStruct):
    def __init__(self, mem, addr, **kwargs):
        super().__init__(mem, addr, **kwargs)
        # name?
        name = kwargs.get("name")
        if name:
            self.node.name.setup(name, self._alloc, self._free_refs)

    def new_task(self, pri=0, flags=0, nt=NodeType.NT_TASK):
        node = self.node
        node.type.val = nt
        node.pri.val = pri

        self.flags.val = flags
        self.state.val = TaskState.TS_INVALID
        self.mem_entry.new_list(NodeType.NT_MEMORY)
