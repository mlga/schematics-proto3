# -*- coding:utf-8 -*-


def mimic_protobuf_wire_transfer(msg):
    # This mimics wire transfer (serialization and deserialization) of protobuf
    # message.
    new_msg = type(msg)()
    new_msg.ParseFromString(msg.SerializeToString())

    return new_msg
