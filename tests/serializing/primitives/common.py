# -*- coding:utf-8 -*-
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

        model_class_optional = self.get_model_class_optional()
        model_class_none_not_dumped = self.get_model_class_none_not_dumped()
        model_class_renamed = self.get_model_class_renamed()

        value = self.get_value()

        if param_rule == 'serializing + field set cases':
            metafunc.parametrize(
                'field_name,model',
                [
                    ('value', model_class_optional({'value': value})),
                    ('value', model_class_none_not_dumped({'value': value})),
                    ('custom_name', model_class_renamed({'custom_name': value})),
                ],
                ids=[
                    'optional+all_set',
                    'none_not_dumped+all_set',
                    'renamed+all_set',
                ]
            )
        if param_rule == 'not serializing + field unset cases':
            metafunc.parametrize(
                'field_name,model',
                [
                    ('value', model_class_none_not_dumped({})),
                ],
                ids=[
                    'none_not_dumped+unset',
                ]
            )
        if param_rule == 'serializing + field unset cases':
            metafunc.parametrize(
                'field_name,model',
                [
                    ('value', model_class_optional({})),
                    ('custom_name', model_class_renamed({})),
                ],
                ids=[
                    'optional+unset',
                    'renamed+unset',
                ]
            )

    def get_model_class_optional(self):
        class ModelOptional(Model, protobuf_message=self.protobuf_msg_class):
            value = self.field_type_class()

        return ModelOptional

    def get_model_class_none_not_dumped(self):
        class ModelNoneNotDumped(Model, protobuf_message=self.protobuf_msg_class):
            value = self.field_type_class()

            class Options:
                serialize_when_none = False

        return ModelNoneNotDumped

    def get_model_class_renamed(self):
        class ModelFieldRenamed(Model, protobuf_message=self.protobuf_msg_class):
            custom_name = self.field_type_class(metadata=dict(protobuf_field='value'))

        return ModelFieldRenamed

    # value getters

    def get_value(self):
        raise NotImplementedError()

    def get_zero_value(self):
        raise NotImplementedError()

    # test cases

    @parametrize_for('serializing + field set cases')
    def test_serialize_message__all_set(self, field_name, model):
        nat = model.to_native()
        pri = model.to_primitive()
        msg = model.to_protobuf()

        assert nat[field_name] == self.get_value()
        assert pri[field_name] == self.get_value()
        assert msg.value == self.get_value()

    @parametrize_for('not serializing + field unset cases')
    def test_skip_serialize_message__unsets(self, field_name, model):
        nat = model.to_native()
        pri = model.to_primitive()
        msg = model.to_protobuf()

        assert nat == {}
        assert pri == {}
        assert msg.value == self.get_zero_value()

    @parametrize_for('serializing + field unset cases')
    def test_serialize_message__unsets(self, field_name, model):
        nat = model.to_native()
        pri = model.to_primitive()
        msg = model.to_protobuf()

        assert nat[field_name] is None
        assert pri[field_name] is None
        assert msg.value == self.get_zero_value()
