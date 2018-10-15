import pytest
from blagh import parser

class TestParser(object):



    # Variable Matching/Parsing Tests



    def test_matches_valid_variable(self):
        match = parser.match_variable('$name$')
        assert match
        assert match.group(1) == '$name$'

    def test_does_not_match_empty_variable(self):
        match = parser.match_variable('$$')
        assert match is None

    def test_does_not_match_whitespace_before_variable(self):
        match = parser.match_variable(' $$')
        assert match is None

    def test_matches_valid_variable_without_pursuing_text(self):
        match = parser.match_variable('$name$stuff')
        assert match
        assert match.group(1) == '$name$'

    def test_removes_dollar_couching_from_string(self):
        assert parser.getvarname('$name$') == 'name'

    def test_matches_valid_macro(self):
        match = parser.match_macro('convo', '<convo> some stuff </convo>\n')
        assert match
        assert match.group(1) == '<convo> some stuff </convo>'
        assert match.group(2) == 'convo'
        assert match.group(3) == ' some stuff '

    def test_does_not_match_unclosed_macro(self):
        match = parser.match_macro('convo', '<convo> some stuff')
        assert match is None


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



    # Injection and Replacement Tests



    def test_replaces_variable_with_data_and_zero_offset(self):
        src = '$name$ is cool'
        data = 'Ammar'
        assert parser.replace_variable('$name$', data, src, 0) == 'Ammar is cool'

    def test_replaces_variable_with_data_and_nonzero_offset(self):
        src = '12345$name$ is cool'
        data = 'Ammar'
        offset = 5
        assert parser.replace_variable('$name$', data, src, offset) == '12345Ammar is cool'

    def test_injects_variable_data_into_string(self):
        variables = { '$convo$': 'my-convo', '$test$': 'my-test'}
        src = '<div> $convo$ </div> <li> $test$ </li> $end$'

        expected = '<div> my-convo </div> <li> my-test </li> '
        assert parser.inject_variables(variables, src) == expected

    def test_injects_variable_and_macro_data_into_string(self):
        src = '<div> $convo$ </div> <li> $test$ </li> $end$'
        pass
