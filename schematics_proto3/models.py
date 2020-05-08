# -*- coding:utf-8 -*-
import schematics
from google.protobuf.message import Message

from schematics_proto3.types.base import ProtobufTypeMixin
from schematics_proto3.unset import Unset
from schematics_proto3.utils import get_value_fallback


class Model(schematics.Model):
    """
    Base class for models operating with protobuf messages.
    """
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
            pb_field_name = field.metadata.get('protobuf_field', name)
            value_getter_func = getattr(field, 'convert_protobuf', get_value_fallback)

            values[name] = value_getter_func(msg, pb_field_name, field_names)

        return cls(values)

    def to_protobuf(self: schematics.Model) -> Message:
        assert isinstance(self, schematics.Model)

        msg = self._options.extras['_protobuf_class']()

        for name, field in self.fields.items():
            pb_name = field.metadata.get('protobuf_field', name)

            if isinstance(field, ProtobufTypeMixin):
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
