from amitools.vamos.libstructs import ExecLibraryStruct, NodeType
from .library import Library
from amitools.vamos.astructs import AmigaClassDef


@AmigaClassDef
class ExecLibrary(ExecLibraryStruct):
    def __init__(self, mem, addr, **kwargs):
        # if 'neg_size' is given then move base_addr of lib struct
        neg_size = kwargs.get("neg_size")
        if neg_size:
            addr += neg_size
        # now setup library struct
        super().__init__(mem, addr, **kwargs)

    @classmethod
    def _alloc(cls, alloc, tag, pos_size, neg_size, fd):
        if tag is None:
            tag = cls.get_signature()
        return alloc.alloc_lib(tag, cls, pos_size=pos_size, neg_size=neg_size, fd=fd)

    @classmethod
    def _free(cls, alloc, mem_obj):
        alloc.free_lib(mem_obj)

    @classmethod
    def alloc(cls, alloc, tag=None, pos_size=0, neg_size=0, fd=None, **kwargs):
        if pos_size == 0:
            pos_size = cls.get_byte_size()
        # round size
        neg_size = (neg_size + 3) & ~3
        # alloc lib
        return super().alloc(
            alloc,
            pos_size,
            neg_size,
            fd,
            tag=tag,
            pos_size=pos_size,
            neg_size=neg_size,
            **kwargs
        )

    def new_lib(self, version=0, revision=0, attn_flags=0, max_loc_mem=0):
        self.lib_node.new_lib(version, revision)
        self.attn_flags.val = attn_flags
        self.max_loc_mem.val = max_loc_mem
        # init lists
        self.mem_list.new_list(NodeType.NT_MEMORY)
        self.resource_list.new_list(NodeType.NT_RESOURCE)
        self.device_list.new_list(NodeType.NT_DEVICE)
        self.intr_list.new_list(NodeType.NT_INTERRUPT)
        self.lib_list.new_list(NodeType.NT_LIBRARY)
        self.port_list.new_list(NodeType.NT_MSGPORT)
        self.task_ready.new_list(NodeType.NT_TASK)
        self.task_wait.new_list(NodeType.NT_TASK)
        self.semaphore_list.new_list(NodeType.NT_SEMAPHORE)
        self.mem_handlers.new_list()

    def fill_funcs(self, opcode=None, param=None):
        self.lib_node.fill_funcs(opcode, param)
