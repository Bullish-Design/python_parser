from __future__ import annotations
from dataclasses import dataclass
from os import close
from typing import List, Optional, Union
from parsy import (
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
class FrontMatter:
    content: dict


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
space = regex(r"[ \t]")
spaces = space.many()
newline = string("\n")
blank_line = regex(r"[ \t]*\n")
optional_spaces = regex(r"[ \t]*")
whitespace_char = regex(r"[ \t\n]")
whitespace_chars = whitespace_char.many()


# --- Inline Parsers ---
@generate
def inline_code():
    yield string("`")
    content = yield regex(r"[^`]+")
    yield string("`")
    return InlineCode(content)


@generate
def wiki_link():
    """Parser for Obsidian wiki links ([[page]] or [[page|alias]])"""
    yield string("[[")
    target = yield regex(r"[^\]\|]+").map(str.strip)
    alias_parser = (string("|") >> regex(r"[^\]]+").map(str.strip)).optional()
    alias = yield alias_parser
    yield string("]]")
    return WikiLink(target, alias)


@generate
def external_link():
    yield string("[")
    text = yield regex(r"[^\]]+")
    yield string("]")
    yield string("(")
    url = yield regex(r"[^)]+")
    yield string(")")
    return ExternalLink(url, text)


@generate
def tag():
    yield string("#")
    name = yield regex(r"[A-Za-z0-9/_-]+")
    return Tag(name)


# --- Block Level Parsers ---


@generate
def front_matter():
    """Parser for YAML front matter with proper YAML parsing"""
    yield string("---")
    yield newline

    # Collect all lines until closing delimiter
    lines = []
    while True:
        line = yield regex(r"[^\n]*")
        yield newline
        if line.strip() == "---":
            break
        lines.append(line)

    # Join lines and parse as YAML
    yaml_content = "\n".join(lines)
    try:
        parsed_yaml = yaml.safe_load(yaml_content)
        # Handle empty front matter or non-dictionary results
        if not parsed_yaml:
            parsed_yaml = {}
        elif not isinstance(parsed_yaml, dict):
            parsed_yaml = {"content": parsed_yaml}
    except yaml.YAMLError:
        # If YAML parsing fails, return empty dict rather than failing the parse
        parsed_yaml = {}

    return FrontMatter(parsed_yaml)


@generate
def header():
    """Parser for headers"""
    yield optional_spaces
    markers = yield regex(r"#{1,6}")
    yield space
    content = yield regex(r"[^\n]+")
    yield newline
    return Header(level=len(markers), content=content.strip())


@generate
def code_block():
    """Parser for fenced code blocks"""
    # Opening fence and language
    yield string("```")
    language = yield regex(r"[^\n]*")
    yield newline

    content_lines = []
    while True:
        line = yield regex(r"[^\n]*")
        if line.strip() == "```":
            break
        content_lines.append(line)
        yield newline

    # Consume final newline after closing fence
    yield newline

    # Process language and content
    language = language.strip() if language.strip() else None
    content = "\n".join(content_lines)
    if content:
        content += "\n"

    return CodeBlock(content, language)


@generate
def callout():
    """Parser for Obsidian callouts"""
    # Opening line
    yield string("> [!")
    callout_type = yield regex(r"[A-Za-z]+")
    yield string("]")
    yield newline

    content_lines = []
    # Parse first content line (required)
    yield string(">")
    yield optional_spaces
    first_line = yield regex(r"[^\n]+")
    content_lines.append(first_line.strip())
    yield newline

    # Parse additional lines (optional)
    try:
        while True:
            more_ahead = yield string(">").optional()
            if more_ahead is None:
                break
            yield optional_spaces
            line = yield regex(r"[^\n]+")
            content_lines.append(line.strip())
            yield newline
    except:
        pass

    return Callout(callout_type, content_lines)


# Inline element parser
inline_element = inline_code | wiki_link | external_link | tag


@generate
def text():
    """Parser for plain text between inline elements"""
    content = yield regex(r"[^`\[\]#\n]+")
    return Text(content)


@generate
def paragraph():
    """Parser for paragraphs with inline elements"""
    # First line must not start with special characters
    first_line = yield regex(r"[^#>```\n][^\n]*")
    yield newline

    # Optional additional lines
    other_lines = yield (regex(r"[^#>```\n][^\n]*") << newline).many()

    # Combine lines
    all_lines = [first_line] + list(other_lines)
    content = "\n".join(all_lines)

    return Paragraph(content.strip())


# Block level parser (order matters for alternatives)
block = header | code_block | callout | paragraph


@generate
def document():
    """Parser for complete Obsidian markdown documents"""
    # Optional front matter
    front = yield front_matter.optional()  # .map(FrontMatter)

    # Optional whitespace/blank lines
    yield whitespace_chars.optional()

    # Content blocks
    blocks = (
        yield (block << whitespace_chars.optional()).many().map(ObsidianMarkdownContent)
    )

    # Final optional whitespace
    yield whitespace_chars.optional()
    yield eof

    if front is not None:
        return front, blocks
    return blocks


# Export the main parser
markdown_parser = document


@dataclass
class MarkdownRule:
    """Rule for processing markdown based on frontmatter conditions"""

    frontmatter_conditions: Dict[str, Any]  # e.g. {"type": "note", "status": "draft"}
    parser_generator: Callable[[], Parser]  # Function that returns a parser
    processor: Optional[Callable[[List[Any]], Any]] = (
        None  # Optional post-processing function
    )


def print_parsed(parsed_text):
    print(f"\nType: {type(parsed_text)}:\n\n{parsed_text}\n")


class MarkdownRuleProcessor:
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

            # Handle different types of condition values
            if isinstance(expected_value, (str, int, float, bool)):
                if actual_value != expected_value:
                    return False
            elif isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            elif callable(expected_value):
                if not expected_value(actual_value):
                    return False
            elif isinstance(expected_value, dict):
                if not isinstance(actual_value, dict):
                    return False
                if not self._matches_conditions(actual_value, expected_value):
                    return False

        return True

    def process_markdown(self, content: str) -> Optional[Any]:
        """Process markdown content using the first matching rule"""
        try:
            # First parse the document to get frontmatter and content
            doc = markdown_parser.parse(content)

            if not doc or not isinstance(doc[0], FrontMatter):
                return None

            frontmatter = doc[0].content
            content_blocks = doc[1:]

            # Find first matching rule
            for rule in self.rules:
                if self._matches_conditions(frontmatter, rule.frontmatter_conditions):
                    # Generate parser for content blocks
                    content_parser = rule.parser_generator()

                    # Parse content blocks
                    parsed_content = content_parser.parse(content_blocks)

                    # Apply post-processing if defined
                    if rule.processor:
                        return rule.processor(parsed_content)
                    return parsed_content

            return None

        except Exception as e:
            print(f"Error processing markdown: {str(e)}")
            return None
