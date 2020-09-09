import json
import logging
from types import MethodType
from typing import (
    Any,
    Callable,
    Union
)

from jsonier.adapter import Adapter
from jsonier.util.typespec import TypeSpecMap, TypeSpec

_FIELDS = '__JSON'
_MISSING = (None,)  # a special value indicating that a value is not specified (but is not None)


def require_jsonified(cls):
    if not hasattr(cls, _FIELDS):
        raise TypeError(f'{cls.__name__} is not a jsonclass object.')


def is_jsonified(cls):
    return hasattr(cls, _FIELDS)


class TypeSpecParser:
    def __init__(self):
        self._type_handlers = TypeSpecMap()
        self._object_handler = None

    def register(self, ts: Union[type, TypeSpec], handler: Callable, recurse: bool = False):
        self._type_handlers.set(ts, (handler, recurse))

    def register_object_handler(self, handler: Callable):
        self._object_handler = handler

    def parse_type_spec(self, ts):
        if is_jsonified(ts):  # a jsonified sub-class
            if self._object_handler:
                return self._object_handler(ts)
            else:
                raise TypeError(f'Object handler is not defined')

        if isinstance(ts, TypeSpec):  # a type-spec class with optional argumants
            arg = ts.tail()
        elif isinstance(ts, type):
            arg = None
        else:
            raise TypeError(f'Invalid type: {ts}')

        try:
            type_handler, recurse = self._type_handlers.get(ts)
        except KeyError:
            raise TypeError(f'Don\'t know how to handle type: {ts}')
        if recurse:
            arg = self.parse_type_spec(arg)
        return type_handler(arg)


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
