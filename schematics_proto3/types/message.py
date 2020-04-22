# -*- coding:utf-8 -*-
from schematics.types import ModelType

from schematics_proto3.types.base import ProtobufTypeMixin


__all__ = ['MessageType']


class MessageType(ProtobufTypeMixin, ModelType):

    def convert(self, value, context):
        # TODO: If instance does not match protobuf msg type but is a
        #       protobuf msg nerveless, raise informative exception.
        # pylint: disable=protected-access
        if isinstance(value, self.model_class._options.extras['_protobuf_class']):
            return self.model_class.load_protobuf(value)

        return super().convert(value, context)
