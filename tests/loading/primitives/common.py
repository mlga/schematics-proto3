# -*- coding:utf-8 -*-
from unittest.mock import Mock

import pytest
from schematics.exceptions import DataError, ValidationError

from schematics_proto3.models import Model


def parametrize_for(tag):
    def _decorator(func):
        func._paramertize_for = tag

        return func
    return _decorator


class CommonPrimitivesTests:

    field_type_class = NotImplemented
    protobuf_msg_class = NotImplemented

    def pytest_generate_tests(self, metafunc):
        param_rule = getattr(metafunc.function, '_paramertize_for', None)

        if param_rule == 'all validation cases':
            metafunc.parametrize(
                'field_name,model_factory',
                [
                    ('value', self.get_model_class_validated),
                    ('custom_name', self.get_model_class_renamed_validated),
                ],
                ids=[
                    'optional',
                    'renamed',
                ]
            )
            metafunc.parametrize(
                'msg',
                [
                    self.get_msg_all_set(),
                    self.get_msg_unsets(),
                ],
                ids=[
                    'msg_all_set',
                    'msg_unsets',
                ]
            )
        if param_rule == 'positive loading cases':
            metafunc.parametrize(
                'field_name,model_cls',
                [
                    ('value', self.get_model_class_optional()),
                    ('value', self.get_model_class_none_not_dumped()),
                    ('value', self.get_model_class_required()),
                    ('custom_name', self.get_model_class_renamed()),
                ],
                ids=[
                    'optional',
                    'none_not_dumped',
                    'required',
                    'renamed',
                ]
            )
            metafunc.parametrize(
                'msg',
                [
                    self.get_msg_all_set(),
                    self.get_msg_unsets(),
                ],
                ids=[
                    'msg_all_set',
                    'msg_unsets',
                ]
            )

    def get_model_class_optional(self):
        class ModelOptional(Model):
            value = self.field_type_class()

            class Options:
                _protobuf_class = self.protobuf_msg_class

        return ModelOptional

    def get_model_class_required(self):
        class ModelRequired(Model):
            value = self.field_type_class(required=True)

            class Options:
                _protobuf_class = self.protobuf_msg_class

        return ModelRequired

    def get_model_class_none_not_dumped(self):
        class ModelNoneNotDumped(Model):
            value = self.field_type_class()

            class Options:
                _protobuf_class = self.protobuf_msg_class
                serialize_when_none = False

        return ModelNoneNotDumped

    def get_model_class_renamed(self):
        class ModelFieldRenamed(Model):
            custom_name = self.field_type_class(metadata=dict(protobuf_field='value'))

            class Options:
                _protobuf_class = self.protobuf_msg_class

        return ModelFieldRenamed

    def get_model_class_validated(self, validator_func):
        class ModelValidated(Model):
            value = self.field_type_class(validators=[validator_func])

            class Options:
                _protobuf_class = self.protobuf_msg_class

        return ModelValidated

    def get_model_class_renamed_validated(self, validator_func):
        class ModelValidated(Model):
            custom_name = self.field_type_class(
                metadata=dict(protobuf_field='value'),
                validators=[validator_func],
            )

            class Options:
                _protobuf_class = self.protobuf_msg_class

        return ModelValidated

    # protobuf message getters

    def get_msg_all_set(self):
        raise NotImplementedError()

    def get_msg_unsets(self):
        raise NotImplementedError()

    # test cases

    @parametrize_for('positive loading cases')
    def test_load_message__ok(self, field_name, model_cls, msg):
        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert getattr(model, field_name) == msg.value

        # check primitive dump
        data = model.to_primitive()

        assert field_name in data
        assert data[field_name] == msg.value

        # compare dump to native
        assert model.to_native() == data

    @parametrize_for('all validation cases')
    def test_validate__ok(self, field_name, model_factory, msg):
        validator_func = Mock()
        model_cls = model_factory(validator_func)

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert getattr(model, field_name) == msg.value
        validator_func.assert_called_once_with(msg.value)

        # check primitive dump
        data = model.to_primitive()

        assert field_name in data
        assert data[field_name] == msg.value

        # compare dump to native
        assert model.to_native() == data

    @parametrize_for('all validation cases')
    def test_validate__error(self, field_name, model_factory, msg):
        validator_func = Mock(side_effect=ValidationError('Please speak up!'))
        model_cls = model_factory(validator_func)

        model = model_cls.load_protobuf(msg)
        with pytest.raises(DataError) as ex:
            model.validate()

        errors = ex.value.to_primitive()
        assert field_name in errors
        assert 'Please speak up!' in errors[field_name][0], f"`Please speak up!` in `{errors[field_name][0]}`"
