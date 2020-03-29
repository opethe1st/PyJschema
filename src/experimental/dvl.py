import numbers
import re
from typing import Dict, Iterable, Optional, Pattern


class IValidator:
    def __call__(self, instance):
        raise NotImplementedError


# The Primitives!
class Type(IValidator):
    pass


class Range:
    single_number = re.compile(r"([0-9]+)")
    range_ = re.compile(r"([[(])([0-9]*)\s*,\s*([0-9]*)([])])")

    def __init__(self, exclusive_mini=None, exclusive_maxi=None, mini=None, maxi=None):
        if mini is not None and exclusive_mini is not None:
            raise Exception()
        if maxi is not None and exclusive_maxi is not None:
            raise Exception()

        self.checks = []
        if mini is not None:
            self.checks.append(lambda x: mini <= x)
        if exclusive_mini is not None:
            self.checks.append(lambda x: exclusive_mini < x)
        if maxi is not None:
            self.checks.append(lambda x: x <= maxi)
        if exclusive_maxi is not None:
            self.checks.append(lambda x: x < exclusive_maxi)

    @classmethod
    def from_string(cls, string):
        match = cls.single_number.match(string)
        if match:
            # need to find out whether it is mini or exclusive_min etc.
            return cls(mini=int(match.group(1)), maxi=int(match.group(1)))

        match = cls.range_.match(string)
        mini, exclusive_mini, maxi, exclusive_maxi = None, None, None, None
        if match:
            value = match.group(2)
            if value:
                if match.group(1) == "(":
                    exclusive_mini = int(value)
                elif match.group(1) == "[":
                    mini = int(value)
                else:
                    raise Exception(f"unknown: {match.group(1)}")

            value = match.group(3)
            if value:
                if match.group(4) == ")":
                    exclusive_maxi = int(value)
                elif match.group(4) == "]":
                    maxi = int(value)
                else:
                    raise Exception(f"unknown: {match.group(4)}")

            return cls(
                mini=mini,
                exclusive_mini=exclusive_mini,
                maxi=maxi,
                exclusive_maxi=exclusive_maxi,
            )

        raise Exception(f"unrecognised string {string}")

    def __contains__(self, value):
        return all(check(value) for check in self.checks)


def check_type(type_):
    def decorator(func):
        def wrapper(self, instance):
            if not isinstance(instance, type_):
                return False
            return func(self, instance)

        return wrapper

    return decorator


class String(Type):
    def __init__(self, regex=None):
        self.regex = re.compile(regex) if regex else None

    @check_type(str)
    def __call__(self, instance):
        if self.regex:
            return bool(self.regex.match(instance))
        return True


class Number(Type):
    def __init__(self, range_=None, multipleOf=None):
        self.range = Range.from_string(range_) if range_ else None
        self.multipleOf = multipleOf

    @check_type(numbers.Number)
    def __call__(self, instance):
        if self.range and instance not in self.range:
            return False
        if self.multipleOf and instance % self.multipleOf != 0:
            return False
        return True


class Integer(Number):
    @check_type(int)
    def __call__(self, instance):
        return super().__call__(instance)


class Bool(Type):
    @check_type(bool)
    def __call__(self, instance):
        return True


class Null(Type):
    @check_type(type(None))
    def __call__(self, instance):
        return True


class Any(IValidator):
    def __call__(self, instance):
        return True


class Nothing(IValidator):
    def __call__(self, instance):
        return False


class Const(IValidator):
    def __init__(self, literal):
        self.literal = literal

    def __call__(self, instance):
        return instance == self.literal


class Array(Type):
    def __init__(
        self,
        validators: Optional[Iterable[IValidator]] = None,
        range_: Optional[Range] = None,
        unique: bool = False,
    ):
        self.validators = validators if validators else []
        self.range = range_
        self.unique = unique

    @check_type(list)
    def __call__(self, instance):
        res = all(validator(item) for validator, item in zip(self.validators, instance))
        if not res:
            return False

        if self.range:
            if not len(instance) in self.range:
                return False

        if self.unique:
            # need to convert to string because not every item will be hashable
            if len(set([str(item) for item in instance])) != len(instance):
                return False
        return True


class Object(Type):
    def __init__(
        self,
        validators: Optional[Dict[str, IValidator]] = None,
        range_: Optional[Range] = None,
        key: Optional[Pattern] = None,
        value: Optional[IValidator] = None,
    ):
        self.validators = validators if validators else {}
        self.range = range_
        self.key = re.compile(key) if key else None
        self.value = value if value else None

    @check_type(dict)
    def __call__(self, instance):
        for key, value in instance.items():
            if key in self.validators:
                if not self.validators[key](value):
                    return False
            else:
                if self.key:
                    if not self.key.match(key):
                        return False
                if self.value:
                    if not self.value(value):
                        return False

        if self.range:
            if not len(instance) in self.range:
                return False
        return True


# The Combinators!
class Not(IValidator):
    def __init__(self, validator):
        self.validator = validator

    def __call__(self, instance):
        res = self.validator(instance)
        return not res


class Or(IValidator):
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, instance):
        return any(validator(instance) for validator in self.validators)


class And(IValidator):
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, instance):
        return all(validator(instance) for validator in self.validators)


class Xor(IValidator):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, instance):
        return self.left(instance) ^ self.right(instance)


class If(IValidator):
    def __init__(
        self, condition: IValidator, then: IValidator = None, else_: IValidator = None
    ):
        self.condition = condition
        self.then = then
        self.else_ = else_

    def __call__(self, instance):
        if self.condition(instance):
            return self.then(instance) if self.then else True
        else:
            return self.else_(instance) if self.else_ else True
        return


# Means of abstraction!
# just give it a name. assign to a variable. Create a function? or create an ivalidator?
phoneNumber = String(regex=r"^[0-9]{11}$")


# What about if there needs to be a parameter, then write a function or a callable. Callable just means the value can be baked in once.
class Optional:
    def __init__(self, validator):
        self.validator = validator

    def __call__(self, instance):
        return Or(self.validator, Null())(instance=instance)


profile = Object(
    {
        "name": String(),
        "age": Integer(),
        "gender": Or(Const("Male"), Const("Female"), Const("Other")),
    },
    range_="[3, 5)",
    key="x_.*",
    value=Any,
)
if __name__ == "__main__":
    print(phoneNumber("08098353808"))
    print(Optional(Integer())(None))
    print(Optional(String())(None))
    print(Optional(String())("a string"))
    print(Not(Optional(String()))(12242423))
    range_ = Range.from_string("3")
    print(4 not in range_)
    print(3 in range_)
    range_ = Range.from_string("[1,5)")
    print(1 in range_)
    print(4 in range_)
    print(5 not in range_)
