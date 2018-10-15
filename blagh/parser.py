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
