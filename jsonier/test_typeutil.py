import unittest

from jsonier.util.typeutil import *


class TypespecTestCase(unittest.TestCase):
    def test_equality(self):
        a1 = TypeSpec(str)
        b1 = TypeSpec(int)
        self.assertNotEqual(a1, b1)

        a2 = TypeSpec(int)
        self.assertEqual(a2, int)

        a3 = TypeSpec(dict)
        b3 = TypeSpec(dict)
        c3 = TypeSpec(str)
        self.assertEqual(a3, b3)
        self.assertNotEqual(a3, c3)

        a4 = MapOf[ListOf[str]]
        b4 = MapOf[ListOf[str]]
        c4 = MapOf[ListOf[int]]
        self.assertEqual(a4, b4)
        self.assertNotEqual(b4, c4)

if __name__ == '__main__':
    unittest.main()
