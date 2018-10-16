"""
Expands variables and macros.

macro expansion := <macro-name> {} </macro-name
variable expansion := $variable$ value
"""

import re
import logging


logger = logging.getLogger('Expansion')
logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")


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
    return re.match('(<(.+)>).+', contents)


def match_macro_close(name, contents):
    """matches for a specific closing </{name}>"""
    return re.match('(.+)(<\/{name}>).?'.format(name=re.escape(name)), contents)


def getvarname(variable):
    """get varname from $varname$"""
    return variable[1:-1]


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
        memo = pipe(
                find_variable,
                expand_variable,
                advance_to_next_variable
                )(memo)

        logger.debug('expand_variables() -> %s', repr(memo))

    return memo['contents']



def expand_macros(macros, contents):
    """replaces all $macros$ in contents with their corresponding {} data"""

    # iteratively matches for <macro-name>{}</macro-name>, replaces with data,
    # then updates offset pointer until it exceeds length of contents
    offset = 0

    while offset < len(contents):
        macro_match = match_macro_open(contents[offset:])

        if macro_match is not None:
            macro_opener = macro_match.group(1)     # <$macro$>
            macro_name = macro_match.group(2)       # $macro$

            macro_close_match = match_macro_close(macro_name, contents[offset + len(macro_opener):])
            if macro_close_match is None:
                raise Exception('Expected closure of macro "%s" in contents "%s"', macro_name, contents[offset + len(macro_opener):])

            macro_content = macro_close_match.group(1)
            macro_closure = macro_close_match.group(2)

            # TODO: recursive expansion on macro_content to support nested macros
            # expanded_macro_content = expand_macros(macros, macro_content)

            # expand! <convo>{}</convo> becomes <div>your-content</div>
            data = macros[macro_name] if macro_name in macros else ''
            full_expansion = data.format(macro_content)

            # TODO: recurse: full expansion may yield nested expansions
            # expanded_expansion = expand_macros(macros, full_expansion)

            # replace old, unexpanded text with new, expanded text. increment offset accordingly
            unexpanded = macro_opener + macro_content + macro_closure
            contents = replace_variable(unexpanded, full_expansion, contents, offset)
            offset += len(full_expansion)

            logger.debug('expand_macros() -> Contents: %s, offset: %d, macro: %s, data: %s', contents, offset, macro_name, data)

        offset += 1

    return contents


def inject_data_into_content(ctx, contents):
    """injects variables then macros into contents"""
    contents = expand_variables(ctx['variables'], contents)
    contents = expand_macros(ctx['macros'], contents)
    return contents



def expand(ctx={}):
    """
    Handles variable and macro expansion into content tags.
    Input must be a dict of parsed macros, variables, globals,
    and custom content tags.
    """

    # inject macros and variables into custom content tags
    custom_tags = ctx['custom_tags']
    for tag_name,tag_contents in ctx['custom_tags'].items():
        custom_tags[tag_name] = inject_data_into_content(ctx, tag_contents)

    return ctx
