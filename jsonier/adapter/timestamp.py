from datetime import datetime
from typing import Optional

from jsonier.adapter import Adapter
from jsonier.util.datetimeutil import (
    auto_to_datetime,
    str_to_datetime,
    datetime_to_str,
    float_to_datetime,
    datetime_to_float,
    int_to_datetime,
    datetime_to_int
)
from jsonier.util.typespec import TypeSpec


class TimestampBaseAdapter(Adapter):
    def set_default(self, default):
        if default is None:
            self.default = None
        else:
            self.default = auto_to_datetime(default)

    def load(self, json_data):
        raise NotImplementedError('from_json')

    def dump(self, json_data) -> Optional[str]:
        raise NotImplementedError('to_json')


class TimestampStrAdapter(TimestampBaseAdapter):
    def load(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return str_to_datetime(json_data)

    def dump(self, json_data) -> Optional[str]:
        if json_data is None:
            return None
        return datetime_to_str(json_data)


class TimestampFloatAdapter(TimestampBaseAdapter):
    def load(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return float_to_datetime(json_data)

    def dump(self, obj_data) -> Optional[float]:
        if obj_data is None:
            return None
        return datetime_to_float(obj_data)


class TimestampIntAdapter(TimestampBaseAdapter):
    def load(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return int_to_datetime(json_data)

    def dump(self, obj_data) -> Optional[int]:
        if obj_data is None:
            return None
        return datetime_to_int(obj_data)


class TimestampAutoAdapter(TimestampBaseAdapter):
    def load(self, json_data) -> Optional[datetime]:
        if json_data is None:
            return None
        return auto_to_datetime(json_data)

    def dump(self, obj_data) -> Optional[str]:
        if obj_data is None:
            return None
        return datetime_to_str(obj_data)


Timestamp = TypeSpec(TypeSpec.Timestamp)