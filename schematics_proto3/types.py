# -*- coding:utf-8 -*-
import os
import random

from schematics.common import NOT_NONE
from schematics.exceptions import ConversionError, ValidationError
from schematics.types import BaseType, FloatType, BooleanType, StringType, IntType, ModelType as SchModelType, ListType, \
    PolyModelType
from schematics.undefined import Undefined

from schematics_proto3.unset import Unset


class ProtobufWrapperMixin:
    """
    Extension to schematics' type classes. It provides proper handling of Unset
    value, which accounts for:
     * serialization
     * deserialization
     * validation

    Implemented as a mixin to be an intermediate class between concrete type
    classes and schematics base classes.

    For example:
    ```
    class IntValueType(ProtobufWrapperMixin, IntType):
    pass
    ```
    Above, handling of Unset value if done by ProtobufWrapperMixin, proper int
    values will be serialized, deserialized and validated by IntType. This way
    we can utilise what we already have.
    """

    # def to_primitive(self: BaseType, value, context=None):
    #     """Convert internal data to a value safe to serialize.
    #     """
    #     # We have to serialize Unset to a value that schematics' internals
    #     # understand and treats as null/empty values.
    #     # This way, field will be correctly omitted during serialization if
    #     # configured this way.
    #     if self.get_export_level(context) <= NOT_NONE and value is Unset:
    #         return 'Unset'
    #
    #     return super().to_primitive(value, context)

    # def to_native(self: BaseType, value, context=None):
    #     """Convert untrusted data to a richer Python construct.
    #     """
    #     # Type conversions will fail on Unset for types like float etc. Treat
    #     # it as accepted primitive value without further mangling.
    #     if value is Unset:
    #         return Unset
    #
    #     return super().to_native(value, context)

    def check_required(self: BaseType, value, context):
        # Treat Unset as required rule violation.
        if self.required and value is Unset:
            raise ConversionError(self.messages['required'])

        super().check_required(value, context)

    def validate(self: BaseType, value, context=None):
        # If a value is Unset, we want to perform only require check alone.
        # Other validators provided for types like float etc. will fail
        # here and have no point in bing executed.
        if value is Unset:
            return Unset

        return super().validate(value, context)

    def convert(self, value, context):
        if value is Unset:
            return Unset

        return super().convert(value, context)

    def export(self, value, format, context):
        if value is Unset:
            export_level = self.get_export_level(context)

            if export_level <= NOT_NONE:
                return Undefined

            return Unset

        return super().export(value, format, context)


class IntValueType(ProtobufWrapperMixin, IntType):
    pass


class FloatValueType(ProtobufWrapperMixin, FloatType):
    pass


class BoolValueType(ProtobufWrapperMixin, BooleanType):
    pass


class StringValueType(ProtobufWrapperMixin, StringType):
    pass


class BytesValueType(ProtobufWrapperMixin, BaseType):

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


class ModelType(ProtobufWrapperMixin, SchModelType):

    def convert(self, value, context):
        # TODO: If instance does not match protobuf msg type but is a
        #       protobuf msg nerveless, raise informative exception.
        if isinstance(value,  self.model_class._options.extras['_protobuf_class']):
            return self.model_class.load_protobuf(value)

        return super().convert(value, context)


class RepeatedType(ProtobufWrapperMixin, ListType):
    pass


# class OneOfType(ProtobufWrapperMixin, BaseType):
#
#     def __init__(self, variants_spec, *args, **kwargs):
#         # TODO: Check that each:
#         #       1) key in variants_spec exists in protobuf message
#         #          (with respect to renaming)
#         #       2) value in variants_spec is a subclass of BaseType
#         super().__init__(*args, **kwargs)
#
#         self.variants_spec = variants_spec
#
#     def
#
#     def convert(self, value, context):
#         if value is Unset:
#             return Unset
#
#
#
#         msg_class = None
#         for kls in self.allowed_msg_classes:
#             if isinstance(value, kls):
#                 msg_class = kls
#                 break
#
#         if msg_class is None:
#             raise Exception('No match for oneof field found!')
#
#         # TODO: If instance does not match protobuf msg type but is a
#         #       protobuf msg nerveless, raise informative exception.
#         return msg_class.load_protobuf(value)
