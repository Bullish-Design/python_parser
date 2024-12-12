# Imports -----------------------------------------
from __future__ import annotations
import re
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, List, Any, Dict, Union
from pydantic import BaseModel
from parsy import Parser
from python_parser.src.models import (
    ObsidianFile,
    ObsidianMarkdownContent,
    ObsidianFileBase,
    FrontMatter,
    DataType,
    MarkdownNode,
    ParsyBase,
    basic_markdown_parser,
)


"""
parse_content import (
    MarkdownNode,
    ParsyBase,
    DataType,
    basic_markdown_parser,
    FrontMatter,
    ObsidianMarkdownContent,
    ObsidianFileBase,
    ObsidianFile,
)
"""
# BaseModel ---------------------------------------


# File Parser Base:
class FileParserBase(ParsyBase):
    """
    Base Class for Parsing Files
    """

    file_type: str
    parser: Parser

    def parse_file(self, file_path: str) -> DataType | None:
        if file_path.endswith(self.file_type):
            with open(file_path, "r") as file:
                file_contents = file.read()
            parsed_result = self.parser.parse(file_contents)
            if isinstance(parsed_result, DataType):
                return parsed_result
            else:
                raise ValueError(
                    f"\nParser did not return a DataType object for file: {file_path}\n\n"
                )
        else:
            raise ValueError(
                f"\nFile type does not match expected type for file: {file_path}\n\n"
            )

    def __call__(self, file_path: str) -> DataType | None:
        return self.parse_file(file_path)


# Obsidian Parser Base:
class ObsidianParserBase(FileParserBase):
    """
    Base Class for Parsing obsidian files
    """

    file_type: str = "md"
    parser: Parser = basic_markdown_parser
    content_parser: Parser

    def parse(self, file_path: str) -> tuple[FrontMatter, DataType] | None:
        parsed_result = super().parse_file(file_path)
        # print(f"\nParsed Result: {parsed_result}\n")
        if parsed_result and isinstance(parsed_result, ObsidianFileBase):
            frontmatter = parsed_result.frontmatter
            content = parsed_result.content
            parsed_content = self.content_parser.parse(content)
            # print(f"\nParsed Content: {parsed_content}\n")
            if isinstance(parsed_content, ObsidianMarkdownContent):
                return ObsidianFile(frontmatter=frontmatter, content=parsed_content)
            else:
                raise ValueError(
                    f"\nObsidian Parser did not return a DataType object for content in file: {file_path}\n\n"
                )

    def __call__(self, file_path: str) -> tuple[FrontMatter, DataType] | None:
        return self.parse(file_path)


'''
# Secondary Parser Base:
class SecondaryParserBase(ParsyBase):
    """
    Base Class for Parsing the output of the base file parser
    """

    primary_parser: FileParserBase
    parser: Parser

    def parse(self, file_path: str) -> DataType | None:
        primary_result = self.primary_parser.parse(file_path)
        if primary_result:
            parsed_result = self.parser.parse(primary_result)
            if isinstance(parsed_result, DataType):
                return parsed_result
            else:
                raise ValueError(
                    f"\nParser did not return a DataType object for file: {file_path}\n\n"
                )

    def __call__(self, file_path: str):
        return self.parse(file_path)
'''
