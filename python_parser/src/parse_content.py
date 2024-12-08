from parsy import generate, regex, string, seq, any_char

# Basic building blocks
newline = string("\n")
whitespace = regex(r"[ \t]+")
indent = whitespace.map(len)
empty_line = (whitespace.optional() >> newline).desc("empty_line")

# Links: [[link|text]] or [[link]]
link = regex(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]").map(
    lambda m: {"type": "link", "address": m.group(1), "text": m.group(2) or None}
)

# Tags: #tagname (no space)
tag = regex(r"#(\w+)").map(lambda m: {"type": "tag", "name": m.group(1)})

# Inline text content (including links and tags)
inline_content_item = link | tag | regex(r"[^#\[\n]+")
inline_content = inline_content_item.many().map(
    lambda items: [
        i if isinstance(i, dict) else {"type": "text", "content": i} for i in items
    ]
)

# Headers: e.g. "## Header Title"
header_line = regex(r"^(#+)\s+(.*)$").map(
    lambda m: {"type": "header", "level": len(m.group(1)), "title": m.group(2)}
)

# Bullet items: e.g. "   - item text"
bullet_line = regex(r"^( *)(-)\s+(.*)$").map(
    lambda m: {"type": "bullet", "indent": len(m.group(1)), "content": m.group(3)}
)

# Code blocks: triple backticks followed by lines until triple backticks
code_block_start = string("```") >> newline
code_block_end = string("```")
code_line = regex(r"^[^\n]*").map(lambda l: {"type": "code_line", "content": l})


@generate
def code_block():
    yield code_block_start
    lines = []
    while True:
        nxt = yield (code_line << newline).optional()
        if nxt is None:
            # End not found, error out
            raise ValueError("Missing closing ``` for code block")
        if nxt["content"].strip() == "```":
            # Found end marker line
            break
        lines.append(nxt)
    return {"type": "code_block", "content": lines}


# Generic line (if not header/bullet/code): inline text
line = (inline_content << newline).map(lambda c: {"type": "line", "content": c})

# A block is either a header, bullet, code_block, or line
block = (header_line | bullet_line | code_block | line).desc("block")

# Recursive structure:
# Sections are defined by headers. Content within a section is determined by indentation levels and bullet nesting.
# We'll define a recursive parser that groups blocks under headers and indentation.


@generate
def section():
    # Parse a header
    hdr = yield header_line << newline
    # Now parse zero or more child elements until a header of equal or lesser indent appears
    children = []
    while True:
        # We peek ahead to see if next line is a header of <= this level
        # or if we're at end of input.
        nxt = yield block.optional()
        if nxt is None:
            break
        if nxt["type"] == "header" and nxt["level"] <= hdr["level"]:
            # Put back the header for outer parser to consume
            yield block.backtrack()
            break
        # If it's a bullet or line, we handle indentation by grouping them as children.
        children.append(nxt)
    return {
        "type": "section",
        "level": hdr["level"],
        "title": hdr["title"],
        "children": children,
    }


# Top-level parser: one or more sections or blocks
document = (section.many() | block.many()).map(
    lambda items: {"type": "document", "children": items}
)
