from typing import Optional

from jsonier.util.typespec import JsonType


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