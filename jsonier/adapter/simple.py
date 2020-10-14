from jsonier.adapter import Adapter


class IntAdapter(Adapter):
    def load(self, json_data) -> int:
        return int(json_data)

    def dump(self, json_data) -> int:
        return int(json_data)

    def set_default(self, default):
        if default is None:
            self.default = 0
        else:
            self.default = int(default)


class FloatAdapter(Adapter):
    def load(self, json_data) -> float:
        return float(json_data)

    def dump(self, json_data) -> float:
        return float(json_data)

    def set_default(self, default):
        if default is None:
            self.default = 0.0
        else:
            self.default = float(default)


class StringAdapter(Adapter):
    def load(self, json_data) -> str:
        return str(json_data)

    def dump(self, json_data) -> str:
        return str(json_data)

    def set_default(self, default):
        if default is None:
            self.default = ''
        else:
            self.default = str(default)


class BoolAdapter(Adapter):
    def load(self, json_data) -> bool:
        return bool(json_data)

    def dump(self, json_data) -> bool:
        return bool(json_data)

    def set_default(self, default):
        if default is None:
            self.default = False
        else:
            self.default = bool(default)