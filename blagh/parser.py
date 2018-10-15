"""
Parses a blagh file.

Grammar:

program := block*
block :=
    "<" + "macros" + ">" + macro_content + "</" + "macros" + ">" ||
    "<" + "globals" + ">" + var_content + "</" + "globals" + ">" ||
    "<" + "variables" + ">" + var_content + "</" + "variables" + ">" ||
    "<" + "imports" + ">" + import_content + "</" + "imports" + ">" ||
    "<" + custom_block + ">" + custom_content + "</" + custom_block + ">"
custom_block := STRING

macro_content := html_template*
var_content := var_assignment*
import_content := (var_name + NEWLINE)*
custom_content := STRING

var_assignment := var + STRING + NEWLINE
html_template := HTML_OPENING_TAG + injectable || html_template + HTML_CLOSING_TAG

injectable := "{}"
var := "$" + STRING + "$"
"""

import re
import logging


logger = logging.getLogger('Parser')
logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")


def match_variable(contents):
    return re.match('(\$\w+\$)', contents)


def match_macro(macro_name, contents):
    return re.match('(<({macro})>(.+)<\/({macro})>).?'.format(macro=macro_name), contents)


def getvarname(variable):
    """get varname from $varname$"""
    return variable[1:-1]


def parse_assignments(contents):
    """parses variable assignment: name := value \n"""
    # split on \n and := to parse assignments
    lines = contents.split('\n')
    assignments = map(lambda x: re.sub(r'\s+', '', x).split(':='), lines)

    # only keep pairs!
    return filter(lambda x: len(x) == 2, assignments)


def validate_macros(contents):
    """
    ensure macros have form [ name := <div> some macro {} </div> ],
    where the braces indicate placement of enclosing data
    """
    macros = {}
    assignments = parse_assignments(contents)

    for name,value in assignments:
        if value.find('{}') < 0:
            raise Exception('Macro "{macro}" needs a data placement point represented by braces'.format(macro=name))
        elif name in macros:
            raise Exception('Macro "{macro}" already in dict'.format(macro=name))

        macros[name] = value

    return macros


def validate_variables(contents):
    variables = {}
    assignments = parse_assignments(contents)

    for name,value in assignments:
        if name in variables:
            raise Exception('Variable "{v}" already in dict'.format(v=name))
        variables[name] = value

    return variables


def validate_and_parse_tag(ctx, name, contents):
    """ensure tag is valid, then parse its contents"""
    if name == 'macros':
        ctx['macros'] = validate_macros(contents)
    elif name in ['globals', 'variables']:
        ctx[name] = validate_variables(contents)
    else:
        ctx['custom_tags'][name] = contents

    return ctx


def replace_variable(name, data, contents, offset):
    """removes name from offset and replaces it with data"""
    return contents[:offset] + data + contents[offset + len(name):]


def inject_variables(variables, contents):
    """replaces all $variables$ in contents with their corresponding data"""

    # iteratively matches for $variable-name$, replaces with data,
    # then updates offset pointer until it exceeds length of contents
    offset = 0

    while offset < len(contents):
        varmatch = match_variable(contents[offset:])

        if varmatch is not None:
            varname = varmatch.group(1)
            data = variables[varname] if varname in variables else ''

            contents = replace_variable(varname, data, contents, offset)
            offset += len(data)

            logger.debug('inject_variables() -> Contents: %s, offset: %d, var: %s, data: %s', contents, offset, varname, data)

        offset += 1

    return contents



def inject_macros(macros, contents):
    """replaces all $macros$ in contents with their corresponding {} data"""

    # iteratively matches for <macro-name>{}</macro-name>, replaces with data,
    # then updates offset pointer until it exceeds length of contents
    offset = 0

    """
    Gameplan:

    
    """

    # while offset < len(contents):
    #     # is there any match with any macros? <macro> content </macro>
    #     macro_matches = [match for match in (match_macro(getvarname(m), contents[offset:]) for m in macros) if match is not None]
    #     macro_match = macro_matches[0] if len(macro_matches) > 0 else None
    #
    #     if macro_match is not None:
    #         # gather captured groups
    #         full_tag = macro_match.groups(1)
    #         macroname = macro_match.groups(2)
    #         macrocontent = macro_match.groups(3)
    #
    #         # replace {} with desired data
    #         data = macros[macroname] if macroname in macros else ''
    #         data = re.sub('{}', full_tag, data)
    #
    #         # finally, replace macros with proper values
    #         replace_me = '<' + macroname + '>' +
    #         contents = replace_variable(macroname, data, contents, offset)
    #         offset += len(data)
    #
    #         logger.debug('inject_macros() -> Contents: %s, offset: %d, var: %s, data: %s', contents, offset, macroname, data)
    #
    #     offset += 1
    #
    # return contents


def inject_data_into_content(ctx, contents):
    """injects variables then macros into contents"""
    contents = inject_variables(ctx['variables'], contents)
    contents = inject_macros(ctx['macros'], contents)
    return contents



def parse(tags={}):
    """
    Parses custom content tags, injecting in variables and macros
    into them as necessary.
    """

    ctx = {
        'macros': {},
        'globals': {},
        'variables': {},
        'custom_tags': {}
    }

    # parse tag contents
    for tag_name,tag_contents in tags.items():
        ctx = validate_and_parse_tag(ctx, tag_name, tag_contents)

    # inject macros and variables into custom content tags
    custom_tags = ctx['custom_tags']
    for tag_name,tag_contents in ctx['custom_tags'].items():
        custom_tags[tag_name] = inject_data_into_content(ctx, tag_contents)

    return ctx
