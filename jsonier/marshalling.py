import json
import logging
from types import MethodType
from typing import (
    Any,
    Callable,
    Union, Dict
)

from jsonier.adapter import Adapter
from jsonier.util.typespec import TypeSpecMap, TypeSpec

_FIELDS = '__JSON'
_MISSING = (None,)  # a special value indicating that a value is not specified (but is not None)


def require_jsonified(cls):
    if not is_jsonified(cls):
        raise TypeError(f'{cls.__name__} is not a jsonified object.')


def is_jsonified(cls):
    return hasattr(cls, _FIELDS)


class TypeSpecParser:
    def __init__(self):
        self._type_handlers = TypeSpecMap()
        self._default_handler = None

    def register(self, ts: Union[type, TypeSpec], handler: Callable, recurse: bool = False):
        self._type_handlers.set(ts, handler)

    def register_default_handler(self, handler: Callable):
        self._default_handler = handler

    def parse_typespec(self, ts):
        if isinstance(ts, TypeSpec):  # a type-spec class with optional argumants
            arg = ts.tail()
        elif isinstance(ts, type):
            arg = None
        else:
            raise TypeError(f'Invalid type: {ts}')

        try:
            type_handler = self._type_handlers.get(ts)
        except KeyError:
            if self._default_handler and is_jsonified(ts):
                return self._default_handler(ts)
            else:
                raise TypeError(f'Don\'t know how to handle type: {ts}')
        if type_handler.needs_param_parsing():
            arg = self.parse_typespec(arg)
        return type_handler(arg)


class Field:
    def __init__(self,
                 type_spec: Union[TypeSpec, type],
                 name: str = '',
                 required: bool = False,
                 omit_empty: bool = True,
                 default: Any = None,
                 allow_null: bool = False,
                 **kwargs):
        self.type_spec = type_spec
        self.required = required
        self.omit_empty = omit_empty
        self.default = default
        self.name = name
        self.allow_null = allow_null
        self.options = kwargs

class FieldHandler:
    def __init__(self,
                 adapter: Adapter,
                 required: bool = False,
                 omit_empty: bool = True,
                 allow_null: bool = False,
                 name: str = ''):
        self._adapter = adapter
        self._omit_empty = omit_empty
        self._required = required
        self._name = name
        self._allow_null = allow_null

    def read(self, json_data: dict):
        try:
            json_value = json_data[self._name]
            if json_value is None and self._allow_null:
                return self._adapter.zero()
        except KeyError:
            if self._required:
                raise ValueError(f'Required field {self._name} is missing.')
            return self._adapter.zero()
        return self._adapter.load(json_value)


    def write(self, json_data: dict, attr_value: Any):
        if self._adapter.is_empty(attr_value) and self._omit_empty:
            return
        json_data[self._name] = self._adapter.dump(attr_value)

    def zero(self):
        return self._adapter.zero()


def _maybe_setattr(cls, attr_name, attr_value):
    if not hasattr(cls, attr_name):
        setattr(cls, attr_name, attr_value)


def _update_attr(cls, attr_name, attr_value):
    if hasattr(cls, attr_name):
        f = dict(getattr(cls, attr_name))
        f.update(attr_value)
        setattr(cls, attr_name, f)
    else:
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
        self._typespec_parser = TypeSpecParser()

    def typespec_parser(self):
        return self._typespec_parser

    def __call__(self, cls, /, *args, **kwargs):
        def wrap(c):
            return self._process_class(c)

        # See if we're being called as @dataclass or @dataclass().
        if cls is None:
            # We're called with parens.
            return wrap

        # We're called as @dataclass without parens.
        return self._process_class(cls)

    def _process_class(self, cls):
        fields = self._create_fields(cls)

        if hasattr(cls, _FIELDS):
            f = dict(getattr(cls, _FIELDS))
            f.update(fields)
            setattr(cls, _FIELDS, f)
        else:
            setattr(cls, _FIELDS, fields)

        _maybe_setattr(cls, 'load', MethodType(load, cls))
        _maybe_setattr(cls, 'loads', MethodType(loads, cls))
        _maybe_setattr(cls, 'dump', dump)
        _maybe_setattr(cls, 'dumps', dumps)
        setattr(cls, '__repr__', _to_repr)
        setattr(cls, '__init__', _init_obj)
        return cls

    def _create_fields(self, cls) -> Dict[str, FieldHandler]:
        fields = {}
        for attr_name, attr_value in cls.__dict__.items():
            if not isinstance(attr_value, Field):
                if not attr_name.startswith('_') and not callable(attr_value):
                    # warning
                    logging.warning(f'JSON class {cls.__name__} has an attribute `{attr_name}` that is not a field')
                continue
            fields[attr_name] = self._create_handler(attr_value, attr_name)
        return fields

    def _create_handler(self, field: Field, attr_name: str):
        adapter = self._typespec_parser.parse_typespec(field.type_spec)
        adapter.set_default(field.default)
        adapter.set_options(field.options)
        return FieldHandler(
            adapter=adapter,
            name=field.name or attr_name,
            required=field.required,
            omit_empty=field.omit_empty,
            allow_null=field.allow_null,
        )


def load(cls, json_data: dict):
    require_jsonified(cls)
    fields: dict = getattr(cls, _FIELDS)
    inst = cls()
    for attr_name, field in fields.items():
        try:
            v = field.read(json_data=json_data)
        except (TypeError, ValueError) as e:
            message = str(e)
            raise e.__class__(f'Error parsing {attr_name}: {message}')
        setattr(inst, attr_name, v)
    return inst


def loads(cls, json_str: str):
    return load(cls, json_data=json.loads(json_str))


def dump(obj) -> dict:
    cls = obj.__class__
    require_jsonified(cls)
    converters: dict = getattr(cls, _FIELDS)
    json_data = {}
    for attr_name, field in converters.items():
        field.write(json_data=json_data, attr_value=getattr(obj, attr_name))
    return json_data


def dumps(obj, **kwargs) -> str:
    return json.dumps(dump(obj), **kwargs)


def _to_repr(obj):
    name = obj.__class__.__name__
    args = [f'{k}={repr(v)}' for k, v in vars(obj).items()]
    return name + '(' + ','.join(args) + ')'
