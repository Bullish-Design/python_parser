import parsy


# Utilities
whitespace = parsy.whitespace
lexeme = lambda p: p << whitespace
word = lexeme(parsy.letter | parsy.digit).at_least(1).concat()

# Primitives ---------------------------------------------------------------

# newline parser:
eol = parsy.string(r"\n")

indent = parsy.whitespace.at_least(1).desc("indent")

# Parser for Unix/Linux/macOS newline
unix_newline = parsy.string("\n").desc("Unix newline")  # .many()

# Parser for Windows newline
windows_newline = parsy.string("\r\n").desc("Windows newline")  # .many()

# Combined newline parser that handles both Unix and Windows newlines
newline = unix_newline | windows_newline

# Parser for a single line (captures all characters except newline characters)
# The regex '[^\r\n]*' matches any sequence of characters except '\r' and '\n'
line = parsy.regex(r"[^\r\n]*").map(str)

# Parser that separates lines by newline characters
lines_parser = line.sep_by(newline)

# Define a parser for the '---' delimiter
delimiter = parsy.string("---").desc(
    "Frontmatter delimiter"
)  # .skip(newline)  # .skip(parsy.line_ending)

# Obsidian File Opening Delimiter
obsidian_start = delimiter | (newline + delimiter)

# Parser to capture everything up to the next '---' (frontmatter content)
frontmatter_content = parsy.regex(r"(?s).*?(?=\n---)").desc(
    "Frontmatter Content"
)  # Non-greedy match until the next '---'

# Parser to capture the content after frontmatter
content = parsy.regex(r"(?s).*")  # Capture the rest of the file

# Objects ------------------------------------------------------------------

# Full parser for the Obsidian Markdown file
obsidian_parser = (
    delimiter.skip(newline)
    .then(frontmatter_content)
    .skip(delimiter)
    .then(content)
    .map(lambda content_str: content_str.strip())
)
