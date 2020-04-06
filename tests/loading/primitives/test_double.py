# -*- coding:utf-8 -*-
from schematics_proto3 import types
from tests.loading.primitives.common import CommonWrappersTests
from tests import schematics_proto3_tests_pb2 as pb2
from tests.utils.randoms import value_for_primitive
from tests.utils.wire import mimic_protobuf_wire_transfer


class TestDouble(CommonWrappersTests):

    field_type_class = types.FloatType
    protobuf_msg_class = pb2.Double

    def get_msg_all_set(self):
        msg = self.protobuf_msg_class()
        msg.value = value_for_primitive('double_field')

        return mimic_protobuf_wire_transfer(msg)

    def get_msg_unsets(self):
        return mimic_protobuf_wire_transfer(self.protobuf_msg_class())
