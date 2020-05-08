# -*- coding:utf-8 -*-
from schematics.types import ListType

from schematics_proto3.types.base import ProtobufTypeMixin

__all__ = ['RepeatedType']


class RepeatedType(ProtobufTypeMixin, ListType):
    pass
