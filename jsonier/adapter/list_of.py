from jsonier.adapter import Adapter
from jsonier.util.typespec import (
    type_name, TypeSpec
)


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


ListOf = TypeSpec(TypeSpec.ListOf)
