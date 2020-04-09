# -*- coding:utf-8 -*-
import os
import random

from schematics.common import NOT_NONE
from schematics.exceptions import ConversionError, ValidationError, CompoundError, StopValidationError
from schematics.types import BaseType, FloatType, BooleanType, StringType, IntType, \
    ModelType as SchModelType, ListType, CompoundType
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
        # pylint: disable=protected-access
        if isinstance(value, self.model_class._options.extras['_protobuf_class']):
            return self.model_class.load_protobuf(value)

        return super().convert(value, context)


class RepeatedType(ProtobufWrapperMixin, ListType):
    pass


class OneOfVariant:

    slots = ('variant', 'value')

    def __init__(self, variant, value):
        self.variant = variant
        self.value = value

    def __str__(self):
        return f'OneOfVariant<{self.variant}, {self.value}>'

    def __eq__(self, other):
        if not isinstance(other, OneOfVariant):
            return False

        return self.variant == other.variant and self.value == other.value


class OneOfType(ProtobufWrapperMixin, CompoundType):

    def __init__(self, variants_spec, *args, **kwargs):
        # TODO: Check that each:
        #       1) key in variants_spec exists in protobuf message
        #          (with respect to renaming)
        #       2) value in variants_spec is a subclass of BaseType
        super().__init__(*args, **kwargs)

        self.variants_spec = variants_spec
        self._variant = None
        self._variant_type = None
        self._protobuf_renames = {}

        for name, spec in variants_spec.items():
            pb_name = spec.metadata.get('protobuf_field', None)

            if pb_name is not None:
                if pb_name in variants_spec:
                    raise RuntimeError(f'Duplicated variant name `{pb_name}`')

                self._protobuf_renames[pb_name] = name

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, name):
        if name in self.variants_spec:
            self._variant = name
            self._variant_type = self.variants_spec[name]
        elif name in self._protobuf_renames:
            self._variant = self._protobuf_renames[name]
            self._variant_type = self.variants_spec[self._variant]
        else:
            raise KeyError(name)

    @property
    def variant_type(self):
        return self._variant_type

    def pre_setattr(self, value):
        # TODO: Raise proper exceptions
        variant = None

        if isinstance(value, OneOfVariant):
            variant = value

        if isinstance(value, tuple):
            if len(value) != 2:
                raise RuntimeError(
                    f'OneOfVariant tuple must have 2 items, got {len(value)}'
                )
            variant = OneOfVariant(value[0], value[1])

        if isinstance(value, dict):
            if 'variant' not in value or 'value' not in value:
                raise RuntimeError(
                    f'OneOfVariant dict must have `variant` and `value` keys.'
                )
            variant = OneOfVariant(value['variant'], value['value'])

        if variant is None:
            raise RuntimeError('Unknown value')

        self.variant = variant.variant

        return variant

    def convert(self, value, context):
        # TODO: Raise proper exception (ConversionError)
        if value is Unset:
            return Unset

        if self.variant is None:
            raise RuntimeError('Variant is unset')

        val = self.variant_type.convert(value, context)

        return OneOfVariant(self.variant, val)

    def validate(self: BaseType, value, context=None):
        if value is Unset:
            return Unset

        # Run validation of inner variant field.
        try:
            self.variant_type.validate(value.value, context)
        except ValidationError as ex:
            raise CompoundError({
                self.variant: ex,
            })

        # Run validation for this field itself.
        # Following is basically copy of a code in BaseType :/
        errors = []
        for validator in self.validators:
            try:
                validator(value, context)
            except ValidationError as exc:
                errors.append(exc)
                if isinstance(exc, StopValidationError):
                    break
        if errors:
            raise ValidationError(errors)

        return value

    def export(self, value, format, context):  # pylint:disable=redefined-builtin
        if value is Unset:
            export_level = self.get_export_level(context)

            if export_level <= NOT_NONE:
                return Undefined

            return Unset

        return {
            'variant': value.variant,
            'value': value.value,
        }

    # Those methods are abstract in CompoundType class, override them to
    # silence linters.
    # Raising NotImplementedError does not matter as we already override
    # convert and export (without underscores) which are called earlier.
    def _convert(self, value, context):
        raise NotImplementedError()

    def _export(self, value, format, context):  # pylint:disable=redefined-builtin
        raise NotImplementedError()
