import pytest
from blagh import compiler

class TestCompiler(object):



    # Compiler Tets

    def test_collects_substring_locations(self):
        src = 'aaaaabbbaaaaaaaaaaabbbaaaaabbb'
        expected = [5, 19, 27]
        actual = compiler.collect_substring_locations(src, 'bbb')
        assert repr(actual) == repr(expected)

    def test_does_not_collect_substrings_if_none_found(self):
        src = 'aaaaabbbaaaaaaaaaaabbbaaaaabbb'
        expected = []
        actual = compiler.collect_substring_locations(src, 'ccc')
        assert repr(actual) == repr(expected)

    def test_compiles_global_variables_from_dictionary(self):
        globals = {
            '$title$': 'My Blog',
            '$author$': 'Ammar'
        }

        src = '<title>$title$</title><h1>$author$</h1>'
        expected = '<title>My Blog</title><h1>Ammar</h1>'

        assert compiler.compile_globals(src, globals) == expected

    def test_does_not_compile_global_variables_not_found_in_dictionary(self):
        globals = {
            '$title$': 'My Blog',
            '$author$': 'Ammar'
        }

        src = '<title>$title$</title><h1>$author$ $date$</h1>'
        expected = '<title>My Blog</title><h1>Ammar $date$</h1>'

        assert compiler.compile_globals(src, globals) == expected

    def test_does_not_compile_global_variables_not_found_in_html(self):
        globals = {
            '$title$': 'My Blog',
            '$author$': 'Ammar'
        }

        src = '<title>$title$</title><h1></h1>'
        expected = '<title>My Blog</title><h1></h1>'

        assert compiler.compile_globals(src, globals) == expected

    def test_compiles_content_tags_from_dictionary(self):
        custom_tags = {
            'content': '<div>Hi</div>',
            'footer': '<footer>Peace</footer>'
        }

        src = '<title>My Blog</title><h1>Ammar</h1>$content$\n$footer$'
        expected = '<title>My Blog</title><h1>Ammar</h1><div>Hi</div>\n<footer>Peace</footer>'

        assert compiler.compile_content(src, custom_tags) == expected

    def test_does_not_compile_content_tags_not_found_in_dictionary(self):
        custom_tags = {
            'content': '<div>Hi</div>',
            'footer': '<footer>Peace</footer>'
        }

        src = '<title>My Blog</title><h1>$author$</h1>$content$\n$footer$'
        expected = '<title>My Blog</title><h1>$author$</h1><div>Hi</div>\n<footer>Peace</footer>'

        assert compiler.compile_content(src, custom_tags) == expected

    def test_does_not_compile_content_tags_not_found_in_html(self):
        custom_tags = {
            'content': '<div>Hi</div>',
            'footer': '<footer>Peace</footer>',
            'placeholder': '<li>test</li>'
        }

        src = '<title>My Blog</title><h1>Ammar</h1>$content$\n$footer$'
        expected = '<title>My Blog</title><h1>Ammar</h1><div>Hi</div>\n<footer>Peace</footer>'

        assert compiler.compile_content(src, custom_tags) == expected

    def test_compiles_full_valid_example(self):
        tags = {
            'globals' : {
                '$title$': 'My Blog',
                '$author$': 'Ammar'
            },
            'custom_tags' : {
                'content': '<div>Hi</div>',
                'footer': '<footer>Peace</footer>',
                'placeholder': '<li>test</li>'
            }
        }

        src = '<title>$title$</title><h1>$author$</h1>$content$\n$footer$'
        expected = '<title>My Blog</title><h1>Ammar</h1><div>Hi</div>\n<footer>Peace</footer>'

        assert compiler.compile(tags, src) == expected
