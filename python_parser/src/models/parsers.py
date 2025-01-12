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
    Result,
    line_info,
)
import yaml
from typing import List, Union

# Library Imports -----------------------------------------
from python_parser.src.models.parse_primitives import (
    whitespace_chars,
    space,
    optional_spaces,
    newline,
    backtick,
    pipe,
    bracket_open,
    bracket_close,
    paren_open,
    paren_close,
    hash,
    word,
    front_matter_content,
    frontmatter_delimiter,
    content,
    callout_line,
    callout_start,
    url,
    line_content,
    triple_backtick,
    blank_line,
    hidden_tag,
)

from python_parser.src.models.datatypes import (
    ListItem,
    InlineCode,
    WikiLink,
    ExternalLink,
    Tag,
    FrontMatter,
    ImageLink,
    Header,
    ObsidianFileBase,
    CodeBlock,
    Callout,
    Paragraph,
    ObsidianMarkdownContent,
    DB_Node_Tag,
    DB_Node,
)

from python_parser.logs.logger import get_logger

logger = get_logger(__name__)

# --- Inline Level Parsers ---


# Calculate indentation level (n spaces = 1 level)
def calc_indent_level(spaces: str, n: int) -> int:
    if spaces:
        return len(spaces) // n
    else:
        return 0


# match-case db_node parser based on db_node_tag parse type?


# DB Node parser:
@generate
def db_node_tag():
    """Parser for DB node tags"""
    # logger.info(f"  Parsing DB Node Tag...")
    # yield optional_spaces
    # initial_newline = yield newline.optional()
    initial_text = yield regex(r"[^\%%]+").map(str).optional()
    yield hidden_tag
    node_id = yield regex(r"[^\|\%%]+").map(str) << pipe.optional()
    node_id = node_id.strip()
    # logger.info(f"    Node ID: {node_id}")

    git_version = yield regex(r"[^\|\%%]+").map(str).optional() << pipe.optional()
    if git_version:
        git_version = git_version.strip()
    # logger.info(f"    Git Version: {git_version}")

    node_type = yield regex(r"[^\%%]+").map(str).optional()
    if node_type:
        node_type = node_type.strip()
    # logger.info(f"    Node Type: {node_type}")
    yield hidden_tag

    # Check if this is a block node by looking for only whitespace then newline or EOF
    # is_inline = False
    # try:
    #    spaces = yield optional_spaces
    #    output = yield (newline | eof).optional()
    #    if output:
    #        print(f"  Found block")
    #        is_inline = False
    # except:
    #    print(f"  Found inline")
    #    is_inline = True

    return DB_Node_Tag(node_id=node_id, git_version=git_version, node_type=node_type)


non_node = regex(r"[^\%%]+") | eof


@generate
def db_node():
    """Parser for DB nodes"""
    # file_nodes = []
    logger.info(f"Parsing DB Node...")
    count = 0
    # while True:
    #    try:
    # file_end = yield eof.optional()
    # if file_end:
    #    return file_nodes
    #        count += 1
    node_tag = yield db_node_tag
    logger.info(f"  Node Tag: {node_tag}")
    # try:
    #    file_end = yield eof  # .optional()
    #    if file_end:
    #        file_node = DB_Node(node_tag=node_tag, content=None)
    #        file_nodes.append(file_node)
    #        return file_nodes
    # except:
    #    continue
    content = yield regex(r"[^\%%]+").map(str).optional()  # .until(eof)
    logger.info(f"  Content: {content}")
    # if not content:
    # content = None
    # logger.info(f"  Content: {content}")
    file_node = DB_Node(node_tag=node_tag, content=content)
    # logger.info(f"  File Node {count}: {file_node}")
    # file_nodes.append(file_node)
    # if content:
    #    file_nodes[node_tag] = content
    # else:
    #    file_nodes[node_tag] = None
    #    except:
    #        break
    logger.info(f"  File Node: {file_node}")
    # node_tag = yield db_node_tag
    # content_str = yield regex(r"[^\%%]+").map(str).optional()
    # if content_str:
    #    content = content_str
    # else:
    #    content = None
    return file_node  # content


# Parser for many db_nodes
@generate
def db_nodes():
    """Parser for multiple DB nodes"""
    nodes = yield db_node.many() << eof

    return nodes


