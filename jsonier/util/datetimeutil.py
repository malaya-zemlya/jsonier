from datetime import datetime
from typing import (
    Union
)


def datetime_to_int(dt: datetime) -> int:
    return int(dt.timestamp())


def int_to_datetime(t: int) -> datetime:
    return datetime.utcfromtimestamp(t)


def datetime_to_float(dt: datetime) -> float:
    return dt.timestamp()


def float_to_datetime(t: float) -> datetime:
    return datetime.utcfromtimestamp(t)


def datetime_to_str(dt: datetime) -> str:
    s = dt.isoformat()
    return s + 'Z'


def str_to_datetime(t: str) -> datetime:
    if t.endswith('Z'):
        t = t[:-1]
    return datetime.fromisoformat(t)


def auto_to_datetime(t: Union[int, float, str, datetime]) -> datetime:
    if isinstance(t, datetime):
        return t
    elif isinstance(t, int):
        return int_to_datetime(t)
    elif isinstance(t, float):
        return float_to_datetime(t)
    elif isinstance(t, str):
        return str_to_datetime(t)
    else:
        raise TypeError(f'Cannot convert {type(t)} to datetime')
