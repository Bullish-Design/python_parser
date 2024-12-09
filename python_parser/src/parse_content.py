from __future__ import annotations
from dataclasses import dataclass
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

import yaml


# --- AST Node Definitions ---
@dataclass
class Text:
    content: str


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
    content: str


@dataclass
class Callout:
    type: str
    content: List[str]


@dataclass
class Paragraph:
    content: str


# --- AST Node Definitions ---
@dataclass
class FrontMatter:
    content: Dict[str, Any]


MarkdownNode = Union[
    FrontMatter,
    Text,
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


@dataclass
class ObsidianMarkdownContent:
    nodes: List[MarkdownNode]


# --- Basic Parser Building Blocks ---

# Whitespace
space = regex(r"[ \t]")
spaces = space.many()
newline = regex(r"\r?\n")
blank_line = regex(r"[ \t]*\r?\n")
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
frontmatter_delimiter = triple_dash.desc("Frontmatter delimiter")

triple_backtick = string("```")

# --- Inline Level Parsers ---

# Inline code
inline_code = (backtick >> regex(r"[^`]+").map(str.strip) << backtick).map(InlineCode)

# Wiki links
wiki_link = (
    string("[[")
    >> regex(r"[^\]\|]+").map(str.strip)
    << pipe.optional()
    >> regex(r"[^\]]+").map(str.strip).optional()
    << string("]]")
).map(lambda t: WikiLink(t[0], t[1] if len(t) > 1 else None))

# External links
external_link = (
    bracket_open
    >> regex(r"[^\]]+").map(str.strip)
    << bracket_close
    << paren_open
    >> url.map(str.strip)
    << paren_close
).map(lambda t: ExternalLink(t[1], t[0]))

# Tags
tag = (hash >> word).map(Tag)

# --- Block Level Parsers ---

# Front Matter
# Obsidian File Opening Delimiter
# obsidian_start = delimiter | (newline + delimiter)

# Parser to capture everything up to the next '---' (frontmatter content)
front_matter_content = regex(r"(?s).*?(?=\n---)").desc("Frontmatter Content")

# front_matter_line = regex(r"[^\n\r-]*") << newline
# front_matter_content = front_matter_line.many().map("\n".join)
# Full parser for the Obsidian Markdown file
basic_markdown_parser = seq(
    frontmatter=frontmatter_delimiter.skip(newline) >> front_matter_content << newline,
    content=frontmatter_delimiter.skip(newline) >> content,
)


def parse_frontmatter(frontmatter_content: str) -> FrontMatter:
    """Parse frontmatter content"""
    try:
        parsed_yaml = yaml.safe_load(frontmatter_content)
        if not parsed_yaml:
            parsed_yaml = {}
    except yaml.YAMLError:
        parsed_yaml = {}
    return FrontMatter(parsed_yaml)


@generate
def front_matter():
    # print(f">> Starting front_matter...")
    # yield frontmatter_delimiter
    # print(f">> Triple dash")
    # yield newline
    # print(f">> Newline")
    # content = yield front_matter_content
    # print(f">> Content: \n```\n{content}\n```\n")
    # yield frontmatter_delimiter  # .optional()
    # print(f">> Optional triple dash")
    # yield newline.optional()
    # print(f">> Done with front matter extraction.")

    basic_parsed_file = yield basic_markdown_parser
    # print(f">> Basic Parsed File: {basic_parsed_file}")
    frontmatter = basic_parsed_file["frontmatter"]
    content = basic_parsed_file["content"]
    # print(f">> Frontmatter: \n````\n{frontmatter}\n````\n")
    # print(f">> Content: \n````\n{content}\n````\n")

    parsed_frontmatter = parse_frontmatter(frontmatter)
    return parsed_frontmatter


# Headers
header = seq(
    level=optional_spaces >> regex(r"#{1,6}").map(len) << space,
    content=line_content.map(str.strip) << newline,
).combine_dict(Header)


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

    return CodeBlock(content, language)


# Callouts
callout_start = (
    greater_than
    >> space.optional()
    >> string("[!")
    >> regex(r"[A-Za-z]+").map(str.strip)
    << bracket_close
    << newline
)

callout_line = (
    greater_than >> optional_spaces >> regex(r"[^\n\r]+").map(str.strip) << newline
)


@generate
def callout():
    # print(f">> Starting callout...")
    callout_type = yield callout_start
    first_line = yield callout_line
    other_lines = yield callout_line.many()

    content_lines = [first_line] + other_lines
    return Callout(callout_type, content_lines)


# Paragraphs
paragraph_line = (
    optional_spaces >> regex(r"[^#>```\n\r][^\n\r]*").map(str.strip) << newline
)

# paragraph = (paragraph_line >> paragraph_line.many()).map(
#    lambda t: Paragraph("\n".join([t[0]] + t[1]))
# )


@generate
def paragraph():
    # print(f">> Starting paragraph...")
    first_line = yield paragraph_line
    # print(f">> First line: {first_line}")
    other_lines = yield paragraph_line.many()
    # print(f">> Other lines: {other_lines}")
    content_lines = [first_line] + other_lines
    # print(f">> Content lines: \n````\n{content_lines}\n````\n")
    return Paragraph("\n".join(content_lines))


# Block level parser (order matters for alternatives)
block = header | code_block | callout | paragraph


# --- Document Level Parser ---
@generate
def document():
    """Parser for complete Obsidian markdown documents"""
    print(f">> Starting document parse...")
    # Optional front matter
    front = yield front_matter.optional()
    # print(f">> Front matter: \n````\n{front}\n````\n")
    # Optional whitespace/blank lines
    yield whitespace_chars.optional()

    # Content blocks
    blocks = (
        yield (block << (whitespace_chars.optional() | (optional_spaces + eof)))
        .many()
        .map(ObsidianMarkdownContent)
    )
    # if len(blocks.nodes) > 0:
    #    for item in blocks.nodes:
    #        print(f">> Node: {item}")
    # else:
    #    print(f">> Nodes: \n```\n{blocks}\n```\n")
    # Final optional whitespace and EOF
    yield whitespace_chars.optional()
    yield eof

    if front is not None:
        return front, blocks
    return blocks


@generate
def simple_markdown_parser():
    """Parser for complete Obsidian markdown documents"""
    print(f">> Starting simple document parse...")
    # Optional front matter
    parsed_output = yield basic_markdown_parser
    # print(f">> Parsed Output:")  # " \n\n{parsed_output}\n\n")
    # print(f"\n{parsed_output}")
    front = None
    front = parsed_output["frontmatter"]
    front = parse_frontmatter(front)
    # print(f">> Front matter: \n````\n{front}\n````\n")
    # Optional whitespace/blank lines

    # return the rest of the document content:
    content = parsed_output["content"]
    return front, content


# Export the main parsers
markdown_parser = document
# markdown_parser = simple_markdown_parser


@dataclass
class MarkdownRuleProcessor:
    """Processes markdown content using rules based on frontmatter.

    Processes file content, then optionally calls functions to edit the original file."""

    function: Callable
    post_processor: Optional[Callable] = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"Calling processor function")
        pass


