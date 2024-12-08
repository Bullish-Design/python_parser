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

    @classmethod
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


class MarkdownModel(BaseModel, ABC):
    """
    Abstract base class for all Markdown models.
    """

    # Each subclass must define its own regex pattern
    parser: ClassVar[Parser]

    @classmethod
    @abstractmethod
    def parse_from(cls, file_path: str) -> None:
        """
        Parses markdown string and returns an instance of the model.
        """
        file_type = file_path.split(".")[-1]
        with open(file_path, "r") as file:
            file_contents = file.read()
        result = cls.parser.parse(file_contents)
        return result
        # return f"Not Implemented for {cls.__name__}"

    @abstractmethod
    def generate_to(self, to_type: str, **kwargs) -> str:
        """
        Converts the model instance to another format.
        """
        return f"Not Implemented for {format_type}"
