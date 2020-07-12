# -*- coding:utf-8 -*-
from schematics_proto3.unset import Unset

PRIMITIVE_TYPES = (str, int, float, bool, bytes)


def get_value_fallback(msg, field_name, field_names):
    # TODO: Catch AttributeError and raise proper exception.
    value = getattr(msg, field_name)

    # Always return value of a primitive type. It it always set explicitly or via falling back to default.
    if isinstance(value, PRIMITIVE_TYPES):
        return value

    # For compound types, the field has been set only if it is present on fields list.
    if field_name not in field_names:
        return Unset

    return value


def set_value_fallback(msg, field_name, value):
    if value is Unset:
        return

    setattr(msg, field_name, value)
