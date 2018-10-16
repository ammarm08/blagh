import pytest
from blagh import lexer

class TestLexer(object):



    # Testing Open Tag Matching



    def test_advances_token(self):
        src = 'Some program'
        assert lexer.advance(src, 1) == 'ome program'
        assert lexer.advance(src, 2) == 'me program'

    def test_matches_opening_tag(self):
        src = '<test>there is more here'
        match = lexer.match_open_tag(src)
        assert match
        assert match.group(1) == 'test'

    def test_matches_opening_tag_with_attribute(self):
        src = '<test href="#">there is more here'
        match = lexer.match_open_tag(src)
        assert match
        assert match.group(1) == 'test'

    def test_matches_only_first_opening_tag(self):
        src = '<tag>this is my program</tag>\n<another>hi there</another>'
        match = lexer.match_open_tag(src)
        assert match
        assert match.group(1) == 'tag'

    def test_does_not_match_front_padded_opening_tag(self):
        src = ' <test>there is more here'
        match = lexer.match_open_tag(src)
        assert not match

    def test_does_not_match_open_tag_with_no_contents(self):
        src = '<>stuff'
        match = lexer.match_open_tag(src)
        assert not match

    def test_does_not_match_incomplete_open_tag(self):
        src = 'this is my program</tag>\n<another>hi there</another>'
        match = lexer.match_open_tag(src)
        assert not match



    # Testing Close Tag Matching



    def test_does_not_match_closing_tag_as_open_tag(self):
        src = '</tag>\n<another>hi there</another>'
        match = lexer.match_open_tag(src)
        assert not match

    def test_matches_close_tag_with_its_contents(self):
        src = 'my tag contents</tag>'
        tag_name = 'tag'
        match = lexer.match_close_tag(tag_name, src)
        assert match
        assert match.group(1) == 'my tag contents'
        assert match.group(2) == tag_name

    def test_does_not_match_unclosed_tag(self):
        src = 'my tag contents<tag>'
        tag_name = 'tag'
        match = lexer.match_close_tag(tag_name, src)
        assert not match



    # Testing Full Parsing



    def test_parses_a_full_well_formed_tag(self):
        src = '<tag>this is my program</tag>'
        tags = lexer.scan(src)
        assert tags
        assert 'tag' in tags
        assert tags['tag'] == 'this is my program'

    def test_parses_a_program_with_two_tags(self):
        src = '<tag>this is my program</tag>\n<another>hi there</another>'
        tags = lexer.scan(src)
        assert tags
        assert 'tag' in tags
        assert 'another' in tags
        assert tags['tag'] == 'this is my program'
        assert tags['another'] == 'hi there'

    def test_parses_a_program_with_nested_tags(self):
        src = """
        <globals>
        $display-title$ := On Jibber
        $title$ := An Essay on the Jibber Jabber
        $date$ := October 2018
        </globals>

        <macros>
        $conversation$ := <div>{}</div>
        </macros>

        <content>
        <p> My essay! Yay! </p>
        <conversation>
        <p> Great quote, sir. </p>
        <p> - Albert Einstein </p>
        </conversation>
        </content>
        """

        tags = lexer.scan(src)
        assert 'globals' in tags
        assert 'macros' in tags
        assert 'content' in tags
