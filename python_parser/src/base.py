# Imports -----------------------------------------
from __future__ import annotations
import re
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, List, Any, Dict, Union
from pydantic import BaseModel
from parsy import Parser
from python_parser.src.parse_content import MarkdownNode, ParsyBase, DataType
# BaseModel ---------------------------------------


# File Parser Base:
class FileParserBase(ParsyBase):
    """
    Base Class for Parsing Files
    """

    file_type: str
    parser: Parser

    def parse(self, file_path: str) -> DataType | None:
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

    def __call__(self, file_path: str):
        return self.parse(file_path)


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

    def compare(self, nodes: List[Union[str, MarkdownNode]]) -> bool:
        """
        Compare an input list of nodes against this DataShape's expected shape.
        Supports wildcards (*) for text content in node instances.

        Args:
            nodes: List of strings or MarkdownNode objects to compare against shape

        Returns:
            bool: True if input matches the shape, False otherwise
        """
        # print(f"\n\nself.shape: {type(self.shape)}\n{self.shape}\n\n\nNodes:\n")
        # [print(f"   Node: {type(node).__qualname__} \n{node}") for node in nodes.nodes]
        nodes = nodes.nodes
        # if len(nodes) != len(self.shape):
        #    return False
        print(f"\n\nComparing Node shape:\n")
        for expected, actual in zip(self.shape, nodes):
            # Case 1: String type name comparison
            print(f"  Expected | Actual: {expected} | {actual}")
            if isinstance(expected, str):
                try:
                    expected_type = globals()[expected]
                    if not isinstance(actual, expected_type):
                        return False
                except KeyError:
                    return False

            # Case 2: Type comparison
            elif isinstance(expected, type):
                if not isinstance(actual, expected):
                    return False

            # Case 3: Instance comparison with wildcard support
            elif isinstance(expected, MarkdownNode):
                # Check type match
                if not isinstance(actual, type(expected)):
                    return False

                # Get all attributes of the expected object
                for attr_name, expected_value in vars(expected).items():
                    actual_value = getattr(actual, attr_name)

                    # Skip comparison if expected value is "*"
                    if isinstance(expected_value, str) and expected_value == "*":
                        continue
                    # Special case for lists containing wildcards
                    elif isinstance(expected_value, list) and expected_value == ["*"]:
                        continue
                    # For dictionaries, check each value for wildcards
                    elif isinstance(expected_value, dict):
                        for key, exp_val in expected_value.items():
                            if key not in actual_value:
                                return False
                            if exp_val != "*" and exp_val != actual_value[key]:
                                return False
                    # Otherwise do direct comparison
                    elif expected_value != actual_value:
                        return False

        return True


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
