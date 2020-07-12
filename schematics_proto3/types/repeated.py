# -*- coding:utf-8 -*-
from schematics.types import ListType

from schematics_proto3.types.base import ProtobufTypeMixin
from schematics_proto3.unset import Unset

__all__ = ['RepeatedType']


class RepeatedType(ProtobufTypeMixin, ListType):

    def export_protobuf(self, msg, field_name, value):
        # pylint: disable=no-self-use
        # TODO: Check that model_class is an instance of Model
        if field_name is Unset:
            return

        field = getattr(msg, field_name)
        field.extend(value)
