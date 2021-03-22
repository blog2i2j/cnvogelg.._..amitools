from amitools.vamos.machine import MockMemory
from amitools.vamos.astructs import (
    AmigaStruct,
    AmigaStructDef,
    WORD,
    UWORD,
    BPTR_VOID,
    LONG,
    APTR,
    APTR_SELF,
)


@AmigaStructDef
class MyStruct(AmigaStruct):
    _format = [
        (WORD, "ms_Word"),
        (UWORD, "ms_Pad"),
        (BPTR_VOID, "ms_SegList"),
        (LONG, "ms_StackSize"),
    ]  # 12


@AmigaStructDef
class SubStruct(AmigaStruct):
    _format = [
        (MyStruct, "ss_My"),  # 0 +12
        (APTR(MyStruct), "ss_MyPtr"),  # 12 +4
        (APTR_SELF, "ss_SubPtr"),  # 16 +4
        (MyStruct, "ss_My2"),
    ]  # 20 +12
    # = 32


def astruct_astruct_base_class_test():
    # check class members
    assert MyStruct.get_type_name() == "My"
    assert MyStruct.get_byte_size() == 12
    # get field defs
    field_defs = MyStruct.get_field_defs()
    assert field_defs
    assert len(field_defs) == 4
    # get one field
    field_def = MyStruct.get_field_def(0)
    assert field_def.name == "ms_Word"
    # find by name
    ms_Word = MyStruct.find_field_def_by_name("ms_Word")
    assert MyStruct.ms_Word_def == ms_Word
    res = MyStruct.find_sub_field_defs_by_name("ms_Word")
    assert res == [ms_Word]
    # offset of fields
    fd, delta = MyStruct.find_field_def_by_offset(4)
    assert fd.name == "ms_SegList"
    assert delta == 0
    fd, delta = MyStruct.find_field_def_by_offset(3)
    assert fd.name == "ms_Pad"
    assert delta == 1
    # offset/base offset of fields
    assert MyStruct.ms_Pad_def.offset == 2
    assert MyStruct.ms_Pad_def.base_offset == 2
    # signature
    assert MyStruct.get_signature() == "My"


def astruct_astruct_base_inst_test():
    # check instance
    mem = MockMemory()
    ms = MyStruct(mem, 0x10)
    assert str(ms) == "[AStruct:My,@000010+00000c]"
    # field access
    fields = ms.get_fields()
    assert len(fields) == 4
    field = ms.get_field_by_index(0)
    assert field.get_addr() == 0x10
    assert ms.get("ms_Word") == field
    assert ms.find_field_by_offset(0) == (field, 0)
    assert ms.find_field_by_addr(0x10) == (field, 0)
    assert ms.find_field_def_by_addr(0x10) == (ms.get_field_def(0), 0)
    # access
    ms.get("ms_Word").set(-3000)
    assert ms.get("ms_Word").get() == -3000
    # access via __getattr__
    ms.ms_Word.set(2000)
    assert ms.ms_Word.get() == 2000


def astruct_astruct_sub_struct_test():
    # check class
    assert SubStruct.get_type_name() == "Sub"
    assert SubStruct.get_byte_size() == 32
    assert len(SubStruct.get_field_defs()) == 4
    field_defs = SubStruct.get_field_defs()
    field_names = list(map(lambda x: x.name, field_defs))
    assert field_names == ["ss_My", "ss_MyPtr", "ss_SubPtr", "ss_My2"]
    # find by name
    assert SubStruct.find_field_def_by_name("ss_My")
    res = SubStruct.find_sub_field_defs_by_name("ss_My", "ms_Pad")
    assert res == [SubStruct.ss_My_def, MyStruct.ms_Pad_def]
    assert SubStruct.find_sub_field_defs_by_name("ss_My", "Foo") is None
    assert SubStruct.find_sub_field_defs_by_name("ss_SubPtr", "Foo") is None
    # field defs
    assert SubStruct.find_field_def_by_offset(3) == (SubStruct.ss_My_def, 3)
    assert SubStruct.find_field_def_by_offset(23) == (SubStruct.ss_My2_def, 3)
    # find sub field defs
    sub_fds = SubStruct.find_sub_field_defs_by_offset(3)
    assert sub_fds == ([SubStruct.ss_My_def, MyStruct.ms_Pad_def], 1)
    sub_fds = SubStruct.find_sub_field_defs_by_offset(23)
    assert sub_fds == ([SubStruct.ss_My2_def, MyStruct.ms_Pad_def], 1)
    # access sub field
    assert SubStruct.ss_My_def.ms_Word_def == MyStruct.ms_Word_def
    # offset/base offset of field
    assert SubStruct.ss_My2_def.offset == 20
    assert SubStruct.ss_My2_def.base_offset == 20
    assert SubStruct.ss_My2_def.ms_Pad_def.offset == 2
    assert SubStruct.ss_My2_def.ms_Pad_def.base_offset == 22
    # parent defs
    assert SubStruct.ss_My2_def.ms_Pad_def.parent_def == SubStruct.ss_My2_def

    # check instance
    mem = MockMemory()
    ss = SubStruct(mem, 0x10)
    assert str(ss) == "[AStruct:Sub,@000010+000020]"
    assert ss.mem is mem
    assert ss.addr == 0x10
    # get/find field
    ms = ss.ss_My
    assert type(ms) is MyStruct
    assert ms.addr == 0x10
    assert ms.ms_Pad.addr == 0x12
    assert ss.get("ss_My") is ms
    assert ss.find_field_by_offset(3) == (ms, 3)
    assert ss.find_field_by_addr(0x13) == (ms, 3)
    ms2 = ss.ss_My2
    assert type(ms2) is MyStruct
    assert ms2.addr == 0x10 + 20
    assert ms2.ms_Pad.addr == 0x12 + 20
    assert ss.get("ss_My2") is ms2
    assert ss.find_field_by_offset(23) == (ms2, 3)
    assert ss.find_field_by_addr(0x13 + 20) == (ms2, 3)
    # get sub fields
    sub_fs = ss.find_sub_fields_by_offset(3)
    assert sub_fs == ([ms, ms.ms_Pad], 1)
    sub_fs = ss.find_sub_fields_by_offset(23)
    assert sub_fs == ([ms2, ms2.ms_Pad], 1)
    # getattr/setattr
    ss.ss_My.ms_Word.set(2000)
    assert ss.ss_My.ms_Word.get() == 2000
    # addr/offset/base_offset
    assert ss.ss_My.addr == 0x10
    assert ss.ss_My.mem == mem
    assert ss.ss_My2.addr == 0x10 + 20
    assert ss.ss_My2.offset == 20
    assert ss.ss_My2.base_offset == 20
    # sub field: addr/offset/base_offset
    assert ss.ss_My2.ms_Pad.addr == 0x10 + 22
    assert ss.ss_My2.ms_Pad.offset == 2
    assert ss.ss_My2.ms_Pad.base_offset == 22


def astruct_astruct_baddr_test():
    mem = MockMemory()
    ms = MyStruct(mem, 0x10)
    # write int to baddr
    ms.ms_SegList.set(0x40)
    # bptr auto converts back to baddr
    assert ms.ms_SegList.get() == 0x40
    # baddr is stored in mem
    assert mem.r32(0x14) == 0x40
    # write baddr
    ms.ms_SegList.set(0x20)
    assert mem.r32(0x14) == 0x20
