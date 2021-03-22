from .astruct import (
    AmigaStruct,
    AmigaStructTypes,
    APTR_SELF,
    BPTR_SELF,
    TypeBase,
    FieldDef,
)
from .pointer import APTR, BPTR


class InvalidAmigaTypeException(Exception):
    def __init__(self, type_name):
        self.type_name = type_name

    def __str__(self):
        return self.type_name


class AmigaStructDecorator(object):
    def decorate(self, cls):
        # check class and store base name (without Struct postfix)
        type_name = self._validate_class(cls)
        cls._type_name = type_name
        # setup field data
        self._setup_fields(cls)
        # add to pool
        AmigaStructTypes.add_struct(cls)
        return cls

    def _setup_fields(self, cls):
        total_size = 0
        offset = 0
        index = 0
        name_to_field_def = {}
        field_defs = []

        # run through fields
        for field_type, field_name in cls._format:

            # replace self pointers
            if field_type is APTR_SELF:
                field_type = APTR(cls)
            elif field_type is BPTR_SELF:
                field_type = BPTR(cls)

            # ensure correct format
            if type(field_type) is not type or not issubclass(field_type, TypeBase):
                raise RuntimeError(
                    "invalid field: {}: {} in {}".format(
                        field_name, field_type, cls.__name__
                    )
                )

            field_size = field_type.get_byte_size()
            if field_size is None:
                raise RuntimeError(
                    "invalid field: {}: {} in {}".format(
                        field_name, field_type, cls.__name__
                    )
                )

            # create field
            field_def = FieldDef(
                index=index,
                offset=offset,
                type=field_type,
                name=field_name,
                size=field_size,
                struct=cls,
            )
            field_defs.append(field_def)

            # store name -> index mapping
            name_to_field_def[field_name] = field_def

            # add name to class directly
            field_name = field_name + "_def"
            if getattr(cls, field_name, None) is not None:
                raise RuntimeError("field '%s' already a member of class!" % field_name)
            setattr(cls, field_name, field_def)

            index += 1
            offset += field_size
            total_size += field_size

        # store in class
        cls._byte_size = total_size
        cls._field_defs = field_defs
        cls._name_to_field_def = name_to_field_def
        cls._num_fields = index

    def _validate_class(self, cls):
        # make sure cls is derived from AmigaStruct
        if cls.__bases__ != (AmigaStruct,):
            raise RuntimeError("cls must dervive from AmigaStruct")
        # make sure a format is declared
        _format = getattr(cls, "_format", None)
        if _format is None:
            raise RuntimeError("cls must contain a _format")
        # ensure that class ends with Struct
        name = cls.__name__
        if not name.endswith("Struct"):
            raise RuntimeError("cls must be named *Struct")
        base_name = name[: -len("Struct")]
        return base_name


def AmigaStructDef(cls):
    """a class decorator that setups up an amiga struct class"""
    decorator = AmigaStructDecorator()
    return decorator.decorate(cls)
