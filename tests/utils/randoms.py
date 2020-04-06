# -*- coding:utf-8 -*-
import os
import random
import string

VALUE_PRODUCERS = {
    # TODO: move to partials
    'double_field': lambda: random.uniform(1, 100),
    'float_field': lambda: random.uniform(1, 100),
    'int64_field': lambda: int(random.uniform(2_147_483_648, 9_223_372_036_854_775_806)),
    'uint64_field': lambda: int(random.uniform(9_223_372_036_854_775_808, 18_446_744_073_709_551_614)),
    'int32_field': lambda: int(random.uniform(1, 2_147_483_646)),
    'uint32_field': lambda: int(random.uniform(2_147_483_650, 4_294_967_294)),
    'bool_field': lambda: random.choice([True, False]),
    'string_field': lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(5, 384))),
    'bytes_field': lambda: os.urandom(random.randint(5, 384)),
}


def value_for_primitive(field_name):
    return VALUE_PRODUCERS[field_name]()
