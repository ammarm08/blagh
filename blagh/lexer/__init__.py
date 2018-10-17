"""
Scans a blagh file into its content tags.
"""

import re
import logging


logger = logging.getLogger('Lexer')


def pipe(*args):
    """
    Returns a function that applies an initial value to a list of
    functions, returning the accumulated value.
    """
    def run(sentinel=0):
        for fn in args:
            sentinel = fn(sentinel)
        return sentinel

    return run


def advance(src, n):
    """returns a string truncated by n chars"""
    return src[n:]


def match_open_tag(src):
    """matches for any opening <{tag_name}>"""
    pattern = re.compile('<(\w+)[^>]*>.+', re.DOTALL)
    return pattern.match(src)


def match_close_tag(tag, src):
    """matches for a specific closing </{tag_name}>"""
    pattern = re.compile('(.+)<\/({tag})>.?'.format(tag=tag), re.DOTALL)
    return pattern.match(src)


def find_opening_tag(ctx):
    """wrapper for match_open_tag() that updates input ctx object"""

    # only advance 1 token if no opening tag found
    opening_tag_match = match_open_tag(ctx['source'])
    if opening_tag_match:
        ctx['current_tag'] = opening_tag_match.group(1)
        ctx['cursor_advance'] = len('<' + ctx['current_tag'] + '>')
    else:
        ctx['current_tag'] = None
        ctx['cursor_advance'] = 1

    return ctx


def find_closing_tag(ctx):
    """wrapper for match_close_tag() that updates input ctx object"""
    current_tag = ctx['current_tag']
    if current_tag is None:
        return ctx

    # match against substring that does not include the opening tag
    subset = ctx['source'][ctx['cursor_advance']:]
    closing_tag_match = match_close_tag(current_tag, subset)
    if not closing_tag_match or closing_tag_match.group(2) != current_tag:
        raise Exception('Improperly closed tag "{tag}" at location {loc} ("{str}")'.format(tag=current_tag, loc=ctx['cursor_advance'], str=ctx['contents'][ctx['cursor_advance':]]))

    # advance cursor by length of tag contents and closing tag
    ctx['tag_contents'] = closing_tag_match.group(1)
    ctx['cursor_advance'] += len(ctx['tag_contents']) + len('</' + current_tag + '>')

    return ctx


def add_tag_to_dict(ctx):
    """adds a tag and its content to the dict of tags in the input ctx object"""
    current_tag = ctx['current_tag']
    if current_tag is None:
        return ctx

    if current_tag in ctx['tags']:
        raise Exception('Tag "{tag}" already exists'.format(tag=current_tag))

    ctx['tags'][current_tag] = ctx['tag_contents']
    return ctx


def advance_to_next_tag(ctx):
    """wrapper for advance() that advances cursor based on input ctx object"""
    ctx['source'] = advance(ctx['source'], ctx['cursor_advance'])
    return ctx


def scan(program):
    """
    Scans a program and returns a dict of tag_name:tag_contents pairs
    """
    ctx = {
        'tags': {},
        'source': program[:],
        'current_tag': None,
        'tag_contents': None,
        'cursor_advance': 1
    }

    while len(ctx['source']) > 0:
        logger.info('scan() ->\n parsing ctx: %s', repr(( ctx['cursor_advance'], ctx['source'], ctx['current_tag'] )))

        # runs pipeline of functions in order, transforming ctx in the process
        ctx = pipe(
                find_opening_tag,
                find_closing_tag,
                add_tag_to_dict,
                advance_to_next_tag
                )(ctx)

    return ctx['tags']
