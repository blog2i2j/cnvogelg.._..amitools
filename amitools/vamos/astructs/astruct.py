import collections
from .typebase import TypeBase


class APTR_SELF:
    """Helper Type to identify pointer to structures of my type"""

    pass


class BPTR_SELF:
    """Helper Type to identify pointer to structures of my type"""

    pass


class AmigaStructPool:
    def __init__(self):
        self._pool = {}

    def add_struct(self, cls):
        assert issubclass(cls, AmigaStruct)
        type_name = cls.sdef.get_type_name()
        if not type_name in self._pool:
            self._pool[type_name] = cls

    def find_struct(self, name):
        if name in self._pool:
            return self._pool[name]

    def get_all_structs(self):
        return list(self._pool.values())

    def get_all_struct_names(self):
        return list(self._pool.keys())


# collect all types
AmigaStructTypes = AmigaStructPool()


FieldDefBase = collections.namedtuple(
    "FieldDefBase", ["index", "offset", "type", "name", "size", "struct"]
)


class FieldDef(FieldDefBase):

    _base_offset = 0
    _parent_def = None

    def copy(self):
        return FieldDef(
            self.index, self.offset, self.type, self.name, self.size, self.struct
        )

    def get_base_offset(self):
        return self._base_offset + self.offset

    def get_parent_def(self):
        return self._parent_def

    def get_sub_field_by_name(self, name):
        # only works for astructs
        if issubclass(self.type, AmigaStruct):
            sub_field = getattr(self.type.sdef, name)
            return sub_field

    def __getattr__(self, name):
        """allow to access the field def of a sub astruct by name directly"""
        # special names
        if name == "base_offset":
            return self.get_base_offset()
        elif name == "parent_def":
            return self._parent_def
        # search sub field
        sub_field = self.get_sub_field_by_name(name)
        if sub_field:
            # clone field def and adjust base offset
            new_field = sub_field.copy()
            new_field._base_offset = self._base_offset + self.offset
            new_field._parent_def = self
            return new_field
        else:
            raise AttributeError(name)


class AmigaStructFieldDefs:
    def __init__(self, type_name):
        self._type_name = type_name
        self._field_defs = []
        self._name_to_field_def = {}
        self._total_size = 0

    def get_num_field_defs(self):
        return len(self._field_defs)

    def get_total_size(self):
        return self._total_size

    def add_field_def(self, field_def):
        self._field_defs.append(field_def)
        self._name_to_field_def[field_def.name] = field_def
        self._total_size += field_def.size

    def get_type_name(self):
        return self._type_name

    def get_field_defs(self):
        return self._field_defs

    def get_field_def(self, idx):
        return self._field_defs[idx]

    def __getitem__(self, key):
        return self._field_defs[key]

    def find_field_def_by_name(self, name):
        return self._name_to_field_def.get(name)

    def __getattr__(self, name):
        return self._name_to_field_def.get(name)

    def find_field_def_by_offset(self, offset):
        """return field_def, delta that matches offset, otherwise None, 0"""
        for f in self._field_defs:
            end = f.offset + f.size
            if offset >= f.offset and offset < end:
                delta = offset - f.offset
                return f, delta
        return None, 0

    def find_sub_field_defs_by_offset(self, base_offset):
        """return array with field_def leading to embedded struct field at offset

        return [field_defs], delta or None, 0
        """
        field_defs = []
        cur_cls = self
        offset = base_offset
        while True:
            field_def, delta = cur_cls.find_field_def_by_offset(offset)
            if not field_def:
                return None, 0
            field_defs.append(field_def)
            # is it an embedded struct?
            if not issubclass(field_def.type, AmigaStruct):
                break
            # new search
            offset -= field_def.offset
            cur_cls = field_def.type.sdef
        return field_defs, delta

    def find_sub_field_defs_by_name(self, *names):
        """return array with field_defs or None"""
        if not names:
            return None
        field_defs = []
        cur_cls = self
        for name in names:
            if not cur_cls:
                return None
            field_def = cur_cls.find_field_def_by_name(name)
            if not field_def:
                return None
            field_defs.append(field_def)
            # next sub class
            if issubclass(field_def.type, AmigaStruct):
                cur_cls = field_def.type.sdef
        return field_defs


class AmigaStruct(TypeBase):

    # overwrite in derived class!
    _format = None
    # the structure definition is filled in by the decorator
    sdef = None

    @classmethod
    def get_signature(cls):
        return cls.sdef.get_type_name()

    @classmethod
    def alloc_inst(cls, alloc, tag=None):
        if tag is None:
            tag = cls.get_signature()
        return alloc.alloc_struct(tag, cls)

    @classmethod
    def free_inst(cls, alloc, mem_obj):
        alloc.free_struct(mem_obj)

    # ----- instance -----

    def __init__(self, mem, addr, **kwargs):
        super(AmigaStruct, self).__init__(mem, addr, **kwargs)
        # create field instances
        fields = []
        name_to_field = {}
        for field_def in self.sdef.get_field_defs():
            field = self._create_field_type(field_def)
            fields.append(field)
            name_to_field[field_def.name] = field
        self._fields = fields
        self._name_to_field = name_to_field

    def __str__(self):
        return "[AStruct:%s,@%06x+%06x]" % (
            self.sdef.get_type_name(),
            self._addr,
            self._byte_size,
        )

    def get_fields(self):
        """return all field instances"""
        return self._fields

    def get_field_by_index(self, index):
        """return the type instance associated with the field"""
        return self._fields[index]

    def find_field_by_offset(self, offset):
        """return field, delta or None, 0"""
        field_def, delta = self.sdef.find_field_def_by_offset(offset)
        if not field_def:
            return None, 0
        return self._fields[field_def.index], delta

    def find_sub_fields_by_offset(self, base_offset):
        """return [fields], delta or None, 0"""
        cur_self = self
        offset = base_offset
        fields = []
        while True:
            field, delta = cur_self.find_field_by_offset(offset)
            if not field:
                return None, 0
            fields.append(field)
            # is a struct?
            if not isinstance(field, AmigaStruct):
                break
            # next sub struct
            cur_self = field
            offset -= field.get_offset()
        return fields, delta

    def find_field_def_by_addr(self, addr):
        """return field, delta or None, 0"""
        offset = addr - self._addr
        return self.sdef.find_field_def_by_offset(offset)

    def find_field_by_addr(self, addr):
        """return field, delta or None, 0"""
        offset = addr - self._addr
        return self.find_field_by_offset(offset)

    def find_sub_fields_by_addr(self, addr):
        """return [fields], delta or None, 0"""
        offset = addr - self.addr
        return self.find_sub_fields_by_offset(offset)

    def _create_field_type(self, field_def):
        addr = self._addr + field_def.offset
        base_offset = self._base_offset + field_def.offset
        field = field_def.type(
            self._mem, addr, offset=field_def.offset, base_offset=base_offset
        )
        return field

    def get(self, field_name):
        """return field instance by name"""
        if field_name in self._name_to_field:
            return self._name_to_field[field_name]

    def __getattr__(self, field_name):
        field = self.get(field_name)
        if field:
            return field
        return super(AmigaStruct, self).__getattr__(field_name)
