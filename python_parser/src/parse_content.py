from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from os import close
from typing import List, Optional, Union, Any, Dict, Callable
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
from python_parser.src.parse_primitives import (
    content,
)
from pydantic import BaseModel

import yaml


# Datashape classes --------------------------------
class ParsyBase(BaseModel):
    """
    Base Pydantic model for creating parsers. Sets configs for everything else.
    """

    class Config:
        arbitrary_types_allowed = True


class DataType(ParsyBase, ABC):
    """
    Base Pydantic model for a parsed node.
    """

    @abstractmethod
    def to_string(self) -> str:
        """
        Convert the parsed node to a string.
        """
        return "Not implemented"

    def to_python(self):
        pass

    def to(self, file_type: str) -> str:
        """
        Matches a file type string to the conversion function in question.

        Args:
            file_type: String indicating desired output format

        Returns:
            Converted string in requested format

        Raises:
            ValueError: If file_type is not supported
        """
        match file_type.lower():
            case "string" | "str":
                return self.to_string()
            case "python" | "py":
                return self.to_python()
            case "json":
                return self.to_json()
            case "yaml" | "yml":
                return self.to_yaml()
            case "markdown" | "md":
                return self.to_string()
            case "html":
                return self.to_html()
            case _:
                raise ValueError(f"Unsupported file type: {file_type}")


# --- AST Node Definitions ---


class Text(DataType):
    """
    Pydantic model for a text node in a Markdown file.
    """

    content: str

    def to_string(self) -> str:
        return self.content


class ListItem(DataType):
    """
    Pydantic model for a list item.
    """

    level: int
    content: str

    def to_string(self) -> str:
        spaces = "  " * self.level
        return f"{spaces}- {self.content}"


class InlineCode(DataType):
    """
    Pydantic model for an inline code block in a Markdown file.
    """

    content: str

    def to_string(self) -> str:
        return f"`{self.content}`"


class CodeBlock(DataType):
    """
    Pydantic model for a code block in a Markdown file.
    """

    content: str
    language: Optional[str]

    def to_string(self) -> str:
        return f"```{self.language}\n{self.content}\n```"


class WikiLink(DataType):
    """
    Pydantic model for a wiki link in a Markdown file.
    """

    target: str
    alias: Optional[str]

    def to_string(self) -> str:
        return f"[[{self.target}|{self.alias}]]"


class ExternalLink(DataType):
    """
    Pydantic model for an external link in a Markdown file.
    """

    url: str
    text: Optional[str]

    def to_string(self) -> str:
        return f"[{self.text}]({self.url})"


class Tag(DataType):
    """
    Pydantic model for a tag in a Markdown file.
    """

    name: str

    def to_string(self) -> str:
        return f"#{self.name}"


class Header(DataType):
    """
    Pydantic model for a header in a Markdown file.
    """

    level: int
    content: str

    def to_string(self) -> str:
        return f"{'#' * self.level} {self.content}"


class Callout(DataType):
    """
    Pydantic model for a callout in a Markdown file.
    """

    type: str
    content: List[str]

    def to_string(self) -> str:
        return f">[!{self.type}]\n" + "\n".join(self.content)


class Paragraph(DataType):
    """
    Pydantic model for a paragraph in a Markdown file.
    """

    content: str

    def to_string(self) -> str:
        return self.content


class FrontMatter(DataType):
    """
    Pydantic model for the frontmatter of a Markdown file.
    """

    content: Dict[str, Any]

    def to_string(self) -> str:
        return (
            "---\n"
            + "\n".join([f"{key}: {value}" for key, value in self.content.items()])
            + "\n---"
        )

    def add(self, key: str, value: Any) -> None:
        self.content[key] = value

    def remove(self, key: str) -> None:
        if key in self.content:
            del self.content[key]

    def update(self, key: str, value: Any) -> None:
        if key in self.content:
            self.content[key] = value


class ObsidianFileBase(DataType):
    """
    Base Pydantic model for an Obsidian Markdown file.
    """

    frontmatter: FrontMatter
    content: str

    def to_string(self) -> str:
        return f"{self.frontmatter.to_string()}\n{self.content}"

    def write(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            file.write(self.to_string())


MarkdownNode = Union[
    FrontMatter,
    Text,
    ListItem,
    InlineCode,
    CodeBlock,
    WikiLink,
    ExternalLink,
    Tag,
    Header,
    Callout,
    FrontMatter,
    Paragraph,
]


# @dataclass
class ObsidianMarkdownContent(DataType):
    """
    Represents an Obsidian Markdown file.
    """

    nodes: List[MarkdownNode]

    def to_string(self) -> str:
        return "\n".join([node.to_string() for node in self.nodes])


class ObsidianFile(DataType):
    """
    Represents an Obsidian Markdown file.
    """

    frontmatter: FrontMatter
    content: ObsidianMarkdownContent

    def to_string(self) -> str:
        return f"{self.frontmatter.to_string()}\n{self.content.to_string()}"

    def write(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            file.write(self.to_string())


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

triple_backtick = string("```")

# --- Inline Level Parsers ---


# Calculate indentation level (n spaces = 1 level)
def calc_indent_level(spaces: str, n: int) -> int:
    if spaces:
        return len(spaces) // n
    else:
        return 0


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


# Tags
@generate
def tag():
    yield hash
    name = yield word
    return Tag(name=name)


# --- Block Level Parsers ---

# Front Matter
# Obsidian File Opening Delimiter
# obsidian_start = delimiter | (newline + delimiter)

# Parser to capture everything up to the next '---' (frontmatter content)
front_matter_content = regex(r"(?s).*?(?=\n---)").desc("Frontmatter Content")

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
    level = yield optional_spaces >> regex(r"#{1,6}").map(len) << space
    content = yield line_content.map(str) << newline
    return Header(level=level, content=content)


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

    yield newline

    content = "\n".join(content_lines)
    if content:
        content += "\n"
    # print(f">> CodeBlock Content: \n```\n{content}\n```\n")

    return CodeBlock(content=content, language=language)


# Callouts
callout_start = (
    greater_than
    >> space.optional()
    >> string("[!")
    >> regex(r"[A-Za-z]+").map(str)
    << bracket_close
    << newline
)

callout_line = greater_than >> optional_spaces >> regex(r"[^\n\r]+").map(str) << newline


@generate
def callout():
    # print(f">> Starting callout parse...")
    callout_type = yield callout_start
    first_line = yield callout_line
    other_lines = yield callout_line.many()

    content_lines = [first_line] + other_lines
    return Callout(type=callout_type, content=content_lines)


# Paragraphs
paragraph_line = (
    optional_spaces >> regex(r"[^#>```\n\r][^\n\r]*").map(str) << (newline | eof)
)

# paragraph = (paragraph_line >> paragraph_line.many()).map(
#    lambda t: Paragraph("\n".join([t[0]] + t[1]))
# )


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
block = header | code_block | callout | list_item | paragraph


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
    yield blank_line.optional()
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
