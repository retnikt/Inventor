from . import InvalidUserSuppliedValue
import re


def contains(value):
    def apply(item):
        return value in item
    return apply


def regex(value):
    try:
        pattern = re.compile(value)
    except re.error as e:
        # invalid regular expression
        raise InvalidUserSuppliedValue(e, msg="Invalid regular expression: " + e.args[0])

    return pattern.match
