# -*- coding:utf-8 -*-
from dataclasses import dataclass
from typing import Type

import schematics
from google.protobuf.message import Message

from schematics_proto3.types import OneOfType
from schematics_proto3.types.wrappers import WrapperTypeMixin
from schematics_proto3.utils import get_value_fallback


class _Ignore:
    """
    Sentinel class to denote `protobuf_enum` argument in ProtobufEnum base
    class.
    """
    # pylint: disable=too-few-public-methods
    __slots__ = []


@dataclass(frozen=True)
class ModelOptions:
    message_class: Type[Message]


class ModelMeta(schematics.ModelMeta):

    def __new__(mcs, name, bases, attrs, protobuf_message=None):
        cls = super().__new__(mcs, name, bases, attrs)

        if protobuf_message is _Ignore:
            return cls

        if protobuf_message is None:
            raise RuntimeError(f'protobuf_enum argument of class {name} must be set')

        if not issubclass(protobuf_message, Message):
            raise RuntimeError('protobuf_enum must be a subclass of Protobuf message')

        # TODO: Validate fields against protobuf message definition
        cls.protobuf_options = ModelOptions(
            message_class=protobuf_message,
        )

        return cls


class Model(schematics.Model, metaclass=ModelMeta, protobuf_message=_Ignore):
    """
    Base class for models operating with protobuf messages.
    """
    # pylint: disable=no-member

    protobuf_options: ModelOptions

    @classmethod
    def load_protobuf(cls, msg):
        field_names = {descriptor.name for descriptor, _ in msg.ListFields()}
        values = {}

        for name, field in cls.fields.items():
            pb_field_name = field.metadata.get('protobuf_field', name)
            value_getter_func = getattr(field, 'convert_protobuf', get_value_fallback)

            values[name] = value_getter_func(msg, pb_field_name, field_names)

        return cls(values)

    def to_protobuf(self: 'Model') -> Message:
        assert isinstance(self, schematics.Model)

        msg = self.protobuf_options.message_class()

        for name, field in self.fields.items():
            pb_name = field.metadata.get('protobuf_field', name)

            if isinstance(field, WrapperTypeMixin):
                # This is a wrapped value, assign it iff not Unset.
                val = getattr(self, name)
                field.export_protobuf(msg, pb_name, val)
            elif isinstance(field, Model):
                # Compound, nested field, delegate serialisation to model
                # instance.
                setattr(msg, pb_name, field.to_protobuf())
            elif isinstance(field, OneOfType):
                val = getattr(self, name)
                field.export_protobuf(msg, pb_name, val)
            else:
                # Primitive value, just assign it.
                val = getattr(self, name)
                if val is not None:
                    setattr(msg, pb_name, val)

        return msg

    def __hash__(self):
        return hash(tuple(field for field in self.fields))
