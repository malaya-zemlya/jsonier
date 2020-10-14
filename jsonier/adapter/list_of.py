from jsonier.adapter import Adapter
from jsonier.util.typespec import (
    type_name, TypeSpec
)


class ListOfAdapter(Adapter):
    def __init__(self, child: Adapter):
        super().__init__()
        self._child = child

    def load(self, json_data: list):
        if not isinstance(json_data, list):
            raise TypeError(f'Expecting a list, got {type(json_data)} instead')
        return [self._child.load(item) for item in json_data]

    def dump(self, obj: list):
        if not isinstance(obj, list):
            raise TypeError(f'Expecting a list, got {type_name(obj)} instead')
        return [self._child.dump(item) for item in obj]

    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = list(default)

    @staticmethod
    def needs_param_parsing():
        # In ListOf[T], T itself needs parsing.
        return True


ListOf = TypeSpec(TypeSpec.ListOf)
