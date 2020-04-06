# -*- coding:utf-8 -*-
import threading
from typing import Type


class UnsetType:

    __slots__ = []

    _instance: 'UnsetType' = None
    _lock: threading.Lock = threading.Lock()

    def __str__(self):
        return 'Unset'

    def __repr__(self):
        return 'Unset'

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __len__(self):
        return 0

    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __new__(cls: Type['UnsetType']):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance


Unset = UnsetType()  # pylint: disable=invalid-name
