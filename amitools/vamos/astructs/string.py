from .typebase import TypeBase
from .pointer import APTR, BPTR


class StringType(TypeBase):
    def __init__(self, mem, addr, **kwargs):
        super(StringType, self).__init__(mem, addr, **kwargs)

    def get(self):
        return self._mem.r_cstr(self._addr)

    def set(self, val):
        self._mem.w_cstr(self._addr, val)

    def __getattr__(self, key):
        if key == "str":
            return self.get()
        return super(StringType, self).__getattr__(key)

    def __setattr__(self, key, val):
        if key == "str":
            self.set(val)
        super(StringType, self).__setattr__(key, val)


class BCPLStringType(TypeBase):
    def __init__(self, mem, addr, **kwargs):
        super(BCPLStringType, self).__init__(mem, addr, **kwargs)

    def get(self):
        return self._mem.r_bstr(self._addr)

    def set(self, val):
        self._mem.w_bstr(self._addr, val)


class CSTR(APTR(StringType)):
    @classmethod
    def get_signature(cls):
        return "CSTR"

    def get_str(self):
        return self.ref().get()

    def set_str(self, val):
        self.ref().set(val)


class BSTR(BPTR(BCPLStringType)):
    @classmethod
    def get_signature(cls):
        return "BSTR"

    def get_str(self):
        return self.ref().get()

    def set_str(self, val):
        self.ref().set(val)
