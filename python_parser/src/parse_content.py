from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union
from parsy import (
    generate,
    regex,
    string,
    string_from,
    whitespace,
    forward_declaration,
    eof,
)
from python_parser.src.parse_primitives import newline, whitespace

# --- AST Node Definitions ---


@dataclass
class Text:
    content: str


@dataclass
class Bold:
    content: List["MarkdownNode"]


@dataclass
class Italic:
    content: List["MarkdownNode"]


@dataclass
class InlineCode:
    content: str


@dataclass
class CodeBlock:
    content: str
    language: Optional[str]


@dataclass
class WikiLink:
    target: str
    alias: Optional[str]


@dataclass
class ExternalLink:
    url: str
    text: Optional[str]


@dataclass
class Tag:
    name: str


@dataclass
class Header:
    level: int
    content: List["MarkdownNode"]


@dataclass
class ListItem:
    content: List["MarkdownNode"]
    indent_level: int
    is_ordered: bool


@dataclass
class Callout:
    type: str
    content: List[List["MarkdownNode"]]


@dataclass
class FrontMatter:
    content: dict


@dataclass
class Paragraph:
    content: List["MarkdownNode"]


MarkdownNode = Union[
    Text,
    Bold,
    Italic,
    InlineCode,
    CodeBlock,
    WikiLink,
    ExternalLink,
    Tag,
    Header,
    ListItem,
    Callout,
    FrontMatter,
    Paragraph,
]

# --- Basic Parser Building Blocks ---

# Whitespace
space = regex(r"[ \t]")
spaces = space.many()
newline = string("\n")
blank_line = regex(r"[ \t]*\n")
whitespace = regex(r"[ \t\n]+")

# Basic text building blocks
word = regex(r"[A-Za-z0-9]+")
punctuation = regex(r"[.,!?;:]+")
plain_text = regex(r"[^*`#\[\]\n\\]+").map(Text)

# Inline formatting markers
asterisk = string("*")
backtick = string("`")
underscore = string("_")
hash_sign = string("#")

# Link markers
open_bracket = string("[")
close_bracket = string("]")
open_paren = string("(")
close_paren = string(")")

# --- Content Parsers (to avoid recursion) ---


@generate
def bold_content():
    """Parser for content inside bold markers"""
    return (plain_text | inline_code | wiki_link | external_link | tag).many()


@generate
def italic_content():
    """Parser for content inside italic markers"""
    return (plain_text | inline_code | wiki_link | external_link | tag).many()


# --- Inline Parsers ---


@generate
def bold():
    """Parser for bold text (**bold** or __bold__)"""
    marker = yield string("**") | string("__")
    content = yield bold_content
    end_marker = yield string("**") if marker == "**" else string("__")
    return Bold(content)


@generate
def italic():
    """Parser for italic text (*italic* or _italic_)"""
    marker = yield string("*") | string("_")
    content = yield italic_content
    end_marker = yield string("*") if marker == "*" else string("_")
    return Italic(content)


@generate
def inline_code():
    """Parser for inline code (`code`)"""
    yield backtick
    content = yield regex(r"[^`]+")
    yield backtick
    return InlineCode(content)


@generate
def wiki_link():
    """Parser for Obsidian wiki links ([[page]] or [[page|alias]])"""
    yield string("[[")
    target = yield regex(r"[^\]\|]+")
    alias = yield (string("|") >> regex(r"[^\]]+").desc("alias")).optional()
    yield string("]]")
    return WikiLink(target, alias)


@generate
def external_link():
    """Parser for markdown links [text](url)"""
    yield open_bracket
    text = yield regex(r"[^\]]+")
    yield close_bracket + open_paren
    url = yield regex(r"[^)]+")
    yield close_paren
    return ExternalLink(url, text)


@generate
def tag():
    """Parser for Obsidian tags (#tag)"""
    yield string("#")
    name = yield regex(r"[A-Za-z0-9/_-]+")
    return Tag(name)


# --- Block Level Parsers ---


@generate
def header():
    """Parser for headers (# Header)"""
    level = yield hash_sign.at_least(1).map(len)
    yield space
    content = yield inline_content << newline
    return Header(level, content)


@generate
def code_block():
    """Parser for fenced code blocks"""
    yield string("```")
    language = yield (regex(r"[a-zA-Z0-9]+") << newline).optional()
    content = yield regex(r"(?:(?!```\n).*\n)*")
    yield string("```") + newline
    return CodeBlock(content, language)


@generate
def front_matter():
    """Parser for YAML front matter"""
    yield string("---") + newline
    content = yield regex(r"(?:(?!---\n).*\n)*")
    yield string("---") + newline
    # Note: You'll need to add YAML parsing here
    return FrontMatter({})


@generate
def callout():
    """Parser for Obsidian callouts (> [!TYPE])"""
    yield string("> [!")
    type_ = yield regex(r"[A-Za-z]+")
    yield string("]") + newline
    content = yield (string("> ") >> inline_content << newline).many()
    return Callout(type_, content)


@generate
def paragraph():
    """Parser for paragraphs"""
    content = yield inline_content << newline
    return Paragraph(content)


# Forward declaration for inline_content
inline_content = forward_declaration()

# --- Complete Document Parser ---


@generate
def document():
    """Parser for complete Obsidian markdown document"""
    # Optional front matter
    front = yield front_matter.optional()

    # Main content - blocks separated by blank lines
    blocks = yield (header | callout | code_block | paragraph).sep_by(blank_line)

    return [front, *blocks] if front else blocks


# Initialize recursive parsers
inline_content = (
    bold | italic | inline_code | wiki_link | external_link | tag | plain_text
).many()

# Export the main parser
markdown_parser = document
