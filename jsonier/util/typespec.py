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
    """
    A class that represents a parametrized type.
    head represents the template type. specified as a string
    tail is the parameter. None stands for a type with no parameters T<>
         while Ellipsis is a wildcard that matches any type
    """
    Int = 'int'
    Float = 'float'
    Bool = 'bool'
    Str = 'str'
    ListOf = 'list'
    MapOf = 'map'
    Timestamp = 'timestamp'

    def __init__(self, head: str, arg=None):
        self._tuple = (head, arg)

    def head(self):
        return self._tuple[0]

    def tail(self):
        return self._tuple[1]

    def as_tuple(self):
        return self._tuple

    def __getitem__(self, arg):
        return TypeSpec(self._tuple[0], arg)

    def __hash__(self):
        return hash(self._tuple)

    def __eq__(self, other: 'TypeSpec') -> bool:
        if other is self:
            return True
        if not isinstance(other, TypeSpec):
            return False
        return self._tuple == other._tuple

    def matches(self, other: 'TypeSpec') -> bool:
        if other is self:
            return True
        if not isinstance(other, TypeSpec):
            return False
        if self._tuple == other._tuple:
            return True
        if self._tuple == (other.head(), Ellipsis):
            return True
        return False

    def __str__(self) -> str:
        h, t = self._tuple
        return f'{h}<{t}>'

    def __repr__(self) -> str:
        h, t = self._tuple
        return f'TypeSpec({repr(h), repr(t)}'


class TypeSpecMap:
    def __init__(self):
        self._map = {}
        self._map_param = {}

    def set(self, key: Union[type, 'TypeSpec'], value: Any):
        if isinstance(key, type):
            self._map[key] = value
        elif isinstance(key, TypeSpec):
            if key.tail() == Ellipsis:
                self._map_param[key.head()] = value
            else:
                self._map[key] = value
        else:
            raise TypeError(f'Key must be a type or TypeSpec, got {type_name(key)}')

    def get(self, key: Union[type, 'TypeSpec']) -> Any:
        """
        Looks up a value in the map, given a type or typespec
        :param key: typespec or type to look up
        :raises KeyError: if the key doesn't match any parameters
        :return:
        """
        try:
            return self._map[key]
        except KeyError:
            if not isinstance(key, TypeSpec):
                raise
            return self._map_param[key.head()]

