from typing import TypeVar

__Number = TypeVar("__Number", int, float)


FULL_DEGREES_ANGLE = 360.0


def limit_value(value: __Number, min_: __Number, max_: __Number) -> __Number:
    """Limit a value to a minimum and maximum

    Args:
        value (__Number): the value
        min_ (__Number): the allowed minimum
        max_ (__Number): the allowed maximum

    Returns:
        __Number: the resulting value if the boundaries have been checked.
    """
    if value < min_:
        return min_
    elif value > max_:
        return max_
    return value

