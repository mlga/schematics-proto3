# -*- coding:utf-8 -*-
from schematics.common import NOT_NONE
from schematics.exceptions import ValidationError, DataError, CompoundError, StopValidationError
from schematics.types import CompoundType, BaseType
from schematics.undefined import Undefined

from schematics_proto3.oneof import OneOfVariant
from schematics_proto3.types.base import ProtobufTypeMixin
from schematics_proto3.unset import Unset
from schematics_proto3.utils import get_value_fallback, set_value_fallback

__all__ = ['OneOfType']


class OneOfType(ProtobufTypeMixin, CompoundType):

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
        self._default = Unset

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
                    'OneOfVariant dict must have `variant` and `value` keys.'
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
        except (ValidationError, DataError) as ex:
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
        if value in {Unset, None}:
            export_level = self.get_export_level(context)

            if export_level <= NOT_NONE:
                return Undefined

            return Unset

        return {
            'variant': value.variant,
            'value': self.variant_type.export(value.value, format, context),
        }

    # Those methods are abstract in CompoundType class, override them to
    # silence linters.
    # Raising NotImplementedError does not matter as we already override
    # convert and export (without underscores) which are called earlier.
    def _convert(self, value, context):
        raise NotImplementedError()

    def _export(self, value, format, context):  # pylint:disable=redefined-builtin
        raise NotImplementedError()

    def convert_protobuf(self, msg, field_name, field_names):
        # TODO: Handle value error:
        #       ValueError: Protocol message has no oneof "X" field.
        variant_name = msg.WhichOneof(field_name)

        if variant_name is None:
            return Unset

        self.variant = variant_name
        convert_func = getattr(self.variant_type, 'convert_protobuf', get_value_fallback)

        return convert_func(msg, variant_name, field_names)

    def export_protobuf(self, msg, field_name, value):  # pylint: disable=unused-argument
        # TODO: Check that model_class is an instance of Model
        if value in {Unset, None}:
            return

        # self.variant = field_name
        set_value = getattr(self.variant_type, 'export_protobuf', set_value_fallback)
        set_value(msg, self.variant, value.value)