@dataclass
class MarkdownRule:
    """Rule for processing markdown based on frontmatter conditions

    frontmatter_conditions: Dict[str, Any]  # e.g. {"type": "note", "status": "draft"}
    parser: Parser  # Function that returns a parser
    processor: Optional[Callable[[List[Any]], Any]] = (
        None  # Optional post-processing function
    )

    """

    frontmatter_conditions: Dict[str, Any]  # e.g. {"type": "note", "status": "draft"}
    parser: Parser  # Function that returns a parser
    processor: Optional[Callable] = None  # Optional post-processing function

    # @classmethod
    def process(self, file_path: str) -> None:
        """Process a markdown file using the rule"""

        # self = cls()

        with open(file_path, "r") as file:
            content = file.read()
        parsed_content = self.parser.parse(content)

        if self.processor:
            processed_content = self.processor(parsed_content)
        else:
            processed_content = parsed_content
        return processed_content


def print_parsed(parsed_text):
    print(f"\nType: {type(parsed_text)}:\n\n{parsed_text}\n")


class MarkdownRuleWatcher:
    """Processes markdown content using rules based on frontmatter"""

    def __init__(self):
        self.rules: List[MarkdownRule] = []

    def add_rule(self, rule: MarkdownRule) -> None:
        """Add a new rule to the processor"""
        self.rules.append(rule)

    def _matches_conditions(
        self, frontmatter: Dict[str, Any], conditions: Dict[str, Any]
    ) -> bool:
        """Check if frontmatter matches the given conditions"""
        for key, expected_value in conditions.items():
            if key not in frontmatter:
                return False
            actual_value = frontmatter[key]

            ## Handle different types of condition values
            # if isinstance(expected_value, (str, int, float, bool)):
            #    if actual_value != expected_value:
            #        return False
            # elif isinstance(expected_value, list):
            #    if actual_value not in expected_value:
            #        return False
            # elif callable(expected_value):
            #    if not expected_value(actual_value):
            #        return False
            # elif isinstance(expected_value, dict):
            #    if not isinstance(actual_value, dict):
            #        return False
            #    if not self._matches_conditions(actual_value, expected_value):
            #        return False

        return True

    def process_markdown(self, content: str) -> Optional[Any]:
        """Process markdown content using the first matching rule"""
        try:
            # print(f"Starting initial parse...")
            # First parse the document to get frontmatter and content
            frontmatter, content_str = simple_markdown_parser.parse(content)
            # print(f"\nFrontmatter: \n{frontmatter}")
            # print(f"\nContent: \n{content_str}")
            if not frontmatter:
                print(f"Misc Frontmatter Failure")
                return None

            # frontmatter = doc["frontmatter"]  # .content
            print(f"\nFrontmatter: ")
            for key, value in frontmatter.content.items():
                print(f"  {key}: {value}")
            # content = doc["content"]
            # for item in content:
            #    print(f"  {item}")

            print(f"\nContent: \n```\n{content_str}\n```\n")
            # Find first matching rule
            for rule in self.rules:
                if self._matches_conditions(
                    frontmatter.content, rule.frontmatter_conditions
                ):
                    print(f"\n\n**Matched Rule: **  {rule.__qualname__}\n\n")
                    # Generate parser for content blocks
                    content_parser = rule.parser
                    # print(f"Parsing content per rule")
                    # Parse content blocks
                    parsed_content = content_parser.parse(content_str)
                    # print(f"**Parsed Content: **\n\n{parsed_content}\n\n")
                    # Apply post-processing if defined
                    if rule.processor:
                        print(f"Processing content per rule processor")
                        result = rule.processor(parsed_content)
                        print(f"\n\n**Processed Result: **\n\n{result}\n\n")
                        return result
                    else:
                        print(f"**Parsed Content: **\n\n{parsed_content}\n\n")
                    return parsed_content

            return None

        except Exception as e:
            print(f"Error processing markdown: {str(e)}")
            return None

    def process_file(self, file_path: str) -> Optional[Any]:
        """Process a markdown file using the first matching rule"""
        with open(file_path, "r") as file:
            content = file.read()
        return self.process_markdown(content)
