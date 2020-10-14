from typing import Optional

from jsonier.util.typespec import JsonType


class Adapter:
    def __init__(self, *args, **kwargs):
        self.default = None

    def set_options(self, options: Optional[dict] = None):
        pass

    def set_default(self, default):
        self.default = default

    @staticmethod
    def needs_param_parsing():
        # return True if type parameters themselves need to be converted to adapters
        # for example, in MapOf[T] or ListOf[T] generic types, T itself needs parsing.
        return False

    def load(self, json_data):
        raise NotImplementedError('load')

    def dump(self, json_data) -> JsonType:
        raise NotImplementedError('dump')

    def zero(self):
        return self.default

    def is_empty(self, obj):
        return not obj