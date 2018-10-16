"""
Expands variables and macros.

macro expansion := <macro-name> {} </macro-name
variable expansion := $variable$ value
"""

import re
import logging


logger = logging.getLogger('Expansion')
logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")


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




def expand_variables(variables, contents):
    """replaces all $variables$ in contents with their corresponding data"""

    # iteratively matches for $variable-name$, replaces with data,
    # then updates offset pointer until it exceeds length of contents
    offset = 0

    while offset < len(contents):
        varmatch = match_variable(contents[offset:])

        if varmatch is not None:
            varname = varmatch.group(1)
            data = variables[varname] if varname in variables else ''

            # replace $title$ with data (such as "My Blog Title")
            contents = replace_variable(varname, data, contents, offset)
            offset += len(data)

            logger.debug('expand_variables() -> Contents: %s, offset: %d, var: %s, data: %s', contents, offset, varname, data)

        offset += 1

    return contents



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
    Handles variable and macro expansion into content tags
    """

    # inject macros and variables into custom content tags
    custom_tags = ctx['custom_tags']
    for tag_name,tag_contents in ctx['custom_tags'].items():
        custom_tags[tag_name] = inject_data_into_content(ctx, tag_contents)

    return ctx
