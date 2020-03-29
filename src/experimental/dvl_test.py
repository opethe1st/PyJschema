import unittest
from itertools import repeat

from parameterized import parameterized

from dvl import (And, Any, Array, Bool, Const, If, Integer, Not, Nothing, Null,
                 Number, Object, Or, Range, String, Xor)


# Primitives
class TestRange(unittest.TestCase):

    @parameterized.expand([
        (0, False),
        (1, True),
        (3, True),
        (40003232, True),
    ])
    def test_one_end_missing(self, instance, result):
        range_string = "[1,)"
        range_ = Range.from_string(range_string)
        self.assertEqual(instance in range_, result)

    @parameterized.expand([
        (0, False),
        (1, True),
        (3, True),
        (4, False),
    ])
    def test_both_closed(self, instance, result):
        range_string = "[1,3]"
        range_ = Range.from_string(range_string)
        self.assertEqual(instance in range_, result)

    @parameterized.expand([
        (1, False),
        (2, True),
        (3, False),
    ])
    def test_both_open(self, instance, result):
        range_string = "(1,3)"
        range_ = Range.from_string(range_string)
        self.assertEqual(instance in range_, result)

    @parameterized.expand([
        (1, False),
        (2, True),
        (3, True),
    ])
    def test_open_and_closed(self, instance, result):
        range_string = "(1,3]"
        range_ = Range.from_string(range_string)
        self.assertEqual(instance in range_, result)

    @parameterized.expand([
        (1, True),
        (2, True),
        (3, False),
    ])
    def test_closed_and_open(self, instance, result):
        range_string = "[1,3)"
        range_ = Range.from_string(range_string)
        self.assertEqual(instance in range_, result)


class TestString(unittest.TestCase):
    def test(self):
        string = String(r"[0-9]{11}")
        self.assertTrue(string("08098353808"))


class TestNumber(unittest.TestCase):
    def test(self):
        number = Number(range_="[1, 30)", multipleOf=5)
        self.assertTrue(number(10))

    def test_false(self):
        number = Number(range_="[1, 30)", multipleOf=11)
        self.assertFalse(number(10))


class TestBool(unittest.TestCase):
    @parameterized.expand([
        (5, False),
        (True, True),
        (False, True),
    ])
    def test(self, instance, result):
        boolean = Bool()
        self.assertEqual(boolean(instance), result)


class TestNull(unittest.TestCase):
    @parameterized.expand([
        (5, False),
        (None, True)
    ])
    def test(self, instance, result):
        null = Null()
        self.assertEqual(null(instance), result)


class TestAny(unittest.TestCase):
    def test(self):
        any_ = Any()
        self.assertTrue(any_({12: 12}))


class TestNothing(unittest.TestCase):
    def test(self):
        any_ = Nothing()
        self.assertFalse(any_({12: 12}))


class TestConst(unittest.TestCase):
    def test(self):
        const = Const("a literal")
        self.assertTrue(const("a literal"))


class TestArray(unittest.TestCase):
    @parameterized.expand([
        (["s1", "s2"], True),
        ([], True),
        (["s1"], True),
        (["s1", 12], False),
    ])
    def test_validators(self, instance, result):
        array = Array(validators=repeat(String()))
        self.assertEqual(array(instance), result)

    @parameterized.expand([
        ([], False),
        (["s1"], True),
        (["s1", "s2"], True),
        (["s1", "s2", "s3"], False),
    ])
    def test_range(self, instance, result):
        array = Array(range_=Range.from_string("[1, 3)"))
        self.assertEqual(array(instance), result)

    @parameterized.expand([
        ([], True),
        (["s1"], True),
        (["s1", "s1"], False),
        (["s1", "s2", "s3"], True),
        (["s1", "s2", "s2"], False),
    ])
    def test_unique(self, instance, result):
        array = Array(unique=True)
        self.assertEqual(array(instance), result)


class TestObject(unittest.TestCase):

    @parameterized.expand([
        ({"name": "Ope", "age": 23}, True),
    ])
    def test_validators(self, instance, result):
        obj = Object(validators={"name": String(), "age": Integer()})
        self.assertEqual(obj(instance), result)

    @parameterized.expand([
        ({"name": "Ope", "age": 23}, True),
        ({"name": "Ope", "age": 23, "address": "2324"}, False),
    ])
    def test_range(self, instance, result):
        obj = Object(range_=Range.from_string("[1, 3)"))
        self.assertEqual(obj(instance), result)

    @parameterized.expand([
        ({"x_header": 23}, True),
        ({"age": "23"}, False),
    ])
    def test_key(self, instance, result):
        obj = Object(key="x_.*")
        self.assertEqual(obj(instance), result)

    @parameterized.expand([
        ({"age": 23}, True),
        ({"age": "23"}, False),
    ])
    def test_value(self, instance, result):
        obj = Object(value=Number())
        self.assertEqual(obj(instance), result)


# Combinations
class TestNot(unittest.TestCase):

    @parameterized.expand([
        ("value", True),
        ("a literal", False),
    ])
    def test(self, instance, result):
        not_ = Not(Const("a literal"))
        self.assertEqual(not_(instance), result)


class TestOr(unittest.TestCase):
    @parameterized.expand([
        ("value", True),
        ("anotherValue", True),
        ("blah blah", False),
    ])
    def test(self, instance, result):
        or_ = Or(Const("value"), Const("anotherValue"))
        self.assertEqual(or_(instance), result)


class TestAnd(unittest.TestCase):
    @parameterized.expand([
        (0, True),
        (4, True),
        (7, False),
        (16, False),
    ])
    def test(self, instance, result):
        and_ = And(Number(range_="[0, 10)"), Number(multipleOf=4))
        self.assertEqual(and_(instance), result)


class TestXor(unittest.TestCase):
    @parameterized.expand([
        (0, False),
        (4, False),
        (7, True),
        (16, True),
    ])
    def test(self, instance, result):
        and_ = Xor(Number(range_="[0, 10)"), Number(multipleOf=4))
        self.assertEqual(and_(instance), result)


class TestIf(unittest.TestCase):
    @parameterized.expand([
        (0, True),
        ("a string", True),
        ([], False),
        ({}, False),
    ])
    def test(self, instance, result):
        if_ = If(Number(), then=Number(range_="[0, 10)"), else_=String())
        self.assertEqual(if_(instance), result)
