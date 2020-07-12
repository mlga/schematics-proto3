# -*- coding:utf-8 -*-
from enum import EnumMeta, IntEnum

from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper

__all__ = ['ProtobufEnum']


class _Ignore:
    """
    Sentinel class to denote `protobuf_enum` argument in ProtobufEnum base
    class.
    """
    # pylint: disable=too-few-public-methods
    __slots__ = []


class ProtobufEnumMeta(EnumMeta):

    @classmethod
    def __prepare__(mcs, name, bases, protobuf_enum=None):
        # pylint: disable=arguments-differ,unused-argument
        return super().__prepare__(name, bases)

    def __new__(mcs, name, bases, attrs, protobuf_enum=None):
        if protobuf_enum is _Ignore:
            return super().__new__(mcs, name, bases, attrs)

        if protobuf_enum is None:
            raise RuntimeError(f'protobuf_enum argument of class {name} must be set')

        if not isinstance(protobuf_enum, EnumTypeWrapper):
            raise RuntimeError('protobuf_enum must be a Protobuf enum')

        for key, value in protobuf_enum.items():
            attrs[key] = value

        cls = super().__new__(mcs, name, bases, attrs)

        mcs._validate_cls(protobuf_enum, cls)

        return cls

    @staticmethod
    def _validate_cls(pb_enum_cls, cls):
        pb_enum_variants = set(pb_enum_cls.keys())
        cls_enum_variants = {v.name for v in cls}

        if pb_enum_variants != cls_enum_variants:
            additional = cls_enum_variants - pb_enum_variants

            raise RuntimeError(
                f'ProtobufEnum subclass cannot contain members other than '
                f'`protobuf_enum`. '
                f'\n'
                f'`{cls.__qualname__}` contains following '
                f'excess members: {",".join(additional)}.'
            )


class ProtobufEnum(IntEnum, metaclass=ProtobufEnumMeta, protobuf_enum=_Ignore):
    pass
