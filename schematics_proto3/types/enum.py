# -*- coding:utf-8 -*-
from typing import Type

from schematics.common import NOT_NONE
from schematics.exceptions import ConversionError
from schematics.types import BaseType
from schematics.undefined import Undefined

from schematics_proto3.enum import ProtobufEnum
from schematics_proto3.types.base import ProtobufTypeMixin
from schematics_proto3.unset import Unset

__all__ = ['EnumType']


class EnumType(ProtobufTypeMixin, BaseType):

    def __init__(self, enum_class: Type[ProtobufEnum], *, unset_variant=Unset, **kwargs):
        super().__init__(**kwargs)

        self.enum_class: Type[ProtobufEnum] = enum_class
        self.unset_variant = unset_variant

    def check_required(self: BaseType, value, context):
        # Treat Unset as required rule violation.
        if self.required and value in {Unset, self.unset_variant}:
            raise ConversionError(self.messages['required'])

        super().check_required(value, context)

    def convert(self, value, context):
        if value in {Unset, self.unset_variant}:
            return Unset

        if isinstance(value, str):
            return self.enum_class[value]

        if isinstance(value, int):
            return self.enum_class(value)

        raise AttributeError(f'Expected int or str, got {type(value)}')

    def export(self, value, format, context):  # pylint:disable=redefined-builtin
        if value is Unset:
            export_level = self.get_export_level(context)

            if export_level <= NOT_NONE:
                return Undefined

            return Unset

        return value.name

    def convert_protobuf(self, msg, field_name, field_names):
        # pylint:disable=unused-argument
        # TODO: Catch AttributeError and raise proper exception.
        value = getattr(msg, field_name)

        if value in {Unset, self.unset_variant}:
            return Unset

        return value

    def export_protobuf(self, msg, field_name, value):
        # pylint: disable=no-self-use
        # TODO: Check that model_class is an instance of Model
        if field_name is Unset:
            return

        setattr(
            msg,
            field_name,
            value.value,
        )
