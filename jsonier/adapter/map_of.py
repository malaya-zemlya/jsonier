from jsonier.adapter import Adapter
from jsonier.util.typespec import type_name, TypeSpec


class MapOfAdapter(Adapter):
    # In MapOf[T], T itself needs parsing.
    @staticmethod
    def needs_param_parsing():
        return True

    def __init__(self, child: Adapter):
        super().__init__()
        self._child = child

    def load(self, json_data: dict):
        if not isinstance(json_data, dict):
            raise TypeError(f'Expecting a dict, got {type(json_data)} instead')
        return {k: self._child.load(v) for k, v in json_data.items()}

    def dump(self, obj: dict):
        if not isinstance(obj, dict):
            raise TypeError(f'Expecting a dict, got {type_name(obj)} instead')
        return {k: self._child.dump(v) for k, v in obj.items()}

    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = dict(default)


MapOf = TypeSpec(TypeSpec.MapOf)
