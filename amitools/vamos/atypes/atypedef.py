import re
from amitools.vamos.astructs import CSTR, BSTR, AmigaStruct, PointerType
from .atype import AmigaType, AmigaTypeWithName
from .cstring import CString
from .bstring import BString


class AmigaTypeDecorator(object):
    def __init__(self, struct_def, wrap):
        if wrap is None:
            wrap = {}
        self.struct_def = struct_def
        self.wrap = wrap

    def decorate(self, cls):
        name = self._validate_class(cls)
        cls._type_name = name
        # store struct def
        cls._struct_def = self.struct_def
        # add to pool
        cls._type_pool[name] = cls
        # finally create methods
        self._gen_field_methods(cls)
        return cls

    def _validate_class(self, cls):
        # make sure cls is derived from AmigaStruct
        if not issubclass(cls, AmigaType):
            raise RuntimeError("cls must dervive from AmigaType")
        # get name of type
        name = self.struct_def.sdef.get_type_name()
        return name

    def _gen_field_methods(self, cls):
        # add get/set methods
        for field_def in self.struct_def.sdef.get_field_defs():
            # make a lowercase/underscore name without prefix
            # e.g. lh_TailPred -> tail_pred
            base_name = self._name_convert(field_def.name)

            # string handling
            if field_def.type is CSTR:
                self._gen_str_get_set(base_name, cls, field_def, CString)
            elif field_def.type is BSTR:
                self._gen_str_get_set(base_name, cls, field_def, BString)
            # struct types
            elif issubclass(field_def.type, AmigaStruct):
                self._gen_struct_get(base_name, cls, field_def)
            # pointer
            elif issubclass(field_def.type, PointerType):
                ref_type = field_def.type.get_ref_type()
                if issubclass(ref_type, AmigaStruct):
                    self._gen_struct_ptr_get_set(base_name, cls, field_def)
                else:
                    self._gen_default_get_set(base_name, cls, field_def)
            # base types
            else:
                wrap_funcs = self._is_wrapped(field_def, base_name)
                if wrap_funcs:
                    self._gen_wrap_get_set(base_name, cls, field_def, wrap_funcs)
                else:
                    self._gen_default_get_set(base_name, cls, field_def)

            # common field method
            self._gen_common_field_methods(base_name, cls, field_def)

    def _get_gen_type(self, cls, ref_stype):
        # its me -> use my type class
        if cls._struct_def == ref_stype:
            return cls
        # find an atype with the same name
        name = ref_stype.sdef.get_type_name()
        ref_atype = cls.find_type(name)
        if ref_atype is not None:
            return ref_atype
        # stick with struct type
        return ref_stype

    def _gen_struct_ptr_get_set(self, base_name, cls, field_def):
        """access a struct pointer. return associated struct_type"""
        index = field_def.index
        ref_stype = field_def.type.get_ref_type()
        gen_type = self._get_gen_type(cls, ref_stype)

        def get_struct_ptr(self, ptr=False):
            addr = int(self._struct.get_field_by_index(index))
            if ptr:
                return addr
            if addr == 0:
                return None
            return gen_type(self.mem, addr)

        def set_struct_ptr(self, val):
            if not type(val) is int:
                if val is None:
                    val = 0
                elif isinstance(val, gen_type):
                    # make sure its the correct type
                    val = val.addr
                else:
                    raise ValueError(
                        "invalid type assign: want=%s, got=%s" % (gen_type, type(val))
                    )
            self._struct.get_field_by_index(index).set(val)

        self._setup_get_set(base_name, cls, get_struct_ptr, set_struct_ptr)

    def _gen_struct_get(self, base_name, cls, field_def):
        """generate a getter for embedded structs"""
        gen_type = self._get_gen_type(cls, field_def.type)

        def get_struct(self):
            addr = self.addr + field_def.offset
            return gen_type(self.mem, addr)

        setattr(cls, "get_" + base_name, get_struct)

    def _is_wrapped(self, field_def, base_name):
        # allow field name
        if field_def.name in self.wrap:
            return self.wrap[field_def.name]
        # and converted base name
        elif base_name in self.wrap:
            return self.wrap[base_name]

    def _gen_common_field_methods(self, base_name, cls, field_def):
        def get_field_addr(self):
            """return the address of the field itself"""
            return self.addr + field_def.offset

        setattr(cls, "get_" + base_name + "_addr", get_field_addr)

    def _gen_str_get_set(self, base_name, cls, field_def, str_cls):
        index = field_def.index

        def get_str(self, ptr=False):
            """return the str or "" if ptr==0
            or the addr of the pointer (addr=True)"""
            addr = self._struct.get_field_by_index(index).get_ref_addr()
            if ptr:
                return addr
            return str_cls(self.mem, addr)

        def set_str(self, val):
            """set a str either by address or with a B/CString object"""
            if type(val) is int:
                ptr = val
            elif isinstance(val, str_cls):
                ptr = val.get_addr()
            else:
                raise ValueError("set cstring: wrong value: %s" % val)
            self._struct.get_field_by_index(index).set_ref_addr(ptr)

        self._setup_get_set(base_name, cls, get_str, set_str)

    def _setup_get_set(self, base_name, cls, get_func, set_func):
        setattr(cls, "get_" + base_name, get_func)
        setattr(cls, "set_" + base_name, set_func)

    def _gen_default_get_set(self, base_name, cls, field_def):
        index = field_def.index

        def get_func(self):
            return self._struct.get_field_by_index(index).get()

        def set_func(self, val):
            self._struct.get_field_by_index(index).set(val)

        self._setup_get_set(base_name, cls, get_func, set_func)

    def _gen_wrap_get_set(self, base_name, cls, field_def, wrap_funcs):
        if type(wrap_funcs) in (list, tuple):
            get_wrap = wrap_funcs[0]
            set_wrap = wrap_funcs[1]
        else:
            get_wrap = wrap_funcs
            set_wrap = None

        # default conversion is integer conversion
        if set_wrap is None:
            set_wrap = int

        index = field_def.index
        if get_wrap:

            def get_func(self, raw=False):
                val = self._struct.get_field_by_index(index).get()
                if raw:
                    return val
                return get_wrap(val)

        else:

            def get_func(self):
                return self._struct.get_field_by_index(index).get()

        if set_wrap:

            def set_func(self, val, raw=False):
                if not raw:
                    val = set_wrap(val)
                self._struct.get_field_by_index(index).set(val)

        else:

            def set_func(self, val):
                self._struct.get_field_by_index(index).set(val)

        self._setup_get_set(base_name, cls, get_func, set_func)

    def _name_convert(self, name):
        """convert camel case names to underscore"""
        # strip leading prefix
        pos = name.find("_")
        if pos > 0:
            name = name[pos + 1 :]
        # to underscore
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def AmigaTypeDef(struct_def, wrap=None):
    """a class decorator that automatically adds get/set methods
    for AmigaStruct fields"""
    decorator = AmigaTypeDecorator(struct_def, wrap)

    def deco_func(cls):
        return decorator.decorate(cls)

    return deco_func
