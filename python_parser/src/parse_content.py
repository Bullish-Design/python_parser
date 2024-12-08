import re
from parsy import generate, regex, string, any_char, eof
from python_parser.src.parse_primitives import newline, whitespace

# newline = string("\n")
# whitespace = regex(r"[ \t]+")
indent = whitespace.map(len)
empty_line = (whitespace.optional() >> newline).desc("empty_line")

link = regex(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]").map(
    lambda m: {"type": "link", "address": m.group(1), "text": m.group(2) or None}
)

tag = regex(r"#(\w+)").map(lambda m: {"type": "tag", "name": m.group(1)})

inline_content_item = link | tag | regex(r"[^#\[\n]+")
inline_content = inline_content_item.many().map(
    lambda items: [
        i if isinstance(i, dict) else {"type": "text", "content": i} for i in items
    ]
)

header_line = regex(r"^(#+)\s+(.*)$", flags=re.MULTILINE).map(
    lambda m: {"type": "header", "level": len(m.group(1)), "title": m.group(2)}
)

bullet_line = regex(r"^( *)(-)\s+(.*)$", flags=re.MULTILINE).map(
    lambda m: {"type": "bullet", "indent": len(m.group(1)), "content": m.group(3)}
)

code_block_start = string("```") >> newline
code_block_end = string("```")


@generate
def code_block():
    yield code_block_start
    lines = []
    while True:
        line_match = yield (regex(r"^(.*)$", flags=re.MULTILINE) << newline).optional()
        if line_match is None:
            raise ValueError("Missing closing ``` for code block")
        if line_match.strip() == "```":
            break
        lines.append({"type": "code_line", "content": line_match})
    return {"type": "code_block", "content": lines}


# Allow lines without mandatory trailing newline (line or EOF)
line = (inline_content + (newline | eof)).map(
    lambda c: {"type": "line", "content": c[:-1]}
)

block = (header_line | bullet_line | code_block | line).desc("block")


@generate
def section():
    hdr = yield header_line << (newline | eof)
    children = []
    while True:
        nxt = yield block.optional()
        if nxt is None:
            break
        if nxt["type"] == "header" and nxt["level"] <= hdr["level"]:
            yield block.backtrack()
            break
        children.append(nxt)
    return {
        "type": "section",
        "level": hdr["level"],
        "title": hdr["title"],
        "children": children,
    }


document = (section.many() | block.many()).map(
    lambda items: {"type": "document", "children": items}
) << eof
