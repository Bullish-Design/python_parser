# Imports -----------------------------------------
from parsy import (
    seq,
    generate,
    regex,
    string,
    string_from,
    whitespace,
    forward_declaration,
    eof,
    Parser,
)
import yaml

# Library Imports ----------------------------------

# --- Basic Parser Building Blocks ---

# Whitespace
space = regex(r" ")
spaces = space.many()
tab = regex("\t")
indent = spaces | tab.many()
newline = regex(r"\r?\n")
blank_line = regex(r"[ \t]*[\r\n]")
optional_spaces = regex(r"[ \t]*")
whitespace_char = regex(r"[ \t\r\n]")
whitespace_chars = whitespace_char.many()

# Basic characters
hash = string("#")
dash = string("-")
backtick = string("`")
bracket_open = string("[")
bracket_close = string("]")
paren_open = string("(")
paren_close = string(")")
pipe = string("|")
greater_than = string(">")
exclamation = string("!")
hidden_tag = string("%%")

# Basic text patterns
non_special_char = regex(r"[^#>\[\]`\n\r]")
non_special_text = non_special_char.many().map("".join)
non_special_line = non_special_char.many().map("".join) << newline

# Common text patterns
word = regex(r"[A-Za-z0-9_-]+")
url = regex(r"[^\)\s]+")
line_content = regex(r"[^\n\r]+")
indented_line = optional_spaces >> line_content << newline

# Common sequences
triple_dash = string("---")
frontmatter_delimiter = triple_dash.desc("Frontmatter Delimiter")
triple_quote = string('"""')
python_frontmatter_delimiter = triple_quote.desc("Python Frontmatter Delimiter")

triple_backtick = string("```")

# Parser to capture everything up to the next '---' (frontmatter content)
front_matter_content = regex(r"(?s).*?(?=\n---)").desc("Frontmatter Content")
python_frontmatter_content = regex(r"(?s).*?(?=\n\"\"\")").desc(
    "Python Frontmatter Content"
)
# Callouts
callout_start = (
    greater_than
    >> space.optional()
    >> string("[!")
    >> regex(r"[A-Za-z]+").map(str)
    << bracket_close
    << newline
)

callout_line = (
    greater_than >> optional_spaces >> regex(r"[^\n\r]+").map(str).optional() << newline
)


# Parser to capture the content after frontmatter
content = regex(r"(?s).*")  # Capture the rest of the file
