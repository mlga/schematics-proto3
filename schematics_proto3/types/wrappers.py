# -*- coding:utf-8 -*-
import os
import random
from datetime import datetime, timedelta, timezone

from google.protobuf import wrappers_pb2
from schematics.exceptions import ValidationError
from schematics.types import IntType, FloatType, BooleanType, StringType, BaseType

from schematics_proto3.types.base import ProtobufTypeMixin
from schematics_proto3.unset import Unset

__all__ = ['IntWrapperType', 'FloatWrapperType', 'BoolWrapperType',
           'StringWrapperType', 'BytesWrapperType', 'TimestampType']


WRAPPER_TYPES = (
    wrappers_pb2.Int32Value,
    wrappers_pb2.Int64Value,
    wrappers_pb2.BytesValue,
    wrappers_pb2.StringValue,
    wrappers_pb2.BoolValue,
    wrappers_pb2.UInt32Value,
    wrappers_pb2.UInt64Value,
    wrappers_pb2.FloatValue,
    wrappers_pb2.DoubleValue,
)


class WrapperTypeMixin(ProtobufTypeMixin):

    def convert(self, value, context):
        if value is Unset:
            return Unset

        # TODO: Is is avoidable to use this?
        if isinstance(value, WRAPPER_TYPES):
            value = value.value

        return super().convert(value, context)

    def convert_protobuf(self, msg, field_name, field_names):
        # pylint: disable=no-self-use
        if field_name not in field_names:
            return Unset

        value = getattr(msg, field_name)

        return value.value

    def export_protobuf(self, msg, field_name, value):
        # pylint: disable=no-self-use
        # TODO: Check that model_class is an instance of Model
        if value is Unset or value is None:
            return

        field = getattr(msg, field_name)
        field.value = value


class IntWrapperType(WrapperTypeMixin, IntType):
    pass


class FloatWrapperType(WrapperTypeMixin, FloatType):
    pass


class BoolWrapperType(WrapperTypeMixin, BooleanType):
    pass


class StringWrapperType(WrapperTypeMixin, StringType):
    pass


class BytesWrapperType(WrapperTypeMixin, BaseType):

    MESSAGES = {
        'max_length': "Bytes value is too long.",
        'min_length': "Bytes value is too short.",
    }

    def __init__(self, max_length=None, min_length=None, **kwargs):
        # TODO: Validate boundaries.
        self.max_length = max_length
        self.min_length = min_length

        super().__init__(**kwargs)

    def validate_length(self, value, context=None):
        # pylint: disable=unused-argument
        length = len(value)
        if self.max_length is not None and length > self.max_length:
            raise ValidationError(self.messages['max_length'])
        if self.min_length is not None and length < self.min_length:
            raise ValidationError(self.messages['min_length'])

    def _mock(self, context=None):
        length = random.randint(
            self.min_length if self.min_length is None else 5,
            self.max_length if self.max_length is None else 256,
        )
        return os.urandom(length)


class TimestampType(ProtobufTypeMixin, BaseType):

    def convert_protobuf(self, msg, field_name, field_names):
        # pylint: disable=no-self-use
        if field_name not in field_names:
            return Unset

        value = getattr(msg, field_name)

        return value

    def to_native(self, value, context=None):
        if isinstance(value, datetime):
            return value

        try:
            return (
                datetime(1970, 1, 1, tzinfo=timezone.utc)
                + timedelta(seconds=value.seconds, microseconds=value.nanos // 1000)
            )
        except (ValueError, TypeError):
            # TODO: Informative error or Unset?
            return None
