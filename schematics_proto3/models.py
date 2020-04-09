# -*- coding:utf-8 -*-
from typing import Iterable

import schematics
from google.protobuf import wrappers_pb2
from google.protobuf.message import Message
from schematics.types import ModelType, ListType

from schematics_proto3.types import ProtobufWrapperMixin, OneOfType
from schematics_proto3.unset import Unset

PRIMITIVE_TYPES = (str, int, float, bool, bytes)
WRAPPER_TYPES = (
    wrappers_pb2.DoubleValue,
    wrappers_pb2.FloatValue,
    wrappers_pb2.Int64Value,
    wrappers_pb2.UInt64Value,
    wrappers_pb2.Int32Value,
    wrappers_pb2.UInt32Value,
    wrappers_pb2.BoolValue,
    wrappers_pb2.StringValue,
    wrappers_pb2.BytesValue,
    # timestamp_pb2.Timestamp,
)


def get_value(msg, field_name, field_names):
    # TODO: Catch AttributeError and raise proper exception.
    value = getattr(msg, field_name)

    # Always return value of a primitive type. It it always set explicitly or via falling back to default.
    if isinstance(value, PRIMITIVE_TYPES):
        return value

    # For compound types, the field has been set only if it is present on fields list.
    if field_name not in field_names:
        return Unset

    if isinstance(value, WRAPPER_TYPES):
        return value.value

    if isinstance(value, Iterable):
        # repeated field
        return value

    # if isinstance(value, timestamp_pb2.Timestamp):
    #     return value

    raise RuntimeError(f'Value of unknown type {type(value)}')


class Model(schematics.Model):
    # pylint: disable=no-member

    def __init__(self, *args, **kwargs):
        # TODO: Drop this when todo below is done.
        # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)
        # TODO: Validate fields compatibility between schematics model and
        #       protobuf message.

    @classmethod
    def load_protobuf(cls, msg):
        # pylint: disable=too-many-branches
        # TODO: Refactor this method and remove above comment.
        assert issubclass(cls, schematics.Model)

        field_names = {descriptor.name for descriptor, _ in msg.ListFields()}
        values = {}

        for name, field in cls.fields.items():
            pb_name = field.metadata.get('protobuf_field', name)

            if isinstance(field, ModelType):
                # TODO: Check that model_class is an instance of Model

                if pb_name not in field_names:
                    values[name] = Unset
                else:
                    # TODO: Catch AttributeError and raise proper exception.
                    value = getattr(msg, pb_name)
                    values[name] = field.model_class.load_protobuf(value)
            elif isinstance(field, ListType):
                if isinstance(field.field, ModelType):
                    # TODO: recursively load model
                    values[name] = get_value(msg, pb_name, field_names)
                else:
                    values[name] = get_value(msg, pb_name, field_names)
            elif isinstance(field, OneOfType):
                # TODO: Handle value error:
                #       ValueError: Protocol message has no oneof "X" field.
                variant_name = msg.WhichOneof(pb_name)

                if variant_name is None:
                    values[name] = Unset
                else:
                    field.variant = variant_name
                    if isinstance(field.variant_type, ModelType):
                        # TODO: Catch AttributeError and raise proper exception.
                        value = getattr(msg, variant_name)
                        values[name] = field.variant_type.model_class.load_protobuf(value)
                    else:
                        values[name] = get_value(msg, variant_name, field_names)
            else:
                values[name] = get_value(msg, pb_name, field_names)

        return cls(values)

    def to_protobuf(self: schematics.Model) -> Message:
        assert isinstance(self, schematics.Model)

        msg = self._options.extras['_protobuf_class']()

        for name, field in self.fields.items():
            pb_name = field.metadata.get('protobuf_field', name)

            if isinstance(field, ProtobufWrapperMixin):
                # This is a wrapped value, assign it iff not Unset.
                val = getattr(self, name)
                if val is not Unset:
                    wrapper = getattr(msg, pb_name)
                    wrapper.value = val
            elif isinstance(field, Model):
                # Compound, nested field, delegate serialisation to model
                # instance.
                setattr(msg, pb_name, field.to_protobuf())
            else:
                # Primitive value, just assign it.
                setattr(msg, pb_name, getattr(self, name))

        return msg
