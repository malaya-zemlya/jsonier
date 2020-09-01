import json
import logging
from datetime import datetime
from types import MethodType
from typing import (
    Any,
    Optional,
    Union
)

from jsonier.util.datetimeutil import (
    datetime_to_int,
    datetime_to_float,
    datetime_to_str,
    int_to_datetime,
    float_to_datetime,
    str_to_datetime,
    auto_to_datetime,
)
from jsonier.util.typeutil import (
    JsonType,
    TypeSpec,
    type_check,
    type_name,
)

_FIELDS = '__FLD'
_MISSING = (None,)  # a special value indicating that a value is not specified (but is not None)


def require_jsonclass(cls):
    if not hasattr(cls, _FIELDS):
        raise TypeError(f'{cls.__name__} is not a jsonclass object.')


def is_jsonclass(cls):
    return hasattr(cls, _FIELDS)


class Value:
    def __init__(self, strict: bool = False, default: Any = None):
        """
        :param strict: True to perform type-check during data conversion
        :param default: Value to return for a missing optional field
        """
        self.strict = strict
        self.default = default

    def from_json(self, json_data):
        raise NotImplementedError('from_json')

    def to_json(self, json_data) -> JsonType:
        raise NotImplementedError('to_json')

    def zero(self):
        return self.default

    def is_empty(self, obj):
        return not obj


class IntValue(Value):
    def __init__(self, strict: bool = False, default: Optional[int] = None):
        if default is None:
            default = 0
        super().__init__(strict=strict, default=default)

    def from_json(self, json_data) -> int:
        if self.strict:
            type_check(json_data, int)
        return int(json_data)

    def to_json(self, json_data) -> int:
        if self.strict:
            type_check(json_data, int)
        return int(json_data)


class FloatValue(Value):
    def __init__(self, strict: bool = False, default: Optional[float] = None):
        if default is None:
            default = 0.0
        super().__init__(strict=strict, default=default)

    def from_json(self, json_data) -> float:
        if self.strict:
            type_check(json_data, float)
        return float(json_data)

    def to_json(self, json_data) -> float:
        if self.strict:
            type_check(json_data, float)
        return float(json_data)


class StringValue(Value):
    def __init__(self, strict: bool = False, default: Optional[str] = None):
        if default is None:
            default = ''
        super().__init__(strict=strict, default=default)

    def from_json(self, json_data) -> str:
        if self.strict:
            type_check(json_data, str)
        return str(json_data)

    def to_json(self, json_data) -> str:
        if self.strict:
            type_check(json_data, str)
        return str(json_data)


class BoolValue(Value):
    def __init__(self, strict: bool = False, default: Optional[bool] = None):
        if default is None:
            default = False
        super().__init__(strict=strict, default=default)

    def from_json(self, json_data) -> bool:
        if self.strict:
            type_check(json_data, bool)
        return bool(json_data)

    def to_json(self, json_data) -> bool:
        if self.strict:
            type_check(json_data, bool)
        return bool(json_data)


EPOCH = datetime.utcfromtimestamp(0)


class TimestampStrValue(Value):
    def __init__(self,
                 default: Any = None):
        if default is not None:
            default = auto_to_datetime(default)
        super().__init__(strict=True, default=default)

    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return str_to_datetime(json_data)

    def to_json(self, json_data) -> Optional[str]:
        if json_data is None:
            return None
        return datetime_to_str(json_data)


class TimestampFloatValue(Value):
    def __init__(self,
                 default: Optional[datetime] = None):
        if default is not None:
            default = auto_to_datetime(default)
        super().__init__(strict=True, default=default)

    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return float_to_datetime(json_data)

    def to_json(self, obj_data) -> Optional[float]:
        if obj_data is None:
            return None
        return datetime_to_float(obj_data)


class TimestampIntValue(Value):
    def __init__(self,
                 default: Optional[datetime] = None):
        if default is not None:
            default = auto_to_datetime(default)
        super().__init__(strict=True, default=default)

    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return int_to_datetime(json_data)

    def to_json(self, obj_data) -> Optional[int]:
        if obj_data is None:
            return None
        return datetime_to_int(obj_data)


class TimestampAutoValue(Value):
    def __init__(self,
                 default: Optional[datetime] = None):
        if default is not None:
            default = auto_to_datetime(default)
        super().__init__(strict=True, default=default)

    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return auto_to_datetime(json_data)

    def to_json(self, obj_data) -> Optional[str]:
        if obj_data is None:
            return None
        return datetime_to_str(obj_data)


class ListOfValue(Value):
    def __init__(self, sub_value: Value):
        self._sub_value = sub_value
        super().__init__(strict=True)

    def from_json(self, json_data: list):
        if not isinstance(json_data, list):
            raise TypeError(f'Expecting a list, got {type(json_data)} instead')
        return [self._sub_value.from_json(item) for item in json_data]

    def to_json(self, obj: list):
        if not isinstance(obj, list):
            raise TypeError(f'Expecting a list, got {type_name(obj)} instead')
        return [self._sub_value.to_json(item) for item in obj]

    def zero(self):
        return []


