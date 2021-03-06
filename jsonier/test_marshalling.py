import unittest
from datetime import (
    datetime,
    timezone,
    timedelta
)

from jsonier import *


@jsonified
class Present:
    name = Field(str, required=True)
    price = Field(float, required=True)


@jsonified
class Address:
    street = Field(str, omit_empty=False)
    street2 = Field(str)
    city = Field(str, required=True)
    state = Field(str, required=True)


@jsonified
class Position:
    name = Field(str, omit_empty=False)
    level = Field(int)


@jsonified
class Contact:
    kind = Field(str, required=True)
    data = Field(str, required=True)


@jsonified
class Person:
    name = Field(str, required=True, omit_empty=False)
    last_name = Field(str, required=True, name='last-name', omit_empty=False)
    age = Field(int, default=33)
    birthday = Field(Timestamp, default=0)
    hobbies = Field(ListOf[str])
    is_enrolled = Field(bool, name='is-enrolled')
    is_admin = Field(bool, name='is-admin')
    address = Field(Address)
    position = Field(Position, required=False)
    contacts = Field(MapOf[Contact])


@jsonified
class Person2:
    first = Field(str, omit_empty=False, name='first-name')
    last = Field(str, omit_empty=False, name='surname')
    age = Field(int)
    address = Field(Address)


class MarshallingTestCase(unittest.TestCase):
    def test_equality(self):
        data = """
        {
           "name": "John",
           "last-name": "Smith",
           "age": 44,
           "hobbies": ["swimming", "running"],
           "is-enrolled": false,
           "is-admin": true,

           
           "address": {
                "street": "123 Main st",
                "city": "New Fork",
                "state": "NF"
           },
           "contacts": {
              "home": {
                 "kind": "phone",
                 "data": "123-45-56"
              },
              "work": {
                 "kind": "fax",
                 "data": "456-99-99"
              }
           }
        }
        """
        p = Person.loads(data)
        self.assertEqual(p.name, 'John')
        self.assertEqual(p.last_name, 'Smith')
        self.assertEqual(p.age, 44)
        self.assertListEqual(p.hobbies, ['swimming', 'running'])
        self.assertEqual(p.is_enrolled, False)
        self.assertEqual(p.address.city, 'New Fork')
        self.assertEqual(p.address.street, '123 Main st')
        self.assertEqual(p.address.street2, '')
        self.assertEqual(p.address.state, 'NF')
        self.assertIsNone(p.position)  # not specified
        self.assertEqual(p.contacts['home'].kind, 'phone')
        self.assertEqual(p.contacts['home'].data, '123-45-56')
        self.assertEqual(p.contacts['work'].kind, 'fax')
        self.assertEqual(p.contacts['work'].data, '456-99-99')

        q = p.dump()
        self.assertEqual(q['name'], 'John')
        self.assertEqual(q['last-name'], 'Smith')
        self.assertEqual(q['age'], 44)
        self.assertListEqual(q['hobbies'], ['swimming', 'running'])
        self.assertNotIn('is-enrolled', q)
        self.assertNotIn('is_enrolled', q)
        self.assertNotIn('position', q)

    def test_creation(self):
        obj = Person2(first='Adam',
                      last='Smith',
                      age='100',
                      address=Address(
                          street='600 Heavenward Ave',
                          city='New Bork City',
                          state='NB'
                      ))
        j = obj.dump()
        self.assertEqual(j['first-name'], 'Adam')
        self.assertEqual(j['surname'], 'Smith')
        self.assertEqual(j['age'], 100)
        self.assertEqual(j['address']['street'], '600 Heavenward Ave')
        self.assertEqual(j['address']['city'], 'New Bork City')
        self.assertEqual(j['address']['state'], 'NB')

    def test_creation_wrong_arg(self):
        with self.assertRaises(ValueError) as context:
            address = Address(
                street='600 Heavenward Ave',
                city='New Bork City',
                province='NB'  # should be 'state'
            )


@jsonified
class Dates:
    date = Field(Timestamp, default='2020-03-12T00:00:00', name='date')
    birthday = Field(Timestamp, default=0)
    started = Field(Timestamp[str])
    finished = Field(Timestamp[int])
    valid_since = Field(Timestamp[float])
    valid_until = Field(Timestamp, omit_empty=False)


class TestTimestamp(unittest.TestCase):
    def test_timestamp(self):
        # print ('test_timestamps')
        data = """
        {
           "started": "2002-12-25T00:00:00-06:00",
           "finished": 1040798,
           "valid_since": 1040798340.0
        }
        """
        bd = Dates.loads(data)
        self.assertEqual(bd.date, datetime(2020, 3, 12, 0, 0))
        self.assertEqual(bd.started, datetime(2002, 12, 25, 0, 0,
                                              tzinfo=timezone(timedelta(days=-1, seconds=64800))))
        self.assertEqual(bd.finished, datetime(1970, 1, 13, 1, 6, 38))
        self.assertEqual(bd.valid_since, datetime(2002, 12, 25, 6, 39))
        self.assertIsNone(bd.valid_until)


if __name__ == '__main__':
    unittest.main()
