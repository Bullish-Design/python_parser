# Imports -----------------------------------------------
import re
from typing import ClassVar
from parsy import Parser
from python_parser.src.base import (
    # MarkdownModel,
    ParserBase,
    GeneratorBase,
    ParserGereratorBase,
)
from python_parser.src.parse_primitives import (
    delimiter,
    frontmatter_content,
    content,
    lines_parser,
    newline,
    obsidian_start,
    indent,
    lexeme,
    whitespace,
    word,
)
from python_parser.src.parser import basic_markdown_parser

# Constants ---------------------------------------------




# Classes -----------------------------------------------

class MarkdownParser(ParserBase):
    """
    Base parser for Markdown parsing.
    """

    file_type: str = "md"
    parser: Parser = basic_markdown_parser

    @classmethod
    def parse(cls, text: str) -> GeneratorBase:
        """
        Parse the text and return a MarkdownModel object.
        """
        match = cls.pattern.search(text)
        if match:
            return MarkdownModel(content=match.group("content"))
        else:
            raise ValueError("No match found")"

class MarkdownBase(ParserGereratorBase):
    """
    Example model representing a specific Markdown structure.
    """

    # Define the regex pattern to match the desired Markdown structure
    pattern: ClassVar[re.Pattern] = re.compile(
        r"^# Example Header\s+Content:\s+(?P<content>.+)$", re.MULTILINE
    )

    content: str
