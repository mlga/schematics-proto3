# -*- coding:utf-8 -*-
from schematics.common import NOT_NONE
from schematics.exceptions import ConversionError
from schematics.types import BaseType
from schematics.undefined import Undefined

from schematics_proto3.unset import Unset


class ProtobufTypeMixin:
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
    class IntWrapperType(ProtobufTypeMixin, IntType):
    pass
    ```
    Above, handling of Unset value if done by ProtobufTypeMixin, proper int
    values will be serialized, deserialized and validated by IntType. This way
    we can utilise what we already have.
    """

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

    def export(self, value, format, context):  # pylint:disable=redefined-builtin
        if value is Unset:
            export_level = self.get_export_level(context)

            if export_level <= NOT_NONE:
                return Undefined

            return Unset

        return super().export(value, format, context)
