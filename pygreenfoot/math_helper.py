from typing import TypeVar

__Number = TypeVar("__Number", int, float)


FULL_DEGREES_ANGLE = 360.0


def limit_value(value: __Number, min_: __Number, max_: __Number) -> __Number:
    if value < min_:
        return min_
    elif value > max_:
        return max_
    return value