class MapOfValue(Value):
    def __init__(self, sub_value: Value):
        self._sub_value = sub_value
        super().__init__(strict=True)

    def from_json(self, json_data: dict):
        if not isinstance(json_data, dict):
            raise TypeError(f'Expecting a dict, got {type(json_data)} instead')
        return {k: self._sub_value.from_json(v) for k, v in json_data.items()}

    def to_json(self, obj: dict):
        if not isinstance(obj, dict):
            raise TypeError(f'Expecting a dict, got {type_name(obj)} instead')
        return {k: self._sub_value.to_json(v) for k, v in obj.items()}

    def zero(self):
        return {}


class ObjValue(Value):
    def __init__(self, sub_value: type):
        require_jsonclass(sub_value)
        self._sub_value = sub_value
        super().__init__(strict=True, default=None)

    def from_json(self, json_data: Optional[dict]):
        if json_data is None:
            return None
        if not isinstance(json_data, dict):
            raise TypeError(f'Expecting a dict, got {type_name(json_data)} instead')
        return from_json(self._sub_value, json_data)

    def to_json(self, obj: Optional[dict]):
        if obj is None:
            return None
        if not isinstance(obj, self._sub_value):
            raise TypeError(f'Expecting a {self._sub_value.__name__}, got {type_name(obj)} instead')
        return to_json(obj)

    def zero(self):
        return None


def parse_type_spec(ts: Union[TypeSpec, type], default=None) -> Value:
    if ts == int:
        return IntValue(default=default)
    elif ts == str:
        return StringValue(default=default)
    elif ts == bool:
        return BoolValue(default=default)
    elif ts == float:
        return FloatValue(default=default)
    elif ts == datetime:
        return TimestampAutoValue(default=default)
    elif is_jsonclass(ts):
        return ObjValue(ts)
    elif not isinstance(ts, TypeSpec):
        raise TypeError(f'Invalid type spec: {ts}')
    head, args = ts.head(), ts.tail()
    if head == 'ListOf':
        if len(args) != 1:
            raise TypeError('ListOf requires exactly one type argument')
        sub_value = parse_type_spec(args[0])
        return ListOfValue(sub_value)
    elif head == 'MapOf':
        if len(args) != 1:
            raise TypeError('MapOf requires exactly one type argument')
        sub_value = parse_type_spec(args[0])
        return MapOfValue(sub_value)
    elif head == 'Timestamp':
        if len(args) == 0:
            return TimestampAutoValue(default=default)
        if len(args) != 1:
            raise TypeError('Timestamp requires exactly one type argument')
        arg = args[0]
        if arg == int:
            return TimestampIntValue(default=default)
        elif arg == str:
            return TimestampStrValue(default=default)
        elif arg == float:
            return TimestampFloatValue(default=default)
        else:
            raise TypeError('The argument to timestamp has to be str, int, or float.')
    else:
        raise TypeError('Invalid Typespec')


def _process_class(cls, frozen):
    fields = {}
    for attr_name, attr_value in cls.__dict__.items():
        if not isinstance(attr_value, Field):
            if not attr_name.startswith('_') and not callable(attr_value):
                # warning
                logging.warning(f'JSON class {cls.__name__} has an attribute `{attr_name}` that is not a field')
            continue
        fields[attr_name] = attr_value
    setattr(cls, _FIELDS, fields)
    setattr(cls, 'from_json', MethodType(from_json, cls))
    setattr(cls, 'from_json_str', MethodType(from_json_str, cls))
    setattr(cls, 'to_json', to_json)
    setattr(cls, 'to_json_str', to_json_str)
    setattr(cls, '__str__', to_json_str)

    return cls


def jsonclass(cls=None, /, *, frozen=False):
    def wrap(cls):
        return _process_class(cls, frozen)

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap

    # We're called as @dataclass without parens.
    return wrap(cls)


def from_json(cls, json_data: dict):
    require_jsonclass(cls)
    fields: dict = getattr(cls, _FIELDS)
    inst = cls()
    for attr_name, field in fields.items():
        v = field.get_value(json_data=json_data, attr_name=attr_name)
        setattr(inst, attr_name, v)
    return inst


def from_json_str(cls, json_str: str):
    return from_json(cls, json_data=json.loads(json_str))


def to_json(obj):
    cls = obj.__class__
    require_jsonclass(cls)
    converters: dict = getattr(cls, _FIELDS)
    json_data = {}
    for attr_name, field in converters.items():
        field.set_value(json_data=json_data, attr_name=attr_name, attr_value=getattr(obj, attr_name))
    return json_data


def to_json_str(obj, **kwargs):
    data = to_json(obj)
    return json.dumps(data, **kwargs)


class Field:
    def __init__(self,
                 type_spec: Union[TypeSpec, type],
                 required: bool = False,
                 omit_empty: bool = True,
                 default: Any = None,
                 name: str = ''):
        self.type_spec = type_spec
        self.value = parse_type_spec(type_spec, default=default)
        self.required = required
        self.omit_empty = omit_empty
        self.default = default
        self.name = name

    def get_value(self, json_data: dict, attr_name: str):
        json_name = self.name or attr_name
        try:
            json_value = json_data[json_name]
        except KeyError:
            if self.required:
                raise ValueError(f'Required field {json_name} is missing.')
            return self.value.zero()
        return self.value.from_json(json_value)

    def set_value(self, json_data: dict, attr_name: str, attr_value: Any):
        if self.value.is_empty(attr_value) and self.omit_empty:
            return
        json_name = self.name or attr_name
        json_data[json_name] = self.value.to_json(attr_value)
