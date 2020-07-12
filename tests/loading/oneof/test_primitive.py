# -*- coding:utf-8 -*-
from unittest.mock import Mock

import pytest
from schematics.exceptions import DataError, ValidationError
from schematics.types import IntType, StringType

from schematics_proto3 import types
from schematics_proto3.models import Model
from schematics_proto3.oneof import OneOfVariant
from schematics_proto3.unset import Unset
from tests import schematics_proto3_tests_pb2 as pb2
from tests.utils.randoms import value_for_primitive
from tests.utils.wire import mimic_protobuf_wire_transfer


##########################################
#  Message fixtures                      #
##########################################

@pytest.fixture
def msg_all_set():
    msg = pb2.OneOfPrimitive()
    msg.value2 = value_for_primitive('string_field')

    return mimic_protobuf_wire_transfer(msg)


@pytest.fixture
def msg_unsets():
    return mimic_protobuf_wire_transfer(pb2.OneOfPrimitive())


##########################################
#  Model fixtures                        #
##########################################

@pytest.fixture
def model_class_optional():

    class ModelOptional(Model, protobuf_message=pb2.OneOfPrimitive):

        inner = types.OneOfType(variants_spec={
            'value1': IntType(),
            'value2': StringType(),
        })

    return ModelOptional


@pytest.fixture
def model_class_required():

    class ModelRequired(Model, protobuf_message=pb2.OneOfPrimitive):
        inner = types.OneOfType(
            variants_spec={
                'value1': IntType(),
                'value2': StringType(),
            },
            required=True,
        )

    return ModelRequired


@pytest.fixture
def model_class_none_not_dumped():

    class ModelNoneNotDumped(Model, protobuf_message=pb2.OneOfPrimitive):
        inner = types.OneOfType(variants_spec={
            'value1': IntType(),
            'value2': StringType(),
        })

        class Options:
            serialize_when_none = False

    return ModelNoneNotDumped


@pytest.fixture
def model_class_field_renamed():

    class ModelFieldRenamed(Model, protobuf_message=pb2.OneOfPrimitive):
        custom_inner = types.OneOfType(
            variants_spec={
                'value1': IntType(),
                'custom_value2': StringType(metadata=dict(protobuf_field='value2')),
            },
            metadata=dict(protobuf_field='inner'),
        )

    return ModelFieldRenamed


@pytest.fixture
def model_class_field_renamed_required():

    class ModelFieldRenamedRequired(Model, protobuf_message=pb2.OneOfPrimitive):
        custom_inner = types.OneOfType(
            variants_spec={
                'value1': IntType(),
                'custom_value2': StringType(metadata=dict(protobuf_field='value2')),
            },
            metadata=dict(protobuf_field='inner'),
            required=True,
        )

    return ModelFieldRenamedRequired


@pytest.fixture
def model_class_validated_factory():
    def _factory(validator_func=None, inner_validator_func=None):
        outer_validators = [validator_func] if validator_func else []
        inner_validators = [inner_validator_func] if inner_validator_func else []

        class ModelValidated(Model, protobuf_message=pb2.OneOfPrimitive):
            inner = types.OneOfType(
                variants_spec={
                    'value1': IntType(),
                    'value2': StringType(validators=inner_validators),
                },
                validators=outer_validators,
            )

        return ModelValidated

    return _factory


@pytest.fixture
def model_class_validated_renamed_factory():
    def _factory(validator_func=None, inner_validator_func=None):
        outer_validators = [validator_func] if validator_func else []
        inner_validators = [inner_validator_func] if inner_validator_func else []

        class ModelValidated(Model, protobuf_message=pb2.OneOfPrimitive):
            custom_inner = types.OneOfType(
                variants_spec={
                    'value1': IntType(),
                    'custom_value2': StringType(
                        validators=inner_validators,
                        metadata=dict(protobuf_field='value2'),
                    ),
                },
                validators=outer_validators,
                metadata=dict(protobuf_field='inner'),
            )

        return ModelValidated

    return _factory


##########################################
#  Tests                                 #
##########################################

def test_optional_all_set(model_class_optional, msg_all_set):
    model = model_class_optional.load_protobuf(msg_all_set)
    model.validate()

    # check model instance fields
    assert model.inner.variant == 'value2'
    assert model.inner.value == msg_all_set.value2

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert 'variant' in data['inner']
    assert 'value' in data['inner']
    assert data['inner']['variant'] == 'value2'
    assert data['inner']['value'] == msg_all_set.value2

    # compare dump to native
    assert model.to_native() == data


def test_optional_unsets(model_class_optional, msg_unsets):
    model = model_class_optional.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.inner is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert data['inner'] is Unset

    # compare dump to native
    assert model.to_native() == data


