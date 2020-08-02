# -*- coding:utf-8 -*-
from schematics.types import IntType

from tests.serializing.primitives import CommonPrimitivesTests
from tests import schematics_proto3_tests_pb2 as pb2


class TestInt64(CommonPrimitivesTests):

    field_type_class = IntType
    protobuf_msg_class = pb2.Int64

    def get_value(self):
        return 42

    def get_zero_value(self):
        return 0
