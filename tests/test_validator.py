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
        self.assertEqual(obj.validate({'content': 'hello'}), None)
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'bananas'}))

    def test_integer(self):
        obj = JsonValidator({
            'content': {
                '#type': 'integer',
                '#max_value': 10000,
                '#min_value': -10000,
            },
        })
        self.assertEqual(obj.validate({'content': -123}), None)
        self.assertEqual(obj.validate({'content': 1234}), None)
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
        self.assertEqual(obj.validate({'content': -1.234}), None)
        self.assertEqual(obj.validate({'content': 1.234}), None)
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
        self.assertEqual(obj.validate({'content': {}}), None)
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'hello'}))

    def test_enum_list(self):
        obj = JsonValidator({
            'content': {
                '#type': 'enum',
                '#options': ['one','two'],
                '#default': 'one',
            },
        })
        self.assertEqual(obj.validate({'content': 'one'}), None)
        self.assertEqual(obj.validate({'content': 'two'}), None)
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
                },
            },
            'one': {'#type': 'placeholder'},
            'two': {'#type': 'placeholder' },
        })
        self.assertEqual(obj.validate({'type': 'one', 'one': { 'sub_one': 'something'}}), None)
        self.assertRaises(ValueError, lambda: obj.validate({'type': 'one', 'one': {}}))
        self.assertEqual(obj.validate({'type': 'two', 'two': {}}), None)
        self.assertRaises(ValueError, lambda: obj.validate({'type': 'one'}))

    def test_boolean(self):
        obj = JsonValidator({
            'content': {'#type': 'boolean' },
        })
        self.assertEqual(obj.validate({'content': True}), None)
        self.assertEqual(obj.validate({'content': False}), None)
        self.assertRaises(ValueError, lambda: obj.validate({'content': 0}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': 1}))
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'true'}))

    def test_string_validator(self):
        obj = JsonValidator({
            'content': {'#type': 'string', '#validator': 'hello_world'},
        })
        self.assertEqual(obj.validate({'content': 'hello world'}), None)
        self.assertRaises(ValueError, lambda: obj.validate({'content': 'goodbye'}))

    def test_string_required(self):
        obj = JsonValidator({
            'content': {'#type': 'string', '#required': True},
            'other': {"#type": 'string'}
        })
        self.assertEqual(obj.validate({'content': 'hello world'}), None)
        self.assertRaises(ValueError, lambda: obj.validate({'other': 'yes'}))
