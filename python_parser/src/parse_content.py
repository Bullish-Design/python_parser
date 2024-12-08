import re
from parsy import generate, regex, string, any_char, eof, seq, line_info
from python_parser.src.parse_primitives import newline, whitespace, word  # , line
from dataclasses import dataclass

# newline = string("\n")
# whitespace = regex(r"[ \t]+")

test_indent = "    "
indent = whitespace.map(len)

test_empty = " \n"
empty_line = (whitespace.optional() >> newline).desc("empty_line")

test_link = "[[http://example.com|Example]]"
link = regex(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")  # .map(
#    lambda m: {"type": "link", "address": m.group(1), "text": m.group(2) or None}
# )

test_tag = "#cool"
tag = regex(r"#(\w+)")  # .map(lambda m: {"type": "tag", "name": m.group(1)})

test_line = "Hello world"
str_line = regex(r"[^\r\n]*").map(str)
test_inline_content = "Check this out #cool"
inline_content_item = link | tag | str_line  # regex(r"[^#\[\n]+")
inline_content = inline_content_item  # .many()
# .map(
#    lambda items: [
#        i if isinstance(i, dict) else {"type": "text", "content": i} for i in items
#    ]
# )

test_misc_line = "Check this out\n"
# Allow lines without mandatory trailing newline (line or EOF)
line = inline_content  # + (newline | eof)


test_header = "# Header: an example"
header_line = regex(r"^(#+)\s+(.*)$", flags=re.MULTILINE)
# .map(
#    lambda m: {"type": "header", "level": len(m.group(1)), "title": m.group(2)}
# )

test_bullet_1 = "- Point 1"
test_bullet_2 = "  - Point 2"
bullet_line = regex(r"^( *)(-)\s+(.*)$", flags=re.MULTILINE)
# .map(
#    lambda m: {"type": "bullet", "indent": len(m.group(1)), "content": m.group(3)}
# )

code_block_start = seq(
    string("```"),
    str_line.optional(),
    newline,  # .skip()
)  # string("```").then(str_line).optional().then(newline).skip(newline)
code_block_end = string("```")

test_code_block = """```
Testing code block
```
"""
test_python_code_block = "```python\nprint('Hello world')\n```"


@generate
def block_start():
    block_type = None
    yield string("```")
    block_type = yield str_line.optional()
    yield newline
    return block_type


@dataclass
class CodeBlock:
    block_type: str
    content: str


@generate
def code_block():
    kickoff = yield block_start

    print(f"CodeBlock Type: {kickoff}")
    lines = []
    count = 0
    while True and count < 10:
        count += 1
        line_match = yield (
            str_line << newline.optional()
        )  # .many().optional()  # (regex(r"^(.*)$", flags=re.MULTILINE) << newline).optional()
        print(f"CodeBlock: {line_match}")
        if line_match is None:
            raise ValueError("Missing closing ``` for code block")
        if line_match.strip() == "```":
            break
        lines.append(line_match)
    return CodeBlock(block_type=kickoff, content=lines)


# .map(
# lambda c: {"type": "line", "content": c[:-1]}
# )

block = (header_line | bullet_line | code_block | line).desc("block")


@generate
def section():
    line_deets = yield line_info
    print(f"Line Deets: {line_deets}")
    start = yield (block << (newline | eof)).optional()
    print(f"Start: {start}")
    line_deets = yield line_info
    print(f"Line Deets: {line_deets}")
    hdr = yield header_line << (newline | eof)
    print(f"Header: {hdr}")
    children = []
    count = 0
    while True and count < 20:
        count += 1
        line_deets = yield line_info
        print(f"Line Deets: {line_deets}")
        nxt = yield (block << (newline | eof)).optional()
        print(f"Next: {nxt}")
        if nxt is "":
            break
        # if nxt["type"] == "header" and nxt["level"] <= hdr["level"]:
        #    yield block.backtrack()
        #    break

        children.append(nxt)
    print(f"Children: {children}")
    return


test_doc = """outside text
# Header 1
header1 text
header1 continued
## Header 2
header2 text
header2 text before block
```python
def test_fun():
    pass
```
"""

document = section.many() | block.many()  # << eof
# .map(
#    lambda items: {"type": "document", "children": items}
# ) << eof


def test_parser(test_parser, text):
    return test_parser.parse(text)


parser_to_test = document
test_str = test_doc


def test_function():
    result = test_parser(parser_to_test, test_str)
    print(f"Result: \n```\n{result}\n```\n")
