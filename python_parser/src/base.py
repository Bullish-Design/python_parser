# Imports -----------------------------------------

import re
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, List, Any, Dict
from pydantic import BaseModel
from parsy import Parser

# BaseModel ---------------------------------------


class ObsidianFrontmatterParameter(BaseModel):
    """
    Pydantic model for the frontmatter properties of a Markdown file.
    """

    name: str = ""
    value: Optional[str | List[str]]


class ObsidianFrontmatter(BaseModel):
    """
    Pydantic model for the frontmatter of a Markdown file.
    """

    parameters: List[ObsidianFrontmatterParameter] = []

    def __str__(self) -> str:
        return_str = "---"
        if len(self.parameters) == 0:
            return_str += "\nNone"
            return_str += "\n---"
        else:
            for parameter in self.parameters:
                return_str += f"\n{parameter.name}: {parameter.value}"
            return_str += "\n---"
        return return_str


class ObsidianFile(BaseModel):
    """
    Base Pydantic model for an Obsidian Markdown file.
    """

    frontmatter: ObsidianFrontmatter
    content: str

    def __str__(self) -> str:
        return_str = "\nObsidian File:\n"
        return_str += f"\n{self.frontmatter}"
        return_str += f"\n{self.content}\n"
        return return_str


class ParserBase(BaseModel, ABC):
    """
    Abstract base class for a parser.
    """

    file_type: str
    parser: Parser

    @abstractmethod
    def parse(self, file_contents: str) -> Any:
        """
        Parses the file contents and returns the result.
        """
        return self.parser.parse(file_contents)

    # @classmethod
    # @abstractmethod
    # def
    # Each subclass must define


class GeneratorBase(BaseModel, ABC):
    """
    Abstract base class for a generator.
    """

    file_type: str

    @abstractmethod
    def generate(self, **kwargs) -> str:
        """
        Generates the file contents and returns the result.
        """
        return "Not Implemented"


class ParsedTree(BaseModel):
    """
    Pydantic model for the parsed tree of a file.

    Serves as the "data shape" for the file. The parsed tree is a nested
        structure that represents the file contents in a structured format,
        for use in generating other file types.

    """

    pass


class ParserGereratorBase(BaseModel, ABC):
    """
    Abstract base class for a parser/generator type.

    Inclides a list of ParserBase and GeneratorBase subclasses that can be used to parse and generate files of the given type.
    """

    data_type: str
    parsers: List[ParserBase]
    generators: List[GeneratorBase]

    @abstractmethod
    def parse(self, file_contents: str) -> Any:
        """
        Parses the file contents and returns the result.
        """
        return "Not Implemented"

    @abstractmethod
    def generate(self, **kwargs) -> str:
        """
        Generates the file contents and returns the result.
        """
        return "Not Implemented"
