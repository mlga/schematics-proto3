# -*- coding:utf-8 -*-
from schematics.types import StringType

from tests.serializing.primitives import CommonPrimitivesTests
from tests import schematics_proto3_tests_pb2 as pb2


class TestString(CommonPrimitivesTests):

    field_type_class = StringType
    protobuf_msg_class = pb2.String

    def get_value(self):
        return "hello!"

    def get_zero_value(self):
        return ""
