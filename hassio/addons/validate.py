"""Validate addons options schema."""
import voluptuous as vol

V_STR = 'str'
V_INT = 'int'
V_FLOAT = 'float'
V_BOOL = 'bool'


def validate_options(raw_schema):
    """Validate schema."""
    def validate(struct):
        """Create schema validator for addons options."""
        options = {}

        # read options
        for key, value in struct.items():
            if key not in raw_schema:
                raise vol.Invalid("Unknown options {}.".format(key))

            typ = raw_schema[key]
            try:
                if isinstance(typ, list):
                    # nested value
                    options[key] = _nested_validate(typ[0], value)
                else:
                    # normal value
                    options[key] = _single_validate(typ, value)
            except (IndexError, KeyError):
                raise vol.Invalid(
                    "Type error for {}.".format(key)) from None

        return options

    return validate


def _single_validate(typ, value):
    """Validate a single element."""
    try:
        if typ == V_STR:
            return str(value)
        elif typ == V_INT:
            return int(value)
        elif typ == V_FLOAT:
            return float(value)
        elif typ == V_BOOL:
            return vol.Boolean()(value)

        raise vol.Invalid("Fatal error for {}.".format(value))
    except TypeError:
        raise vol.Invalid(
            "Type {} error for {}.".format(typ, value)) from None


def _nested_validate(typ, data_list):
    """Validate nested items."""
    options = []

    for element in data_list:
        # dict list
        if isinstance(typ, dict):
            c_options = {}
            for c_key, c_value in element.items():
                if c_key not in typ:
                    raise vol.Invalid(
                        "Unknown nested options {}.".format(c_key))

                c_options[c_key] = _single_validate(typ[c_key], c_value)
            options.append(c_options)
        # normal list
        else:
            options.append(_single_validate(typ, element))

    return options
