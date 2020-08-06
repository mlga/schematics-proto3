# -*- coding:utf-8 -*-
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from google.protobuf import timestamp_pb2
from schematics.exceptions import DataError, ValidationError

from schematics_proto3 import types
from schematics_proto3.models import Model
from schematics_proto3.unset import Unset
from tests import schematics_proto3_tests_pb2 as pb2
from tests.utils.wire import mimic_protobuf_wire_transfer


DUMMY_DATETIME_1 = datetime(1970, 5, 23, 15, 25, 46, 333, tzinfo=timezone.utc)
DUMMY_DATETIME_2 = datetime(2080, 6, 16, 5, 4, 0, 290, tzinfo=timezone.utc)


##########################################
#  Message fixtures                      #
##########################################

@pytest.fixture
def msg_all_set():
    msg = pb2.RepeatedTimestamp()

    ts1 = timestamp_pb2.Timestamp()
    ts1.seconds = 12324346
    ts1.nanos = 333222

    ts2 = timestamp_pb2.Timestamp()
    ts2.seconds = 3485739840
    ts2.nanos = 290348

    msg.value.extend([
        ts1,
        ts2,
    ])

    return mimic_protobuf_wire_transfer(msg)


@pytest.fixture
def msg_unsets():
    return mimic_protobuf_wire_transfer(pb2.RepeatedTimestamp())


##########################################
#  Model fixtures                        #
##########################################

@pytest.fixture
def model_class_optional():

    class ModelOptional(Model, protobuf_message=pb2.RepeatedTimestamp):
        value = types.RepeatedType(
            types.TimestampType(),
        )

    return ModelOptional


@pytest.fixture
def model_class_required():

    class ModelRequired(Model, protobuf_message=pb2.RepeatedTimestamp):
        value = types.RepeatedType(
            types.TimestampType(),
            required=True,
        )

    return ModelRequired


@pytest.fixture
def model_class_required_renamed():

    class ModelRequiredRenamed(Model, protobuf_message=pb2.RepeatedTimestamp):
        custom_value = types.RepeatedType(
            types.TimestampType(),
            required=True,
            metadata=dict(protobuf_field='value'),
        )

    return ModelRequiredRenamed


@pytest.fixture
def model_class_none_not_dumped():

    class ModelNoneNotDumped(Model, protobuf_message=pb2.RepeatedTimestamp):
        value = types.RepeatedType(
            types.TimestampType(),
        )

        class Options:
            serialize_when_none = False

    return ModelNoneNotDumped


@pytest.fixture
def model_class_field_renamed():

    class ModelFieldRenamed(Model, protobuf_message=pb2.RepeatedTimestamp):
        custom_value = types.RepeatedType(
            types.TimestampType(),
            metadata=dict(protobuf_field='value'),
        )

    return ModelFieldRenamed


@pytest.fixture
def model_class_validated_factory():
    def _factory(validator_func=None, inner_validator_func=None):
        outer_validators = [validator_func] if validator_func else []
        inner_validators = [inner_validator_func] if inner_validator_func else []

        class ModelValidated(Model, protobuf_message=pb2.RepeatedTimestamp):
            value = types.RepeatedType(
                types.TimestampType(validators=inner_validators),
                validators=outer_validators,
            )

        return ModelValidated

    return _factory


@pytest.fixture
def model_class_validated_renamed_factory():
    def _factory(validator_func=None, inner_validator_func=None):
        outer_validators = [validator_func] if validator_func else []
        inner_validators = [inner_validator_func] if inner_validator_func else []

        class ModelValidated(Model, protobuf_message=pb2.RepeatedTimestamp):
            custom_value = types.RepeatedType(
                types.TimestampType(validators=inner_validators),
                validators=outer_validators,
                metadata=dict(protobuf_field='value'),
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
    assert model.value == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]

    # check primitive dump
    data = model.to_primitive()

    assert 'value' in data
    assert data['value'] == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]

    # compare dump to native
    assert model.to_native() == data


def test_optional_unsets(model_class_optional, msg_unsets):
    model = model_class_optional.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.value is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'value' in data
    assert data['value'] is Unset

    # compare dump to native
    assert model.to_native() == data


