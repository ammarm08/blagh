"""
Parses a blagh file.

Grammar:

program := tag*
tag :=
    "<" + "macros" + ">" + macro_content + "</" + "macros" + ">" ||
    "<" + "globals" + ">" + var_content + "</" + "globals" + ">" ||
    "<" + "variables" + ">" + var_content + "</" + "variables" + ">" ||
    "<" + "imports" + ">" + import_content + "</" + "imports" + ">" ||
    "<" + custom_tag + ">" + custom_content + "</" + custom_tag + ">"
custom_tag := STRING

macro_content := html_template*
var_content := var_assignment*
import_content := (var_name + NEWLINE)*
custom_content := STRING

var_assignment := var + STRING + NEWLINE
html_template := HTML_OPENING_TAG + [injectable or html_template] + HTML_CLOSING_TAG

injectable := "{}"
var := "$" + STRING + "$"
"""

import re
import logging


logger = logging.getLogger('Parser')


def parse_assignments(contents):
    """parses variable assignment: name := value \n"""
    # split on \n and := to parse assignments
    lines = contents.split('\n')
    assignments = [ re.sub(r'[\n\t]', '', x).split(':=') for x in lines ]

    # strip trailing whitespace. only keep pairs
    return [ [ pair[0].lstrip().rstrip(), pair[1].lstrip().rstrip() ] for pair in assignments if len(pair) == 2 ]


def validate_one_macro(name, value, macros):
    if value.find('{}') < 0:
        raise Exception('Macro "{macro}" needs a data placement point represented by braces'.format(macro=name))
    elif name in macros:
        raise Exception('Macro "{macro}" already in dict'.format(macro=name))

    return value


def validate_one_variable(name, value, variables):
    if name in variables:
        raise Exception('Variable "{v}" already in dict'.format(v=name))

    return value


def validate_macros(contents):
    """
    ensure macros have form [ name := <div> some macro {} </div> ],
    where the braces indicate placement of enclosing data
    """
    macros = {}
    assignments = parse_assignments(contents)

    for name,value in assignments:
        macros[name] = validate_one_macro(name, value, macros)

    return macros


def validate_variables(contents):
    variables = {}
    assignments = parse_assignments(contents)

    for name,value in assignments:
        variables[name] = validate_one_variable(name, value, variables)

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


def parse(tags={}):
    """
    Parses custom content tags into a dict
    """
    logger.info('parse() ->\n %s', repr(tags))

    ctx = {
        'macros': {},
        'globals': {},
        'variables': {},
        'custom_tags': {}
    }

    # parse tag contents
    for tag_name,tag_contents in tags.items():
        ctx = validate_and_parse_tag(ctx, tag_name, tag_contents)

    return ctx
