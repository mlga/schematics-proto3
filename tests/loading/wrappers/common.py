# -*- coding:utf-8 -*-
from unittest.mock import Mock

import pytest
from schematics.exceptions import DataError, ValidationError

from schematics_proto3.models import Model
from schematics_proto3.unset import Unset


def construct_model_class_optional(field_type_cls, protobuf_msg_cls):
    class ModelOptional(Model, protobuf_message=protobuf_msg_cls):
        wrapped = field_type_cls()

    return ModelOptional


def construct_model_class_required(field_type_cls, protobuf_msg_cls):
    class ModelRequired(Model, protobuf_message=protobuf_msg_cls):
        wrapped = field_type_cls(required=True)

    return ModelRequired


def construct_model_class_none_not_dumped(field_type_cls, protobuf_msg_cls):
    class ModelNoneNotDumped(Model, protobuf_message=protobuf_msg_cls):
        wrapped = field_type_cls()

        class Options:
            serialize_when_none = False

    return ModelNoneNotDumped


def construct_model_class_field_renamed(field_type_cls, protobuf_msg_cls):
    class ModelFieldRenamed(Model, protobuf_message=protobuf_msg_cls):
        custom_name = field_type_cls(metadata=dict(protobuf_field='wrapped'))

    return ModelFieldRenamed


def construct_model_class_field_renamed_required(field_type_cls, protobuf_msg_cls):
    class ModelFieldRenamedRequired(Model, protobuf_message=protobuf_msg_cls):
        custom_name = field_type_cls(
            metadata=dict(protobuf_field='wrapped'),
            required=True,
        )

    return ModelFieldRenamedRequired


def construct_model_class_validated(
        field_type_cls,
        protobuf_msg_cls,
        validator_func,
):
    class ModelValidated(Model, protobuf_message=protobuf_msg_cls):
        wrapped = field_type_cls(validators=[validator_func])

    return ModelValidated


def construct_model_class_field_renamed_validated(
        field_type_cls,
        protobuf_msg_cls,
        validator_func,
):
    class ModelValidated(Model, protobuf_message=protobuf_msg_cls):
        custom_name = field_type_cls(
            metadata=dict(protobuf_field='wrapped'),
            validators=[validator_func],
        )

    return ModelValidated


