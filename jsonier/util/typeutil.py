from typing import (
    Any,
    Callable,
    Tuple,
    Union
)

TypeList = Union[type, Tuple[type, ...]]
NoneType = type(None)
AtomicType = Union[int, str, float, bool, NoneType]  # types that can be returned by value
JsonType = Union[AtomicType, dict, list]  # types that can appear in a JSON object


def wrap_value(x: Any) -> Callable:
    """
    Puts a value inside a function
    :param x:
    :return:
    """
    def wrapped() -> Any:
        return x
    return wrapped


def is_atomic(x: Any) -> bool:
    """
    :param x:
    :return: True if an atomic value can appear inside JSON and be passed by value
    """
    return isinstance(x, (int, str, float, bool, NoneType))


def type_name(x) -> str:
    return type(x).__name__


def type_check(x, types):
    if not isinstance(x, types):
        raise TypeError(f'Expected {types} value, got: `{type_name(x)}`')


class TypeSpec:
    Int = 'int'
    Float = 'float'
    Bool = 'bool'
    Str = 'str'
    ListOf = 'list'
    MapOf = 'map'
    Timestamp = 'timestamp'

    def __init__(self, head: str, *args):
        self._head = head
        self._args = tuple(args)

    def head(self):
        return self._head

    def tail(self):
        return self._args

    def __getitem__(self, item):
        return TypeSpec(self._head, item)


ListOf = TypeSpec(TypeSpec.ListOf)
MapOf = TypeSpec(TypeSpec.MapOf)
Timestamp = TypeSpec(TypeSpec.Timestamp)