def test_none_not_dumped_all_set(model_class_none_not_dumped, msg_all_set):
    model = model_class_none_not_dumped.load_protobuf(msg_all_set)
    model.validate()

    # check model instance fields
    assert model.inner.variant == 'value2'
    assert model.inner.value == msg_all_set.value2

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert 'variant' in data['inner']
    assert 'value' in data['inner']
    assert data['inner']['variant'] == 'value2'
    assert data['inner']['value'] == msg_all_set.value2

    # compare dump to native
    assert model.to_native() == data


def test_none_not_dumped_unsets(model_class_none_not_dumped, msg_unsets):
    model = model_class_none_not_dumped.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.inner is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' not in data

    # compare dump to native
    assert model.to_native() == data


def test_required_unsets(model_class_required, msg_unsets):
    with pytest.raises(DataError) as ex:
        model_class_required.load_protobuf(msg_unsets)

    errors = ex.value.to_primitive()
    assert 'inner' in errors
    assert 'required' in errors['inner'][0]


def test_required_unsets_renamed(model_class_field_renamed_required, msg_unsets):
    with pytest.raises(DataError) as ex:
        model_class_field_renamed_required.load_protobuf(msg_unsets)

    errors = ex.value.to_primitive()
    assert 'custom_inner' in errors
    assert 'required' in errors['custom_inner'][0]


def test_renamed_all_set(model_class_field_renamed, msg_all_set):
    model = model_class_field_renamed.load_protobuf(msg_all_set)
    model.validate()

    # check model instance fields
    assert model.custom_inner.variant == 'custom_value2'
    assert model.custom_inner.value == msg_all_set.value2

    # check primitive dump
    data = model.to_primitive()

    assert 'custom_inner' in data
    assert 'variant' in data['custom_inner']
    assert 'value' in data['custom_inner']
    assert data['custom_inner']['variant'] == 'custom_value2'
    assert data['custom_inner']['value'] == msg_all_set.value2

    # compare dump to native
    assert model.to_native() == data


def test_renamed_unsets(model_class_field_renamed, msg_unsets):
    model = model_class_field_renamed.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.custom_inner is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'custom_inner' in data
    assert data['custom_inner'] is Unset

    # compare dump to native
    assert model.to_native() == data


def test_validated_all_set(model_class_validated_factory, msg_all_set):
    validator_func = Mock()
    model_cls = model_class_validated_factory(validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    model.validate()

    # check model instance fields
    assert model.inner.variant == 'value2'
    assert model.inner.value == msg_all_set.value2
    validator_func.assert_called_once_with(OneOfVariant('value2', msg_all_set.value2))

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert 'variant' in data['inner']
    assert 'value' in data['inner']
    assert data['inner']['variant'] == 'value2'
    assert data['inner']['value'] == msg_all_set.value2

    # compare dump to native
    assert model.to_native() == data


def test_validated_unsets(model_class_validated_factory, msg_unsets):
    validator_func = Mock()
    model_cls = model_class_validated_factory(validator_func)

    model = model_cls.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.inner is Unset
    validator_func.assert_not_called()

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert data['inner'] is Unset

    # compare dump to native
    assert model.to_native() == data


def test_validated_validation_error(model_class_validated_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_factory(validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    validator_func.assert_called_once_with(OneOfVariant('value2', msg_all_set.value2))
    assert 'inner' in errors
    assert 'Please speak up!' in errors['inner'][0], f"`Please speak up!` in `{errors['inner'][0]}`"


def test_validated_validation_error__inner(model_class_validated_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_factory(None, validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    validator_func.assert_called_once_with(msg_all_set.value2)
    assert 'inner' in errors
    assert 'value2' in errors['inner']
    assert len(errors['inner']['value2']) == 1
    assert 'Please speak up!' in errors['inner']['value2'][0]


def test_validated_validation_error_renamed(model_class_validated_renamed_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_renamed_factory(validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    validator_func.assert_called_once_with(OneOfVariant('custom_value2', msg_all_set.value2))
    assert 'custom_inner' in errors
    assert 'Please speak up!' in errors['custom_inner'][0], f"`Please speak up!` in `{errors['custom_inner'][0]}`"


def test_validated_validation_error_renamed__inner(model_class_validated_renamed_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_renamed_factory(None, validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    validator_func.assert_called_once_with(msg_all_set.value2)
    assert 'custom_inner' in errors
    assert 'custom_value2' in errors['custom_inner']
    assert len(errors['custom_inner']['custom_value2']) == 1
    assert 'Please speak up!' in errors['custom_inner']['custom_value2'][0]
