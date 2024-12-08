# Imports -----------------------------------------

import re
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, List, Any, Dict
from pydantic import BaseModel
from parsy import Parser

# BaseModel ---------------------------------------


class ParsyBase(BaseModel):
    """
    Base Pydantic model for creating parsers. Sets configs for everything else.
    """

    class Config:
        arbitrary_types_allowed = True


class ObsidianFrontmatterParameter(ParsyBase):
    """
    Pydantic model for the frontmatter properties of a Markdown file.
    """

    name: str = ""
    value: Optional[str | List[str]]


class ObsidianFrontmatter(ParsyBase):
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


class ObsidianFile(ParsyBase):
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


class ParserBase(ParsyBase, ABC):
    """
    Abstract base class for a parser.
    """

    file_type: str
    parser: Parser

    @classmethod
    def parse(cls, file_path: str):
        """
        Parses the file contents and returns the result. Checks to see if the file type matches the parser's file type.
        """
        # Check if the file type matches the parser's file type
        self = cls()
        if file_path.endswith(self.file_type):
            with open(file_path, "r") as file:
                file_contents = file.read()
            parsed_results = cls.parse_function(file_contents)
            processed_results = cls.process_results(parsed_results)
            return processed_results
        else:
            return "File type does not match parser type"

    @classmethod
    def parse_function(cls, file_contents: str) -> Any:
        """
        Parses the file contents and returns the result.
        """
        self = cls()
        return self.parser.parse(file_contents)

    @abstractmethod
    def process_results(parsed_results: Any) -> Any:
        """
        Processes the parsed results and returns the result.
        """
        return parsed_results

    # @classmethod
    # @abstractmethod
    # def
    # Each subclass must define


class GeneratorBase(ParsyBase, ABC):
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


class ParsedTree(ParsyBase):
    """
    Pydantic model for the parsed tree of a file.

    Serves as the "data shape" for the file. The parsed tree is a nested
        structure that represents the file contents in a structured format,
        for use in generating other file types.

    """

    pass


class ParserGereratorBase(ParsyBase, ABC):
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
