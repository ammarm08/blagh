"""
Expands variables and macros.

macro expansion := <macro-name> {} </macro-name
variable expansion := $variable$ value
"""

import re
import logging


logger = logging.getLogger('Expansion')


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


def match_variable(contents):
    return re.match('(\$\w+\$)', contents)


def match_macro_open(contents):
    """matches for any opening <{tag_name}>"""
    pattern = re.compile('<(\w+)>.+', re.DOTALL)
    return pattern.match(contents)


def match_macro_close(name, contents):
    """matches for a specific closing </{name}>"""
    pattern = re.compile('(.+)<\/({name})>.?'.format(name=name), re.DOTALL)
    return pattern.match(contents)

def getvarname(variable):
    """get $varname$ from varname"""
    return '$' + variable + '$'


def replace_variable(name, data, contents, offset):
    """removes name from offset and replaces it with data"""
    return contents[:offset] + data + contents[offset + len(name):]


def find_variable(ctx):
    """wrapper for match_variable() that updates ctx object"""
    contents = ctx['contents']
    offset = ctx['offset']

    varmatch = match_variable(contents[offset:])
    if varmatch:
        ctx['current_variable'] = varmatch.group(1)
    else:
        ctx['current_variable'] = None

    return ctx


def expand_variable(ctx):
    """if variable found, look up its expansion content and inject into contents"""

    current_variable = ctx['current_variable']
    variables = ctx['variables']
    contents = ctx['contents']
    offset = ctx['offset']

    if current_variable is None:
        ctx['expanded_variable'] = None
    else:
        ctx['expanded_variable'] = variables[current_variable] if current_variable in variables else ''
        ctx['contents'] = replace_variable(current_variable, ctx['expanded_variable'], contents, offset)

    return ctx


def advance_to_next_variable(ctx):
    """adjust offset by injected data's length or by 1 if no match found"""
    if ctx['expanded_variable'] is not None:
        ctx['offset'] += len(ctx['expanded_variable']) + 1
    else:
        ctx['offset'] += 1

    return ctx


def expand_variables(variables, contents):
    """replaces all $variables$ in contents with their corresponding data"""

    memo = {
        'offset': 0,
        'current_variable': None,
        'expanded_variable': None,
        'contents': contents,
        'variables': variables
    }

    while memo['offset'] < len(contents):
        logger.debug('expand_variables() ->\n %s', repr(memo))

        memo = pipe(
                find_variable,
                expand_variable,
                advance_to_next_variable
                )(memo)

    return memo['contents']


def find_opening_macro_tag(ctx):
    """wrapper for match_macro_open() that updates ctx object"""
    contents = ctx['contents']
    offset = ctx['offset']

    macromatch = match_macro_open(contents[offset:])
    if macromatch is None:
        ctx['current_macro'] = None
        return ctx

    macro_name = macromatch.group(1)
    if getvarname(macro_name) in ctx['macros']:
        ctx['current_macro'] = macro_name
    else:
        ctx['current_macro'] = None

    return ctx


def find_closing_macro_tag(ctx):
    """wrapper for match_macro_close() that updates ctx object"""

    current_macro = ctx['current_macro']
    if current_macro is None:
        return ctx

    # find the current macro's required closing tag (find the subset beyond opening tag)
    subset = ctx['contents'][ctx['offset'] + len('<' + current_macro + '>'):]

    macro_close_match = match_macro_close(current_macro, subset)
    if not macro_close_match or macro_close_match.group(2) != current_macro:
        raise Exception('Improperly closed macro "{macro}"'.format(macro=current_macro))

    # update ctx with the actual content that will be injected in the expanded macro.
    ctx['content_to_inject'] = macro_close_match.group(1)

    return ctx


def expand_macro(ctx):
    """looks up macro in macros table, injects desired content, then performs macro expansion"""

    macros = ctx['macros']
    current_macro = ctx['current_macro']
    content_to_inject = ctx['content_to_inject']
    contents = ctx['contents']
    offset = ctx['offset']


    if current_macro is None:
        ctx['macro_expansion'] = None
        return ctx

    # call expand_macros() in case this injected data can itself be expanded
    # example: "<foo> this </foo>" where foo is a macro
    fully_expanded_content_to_inject = expand_macros(macros, content_to_inject.lstrip().rstrip())

    # macro_expansion looks like "<div> {} <div>", which means
    # we can directly use Python string interpolation

    key = getvarname(current_macro)
    target = macros[key] if key in macros else ''

    # call expand_macros() in case the TARGET data is not fully expanded.
    # example: the key "$convo$" might point to a target "<foo>{}</foo>" where foo is another macro
    fully_expanded_target = expand_macros(macros, target.lstrip().rstrip())

    ctx['macro_expansion'] = fully_expanded_target.format(fully_expanded_content_to_inject)
    content_to_replace = '<' + current_macro + '>' + content_to_inject + '</' + current_macro + '>'

    # now that we've built up the fully expanded macro, time to replace the old content

    ctx['contents'] = replace_variable(content_to_replace, ctx['macro_expansion'], contents, offset)

    return ctx


def advance_to_next_macro(ctx):
    """advances offset so we can continue expanding macros we encounter"""
    if ctx['macro_expansion'] is None:
        ctx['offset'] += 1
    else:
        new_offset = len(ctx['macro_expansion'])
        ctx['offset'] += new_offset

    # reset some context variables
    ctx['current_macro'] = ctx['content_to_inject'] = ctx['macro_expansion'] = None

    return ctx



def expand_macros(macros, contents):
    """replaces all $macros$ in contents with their corresponding {} data"""

    memo = {
        'offset': 0,
        'current_macro': None,
        'content_to_inject': None,
        'macro_expansion': None,
        'contents': contents,
        'macros': macros
    }

    while memo['offset'] < len(contents):
        logger.debug('expand_macros() ->\n %s', repr(memo))

        memo = pipe(
                find_opening_macro_tag,
                find_closing_macro_tag,
                expand_macro,
                advance_to_next_macro
                )(memo)

    return memo['contents']


def inject_data_into_content(ctx, contents):
    """injects variables then macros into contents"""
    contents = re.sub('\s+', ' ', contents)
    contents = expand_variables(ctx['variables'], contents)
    contents = expand_macros(ctx['macros'], contents)
    return contents



def expand(ctx={}):
    """
    Handles variable and macro expansion into content tags.
    Input must be a dict of parsed macros, variables, globals,
    and custom content tags.
    """
    logger.debug('expand() ->\n%s', repr(ctx))

    # inject macros and variables into custom content tags
    custom_tags = ctx['custom_tags']
    for tag_name,tag_contents in ctx['custom_tags'].items():
        custom_tags[tag_name] = inject_data_into_content(ctx, tag_contents)

    return ctx