# Parser for list items
@generate
def list_item():
    # Get indentation at start of line
    # print(f"parsing listitem")
    # full_line = yield line_content
    # print(f"  Line: `{full_line}`")
    indent = yield optional_spaces
    # print(f"  Spaces: '{indent}'")
    indent_level = calc_indent_level(indent, 2)

    # Match the list item marker
    yield string("- ")

    # Get the content after the marker
    content = yield regex(r"[^\n]+").map(str)
    # Consume the newline
    yield (newline | eof)

    return ListItem(level=indent_level, content=content)


# Inline code
@generate
def inline_code():
    yield backtick
    content = yield regex(r"[^`]+").map(str)
    yield backtick
    return InlineCode(content=content)


# Wiki links
@generate
def wiki_link():
    yield string("[[")
    target = yield regex(r"[^\|\]]+").map(str) << pipe.optional()
    alias = yield regex(r"[^\]]+").map(str).optional()
    yield string("]]")
    return WikiLink(target=target, alias=alias)


# External links
@generate
def external_link():
    yield bracket_open
    text = yield regex(r"[^\]]+").map(str)
    yield bracket_close
    yield paren_open
    link_url = yield url.map(str)
    yield paren_close
    return ExternalLink(url=link_url, text=text)


# Image Links
@generate
def image_wiki_link():
    """Parser for Obsidian local image links: ![[image.png]] or ![[image.png|alt text]]"""
    yield string("!")
    yield string("[[")
    target = yield regex(r"[^\|\]]+").map(str) << pipe.optional()
    alias = yield regex(r"[^\]]+").map(str).optional()
    yield string("]]")
    return ImageLink(path=target, is_external=False, alt_text=alias)


@generate
def image_external_link():
    """Parser for markdown image links: ![alt text](url)"""
    yield string("!")
    yield string("[")
    alt_text = yield regex(r"[^\]]+").map(str).optional()
    yield string("]")
    yield string("(")
    link_url = yield url.map(str)
    yield string(")")
    return ImageLink(path=link_url, is_external=True, alt_text=alt_text)


# Combine both image link parsers
image_link = image_wiki_link | image_external_link

non_link = regex(r"[^\[\]#]+")  # Any text that isn't a link or tag

link = wiki_link | external_link | image_link


# Tags
@generate
def tag():
    yield hash
    name = yield word
    return Tag(name=name)


reference = tag | link | inline_code

# --- Block Level Parsers ---


@generate
def reference_parser():
    """Parser that collects all references (links and tags) from text."""
    refs = []
    while True:
        # Try to find a reference
        try:
            # Skip non-reference text
            discarded = yield (non_link | newline | space).many().optional()
            if discarded:
                print(f"  Discarded: '{discarded}'")

            # Get the reference
            ref = yield reference
            if ref:
                print(f"Ref: {ref}")
            refs.append(ref)
        except:
            # break
            continue

    return refs


def parse_references(text: str) -> List[Union[Tag, WikiLink, ExternalLink]]:
    """
    Parse text and return all references found.

    Args:
        text: String to parse

    Returns:
        List of found references (tags and links)
    """
    try:
        return reference_parser.parse(text)
    except Exception as e:
        print(f"Parse error: {e}")
        return []


# Front Matter
# Obsidian File Opening Delimiter
# obsidian_start = delimiter | (newline + delimiter)

# front_matter_line = regex(r"[^\n\r-]*") << newline
# front_matter_content = front_matter_line.many().map("\n".join)
# Full parser for the Obsidian Markdown file


def parse_frontmatter(frontmatter_content: str) -> FrontMatter:
    """Parse frontmatter content"""
    try:
        parsed_yaml = yaml.safe_load(frontmatter_content)
        if not parsed_yaml:
            parsed_yaml = {}
    except yaml.YAMLError:
        parsed_yaml = {}
    return FrontMatter(content=parsed_yaml)


@generate
def front_matter():
    # print(f">> Starting front_matter...")
    yield frontmatter_delimiter
    # print(f"fm delim")
    yield newline
    # print(f"fm content?")
    frontmatter = yield front_matter_content << newline
    # print(f"     Frontmatter: \n`{frontmatter}`")
    yield frontmatter_delimiter << newline

    parsed_frontmatter = parse_frontmatter(frontmatter_content=frontmatter)
    return parsed_frontmatter


# basic_markdown_parser = seq(
#    frontmatter=frontmatter_delimiter.skip(newline) >> front_matter_content << newline,
#    content=frontmatter_delimiter.skip(newline) >> content.desc("Content"),
# )


# Generated basic markdown parser:
@generate
def basic_markdown_parser():
    # print(f">> Starting basic_markdown_parser...")

    parsed_frontmatter = yield front_matter.optional()
    # yield frontmatter_delimiter.skip(newline)
    file_content = yield content.desc("Content")

    return ObsidianFileBase(frontmatter=parsed_frontmatter, content=file_content)


