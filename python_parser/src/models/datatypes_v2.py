from typing import List, Dict, Union, Optional, Any, ClassVar, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime, date
import parsy
from pathlib import Path
from pydantic import BaseModel, ValidationError, Field
from dataclasses import dataclass

from python_parser.src.models import (
    DataType,
    Text,
    # Bold,
    # Italic,
    InlineCode,
    CodeBlock,
    WikiLink,
    ExternalLink,
    ImageLink,
    Tag,
    Header,
    ListItem,
    Callout,
    FrontMatter,
    Paragraph,
    DB_Node,
    DB_Node_Tag,
    ObsidianFileBase,
    PythonFrontMatter,
    PythonFileBase,
    PythonFile,
    ObsidianFile,
    Section,
    list_item,
    markdown_parser,
    basic_markdown_parser,
    paragraph,
    # bold,
    # italic,
    inline_code,
    wiki_link,
    external_link,
    image_link,
    image_external_link,
    image_wiki_link,
    tag,
    header,
    front_matter,
    callout,
    code_block,
    document,
    parse_references,
    db_node_tag,
    db_nodes,
    basic_python_parser,
    python_frontmatter,
    section,
)

# from python_parser.logs.logger import get_logger

# logger = get_logger(__name__)


# Datashape classes --------------------------------
DataType = TypeVar("DataType")


class Parser(BaseModel, Generic[DataType]):
    """
    Base Pydantic model for creating parsers. Sets configs for everything else.
    """

    parser: parsy.Parser
    data_type: Type[DataType]
    class_registry: ClassVar[Dict[str, "Parser"]] = {}

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.__class__.class_registry[self.data_type.__name__] = self

    @classmethod
    def get_parser(cls, data_type: str) -> Optional["Parser"]:
        """Get a parser instance for the given data type from the registry."""
        return cls.class_registry.get(data_type)

    @classmethod
    def parse(cls, data_type: Union[Type[DataType], str], text: str) -> DataType:
        """
        Parse text using the appropriate parser for the given data type.

        Args:
            data_type: The type of data to parse into
            text: The input text to parse

        Returns:
            The parsed data of the specified type

        Raises:
            KeyError: If no parser is registered for the given data type
        """

        if not isinstance(data_type, str):
            data_type = data_type.__name__
        parser = cls.get_parser(data_type)
        if parser is None:
            raise KeyError(f"No parser registered for type {data_type}")
        return parser(text)

    def __call__(self, text: str) -> DataType:
        """Parse the input text using this parser."""
        return self.parser.parse(text)


# Constants --------------------------------
test_file = """---
id: XcEgwWjA6pXuCBmGmckQrX
aliases: ['Python_Parser']
tags: ['']
category: PROJECT_NOTES
vault_path: Projects/python_parser/Notes.md
---
%%mYvdWaq9ogP627SSqfFffP|0.0.0|MarkdownFile%%
# Python_Parser

# What:
A parsing library that utilizes Obsidian based markdown templates as a source to generate the to/from regex based parsing models. 



# Why:
A flexible starting point to "self-bootstrap" an obsidian based development environment. 

Utilize LLM agents as semi-smart "text-expander" functionality. 



# Goals:


# Outline:


# My Questions:


# Learnings:


# Resources:


# Tasks:


# Log:
 - [[Projects/python_parser/Daily/24-49-1.md|24-49-1]]
 - [[Projects/python_parser/Daily/24-49-2.md|24-49-2]]
 - [[Projects/python_parser/Daily/24-49-3.md|24-49-3]]
 - [[Projects/python_parser/Daily/24-49-5.md|24-49-5]]
 - [[Projects/python_parser/Daily/24-50-3.md|24-50-3]]
 - [[Projects/python_parser/Daily/24-50-4.md|24-50-4]]
 - [[Projects/python_parser/Daily/24-50-7.md|24-50-7]]
 - [[Projects/python_parser/Daily/24-51-2.md|24-51-2]]
 - [[Projects/python_parser/Daily/25-01-6.md|25-01-6]]
 - [[Projects/python_parser/Daily/25-01-7.md|25-01-7]]
 - [[Projects/python_parser/Daily/_index.md|_index]]
"""


class ObsidianFileParser(Parser[ObsidianFile]):
    """
    Parser for Obsidian files.
    """

    parser: parsy.Parser = basic_markdown_parser
    data_type: Type[ObsidianFile] = Field(default=ObsidianFile)


class PythonFileParser(Parser[PythonFile]):
    """
    Parser for Obsidian files.
    """

    parser: parsy.Parser = basic_python_parser
    data_type: Type[PythonFile] = Field(default=PythonFile)


"""
# Or instantiate directly:
file_parser = ParserBase[ObsidianFileBase](
    parser=basic_markdown_parser,
    data_type=ObsidianFileBase
)
"""


class HeaderParser(Parser[Header]):
    """
    Parser for headers.
    """

    parser: parsy.Parser = header
    data_type: Type[Header] = Field(default=Header)


class SectionParser(Parser[Section]):
    """
    Parser for sections.
    """

    parser: parsy.Parser = section
    data_type: Type[Section] = Field(default=Section)


class FrontMatterParser(Parser[FrontMatter]):
    """
    Parser for front matter.
    """

    parser: parsy.Parser = front_matter
    data_type: Type[FrontMatter] = Field(default=FrontMatter)


database_parsers = [
    ObsidianFileParser(),
    PythonFileParser(),
    HeaderParser(),
    FrontMatterParser(),
    SectionParser(),
]


# Main
def test_datatypes():
    # try:
    # file_parser = FileParser()
    # except ValidationError as e:
    #    logger.error(f"ERROR: \n\n{e}\n")
    # frontmatter_parser = ParserBase(parser=front_matter, data=FrontMatter)
    # header_parser = ParserBase(parser=header, data=Header)

    # parsed_output = file_parser(text=test_file)

    # print(f"\n\nTesting Parser:\n")
    # print(f"\n{parsed_output}\n\n")
    print(f"\n\nTesting Generic Parser:\n")
    print(f"\n{Parser.parse("ObsidianFile", test_file)}\n\n")
