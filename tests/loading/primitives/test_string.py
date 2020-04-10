# -*- coding:utf-8 -*-
from schematics_proto3 import types
from tests.loading.primitives import CommonPrimitivesTests
from tests import schematics_proto3_tests_pb2 as pb2
from tests.utils.randoms import value_for_primitive
from tests.utils.wire import mimic_protobuf_wire_transfer


class TestString(CommonPrimitivesTests):

    field_type_class = types.StringType
    protobuf_msg_class = pb2.String

    def get_msg_all_set(self):
        msg = self.protobuf_msg_class()
        msg.value = value_for_primitive('string_field')

        return mimic_protobuf_wire_transfer(msg)

    def get_msg_unsets(self):
        return mimic_protobuf_wire_transfer(self.protobuf_msg_class())
