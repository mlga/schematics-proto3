# -*- coding:utf-8 -*-
from schematics_proto3 import types
from tests import schematics_proto3_tests_pb2 as pb2
from tests.serializing.wrappers import CommonWrappersTests


class TestDouble(CommonWrappersTests):

    field_type_class = types.FloatWrapperType
    protobuf_msg_class = pb2.WrappedDouble

    def get_value(self):
        return 42.0

    def get_zero_value(self):
        return 0
