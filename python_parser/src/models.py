# Imports -----------------------------------------------
import re
from abc import ABC, abstractmethod
import yaml
from typing import ClassVar, Any
from parsy import Parser
from python_parser.src.base import (
    # MarkdownModel,
    ParserBase,
    ParsyBase,
    GeneratorBase,
    ParserGereratorBase,
    ObsidianFrontmatter,
    ObsidianFile,
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
from python_parser.src.parser import basic_markdown_parser, parse_frontmatter


# Constants ---------------------------------------------


# Classes -----------------------------------------------


class FrontmatterParser(ParserBase):
    """
    Base parser for frontmatter parsing.
    """

    file_type: str = "md"
    parser: Parser = frontmatter_content

    def process_results(parsed_results: Any) -> Any:
        """
        Processes the parsed results and returns the result.
        """
        print(f"\n\n**Parsed Frontmatter: **\n\n{parsed_results}\n\n")
        processed_results = ObsidianFrontmatter(
            parameters=parsed_results,
        )
        return processed_results


class MarkdownParser(ParserBase):
    """
    Base parser for Markdown parsing.
    """

    file_type: str = "md"
    parser: Parser = basic_markdown_parser

    # @abstractmethod
    def process_results(parsed_results: Any) -> Any:
        """
        Processes the parsed results and returns the result.
        """
        yaml_frontmatter = yaml.safe_load(parsed_results[0]) or {}
        parsed_frontmatter = parse_frontmatter(yaml_frontmatter)
        processed_results = ObsidianFile(
            frontmatter=parsed_frontmatter,
            content=parsed_results[1],
        )
        return processed_results


class MarkdownBase(ParserGereratorBase):
    """
    Example model representing a specific Markdown structure.
    """

    # Define the regex pattern to match the desired Markdown structure
    pattern: ClassVar[re.Pattern] = re.compile(
        r"^# Example Header\s+Content:\s+(?P<content>.+)$", re.MULTILINE
    )

    content: str
