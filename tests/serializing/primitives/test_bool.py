# -*- coding:utf-8 -*-
from schematics.types import BooleanType

from tests.serializing.primitives import CommonPrimitivesTests
from tests import schematics_proto3_tests_pb2 as pb2


class TestBool(CommonPrimitivesTests):

    field_type_class = BooleanType
    protobuf_msg_class = pb2.Bool

    def get_value(self):
        return True

    def get_zero_value(self):
        return 0
