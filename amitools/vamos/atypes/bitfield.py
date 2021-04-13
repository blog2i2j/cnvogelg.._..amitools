import inspect


class BitField:
    _name_to_val = None # will be filled by decorator
    _val_to_name = None # will be filled by decorator

    @classmethod
    def to_strs(cls, val, check=True):
        res = []
        for bf_val in cls._val_to_name:
            if bf_val & val == bf_val:
                name = cls._val_to_name[bf_val]
                res.append(name)
                val &= ~bf_val
        if val != 0:
            if check:
                raise ValueError("invalid bits set: %x" % val)
            else:
                res.append(str(val))
        return res

    @classmethod
    def to_str(cls, val, check=True):
        return "|".join(cls.to_strs(val, check))

    @classmethod
    def from_strs(cls, *args):
        val = 0
        for name in args:
            if name in cls._name_to_val:
                bf_val = cls._name_to_val[name]
                val |= bf_val
            else:
                raise ValueError("invalid bit mask name: " + name)
        return val

    @classmethod
    def from_str(cls, val):
        return cls.from_strs(*val.split("|"))

    @classmethod
    def _get_bit_mask(cls, val):
        if type(val) is str:
            if val in cls._name_to_val:
                return cls._name_to_val[val]
            elif "|" in val:
                res = 0
                for v in val.split("|"):
                    res |= cls._name_to_val[v]
                return res
            else:
                raise ValueError("invalid bit mask name: " + val)
        else:
            return val

    @classmethod
    def is_set(cls, what, val):
        bmask = cls._get_bit_mask(what)
        return val & bmask == bmask

    @classmethod
    def is_clr(cls, what, val):
        bmask = cls._get_bit_mask(what)
        return val & bmask == 0

    def __init__(self, *values):
        val = 0
        for v in values:
            bmask = self._get_bit_mask(v)
            val |= bmask
        self.value = val

    def __str__(self):
        return self.to_str(self.value, False)

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, str(self))

    def __int__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        elif type(other) is int:
            return self.value == other
        else:
            return NotImplemented

    def has_bits(self, what):
        bmask = self._get_bit_mask(what)
        return self.value & bmask == bmask

    def set_bits(self, what):
        bmask = self._get_bit_mask(what)
        self.value |= bmask

    def clr_bits(self, what):
        bmask = self._get_bit_mask(what)
        self.value &= ~bmask

    def get_value(self):
        return self.value


def BitFieldType(cls):
    """a class decorator that generates a bit field class"""

    assert issubclass(cls, BitField)

    # collect integer vals
    _name_to_val = {}
    _val_to_name = {}
    mem = inspect.getmembers(cls)
    for name, val in mem:
        if type(val) in (int, int):
            # check that val is really a bit mask
            if val & (val - 1) != 0:
                raise ValueError("no bit mask in bit field: " % name)
            _name_to_val[name] = val
            _val_to_name[val] = name
    cls._name_to_val = _name_to_val
    cls._val_to_name = _val_to_name

    return cls
