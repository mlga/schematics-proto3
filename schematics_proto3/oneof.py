# -*- coding:utf-8 -*-

class OneOfVariant:

    slots = ('variant', 'value')

    def __init__(self, variant, value):
        self.variant = variant
        self.value = value

    def __str__(self):
        return f'OneOfVariant<{self.variant}, {self.value}>'

    def __eq__(self, other):
        if not isinstance(other, OneOfVariant):
            return False

        return self.variant == other.variant and self.value == other.value

    def __repr__(self):
        return f'OneOfVariant<{self.variant}, {self.value}>'

    def __hash__(self):
        return hash((self.variant, self.value))
