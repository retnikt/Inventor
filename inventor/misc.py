from flask import request
from inventor import TYPE_FUNCS, app, InvalidUserSuppliedValue


def get_new_entity_values(fields, types):
    new = {}
    for key, value in request.form.items():
        # unknown field
        if not key.startswith("field_") or key[6:] not in fields:
            continue
        func = TYPE_FUNCS.get(dict(zip(fields, types))[key[6:]], str)
        try:
            new_value = func(value)
        # user provided an invalid value
        except Exception as e:
            if app.debug:
                raise
            else:
                raise InvalidUserSuppliedValue(key, value, e)
        new[key[6:]] = new_value
    return new
