from amitools.vamos.astructs.typebase import TypeBase
from amitools.vamos.astructs.string import CSTR, BSTR
from amitools.vamos.machine import MockMemory, MockCPU, REG_D0

cpu = MockCPU()
mem = MockMemory()


def astructs_string_cstr_test():
    # prepare mem
    txt = "hello, world!"
    mem.w32(0x20, 0x40)
    mem.w_cstr(0x40, txt)
    # now access with cstr
    cstr = CSTR(mem=mem, addr=0x20)
    assert cstr.get_signature() == "CSTR"
    val = cstr.get_str()
    assert val == txt
    # modify cstr
    txt2 = "wow, str!"
    cstr.set_str(txt2)
    val = mem.r_cstr(0x40)
    assert val == txt2
    # modify ptr
    mem.w_cstr(0x80, txt)
    cstr.set(0x80)
    assert cstr.get_str() == txt
    # access via 'str'
    cstr.str = "now!"
    assert cstr.str == "now!"


def astructs_string_bstr_test():
    # prepare mem
    txt = "hello, world!"
    mem.w32(0x20, 0x10)  # baddr for 0x40
    mem.w_bstr(0x40, txt)
    # now access with cstr
    bstr = BSTR(mem=mem, addr=0x20)
    assert bstr.get_signature() == "BSTR"
    val = bstr.get_str()
    assert val == txt
    # modify cstr
    txt2 = "wow, str!"
    bstr.set_str(txt2)
    val = mem.r_bstr(0x40)
    assert val == txt2
    # modify ptr
    mem.w_bstr(0x80, txt)
    bstr.set(0x20)  # 0x20 is baddr of 0x80
    assert bstr.get_str() == txt
    # access via 'str'
    bstr.str = "now!"
    assert bstr.str == "now!"
