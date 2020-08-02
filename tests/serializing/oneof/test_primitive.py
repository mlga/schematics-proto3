# -*- coding:utf-8 -*-
import pytest
from schematics.types import IntType, StringType

from schematics_proto3 import types
from schematics_proto3.models import Model
from schematics_proto3.unset import Unset
from tests import schematics_proto3_tests_pb2 as pb2


##########################################
#  Data fixtures                         #
##########################################

@pytest.fixture
def data_all_set():
    return {
        'variant': 'value2',
        'value': 'Hello!',
    }


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


##########################################
#  Tests                                 #
##########################################

def test_optional_all_set(model_class_optional, data_all_set):
    model = model_class_optional()
    model.inner = data_all_set
    model.validate()

    # check model instance fields
    assert model.inner.variant == 'value2'
    assert model.inner.value == 'Hello!'

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert 'variant' in data['inner']
    assert 'value' in data['inner']
    assert data['inner']['variant'] == 'value2'
    assert data['inner']['value'] == 'Hello!'

    # compare dump to native
    assert model.to_native() == data

    msg = model.to_protobuf()
    assert msg.value2 == 'Hello!'


def test_optional_unsets(model_class_optional):
    model = model_class_optional()
    model.validate()

    # check model instance fields
    assert model.inner is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert data['inner'] is Unset

    # compare dump to native
    assert model.to_native() == data

    msg = model.to_protobuf()
    assert msg.value1 == 0
    assert msg.value2 == ''


def test_none_not_dumped_all_set(model_class_none_not_dumped, data_all_set):
    model = model_class_none_not_dumped()
    model.inner = data_all_set
    model.validate()

    # check model instance fields
    assert model.inner.variant == 'value2'
    assert model.inner.value == 'Hello!'

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' in data
    assert 'variant' in data['inner']
    assert 'value' in data['inner']
    assert data['inner']['variant'] == 'value2'
    assert data['inner']['value'] == 'Hello!'

    # compare dump to native
    assert model.to_native() == data

    msg = model.to_protobuf()
    assert msg.value2 == 'Hello!'


def test_none_not_dumped_unsets(model_class_none_not_dumped):
    model = model_class_none_not_dumped()
    model.validate()

    # check model instance fields
    assert model.inner is Unset

    # check primitive dump
    data = model.to_primitive()

    assert 'inner' not in data

    # compare dump to native
    assert model.to_native() == data

    msg = model.to_protobuf()
    assert msg.value1 == 0
    assert msg.value2 == ''
