
class JsonValidator:
    def __init__(self, schema, attribute_errors = True):
        self.schema = schema
        self.debug_info = []
        self.attribute_errors = attribute_errors

    def get_debug_info(self):
        return self.debug_info

    #
    # Field Validators
    #
    def validate_hello_world(self, data, schema, subkeys):
        # This is an example. Ordinarily JsonValidator would be subclassed
        # and application-specific validators provided that way.
        if data != "hello world":
            raise ValueError("Hello world failed validation")

    #
    # Elements
    #
    def element_string(self, current, data, schema, subkeys):
        if not isinstance(data, (str, unicode)):
            raise ValueError("not a stringable (%s)" % (type(data)))
        if '#max_length' in schema:
            if len(str(data)) > schema['#max_length']:
                raise ValueError("%d characters long and exceeds maximum length %d" % (len(str(data)), schema['#max_length']))
        if '#min_length' in schema:
            if len(str(data)) < schema['#min_length']:
                raise ValueError("%d characters long and must be at least %d long" % (len(str(data)), schema['#min_length']))


    def element_enum(self, current, data, schema, subkeys):
        if isinstance(schema['#options'], list):
            # just make sure the data is in the list
            if data not in schema['#options']:
                raise ValueError("'%s' is not a valid value" % (data))
        elif isinstance(schema['#options'] ,dict):
            possibles = schema['#options'].keys()
            if data in possibles:
                # Ensure data has the same key as the option
                if data not in current:
                    raise ValueError("%s is a required key when '%s' is set to option '%s'" % ('.'.join(subkeys[:-1] + [data]), '.'.join(subkeys), data))
                # Recurse into the key to ensure dependencies are correct
                # Note: data is 'below' the chunks we want, so we have to use current to get to them
                # also note that the data differs from the structure of the schema at this point
                # because the data doesn't include an extra level, whereas the schema does
                self.recurse(current[data], schema['#options'][data], subkeys[:-1] + [data])
            else:
                raise ValueError("'%s' is not a valid value" % (data))
        else:
            self.debug_info.append("No way to parse element enum with type '%s'" % (type(schema['#options'])))

    def element_fieldset(self, current, data, schema, subkeys):
        if not isinstance(data, dict):
            raise ValueError("Fieldset is not an associative array" )
        self.recurse(data, schema, subkeys)

    def element_boolean(self, current, data, schema, subkeys):
        if not isinstance(data, bool):
            raise ValueError("not a boolean")

    def _element_any_number(self, current, data, schema, subkeys):
        if '#max_value' in schema:
            if data > schema['#max_value']:
                raise ValueError("value is larger than %d" % (schema['#max_value']))
        if '#min_value' in schema:
            if data < schema['#min_value']:
                raise ValueError("value is smaller than %d" % (schema['#min_value']))

    def element_integer(self, current, data, schema, subkeys):
        if not isinstance(data, (int,long)):
            raise ValueError("not an integer")
        self._element_any_number(current, data, schema, subkeys)

    def element_float(self, current, data, schema, subkeys):
        if not isinstance(data, float):
            raise ValueError("not a float")
        self._element_any_number(current, data, schema, subkeys)
    #
    # Main methods
    #
    def recurse(self, data, schema, subkeys):
        global handle
        if type(data) is not dict:
            raise ValueError("'%s' is not an associative array" % ('.'.join(subkeys)))
        # Look for anything that is mandatory at this level in the hierarchy
        for item in schema.keys():
            if type(schema[item]) is dict and '#required' in schema[item]:
                if item not in data:
                    raise ValueError("'%s' is a required key" % ('.'.join(subkeys + [item])))

        for item in data.keys():
            thing = subkeys + [item]
            if item not in schema:
                raise ValueError("%s is not known" % ('.'.join(thing)))
            if schema[item]['#type'] == 'placeholder':
                # Ignore this item for now - it's defined somewhere else
                # and will be checked when we recurse into it later
                continue
            else:
                try:
                    handle = getattr(self, "element_%s" % (schema[item]['#type']))
                except AttributeError:
                    if self.attribute_errors:
                        raise AttributeError("No way to parse element %s for item %s" % (schema[item]['#type'], '.'.join(thing)))
                    self.debug_info.append("No way to parse element %s for item %s" % (schema[item]['#type'], '.'.join(thing)))
                try:
                    handle(data, data[item], schema[item], subkeys + [item])
                except ValueError as e:
                    raise ValueError("%s: %s" % ('.'.join(thing), e))
                # Having parsed the specific element attributes, now check #validator
                if '#validator' in schema[item]:
                    try:
                        handle = getattr(self, "validate_%s" % (schema[item]['#validator']))
                    except AttributeError:
                        if self.attribute_errors:
                            raise AttributeError("No validator '%s' for item %s" % (schema[item]['#validator'], '.'.join(thing)))
                        self.debug_info.append("No validator '%s' for item %s" % (schema[item]['#validator'], '.'.join(thing)))
                    handle(data[item], schema[item], subkeys + [item])

    def validate(self, data):
        self.recurse(data, self.schema, [])
