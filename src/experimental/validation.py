import abc
from abc import ABC
from collections.abc import Sequence
from typing import List


class IValidator(ABC):

    def __init__(self):
        self.context = {}

    @abc.abstractmethod
    def validate(self, instance):
        pass

    def attach_context(self, context):
        self.context = context


class Types(IValidator):
    # needs to be a list of types, if not a list of types raise an error
    def __init__(self, *types):
        super().__init__()
        self.types = types

    def validate(self, instance):
        return isinstance(instance, self.types)

    def attach_context(self, context):
        self.context = context

    def failure_message(self):
        return f"instance is not one of the types in: {self.types}"


class MinLength(IValidator):
    def __init__(self, value: int):
        # if not an int raise an error
        self.value = value

    def validate(self, instance):
        # need to make sure it is a container first though
        return self.value < len(instance)


class MaxLength(IValidator):
    def __init__(self, value: int):
        # if not an int raise an error
        self.value = value

    def validate(self, instance):
        # need to make sure it is a Sequence first though. as long as it has a __len__ it is good
        return len(instance) < self.value


class Pattern(IValidator):
    def __init__(self, value: str):
        # needs to a valid regex
        import re
        self.value = value
        self.regex = re.compile(self.value)

    def validate(self, instance: str):
        # needs to be a string else error
        return bool(self.regex.match(instance))


