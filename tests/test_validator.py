import unittest

from jsonvalidator import JsonValidator

class TestValidator(unittest.TestCase):
    def test_string(self):
        obj = JsonValidator({
            'content': {
                '#type': 'string',
                '#max_length': 5,
            },    
        })
        self.assertRaises(ValueError, lambda: obj.validate({'content': 123}))
        self.assertDictEqual(obj.validate({'content': 'hello'}), {'content': 'hello'})
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'bananas'}))

    def test_integer(self):
        obj = JsonValidator({
            'content': {
                '#type': 'integer',
                '#max_value': 10000,
                '#min_value': -10000,
            },
        })
        self.assertDictEqual(obj.validate({'content': -123}), {'content': -123})
        self.assertDictEqual(obj.validate({'content': 1234}), {'content': 1234})
        self.assertRaises(ValueError, lambda: obj.validate({'content': 1.2345}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'hello'}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': 10001}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': -10001}))

    def test_float(self):
        obj = JsonValidator({
            'content': {
                '#type': 'float',
                '#max_value': 10000.0,
                '#min_value': -10000.0,
            },
        })
        self.assertDictEqual(obj.validate({'content': -1.234}), {'content': -1.234})
        self.assertDictEqual(obj.validate({'content': 1.234}), {'content': 1.234})
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'hello'}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': 10001.0}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': -10001.0}))

    def test_fieldset(self):
        obj = JsonValidator({
            'content': {
                '#type': 'fieldset',
                '#collapsible': True,
                '#collapsed': False,
                '#weight': -10,
            },
        })
        self.assertDictEqual(obj.validate({'content': {}}), {'content': {}})
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'hello'}))

    def test_enum_list(self):
        obj = JsonValidator({
            'content': {
                '#type': 'enum',
                '#options': ['one','two'],
                '#default': 'one',
            },
        })
        self.assertDictEqual(obj.validate({'content': 'one'}), {'content': 'one'})
        self.assertDictEqual(obj.validate({'content': 'two'}), {'content': 'two'})
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'three'}))


    def test_enum_dict(self):
        obj = JsonValidator({
            'type': {
                '#type': 'enum',
                '#default': 'one',
                '#options': {
                    'one': {
                        'sub_one': {
                            '#type': 'string',
                            '#max_length': 200,
                            '#required': True,
                        },
                    },
                    'two': {
                        'sub_two_string': {
                            '#type': 'string',
                            '#max_length': 255,
                        },
                        'sub_two_integer': {
                            '#type': 'string',
                            '#max_length': 20,
                        },
                    },
                    'three': {
                        'thing': {
                            '#type': 'string',
                            '#default': 'someday',
                        },
                    },
                },
            },
            'one': {'#type': 'placeholder'},
            'two': {'#type': 'placeholder' },
        })
        thing = {'type': 'one', 'one': { 'sub_one': 'something'}}
        self.assertDictEqual(obj.validate(thing), thing)
        self.assertRaises(ValueError, lambda: obj.validate({'type': 'one', 'one': {}}))
        self.assertDictEqual(obj.validate({'type': 'two', 'two': {}}), {'type': 'two', 'two': {}})
        self.assertRaises(ValueError, lambda: obj.validate({'type': 'one'}))

        # This can't happen because 'three' becomes a required key
        # TODO: let 'three' be optional, with default or #required key
        #self.assertDictEqual(obj.validate({'type':'three'}), {'type': 'three', 'thing': 'someday'})

    def test_boolean(self):
        obj = JsonValidator({
            'content': {'#type': 'boolean' },
        })
        self.assertDictEqual(obj.validate({'content': True}), {'content': True})
        self.assertDictEqual(obj.validate({'content': False}), {'content': False})
        self.assertRaises(ValueError, lambda: obj.validate({'content': 0}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': 1}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'true'}))

    def test_string_validator(self):
        obj = JsonValidator({
            'content': {'#type': 'string', '#validator': 'hello_world'},
        })
        self.assertDictEqual(obj.validate({'content': 'hello world'}), {'content': 'hello world'})
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'goodbye'}))

    def test_string_required(self):
        obj = JsonValidator({
            'content': {'#type': 'string', '#required': True},
            'other': {"#type": 'string'}
        })
        self.assertDictEqual(obj.validate({'content': 'hello world'}), {'content': 'hello world'})
        self.assertRaises(ValueError, lambda: obj.validate({'other': 'yes'}))

    def test_string_default(self):
        obj = JsonValidator({
            'content': {'#type': 'string', '#default': 'banana'},
        })
        try:
            obj.validate({})
        except ValueError as e:
            self.fail("validate() threw exception: %s" % (e))