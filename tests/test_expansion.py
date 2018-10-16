import pytest
from blagh.parser import expansion

class TestParser(object):



    # Variable Matching/Parsing Tests



    def test_matches_valid_variable(self):
        match = expansion.match_variable('$name$')
        assert match
        assert match.group(1) == '$name$'

    def test_does_not_match_empty_variable(self):
        match = expansion.match_variable('$$')
        assert match is None

    def test_does_not_match_whitespace_before_variable(self):
        match = expansion.match_variable(' $$')
        assert match is None

    def test_matches_valid_variable_without_pursuing_text(self):
        match = expansion.match_variable('$name$stuff')
        assert match
        assert match.group(1) == '$name$'

    def test_adds_dollar_couching_to_string(self):
        assert expansion.getvarname('name') == '$name$'

    def test_matches_valid_macro_opening(self):
        match = expansion.match_macro_open('<convo> some stuff </convo>\n')
        assert match
        assert match.group(1) == 'convo'

    def test_does_not_match_valid_macro_opening(self):
        match = expansion.match_macro_open(' <convo> some stuff </convo>\n')
        assert match is None

    def test_matches_valid_macro_closing(self):
        match = expansion.match_macro_close('convo', 'foofoofoo</convo>\n')
        assert match
        assert match.group(1) == 'foofoofoo'
        assert match.group(2) == 'convo'

    def test_does_not_match_unclosed_macro(self):
        match = expansion.match_macro_close('convo', 'some stuff</notconvo>')
        assert match is None



    # Injection and Replacement Tests



    def test_replaces_variable_with_data_and_zero_offset(self):
        src = '$name$ is cool'
        data = 'Ammar'
        assert expansion.replace_variable('$name$', data, src, 0) == 'Ammar is cool'

    def test_replaces_variable_with_data_and_nonzero_offset(self):
        src = '12345$name$ is cool'
        data = 'Ammar'
        offset = 5
        assert expansion.replace_variable('$name$', data, src, offset) == '12345Ammar is cool'

    def test_expands_variable_data_into_string(self):
        variables = { '$convo$': 'my-convo', '$test$': 'my-test'}
        src = '<div> $convo$ </div> <li> $test$ </li> $end$'

        expected = '<div> my-convo </div> <li> my-test </li> '
        assert expansion.expand_variables(variables, src) == expected

    def test_expands_macro_data_into_string(self):
        macros = { '$conversation$': '<li>{}</li>' }
        src = '<conversation>what</conversation>'

        expected = '<li>what</li>'
        assert expansion.expand_macros(macros, src) == expected

    def test_expands_multiple_macros_into_string(self):
        macros = { '$conversation$': '<li>{}</li>', '$foo$': '<p>{}</p>' }
        src = '<conversation>what</conversation><foo>is this</foo>'

        expected = '<li>what</li><p>is this</p>'
        assert expansion.expand_macros(macros, src) == expected

    def test_expands_multiple_macros_into_string_recursively_from_src(self):
        macros = { '$conversation$': '<li>{}</li>', '$foo$': '<p>{}</p>' }
        src = '<conversation><foo>is this</foo></conversation>'

        expected = '<li><p>is this</p></li>'
        assert expansion.expand_macros(macros, src) == expected

    def test_expands_multiple_macros_into_string_recursively_from_macro(self):
        macros = { '$conversation$': '<li><foo>{}</foo></li>', '$foo$': '<p>{}</p>' }
        src = '<conversation>is this</conversation>'

        expected = '<li><p>is this</p></li>'
        assert expansion.expand_macros(macros, src) == expected

    def test_full_variable_and_macro_expansion_on_one_content_tag(self):
        tags = {
            'variables': {
                '$title$': 'My Blog',
                '$author$': 'Ammar'
            },
            'macros': {
                '$conversation$': '<li><foo>{}</foo></li>',
                '$foo$': '<p>{}</p>',
                '$true$': '<ul>{}</ul>'
            }
        }

        src = """$title$, by $author$
        <true>
        <conversation>
        Yo
        </conversation>
        </true>"""

        expected = 'My Blog, by Ammar <ul><li><p>Yo</p></li></ul>'
        assert expansion.inject_data_into_content(tags, src) == expected

    def test_full_variable_and_macro_expansion_on_multiple_content_tags(self):
        src = """$title$, by $author$
        <true>
        <conversation>
        Yo
        </conversation>
        </true>"""

        footer = '<true><li>$author$</li></true>'


        tags = {
            'variables': {
                '$title$': 'My Blog',
                '$author$': 'Ammar'
            },
            'macros': {
                '$conversation$': '<li><foo>{}</foo></li>',
                '$foo$': '<p>{}</p>',
                '$true$': '<ul>{}</ul>'
            },
            'custom_tags': {
                'content': src,
                'footer': footer
            }
        }



        expected_1 = 'My Blog, by Ammar <ul><li><p>Yo</p></li></ul>'
        expected_2 = '<ul><li>Ammar</li></ul>'

        ctx = expansion.expand(tags)
        assert ctx
        assert 'custom_tags' in ctx
        assert 'content' in ctx['custom_tags']
        assert 'footer' in ctx['custom_tags']

        assert ctx['custom_tags']['content'] == expected_1
        assert ctx['custom_tags']['footer'] == expected_2