# Number keywords
class Max(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        # instance and value just need to be comparable that's all
        # so should be the same type and things like datetimes would also work
        if not isinstance(instance, self.value.__class__):
            return False  # False or raise exception?
        return instance < self.value

    def __repr__(self):
        return f"Max(value={self.value})"


class Min(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        # instance and value just need to be comparable that's all
        # so should be the same type and things like datetimes would also work
        return self.value < instance

    def __repr__(self):
        return f"Min(value={self.value})"


class InclusiveMin(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        return self.value <= instance


class InclusiveMax(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        return instance <= self.value


class MultipleOf(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        multiplier = 100000
        instance = instance * multiplier
        value = self.value * multiplier
        if (instance % value) != 0:
            return False
        return True


# Combinators
class Or(IValidator):
    # maybe add support for using `and` and `^` and `|` and other boolean operators
    def __init__(self, *validators):
        self.validators = validators
        self.context = {}

    def validate(self, instance):
        # what about returning meaniful errors?
        return any(validator.validate(instance) for validator in self.validators)

    def attach_context(self, context):
        self.context = context
        for validator in self.validators:
            validator.attach_context(context=context)


class And(IValidator):
    def __init__(self, *validators, name=None, context=None):
        self.name = name
        self.context = context if context else {}
        self.validators = validators

    def validate(self, instance):
        return all(validator.validate(instance) for validator in self.validators)

    def attach_context(self, context):
        self.context = context
        if self.name:
            self.context[self.name] = self
        for validator in self.validators:
            validator.attach_context(context=context)


# array keywords
class Zip(IValidator):
    def __init__(self, validators: List):
        self.validators = validators

    def validate(self, instance):
        # need to make sure instance is a list - (need to a be ordered)
        if not isinstance(instance, list):
            return False
        return all(validator.validate(value) for value, validator in zip(instance, self.validators))


class Each(IValidator):
    def __init__(self, validator):
        self.validator = validator
        self.context = {}

    def validate(self, instance):
        #  need to be a sequence
        if isinstance(instance, str):
            return False
        if not isinstance(instance, Sequence):
            return False
        return all(self.validator.validate(value) for value in instance)

    def attach_context(self, context):
        self.context = context
        self.validator.attach_context(context)


class PropertyNames(IValidator):
    def __init__(self, validator):
        self.validator = validator

    def validate(self, instance):
        return all(self.validator.validate(key) for key in instance.keys())


class PatternProperties(IValidator):
    def __init__(self, pattern_to_validator):
        # all keys need to be valid regexes
        self.pattern_to_validator = pattern_to_validator

    def validate(self, instance):
        for pattern, validator in self.pattern_to_validator.items():
            for prop, value in instance.items():
                if pattern.match(prop):
                    if not validator.validate(value):
                        return False


class Required(IValidator):
    def __init__(self, required: list):
        self.required = required

    def validate(self, instance):
        return not bool(set(self.required) - set(instance.keys()))


class DependentRequired(IValidator):
    pass


class Equal(IValidator):
    def __init__(self, value):
        self.value = value

    def validate(self, instance):
        return self.value == instance


class Enum(IValidator):
    def __init__(self, values):
        # needs to be a list of values
        self.values = values

    def validate(self, instance):
        return any(value == instance for value in self.values)


class Unique(IValidator):

    def validate(self, instance):
        # needs to a sequence
        return len(set(instance)) == len(instance)


class Any(IValidator):
    def validate(self, instance):
        return True


class Nothing(IValidator):
    def validate(self, instance):
        return False


class If(IValidator):
    def __init__(self, condition, then, else_=Any()):
        self.condition = condition
        self.then = then
        self.else_ = else_

    def validate(self, instance):
        if self.condition.validate(instance):
            return self.then.validate(instance)
        else:
            return self.else_.validate(instance)


class Not(IValidator):
    def __init__(self, validator):
        self.validator = validator

    def validate(self, instance):
        return not self.validator.validate(instance)


class OneOf(IValidator):
    pass


class Ref(IValidator):
    # helps with cyclic/deferred validation?
    # sounds like there needs to be a new argument passed to constructors
    # context - add this via a decorator?
    def __init__(self, value):
        self.value = value
        self.context = {}

    def validate(self, instance):
        validator = self.context.get(self.value)
        if validator:
            return validator.validate(instance=instance)
        else:
            return False

    def attach_context(self, context):
        self.context = context


class Def(IValidator):
    def __init__(self, name_to_validator):
        self.name_to_validator = name_to_validator


"""
This has almost everything except specifying how references would work.
Use validator references exclusive everywhere? Only place you can embedded schemas is def?

# have a __repr__ defined.
# then have a method that returns failure messages. When validation fails. presumed to be only called
# when validation fails
# state of validation failed or not, and save the last instance.
Make sure this works with recursive Schemas
"""


if __name__ == "__main__":
    validator = And(
        Each(
            validator=Or(
                Ref('nested-list'),
                Types(str),
            ),
        ),
        Types(list),
        name="nested-list",
    )
    validator.attach_context(context={})
    assert validator.validate(["string", "string"])
    assert validator.validate(["string", []])
    assert validator.validate("string") is False
    assert validator.validate(["string", [[[[[[]]]]]]])
    assert validator.validate(4121) is False

    validator = And(Min(value=0), Max(value=10))
    assert validator.validate(-12) is False
    assert validator.validate(12) is False
    assert validator.validate(5)

    validator = Each(Or(And(Types(str), MaxLength(10)), Equal(None)))
    assert validator.validate([None])
    assert validator.validate(["Astring"])
    assert validator.validate(["this string is too long"]) is False

"""
New Idea:
validate method but pass in a context that saves all the errors so far.
Do we care about reporting which validator failed and what instance it was trying to validate and where?

Also DSL to make it more idiomatic
so we would have. This should be possible in python actually!
but can't do parametrization in python. Except by defining a new class


validator = eachItem((str & maxlength(10)) | None)

# parameterized validator
Range<start, end> = min(start) & max(end)

Nested<structure, default> = structure(default|structure)

PostCode = pattern("[A-Z0-9]{6}")  # naming is just this

NestedList = eachItem(str | NestedList)  # recursive definitions are allowed
# if not a primitive and appears on the right side of an expression it is a reference

NestedObject =
    properties(data: Any, children: eachItem(NestedObject)
    & required(data)
    & type(object)

NestedArray = eachItem(NestedArray|None)

Types of validators
- primitives validators - doesn't accept validator as argument
- compositive validators - accepts validators as arguments
- Reference

What are the other common validation use cases? Could also use this DSL to generate test data for property-based testing.

Use typescript typing system plus tweaks that allow for validation?
Inspired by typescript and F#

What things do I need? Define a BNF grammar - what are the tokens and the types?
How do I get editor support for this? Linting and autocompletion
"""
