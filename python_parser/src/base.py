# Imports -----------------------------------------
from __future__ import annotations
import re
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, List, Any, Dict
from pydantic import BaseModel
from parsy import Parser
from python_parser.src.parse_content import MarkdownNode
# BaseModel ---------------------------------------


class ParsyBase(BaseModel):
    """
    Base Pydantic model for creating parsers. Sets configs for everything else.
    """

    class Config:
        arbitrary_types_allowed = True


class ParsedNode(ParsyBase):
    """
    Base Pydantic model for a parsed node.
    """

    shape: List[str | ParsedNode] = []

    @classmethod
    def check_shape(cls, shape: List[str | ParsedNode]) -> bool:
        """
        Checks if the shape of the parsed node matches the expected shape.
        """
        return cls.shape == shape


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

    # file_type: str
    parser: Parser

    @classmethod
    def parse_file(cls, file_path: str):
        """
        Parses the file contents and returns the result. Checks to see if the file type matches the parser's file type.
        """
        # Check if the file type matches the parser's file type
        self = cls()
        if file_path.endswith(self.file_type):
            with open(file_path, "r") as file:
                file_contents = file.read()
            parsed_and_processed_results = cls.parse_content(file_contents)
            # processed_results = cls.process_results(parsed_results)
            return parsed_and_processed_results
        else:
            return "File type does not match parser type"

    # @classmethod
    # def parse(cls, file_contents: str) -> Any:
    #    """
    #    Parses the file contents and returns the result.
    #    """
    #    self = cls()
    #    return self.parser.parse(file_contents)

    @classmethod
    def parse_content(cls, file_contents: str) -> Any:
        """
        Parses the file contents and returns the result.
        """
        self = cls()
        parsed_content = self.parser.parse(file_contents)
        processed_content = self.process_results(parsed_content)
        return processed_content

    @abstractmethod
    def process_results(parsed_results: Any) -> Any:
        """
        Processes the results of the Parser call, then returns them.

        If no post-Parser processing is needed, return the parsed_results.
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

    # file_type: str

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


# A class for identifying objects basd on their data shape:
class DataShape(ParsyBase):
    """
    Pydantic model for the data shape of a parsed object.
    Serves as the "data shape" for the file. The data shape is a list of
        structured parsed nodes that represents the file contents in a structured format,
        for use in generating other file types.
    """

    shape: List[str | MarkdownNode] = []


class ParserGeneratorBase(ParsyBase, ABC):
    """
    Abstract base class for a parser/generator type.

    Inclides a list of ParserBase and GeneratorBase subclasses that can be used to parse and generate files of the given type.
    """

    data_type: DataShape
    parser: ParserBase
    generator: GeneratorBase

    @classmethod
    def parse(self, file_path: str) -> Any:
        """
        Parses the file contents and returns the result.
        """
        return self.parser.parse_file(file_path)

    @classmethod
    def parse_str(self, content_str: str) -> Any:
        """
        Parses the file contents and returns the result.
        """
        return self.parser.parse_content(content_str)

    @classmethod
    def generate(self, **kwargs) -> str:
        """
        Generates the file contents and returns the result.
        """
        return self.generator.generate(**kwargs)

    @classmethod
    def generate_node(self, node: MarkdownNode) -> str:
        """
        Generates the file contents for a single node and returns the result.
        """
        return self.generator.generate(node=node)
