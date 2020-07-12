# -*- coding:utf-8 -*-
from schematics.types import ModelType

from schematics_proto3.types.base import ProtobufTypeMixin
from schematics_proto3.unset import Unset

__all__ = ['MessageType']


class MessageType(ProtobufTypeMixin, ModelType):

    def convert(self, value, context):
        # TODO: If instance does not match protobuf msg type but is a
        #       protobuf msg nerveless, raise informative exception.
        # pylint: disable=protected-access
        if isinstance(value, self.model_class.protobuf_options.message_class):
            return self.model_class.load_protobuf(value)

        return super().convert(value, context)

    def convert_protobuf(self, msg, field_name, field_names):
        # TODO: Check that model_class is an instance of Model
        if field_name not in field_names:
            return Unset

        # TODO: Catch AttributeError and raise proper exception.
        value = getattr(msg, field_name)

        return self.model_class.load_protobuf(value)

    def export_protobuf(self, msg, field_name, value):
        # pylint: disable=no-self-use
        # TODO: Check that model_class is an instance of Model
        if field_name is Unset:
            return

        setattr(
            msg,
            field_name,
            value.to_protobuf(),
        )
