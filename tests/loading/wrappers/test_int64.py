# -*- coding:utf-8 -*-
from schematics_proto3 import types
from tests.loading.wrappers import CommonWrappersTests
from tests import schematics_proto3_tests_pb2 as pb2
from tests.utils.randoms import value_for_primitive
from tests.utils.wire import mimic_protobuf_wire_transfer


class TestInt64(CommonWrappersTests):

    field_type_class = types.IntWrapperType
    protobuf_msg_class = pb2.WrappedInt64

    def get_msg_all_set(self):
        msg = self.protobuf_msg_class()
        msg.wrapped.value = value_for_primitive('int64_field')

        return mimic_protobuf_wire_transfer(msg)

    def get_msg_unsets(self):
        return mimic_protobuf_wire_transfer(self.protobuf_msg_class())
