import json
import logging
from datetime import datetime
from types import MethodType
from typing import (
    Any,
    Callable,
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
    auto_to_datetime
)
from jsonier.util.typeutil import (
    JsonType,
    TypeSpec,
    type_name,
)

_FIELDS = '__JSON'
_MISSING = (None,)  # a special value indicating that a value is not specified (but is not None)


def require_jsonified(cls):
    if not hasattr(cls, _FIELDS):
        raise TypeError(f'{cls.__name__} is not a jsonclass object.')


def is_jsonified(cls):
    return hasattr(cls, _FIELDS)


class Adapter:
    def __init__(self, *args, **kwargs):
        self.default = None

    def set_options(self, options: Optional[dict] = None):
        pass

    def set_default(self, default):
        self.default = default

    def from_json(self, json_data):
        raise NotImplementedError('from_json')

    def to_json(self, json_data) -> JsonType:
        raise NotImplementedError('to_json')

    def zero(self):
        return self.default

    def is_empty(self, obj):
        return not obj


class IntAdapter(Adapter):
    def from_json(self, json_data) -> int:
        return int(json_data)

    def to_json(self, json_data) -> int:
        return int(json_data)

    def set_default(self, default):
        if default is None:
            self.default = 0
        else:
            self.default = int(default)


class FloatAdapter(Adapter):
    def from_json(self, json_data) -> float:
        return float(json_data)

    def to_json(self, json_data) -> float:
        return float(json_data)

    def set_default(self, default):
        if default is None:
            self.default = 0.0
        else:
            self.default = float(default)


class StringAdapter(Adapter):
    def from_json(self, json_data) -> str:
        return str(json_data)

    def to_json(self, json_data) -> str:
        return str(json_data)

    def set_default(self, default):
        if default is None:
            self.default = ''
        else:
            self.default = str(default)


class BoolAdapter(Adapter):
    def from_json(self, json_data) -> bool:
        return bool(json_data)

    def to_json(self, json_data) -> bool:
        return bool(json_data)

    def set_default(self, default):
        if default is None:
            self.default = False
        else:
            self.default = bool(default)


class TimestampBaseAdapter(Adapter):
    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = auto_to_datetime(default)

    def from_json(self, json_data):
        raise NotImplementedError('from_json')

    def to_json(self, json_data) -> Optional[str]:
        raise NotImplementedError('to_json')


class TimestampStrAdapter(TimestampBaseAdapter):
    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return str_to_datetime(json_data)

    def to_json(self, json_data) -> Optional[str]:
        if json_data is None:
            return None
        return datetime_to_str(json_data)


class TimestampFloatAdapter(TimestampBaseAdapter):
    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return float_to_datetime(json_data)

    def to_json(self, obj_data) -> Optional[float]:
        if obj_data is None:
            return None
        return datetime_to_float(obj_data)


class TimestampIntAdapter(TimestampBaseAdapter):
    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return int_to_datetime(json_data)

    def to_json(self, obj_data) -> Optional[int]:
        if obj_data is None:
            return None
        return datetime_to_int(obj_data)


