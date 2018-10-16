#!/usr/bin/env python

"""
Template engine for my Github Pages blog posts.
Usage: blagh -f <file> -t <template>

It will create a folder and an index.html for the post, using
a template html and a json file to compile the post.

Template Rules:
- Must be valid HTML EXCEPT for injectable properties
- Injectable properties look like $name$ (dollar-sign-couched)

File Rules:
- File must follow the minimal rules in the README (github.com/ammarm08/blagh)
"""

import lexer, parser, expansion, compiler

import os
import re
import argparse
import logging

# set up basic debugging logger

LOGGER = logging.getLogger("[BLAGH]")



def load_file(filename):
    """open() + read() wrapper"""
    try:
        with open(filename) as f:
            return f.read()
    except Exception as e:
        LOGGER.warn("load_file() -> error loading file from %s", filename)
        raise e


def create_directory(dirname):
    try:
        os.mkdir(dirname)
    except OSError as e:
        LOGGER.warn("create_directory() -> error creating dir %s", dirname)
        raise e


def write_file(path, contents):
    try:
        with open(path, "w+") as f:
            f.write(contents)
    except Exception as e:
        LOGGER.warn("write_file() -> error creating file %s", path)
        raise e


def sluggify(title):
    """creates a slug from a title -- lowercased and dash-delimited"""
    return re.sub(r"(\s+)", "-", title.lower())


def write_blog_post(html, dirname):
    """ mkdir() and touch() the blog post """
    LOGGER.debug("write_blog_post() -> writing %s", dirname)

    create_directory(dirname)
    write_file(dirname + "/index.html", html)

    LOGGER.debug("write_blog_post() -> successfully wrote %s", dirname)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", help="the file to compile", required=True)
    parser.add_argument("-t", "--template", help="the template to compile the file against", required=True)
    parser.add_argument("--debug", action="store_true", help="set to debug mode")

    return parser.parse_args()


def main():
    parsed_args = parse_arguments()
    if parsed_args.debug == True:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s:[%(levelname)s]: %(message)s")


    # 1. read .blagh file and .html template
    blagh_file = load_file(parsed_args.file)
    html_template = load_file(parsed_args.template)

    # 2. lex the file's tag sections (globals, macros, etc)
    lexed = lexer.scan(blagh_file)

    # 3. parse each section and inject all variables into content sections
    parsed_tags = parser.parse(lexed)
    expanded_content = expansion.expand(parsed_tags)

    # 4. compile html from the parsed .blagh file
    html = compiler.compile(expanded_content, html_template)

    # 5. write html to disk
    dirname = sluggify(parsed_args.file)
    write_blog_post(html, dirname)


if __name__ == "__main__":
    main()
