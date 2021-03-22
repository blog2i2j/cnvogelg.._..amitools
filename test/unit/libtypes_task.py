import pytest
from amitools.vamos.machine import MockMemory
from amitools.vamos.mem import MemoryAlloc
from amitools.vamos.libtypes import Task, TaskFlags, TaskState, NodeType


def libtypes_task_base_test():
    mem = MockMemory()
    alloc = MemoryAlloc(mem)
    # alloc task
    name = "my_task"
    task = Task.alloc(alloc, name)
    assert task.get_name() == name
    # task setup
    task.setup(pri=-5, flags=TaskFlags.TF_LAUNCH)
    node = task.get_node()
    assert node.get_type() == NodeType.NT_TASK
    assert node.get_pri() == -5
    assert task.get_flags() == TaskFlags.TF_LAUNCH
    assert task.get_state() == TaskState.TS_INVALID
    assert len(task.mem_entry) == 0
    assert task.mem_entry.type == NodeType.NT_MEMORY
    # done
    task.free()
    assert alloc.is_all_free()