class TimestampAutoAdapter(TimestampBaseAdapter):
    def from_json(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return auto_to_datetime(json_data)

    def to_json(self, obj_data) -> Optional[str]:
        if obj_data is None:
            return None
        return datetime_to_str(obj_data)


class ListOfAdapter(Adapter):
    def __init__(self, child: Adapter):
        super().__init__()
        self._child = child

    def from_json(self, json_data: list):
        if not isinstance(json_data, list):
            raise TypeError(f'Expecting a list, got {type(json_data)} instead')
        return [self._child.from_json(item) for item in json_data]

    def to_json(self, obj: list):
        if not isinstance(obj, list):
            raise TypeError(f'Expecting a list, got {type_name(obj)} instead')
        return [self._child.to_json(item) for item in obj]

    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = list(default)


class MapOfAdapter(Adapter):
    def __init__(self, child: Adapter):
        super().__init__()
        self._child = child

    def from_json(self, json_data: dict):
        if not isinstance(json_data, dict):
            raise TypeError(f'Expecting a dict, got {type(json_data)} instead')
        return {k: self._child.from_json(v) for k, v in json_data.items()}

    def to_json(self, obj: dict):
        if not isinstance(obj, dict):
            raise TypeError(f'Expecting a dict, got {type_name(obj)} instead')
        return {k: self._child.to_json(v) for k, v in obj.items()}

    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = dict(default)


class ObjAdapter(Adapter):
    def __init__(self, child: type):
        super().__init__()
        require_jsonified(child)
        self._child = child

    def from_json(self, json_data: Optional[dict]):
        if json_data is None:
            return None
        if not isinstance(json_data, dict):
            raise TypeError(f'Expecting a dict, got {type_name(json_data)} instead')
        return from_json(self._child, json_data)

    def to_json(self, obj: Optional[dict]):
        if obj is None:
            return None
        if not isinstance(obj, self._child):
            raise TypeError(f'Expecting a {self._child.__name__}, got {type_name(obj)} instead')
        return to_json(obj)

    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = self._child(default)


def _type_handler_list(args, parser):
    if len(args) != 1:
        raise TypeError('ListOf requires exactly one type argument')
    sub_value = parser.parse_type_spec(args[0])
    return ListOfAdapter(sub_value)


def _type_handler_map(args, parser):
    if len(args) != 1:
        raise TypeError('MapOf requires exactly one type argument')
    sub_value = parser.parse_type_spec(args[0])
    return MapOfAdapter(sub_value)


class TypeSpecParser:
    def __init__(self):
        self._type_handlers = {
            str: StringAdapter,
            int: IntAdapter,
            bool: BoolAdapter,
            float: FloatAdapter,
            datetime: TimestampAutoAdapter,
            TypeSpec.MapOf: _type_handler_map,
            TypeSpec.ListOf: _type_handler_list,
            (TypeSpec.Timestamp, tuple()): TimestampAutoAdapter,
            (TypeSpec.Timestamp, (int,)): TimestampIntAdapter,
            (TypeSpec.Timestamp, (str,)): TimestampStrAdapter,
            (TypeSpec.Timestamp, (float,)): TimestampFloatAdapter,
        }

    def register(self, ts: Union[type, str], handler: Callable):
        self._type_handlers[ts] = handler

    def parse_type_spec(self, ts):
        if is_jsonified(ts):  # a jsonified sub-class
            return ObjAdapter(ts)
        if isinstance(ts, TypeSpec):  # a type-spec class with optional argumants
            head, args = ts.head(), ts.tail()
        elif isinstance(ts, type):  # simple type (no arguments)
            head, args = ts, tuple()
        else:
            raise TypeError(f'Invalid type: {ts}')

        try:
            type_handler = self._type_handlers[head]
        except KeyError:
            try:
                type_handler = self._type_handlers[(head, args)]
            except KeyError:
                raise TypeError(f'Don\'t know how to handle type: {head}')
        return type_handler(args, parser=self)


class Field:
    def __init__(self,
                 type_spec: Union[TypeSpec, type],
                 required: bool = False,
                 omit_empty: bool = True,
                 default: Any = None,
                 name: str = '',
                 **kwargs):
        self.type_spec = type_spec
        self.required = required
        self.omit_empty = omit_empty
        self.default = default
        self.name = name
        self.options = kwargs


class FieldHandler:
    def __init__(self,
                 adapter: Adapter,
                 required: bool = False,
                 omit_empty: bool = True,
                 name: str = ''):
        self._adapter = adapter
        self._omit_empty = omit_empty
        self._required = required
        self._name = name

    def read(self, json_data: dict):
        try:
            json_value = json_data[self._name]
        except KeyError:
            if self._required:
                raise ValueError(f'Required field {self._name} is missing.')
            return self._adapter.zero()
        return self._adapter.from_json(json_value)

    def write(self, json_data: dict, attr_value: Any):
        if self._adapter.is_empty(attr_value) and self._omit_empty:
            return
        json_data[self._name] = self._adapter.to_json(attr_value)

    def zero(self):
        return self._adapter.zero()


def _maybe_setattr(cls, attr_name, attr_value):
    if not hasattr(cls, attr_name):
        setattr(cls, attr_name, attr_value)


def _init_obj(obj, **kwargs):
    fields: dict = getattr(obj.__class__, _FIELDS)
    for attr_name, attr_value in fields.items():
        if attr_name in kwargs:
            setattr(obj, attr_name, kwargs[attr_name])
        else:
            setattr(obj, attr_name, attr_value.zero())
    for k in kwargs.keys():
        if k not in fields:
            raise ValueError(f'No matching JSON Field for the initializer `{k}`')


class Jsonier:
    """
    Wrapper class that generates all necessary plumbing around JSON conversion.
    """

    def __init__(self):
        self._parser = TypeSpecParser()

    def type_parser(self):
        return self._parser

    def __call__(self, cls, /, *args, **kwargs):
        def wrap(cls):
            return self._process_class(cls)

        # See if we're being called as @dataclass or @dataclass().
        if cls is None:
            # We're called with parens.
            return wrap

        # We're called as @dataclass without parens.
        return self._process_class(cls)

    @staticmethod
    def _set_default(cls, attr_name, attr_value):
        if not hasattr(cls, attr_name):
            setattr(cls, attr_name, attr_value)

    def _process_class(self, cls):
        fields = {}
        for attr_name, attr_value in cls.__dict__.items():
            if not isinstance(attr_value, Field):
                if not attr_name.startswith('_') and not callable(attr_value):
                    # warning
                    logging.warning(f'JSON class {cls.__name__} has an attribute `{attr_name}` that is not a field')
                continue
            fields[attr_name] = self._create_handler(attr_value, attr_name)

        if hasattr(cls, _FIELDS):
            f = dict(getattr(cls, _FIELDS))
            f.update(fields)
            setattr(cls, _FIELDS, f)
        else:
            setattr(cls, _FIELDS, fields)

        _maybe_setattr(cls, 'from_json', MethodType(from_json, cls))
        _maybe_setattr(cls, 'from_json_str', MethodType(from_json_str, cls))
        _maybe_setattr(cls, 'to_json', to_json)
        _maybe_setattr(cls, 'to_json_str', to_json_str)
        _maybe_setattr(cls, '__str__', to_json_str)
        setattr(cls, '__init__', _init_obj)
        return cls

    def _create_handler(self, field: Field, attr_name: str):
        adapter = self._parser.parse_type_spec(field.type_spec)
        adapter.set_default(field.default)
        adapter.set_options(field.options)
        return FieldHandler(
            adapter=adapter,
            required=field.required,
            omit_empty=field.omit_empty,
            name=field.name or attr_name,
        )


jsonified = Jsonier()


def from_json(cls, json_data: dict):
    require_jsonified(cls)
    fields: dict = getattr(cls, _FIELDS)
    inst = cls()
    for attr_name, field in fields.items():
        v = field.read(json_data=json_data)
        setattr(inst, attr_name, v)
    return inst


def from_json_str(cls, json_str: str):
    return from_json(cls, json_data=json.loads(json_str))


def to_json(obj) -> dict:
    cls = obj.__class__
    require_jsonified(cls)
    converters: dict = getattr(cls, _FIELDS)
    json_data = {}
    for attr_name, field in converters.items():
        field.write(json_data=json_data, attr_value=getattr(obj, attr_name))
    return json_data


def to_json_str(obj, **kwargs) -> str:
    data = to_json(obj)
    return json.dumps(data, **kwargs)