## Headers
# header = seq(
#    level=optional_spaces >> regex(r"#{1,6}").map(len) << space,
#    content=line_content.map(str.strip) << newline,
# ).combine_dict(Header)


@generate
def header():
    # print(f">> Starting header parse...")
    yield whitespace_chars
    level = yield optional_spaces >> regex(r"#{1,6}").map(len)  # << space
    # print(f"   Level: {level}")
    yield space
    # index = yield line_info
    # print(f"   Space: {space_char}")
    content = yield line_content.map(str)  # << newline.optional()
    # print(f"   Content: {content}")
    yield newline.optional()
    # if not space_char:
    #    print(f"   No space")
    #    return Result.failure(index, "No space after header level")
    return Header(level=level, content=content)


# header = header | Exception("Header parse error")


# Code blocks
@generate
def code_block():
    # print(f">> Starting code_block...")
    yield triple_backtick
    language = yield regex(r"[^\n\r]*").map(lambda x: x.strip() if x.strip() else None)
    # print(f">> Language: {language}")
    yield newline

    content_lines = []
    while True:
        line = yield regex(r"[^\n\r]*")
        if line.strip() == "```":
            break
        content_lines.append(line)
        yield newline
    # print(f">> CodeBlock Content lines: \n{content_lines}")

    # while True:
    #    # Try to detect EOF before reading next line
    #    try:
    #        yield eof.should_fail("expected more content or closing ```")
    #    except:
    #        continue  # Not EOF, continue

    #    line = yield regex(r"[^\n\r]*")
    #    if line.strip() == "```":
    #        break
    #    content_lines.append(line)

    #    # Must find a newline or EOF
    #    try:
    #        yield newline
    #    except:
    #        # If we can't find newline, check if we're at EOF
    #        yield eof  # This will fail if we're not at EOF
    #        raise Exception("Code block must be closed with ```")

    yield newline.optional()

    content = "\n".join(content_lines)
    if content:
        content += "\n"
    # print(f">> CodeBlock Content: \n```\n{content}\n```\n")

    return CodeBlock(content=content, language=language)


@generate
def callout():
    # print(f">> Starting callout parse...")
    callout_type = yield callout_start.optional()
    if not callout_type:
        callout_type = None
    first_line = yield callout_line
    other_lines = yield callout_line.many()

    content_lines = [first_line] + other_lines
    return Callout(type=callout_type, content=content_lines)


# Paragraphs
paragraph_line = (
    # optional_spaces >> regex(r"[^#>```!\n\r][^\n\r]*").map(str) << (newline | eof)
    optional_spaces >> regex(r"(?![#>!])[^\n\r]+").map(str) << (newline | eof)
)


@generate
def paragraph():
    # print(f">> Starting paragraph parse...")
    first_line = yield paragraph_line
    # print(f">> First line: {first_line}")
    other_lines = yield paragraph_line.many()
    # print(f">> Other lines: {other_lines}")
    content_lines = [first_line] + other_lines
    # print(f">> Content lines: \n````\n{content_lines}\n````\n")
    return Paragraph(content="\n".join(content_lines))


# Block level parser (order matters for alternatives)
block = header | code_block | callout | list_item | image_link | tag | paragraph


# --- Document Level Parser ---
@generate
def document():
    """Parser for complete Obsidian markdown documents"""
    # print(f">> Starting document parse...")
    # Optional front matter
    front = yield front_matter.optional()
    # print(f">> Front matter: \n````\n{front}\n````\n")
    # Optional whitespace/blank lines
    # yield whitespace_chars.optional()
    yield blank_line.many().optional()
    # Content blocks
    blocks = (
        yield (block << (blank_line.many() | eof | (whitespace + eof))).many()
        # (whitespace_chars.optional() | (optional_spaces + eof))).many()
    )
    blocks = ObsidianMarkdownContent(nodes=blocks)
    # print(f">> Blocks: \n````\n{blocks}\n````\n")
    yield whitespace_chars.optional()
    yield eof

    if front is not None:
        return front, blocks
    return blocks


@generate
def simple_markdown_parser():
    """Parser for complete Obsidian markdown documents"""
    # print(f">> Starting simple document parse...")
    # Optional front matter
    parsed_output = yield basic_markdown_parser
    # print(f">> Parsed Output:")  # " \n\n{parsed_output}\n\n")
    return parsed_output


# Export the main parsers
markdown_parser = document
# markdown_parser = simple_markdown_parser
