# json-validator

Ensure some arbitrary data matches a given schema. Despite it's name, this package
can check any Python data structure and not just Json. It was developed to validate
Json POSTed to a web service, but finds uses in lots of places where it's safer or
easier to ensure the data is correct before attempting to process it.

The validator can ensure nested elements are of the correct (Python) data type and
can perform simple bounds checking (such as max/min value, max/min length etc).

If subclassed, additional methods can be used to create new data types (for example,
'email_address', or 'ip_address'). Additionally, 'validator' methods can also be
created to ensure that values conform to more complex rules than otherwise possible
(for example, ensure an email address is in a certain domain, or ensuring an IP
address is within a certain range, a password meets complexity requirements, etc.).

# Example

```
from jsonvalidator import JsonValidator

schema = {
  'content': {
    '#type': 'string',
    '#max_length': 15,
  },
}

good_data = {
  'content': 'hello world',
}

naughty_data = {
  'content': 'much, much too long',
}

v = JsonValidator(schema)

try:
  v.validate(good_data)
except ValueError as e:
  print "Never gonna happen: %s" % (e)

try:
  v.validate(naughty_data)
except ValueError as e:
  print "Failed to validate: %s" % (e)
```

The `validate()` method will raise `ValueError` for:
- Any element present in the data that is not in the schema
- Any mandatory (`#required`) elements are not present in the data
- Any value is not of the correct element type
- Any value does not conform to the element contraints (`#max_length`,
`#min_length`, `#max_value',`#min_value` etc)
- Any value fails the 'validator' method's enhanced checks
- The supplied data is not an associative array (dict)

Additionally, it will raise `AttributeError`, unless told not to
(eg. `v = JsonValidator(schema, False)`) for:
- Any unknown element type (as defined in the schema)
- Any unknown 'validator' method (as defined in the schema)

If `AttributeError` exceptions are turned off, then an additional method called
`get_debug_info()` can be called and will return a list of issues that would
otherwise have caused an `AttributeError` but were otherwise ignored.

## Subclassing

By subclassing `JsonValidator` and adding in methods, it's possible to
create data types or perform complex value validation. This is an example
of a custom data type:

```
def element_sentence(self, current, data, schema, subkeys):
    # Ensure it's a string
    self.element_string(current,data,schema,subkeys)

    if ' ' not in data:
        raise ValueError("not a sentence")

```

This is an example of a validator method which ensures the data is always
a string equal to 'hello world':

```
def validate_hello_world(self, data, schema, subkeys):
    if data != "hello world":
        raise ValueError("Hello world failed validation")
```
