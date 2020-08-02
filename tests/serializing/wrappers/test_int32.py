# -*- coding:utf-8 -*-
from schematics_proto3 import types
from tests import schematics_proto3_tests_pb2 as pb2
from tests.serializing.wrappers import CommonWrappersTests


class TestInt32(CommonWrappersTests):

    field_type_class = types.IntWrapperType
    protobuf_msg_class = pb2.WrappedInt32

    def get_value(self):
        return 42

    def get_zero_value(self):
        return 0
