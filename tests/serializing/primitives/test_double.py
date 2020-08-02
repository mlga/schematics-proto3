# -*- coding:utf-8 -*-
from schematics.types import FloatType

from tests.serializing.primitives import CommonPrimitivesTests
from tests import schematics_proto3_tests_pb2 as pb2


class TestDouble(CommonPrimitivesTests):

    field_type_class = FloatType
    protobuf_msg_class = pb2.Double

    def get_value(self):
        return 42.33

    def get_zero_value(self):
        return 0
