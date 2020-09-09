import unittest

from jsonier.util.typespec import *
from jsonier.adapter.list_of import ListOf
from jsonier.adapter.map_of import MapOf
from jsonier.adapter.timestamp import Timestamp


class TestTypeSpec(unittest.TestCase):
    def test_equality_simple(self):
        ts1 = TypeSpec('float')
        ts2 = TypeSpec('float')
        self.assertEqual(ts1, ts2)

        ts1 = TypeSpec('float')
        ts2 = TypeSpec('int')
        self.assertNotEqual(ts1, ts2)

    def test_equality_param(self):
        ts1 = TypeSpec('ListOf')[int]
        ts2 = TypeSpec('ListOf')[int]
        self.assertEqual(ts1, ts2)

        ts1 = TypeSpec('ListOf')[str]
        ts2 = TypeSpec('ListOf')[str]
        self.assertEqual(ts1, ts2)

        ts1 = ListOf[MapOf[str]]
        ts2 = ListOf[MapOf[str]]
        self.assertEqual(ts1, ts2)

    def test_match(self):
        ts1 = ListOf[int]
        ts2 = ListOf[int]
        self.assertTrue(ts1.matches(ts2))
        ts3 = ListOf[str]
        self.assertFalse(ts1.matches(ts3))
        ts4 = ListOf[...]
        self.assertTrue(ts4.matches(ts1))
        self.assertTrue(ts4.matches(ts2))
        self.assertTrue(ts4.matches(ts3))


class TestTypeSpecMap(unittest.TestCase):
    def test_simple(self):
        tm = TypeSpecMap()
        tm.set(int, 'int')
        tm.set(str, 'str')
        tm.set(ListOf[int], 'List<int>')
        tm.set(MapOf[...], 'Map<?>')
        tm.set(MapOf[bool], 'Map<bool>')

        self.assertEqual(tm.get(int), 'int')
        self.assertEqual(tm.get(str), 'str')
        self.assertEqual(tm.get(ListOf[int]), 'List<int>')
        self.assertEqual(tm.get(ListOf[str]), None)
        self.assertEqual(tm.get(MapOf[int]), 'Map<?>')
        self.assertEqual(tm.get(MapOf[bool]), 'Map<bool>')
        self.assertEqual(tm.get(MapOf[str]), 'Map<?>')
        self.assertEqual(tm.get(Timestamp[str]), None)


if __name__ == '__main__':
    unittest.main()
