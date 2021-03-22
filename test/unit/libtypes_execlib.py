from amitools.vamos.machine import MockMemory
from amitools.vamos.mem import MemoryAlloc
from amitools.vamos.libtypes import ExecLibrary


def libtypes_execlib_base_test():
    mem = MockMemory()
    el = ExecLibrary(mem, 0x100)
    el.setup()
    el.fill_funcs()


def libtypes_execlib_alloc_test():
    mem = MockMemory()
    alloc = MemoryAlloc(mem)
    el = ExecLibrary.alloc(alloc, "exec.library", "bla", 20)
    el.setup()
    el.fill_funcs()
    el.free()
    assert alloc.is_all_free()
