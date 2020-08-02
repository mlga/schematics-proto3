# -*- coding:utf-8 -*-
from schematics_proto3 import types
from tests import schematics_proto3_tests_pb2 as pb2
from tests.serializing.wrappers import CommonWrappersTests


class TestBool(CommonWrappersTests):

    field_type_class = types.BoolWrapperType
    protobuf_msg_class = pb2.WrappedBool

    def get_value(self):
        return True

    def get_zero_value(self):
        return 0