class CommonWrappersTests:

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

    def get_model_class_optional(self):
        if (self.field_type_class is NotImplemented
                or self.protobuf_msg_class is NotImplemented
        ):
            raise NotImplementedError()

        return construct_model_class_optional(
            self.field_type_class,
            self.protobuf_msg_class,
        )

    def get_model_class_required(self):
        if (self.field_type_class is NotImplemented
                or self.protobuf_msg_class is NotImplemented
        ):
            raise NotImplementedError()

        return construct_model_class_required(
            self.field_type_class,
            self.protobuf_msg_class,
        )

    def get_model_class_none_not_dumped(self):
        if (self.field_type_class is NotImplemented
                or self.protobuf_msg_class is NotImplemented
        ):
            raise NotImplementedError()

        return construct_model_class_none_not_dumped(
            self.field_type_class,
            self.protobuf_msg_class,
        )

    def get_model_class_renamed(self):
        if (self.field_type_class is NotImplemented
                or self.protobuf_msg_class is NotImplemented
        ):
            raise NotImplementedError()

        return construct_model_class_field_renamed(
            self.field_type_class,
            self.protobuf_msg_class,
        )

    def get_model_class_renamed_required(self):
        if (self.field_type_class is NotImplemented
                or self.protobuf_msg_class is NotImplemented
        ):
            raise NotImplementedError()

        return construct_model_class_field_renamed_required(
            self.field_type_class,
            self.protobuf_msg_class,
        )

    def get_model_class_validated(self, validator_func):
        if (self.field_type_class is NotImplemented
                or self.protobuf_msg_class is NotImplemented
        ):
            raise NotImplementedError()

        return construct_model_class_validated(
            self.field_type_class,
            self.protobuf_msg_class,
            validator_func,
        )

    def get_model_class_renamed_validated(self, validator_func):
        if (self.field_type_class is NotImplemented
                or self.protobuf_msg_class is NotImplemented
        ):
            raise NotImplementedError()

        return construct_model_class_field_renamed_validated(
            self.field_type_class,
            self.protobuf_msg_class,
            validator_func,
        )

    # protobuf message getters

    def get_msg_all_set(self):
        raise NotImplementedError()

    def get_msg_unsets(self):
        raise NotImplementedError()

    # test cases

    def test_optional_all_set(self):
        model_cls = self.get_model_class_optional()
        msg = self.get_msg_all_set()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.wrapped == msg.wrapped.value

        # check primitive dump
        data = model.to_primitive()

        assert 'wrapped' in data
        assert data['wrapped'] == msg.wrapped.value

        # compare dump to native
        assert model.to_native() == data

    def test_optional_unsets(self):
        model_cls = self.get_model_class_optional()
        msg = self.get_msg_unsets()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.wrapped is Unset

        # check primitive dump
        data = model.to_primitive()

        assert 'wrapped' in data
        assert data['wrapped'] is Unset

        # compare dump to native
        assert model.to_native() == data

    def test_none_not_dumped_all_set(self):
        model_cls = self.get_model_class_none_not_dumped()
        msg = self.get_msg_all_set()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.wrapped == msg.wrapped.value

        # check primitive dump
        data = model.to_primitive()

        assert 'wrapped' in data
        assert data['wrapped'] == msg.wrapped.value

        # compare dump to native
        assert model.to_native() == data

    def test_none_not_dumped_unsets(self):
        model_cls = self.get_model_class_none_not_dumped()
        msg = self.get_msg_unsets()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.wrapped is Unset

        # check primitive dump
        data = model.to_primitive()

        assert 'wrapped' not in data

        # compare dump to native
        assert model.to_native() == data

    def test_required_unsets(self):
        model_cls = self.get_model_class_required()
        msg = self.get_msg_unsets()

        with pytest.raises(DataError) as ex:
            model_cls.load_protobuf(msg)

        errors = ex.value.to_primitive()
        assert 'wrapped' in errors
        assert 'required' in errors['wrapped'][0], f"`wrapped` in `{errors['wrapped'][0]}`"

    def test_required_renamed_unsets(self):
        model_cls = self.get_model_class_renamed_required()
        msg = self.get_msg_unsets()

        with pytest.raises(DataError) as ex:
            model_cls.load_protobuf(msg)

        errors = ex.value.to_primitive()
        assert 'custom_name' in errors
        assert 'required' in errors['custom_name'][0], f"`custom_name` in `{errors['custom_name'][0]}`"

    def test_renamed_all_set(self):
        model_cls = self.get_model_class_renamed()
        msg = self.get_msg_all_set()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.custom_name == msg.wrapped.value

        # check primitive dump
        data = model.to_primitive()

        assert 'custom_name' in data
        assert data['custom_name'] == msg.wrapped.value

        # compare dump to native
        assert model.to_native() == data

    def test_renamed_unsets(self):
        model_cls = self.get_model_class_renamed()
        msg = self.get_msg_unsets()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.custom_name is Unset

        # check primitive dump
        data = model.to_primitive()

        assert 'custom_name' in data
        assert data['custom_name'] is Unset

        # compare dump to native
        assert model.to_native() == data

    def test_validated_all_set(self):
        validator_func = Mock()
        model_cls = self.get_model_class_validated(validator_func)
        msg = self.get_msg_all_set()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.wrapped == msg.wrapped.value
        validator_func.assert_called_once_with(msg.wrapped.value)

        # check primitive dump
        data = model.to_primitive()

        assert 'wrapped' in data
        assert data['wrapped'] == msg.wrapped.value

        # compare dump to native
        assert model.to_native() == data

    def test_validated_unsets(self):
        validator_func = Mock()
        model_cls = self.get_model_class_validated(validator_func)
        msg = self.get_msg_unsets()

        model = model_cls.load_protobuf(msg)
        model.validate()

        # check model instance fields
        assert model.wrapped is Unset
        validator_func.assert_not_called()

        # check primitive dump
        data = model.to_primitive()

        assert 'wrapped' in data
        assert data['wrapped'] is Unset

        # compare dump to native
        assert model.to_native() == data

    def test_validated_validation_error(self):
        validator_func = Mock(side_effect=ValidationError('Please speak up!'))
        model_cls = self.get_model_class_validated(validator_func)
        msg = self.get_msg_all_set()

        model = model_cls.load_protobuf(msg)
        with pytest.raises(DataError) as ex:
            model.validate()

        errors = ex.value.to_primitive()
        assert 'wrapped' in errors
        assert 'Please speak up!' in errors['wrapped'][0], f"`Please speak up!` in `{errors['wrapped'][0]}`"

    def test_validated_validation_error_renamed(self):
        validator_func = Mock(side_effect=ValidationError('Please speak up!'))
        model_cls = self.get_model_class_renamed_validated(validator_func)
        msg = self.get_msg_all_set()

        model = model_cls.load_protobuf(msg)
        with pytest.raises(DataError) as ex:
            model.validate()

        errors = ex.value.to_primitive()
        assert 'custom_name' in errors
        assert 'Please speak up!' in errors['custom_name'][0], f"`Please speak up!` in `{errors['custom_name'][0]}`"
