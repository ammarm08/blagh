import pytest
from blagh.parser import parser

class TestParser(object):



    # Macro and Variable Validation Tests



    def test_parses_single_variable_assignment(self):
        parsed = parser.parse_assignments('$key$ := value')
        assert repr(parsed) == repr([['$key$', 'value']])

    def test_parses_single_variable_assignment_with_whitespace(self):
        parsed = parser.parse_assignments('   $key$ :=  value')
        assert repr(parsed) == repr([['$key$', 'value']])

    def test_parses_single_variable_assignment_with_trailing_newline(self):
        parsed = parser.parse_assignments('$key$ := value  \n')
        assert repr(parsed) == repr([['$key$', 'value']])

    def test_parses_multi_assignment_with_varying_whitespace(self):
        src = '$key$ := value  \n $key2$:=value2 \t\n$key3$ := value3'
        expected = [['$key$', 'value'], ['$key2$', 'value2'], ['$key3$', 'value3']]

        parsed = parser.parse_assignments(src)
        assert repr(parsed) == repr(expected)

    def test_validates_valid_macros(self):
        src = '$convo$ := <div>{}</div>\n$block$ := <li>{}</li>'
        expected = { '$convo$': '<div>{}</div>', '$block$': '<li>{}</li>'}

        parsed = parser.validate_macros(src)
        assert repr(parsed) == repr(expected)

    def test_fails_for_macros_with_no_placement_point(self):
        src = '$convo$ := <div></div>\n$block$ := <li>{}</li>'

        try:
            parsed = parser.validate_macros(src)
        except Exception as e:
            assert e

    def test_fails_for_duplicate_macros(self):
        src = '$convo$ := <div>{}</div>\n$convo$ := <li>{}</li>'

        try:
            parsed = parser.validate_macros(src)
        except Exception as e:
            assert e

    def test_validates_valid_variables(self):
        src = '$convo$ := my-convo \n $test$ := my-test'
        expected = { '$convo$': 'my-convo', '$test$': 'my-test'}

        parsed = parser.validate_variables(src)
        assert repr(parsed) == repr(expected)

    def test_fails_for_duplicate_variables(self):
        src = '$convo$ := my-convo \n $convo$ := my-test'

        try:
            parsed = parser.validate_variables(src)
        except Exception as e:
            assert e

    def test_parses_valid_default_tag(self):
        ctx = { 'macros': {}, 'globals': {}, 'variables': {}, 'custom_tags': {} }

        macros = '$convo$ := <div>{}</div>\n$man$ := <li>{}</li>'
        globals = '$x$ := my-convo \n $y$ := my-test'
        variables = '$x$ := my-convo \n $y$ := my-test'

        assert 'macros' in parser.validate_and_parse_tag(ctx, 'macros', macros)
        assert 'globals' in parser.validate_and_parse_tag(ctx, 'globals', globals)
        assert 'variables' in parser.validate_and_parse_tag(ctx, 'variables', variables)

    def test_parses_custom_tag_correctly(self):
        ctx = { 'macros': {}, 'globals': {}, 'variables': {}, 'custom_tags': {} }
        custom = 'random text blob'

        res = parser.validate_and_parse_tag(ctx, 'foo', custom)
        assert 'custom_tags' in res
        assert 'foo' in res['custom_tags']
