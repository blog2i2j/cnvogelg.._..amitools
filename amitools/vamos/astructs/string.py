from .typebase import TypeBase
from .pointer import APTR, BPTR


class CStringType(TypeBase):
    def __init__(self, mem, addr, **kwargs):
        super(CStringType, self).__init__(mem, addr, **kwargs)

    def get(self):
        if self._addr == 0:
            return None
        else:
            return self._mem.r_cstr(self._addr)

    def set(self, val):
        if self._addr == 0:
            raise ValueError("Can't set NULL string!")
        else:
            self._mem.w_cstr(self._addr, val)

    def __getattr__(self, key):
        if key == "str":
            return self.get()
        return super(CStringType, self).__getattr__(key)

    def __setattr__(self, key, val):
        if key == "str":
            self.set(val)
        super(CStringType, self).__setattr__(key, val)

    def __eq__(self, other):
        # compare against other string
        if type(other) is str:
            return self.get() == other
        elif other is None:
            return self.get() is None
        else:
            super(CStringType, self).__eq__(other)

    @classmethod
    def alloc_inst(self, alloc, txt, tag=None):
        if tag is None:
            tag = "CString('%s')" % txt
        return alloc.alloc_cstr(tag, txt)

    @classmethod
    def free_inst(self, alloc, mem_obj):
        alloc.free_cstr(mem_obj)


class BStringType(TypeBase):
    def __init__(self, mem, addr, **kwargs):
        super(BStringType, self).__init__(mem, addr, **kwargs)

    def get(self):
        if self._addr == 0:
            return None
        else:
            return self._mem.r_bstr(self._addr)

    def set(self, val):
        if self._addr == 0:
            raise ValueError("Can't set BNULL string!")
        else:
            self._mem.w_bstr(self._addr, val)

    def __getattr__(self, key):
        if key == "str":
            return self.get()
        return super(BStringType, self).__getattr__(key)

    def __setattr__(self, key, val):
        if key == "str":
            self.set(val)
        super(BStringType, self).__setattr__(key, val)

    def __eq__(self, other):
        # compare against other string
        if type(other) is str:
            return self.get() == other
        elif other is None:
            return self.get() is None
        else:
            super(BStringType, self).__eq__(other)

    @classmethod
    def alloc_inst(cls, alloc, txt, tag=None):
        if tag is None:
            tag = "BString('%s')" % txt
        return alloc.alloc_bstr(tag, txt)

    @classmethod
    def free_inst(cls, alloc, mem_obj):
        alloc.free_bstr(mem_obj)


class CSTR(APTR(CStringType)):
    @classmethod
    def get_signature(cls):
        return "CSTR"

    def get_str(self):
        if self.aptr == 0:
            return None
        else:
            return self.ref().get()

    def set_str(self, val):
        if self.aptr == 0:
            raise ValueError("Can't set NULL string!")
        else:
            self.ref().set(val)

    def __getattr__(self, key):
        if key == "str":
            return self.get_str()
        return super(CSTR, self).__getattr__(key)

    def __setattr__(self, key, val):
        if key == "str":
            self.set_str(val)
        super(CSTR, self).__setattr__(key, val)


class BSTR(BPTR(BStringType)):
    @classmethod
    def get_signature(cls):
        return "BSTR"

    def get_str(self):
        if self.bptr == 0:
            return None
        else:
            return self.ref().get()

    def set_str(self, val):
        if self.bptr == 0:
            raise ValueError("Can't set BNULL string!")
        else:
            self.ref().set(val)

    def __getattr__(self, key):
        if key == "str":
            return self.get_str()
        return super(BSTR, self).__getattr__(key)

    def __setattr__(self, key, val):
        if key == "str":
            self.set_str(val)
        super(BSTR, self).__setattr__(key, val)
