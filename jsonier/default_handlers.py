from datetime import datetime

from jsonier.adapter.timestamp import Timestamp
from jsonier.adapter.map_of import MapOf
from jsonier.adapter.list_of import ListOf

from jsonier.adapter.simple import (
    IntAdapter,
    FloatAdapter,
    StringAdapter,
    BoolAdapter
)
from jsonier.adapter.list_of import ListOfAdapter
from jsonier.adapter.map_of import MapOfAdapter
from jsonier.adapter.object import ObjectAdapter
from jsonier.adapter.timestamp import (
    TimestampStrAdapter,
    TimestampFloatAdapter,
    TimestampIntAdapter,
    TimestampAutoAdapter
)


def register_handlers(jsonier):
    parser = jsonier.typespec_parser()
    parser.register_default_handler(ObjectAdapter)
    parser.register(str, StringAdapter)
    parser.register(int, IntAdapter)
    parser.register(bool, BoolAdapter)
    parser.register(float, FloatAdapter)
    parser.register(datetime, TimestampAutoAdapter)
    parser.register(MapOf[...], MapOfAdapter)
    parser.register(ListOf[...], ListOfAdapter)
    parser.register(Timestamp, TimestampAutoAdapter)
    parser.register(Timestamp[int], TimestampIntAdapter)
    parser.register(Timestamp[str], TimestampStrAdapter)
    parser.register(Timestamp[float], TimestampFloatAdapter)
