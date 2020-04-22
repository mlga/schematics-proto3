# -*- coding:utf-8 -*-
from schematics.types import IntType
from tests.loading.primitives import CommonPrimitivesTests
from tests import schematics_proto3_tests_pb2 as pb2
from tests.utils.randoms import value_for_primitive
from tests.utils.wire import mimic_protobuf_wire_transfer


class TestUInt32(CommonPrimitivesTests):

    field_type_class = IntType
    protobuf_msg_class = pb2.UInt32

    def get_msg_all_set(self):
        msg = self.protobuf_msg_class()
        msg.value = value_for_primitive('uint32_field')

        return mimic_protobuf_wire_transfer(msg)

    def get_msg_unsets(self):
        return mimic_protobuf_wire_transfer(self.protobuf_msg_class())
