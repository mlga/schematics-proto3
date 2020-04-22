# -*- coding:utf-8 -*-
import os
import random

from schematics.exceptions import ValidationError
from schematics.types import IntType, FloatType, BooleanType, StringType, BaseType

from schematics_proto3.types.base import ProtobufTypeMixin


__all__ = ['IntWrapperType', 'FloatWrapperType', 'BoolWrapperType',
           'StringWrapperType', 'BytesWrapperType']


class IntWrapperType(ProtobufTypeMixin, IntType):
    pass


class FloatWrapperType(ProtobufTypeMixin, FloatType):
    pass


class BoolWrapperType(ProtobufTypeMixin, BooleanType):
    pass


class StringWrapperType(ProtobufTypeMixin, StringType):
    pass


class BytesWrapperType(ProtobufTypeMixin, BaseType):

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
