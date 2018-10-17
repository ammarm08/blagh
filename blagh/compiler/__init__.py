"""
Compiles a parsed context dictionary into the supplied
html file.
"""

import re
import logging

logger = logging.getLogger('Compiler')


def replace_variable(old, new, target, offset):
    """replace old substring with new substring in target string at offset"""
    return target[:offset] + new + target[offset + len(old):]


def getvarname(variable):
    """get $varname$ from varname"""
    return '$' + variable + '$'


def collect_substring_locations(html, substring):
    """return indexes of all instances of a substring in an html string"""

    locations = []
    last_found = html.find(substring)

    while last_found > 0:
        locations.append(last_found)
        last_found = html.find(substring, last_found + 1)

    return locations


def compile_variables(html, variables):
    """injects $variables$ into appropriate spots in html"""
    for varname, value in variables.items():
        locations = collect_substring_locations(html, varname)
        for loc in locations:
            html = replace_variable(varname, value, html, loc)

    return html


def compile_globals(html, globals):
    """injects global variables into appropriate spots in html"""
    return compile_variables(html, globals)


def compile_content(html, custom_tags):
    """injects custom tags into appropriate spots in html"""

    # couch tag names with $ (because that's how they appear in html)
    tags = { getvarname(k):v for k, v in custom_tags.items() }
    return compile_variables(html, tags)


def compile(tags={}, html=''):
    """
    Compiles an html string from a template html,
    injecting global variables and content sections
    as necessary
    """
    logging.info('compile() ->\n tags: %s\nhtml: %s', repr(tags), html)

    html = compile_globals(html, tags['globals'])
    html = compile_content(html, tags['custom_tags'])
    return html
