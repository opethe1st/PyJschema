import re
import numbers


class IValidator:
    def __call__(self, instance):
        raise NotImplementedError


# The Primitives!
class Type(IValidator):
    pass


class Range:
    single_number = re.compile(r"([0-9]+)")
    range_ = re.compile(r"([[(])([0-9]*),([0-9]*)([])])")

    def __init__(self, exclusive_min=None, exclusive_max=None, mini=None, maxi=None):
        if mini and exclusive_min:
            raise Exception()
        if maxi and exclusive_max:
            raise Exception()

        self.checks = []
        if mini:
            self.checks.append(lambda x: mini <= x)
        if exclusive_min:
            self.checks.append(lambda x: exclusive_min < x)
        if maxi:
            self.checks.append(lambda x: x <= maxi)
        if exclusive_max:
            self.checks.append(lambda x: x < exclusive_min)

    @classmethod
    def from_string(cls, string):
        match = cls.single_number.match(string)
        if match:
            # need to find out whether it is mini or exclusive_min etc.
            return cls(mini=int(match.group(1)), maxi=int(match.group(1)))

        match = cls.range_.match(string)
        if match:
            return cls(mini=int(match.group(1)), maxi=int(match.group(2)))

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
        self.range = range_
        self.multipleOf = multipleOf

    @check_type(numbers.Number)
    def __call__(self, instance):
        if not self.range and not self.multipleOf:
            return True
        return False


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
    def __init__(self, pattern, range_, unique):
        self.pattern = pattern
        self.range = range_
        self.unique = unique

    @check_type(list)
    def __call__(self, instance):
        validators = self._expand(self.pattern)
        res = all(validator(item) for validator, item in zip(validators, instance))
        return res

    def _expand(self, pattern):
        # I will just assume it is expanded at this point
        return pattern


class Object(Type):
    def __init__(self, object_pattern, range_, key, value):
        self.object_pattern = object_pattern
        self.range = range_
        self.key = key
        self.value = value

    @check_type(dict)
    def __call__(self, instance):
        pass


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
        'name': String(),
        'age': Integer(),
        'gender': Or(Const('Male'), Const('Female'), Const('Other')),
    },
    range_="[3, 5)",
    key='x_.*',
    value=Any,
)
if __name__ == "__main__":
    print(phoneNumber('08098353808'))
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