def test_none_not_dumped_all_set(model_class_none_not_dumped, msg_all_set):
    model = model_class_none_not_dumped.load_protobuf(msg_all_set)
    model.validate()

    # check model instance fields
    assert model.value == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]

    # check primitive dump
    data = model.to_primitive()

    assert 'value' in data
    assert data['value'] == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]

    # compare dump to native
    assert model.to_native() == data


def test_none_not_dumped_unsets(model_class_none_not_dumped, msg_unsets):
    model = model_class_none_not_dumped.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.value is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'value' not in data

    # compare dump to native
    assert model.to_native() == data


def test_required_unsets(model_class_required, msg_unsets):
    with pytest.raises(DataError) as ex:
        model_class_required.load_protobuf(msg_unsets)

    errors = ex.value.to_primitive()
    assert 'value' in errors
    assert 'required' in errors['value'][0]


def test_required_renamed_unsets(model_class_required_renamed, msg_unsets):
    with pytest.raises(DataError) as ex:
        model_class_required_renamed.load_protobuf(msg_unsets)

    errors = ex.value.to_primitive()
    assert 'custom_value' in errors
    assert 'required' in errors['custom_value'][0]


def test_renamed_all_set(model_class_field_renamed, msg_all_set):
    model = model_class_field_renamed.load_protobuf(msg_all_set)
    model.validate()

    # check model instance fields
    assert model.custom_value == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]

    # check primitive dump
    data = model.to_primitive()

    assert 'custom_value' in data
    assert data['custom_value'] == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]

    # compare dump to native
    assert model.to_native() == data


def test_renamed_unsets(model_class_field_renamed, msg_unsets):
    model = model_class_field_renamed.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.custom_value is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'custom_value' in data
    assert data['custom_value'] is Unset

    # compare dump to native
    assert model.to_native() == data


def test_validated_all_set(model_class_validated_factory, msg_all_set):
    validator_func = Mock()
    model_cls = model_class_validated_factory(validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    model.validate()

    # check model instance fields
    assert model.value == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]
    validator_func.assert_called_once_with(model.value)

    # check primitive dump
    data = model.to_primitive()

    assert 'value' in data
    assert data['value'] == [
        DUMMY_DATETIME_1,
        DUMMY_DATETIME_2,
    ]

    # compare dump to native
    assert model.to_native() == data


def test_validated_unsets(model_class_validated_factory, msg_unsets):
    validator_func = Mock()
    model_cls = model_class_validated_factory(validator_func)

    model = model_cls.load_protobuf(msg_unsets)
    model.validate()

    # check model instance fields
    assert model.value is Unset
    validator_func.assert_not_called()

    # check primitive dump
    data = model.to_primitive()

    assert 'value' in data
    assert data['value'] is Unset

    # compare dump to native
    assert model.to_native() == data


def test_validated_validation_error(model_class_validated_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_factory(validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    assert 'value' in errors
    assert 'Please speak up!' in errors['value'][0], f"`Please speak up!` in `{errors['value'][0]}`"


def test_validated_validation_error__inner(model_class_validated_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_factory(None, validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    assert 'value' in errors
    assert len(errors['value']) == 2
    assert 'Please speak up!' in errors['value'][0]
    assert 'Please speak up!' in errors['value'][1]


def test_validated_validation_error_renamed(model_class_validated_renamed_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_renamed_factory(validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    assert 'custom_value' in errors
    assert 'Please speak up!' in errors['custom_value'][0], f"`Please speak up!` in `{errors['custom_value'][0]}`"


def test_validated_validation_error_renamed__inner(model_class_validated_renamed_factory, msg_all_set):
    validator_func = Mock(side_effect=ValidationError('Please speak up!'))
    model_cls = model_class_validated_renamed_factory(None, validator_func)

    model = model_cls.load_protobuf(msg_all_set)
    with pytest.raises(DataError) as ex:
        model.validate()

    errors = ex.value.to_primitive()

    assert 'custom_value' in errors
    assert len(errors['custom_value']) == 2
    assert 'Please speak up!' in errors['custom_value'][0]
    assert 'Please speak up!' in errors['custom_value'][1]
