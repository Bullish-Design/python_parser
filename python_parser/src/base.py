# Imports -----------------------------------------

import re
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, List, Any, Dict
from pydantic import BaseModel


# BaseModel ---------------------------------------


class ObsidianFrontmatterParameter(BaseModel):
    """
    Pydantic model for the frontmatter properties of a Markdown file.
    """

    name: str
    value: Optional[str | List[str]]


class ObsidianFrontmatter(BaseModel):
    """
    Pydantic model for the frontmatter of a Markdown file.
    """

    parameters: List[ObsidianFrontmatterParameter] = []

    def __str__(self) -> str:
        return_str = "Parameters:"
        if len(self.parameters) == 0:
            return_str += " None"
        else:
            for parameter in self.parameters:
                return_str += f"\n    {parameter.name}: {parameter.value}"
        return return_str


class ObsidianFile(BaseModel):
    """
    Base Pydantic model for an Obsidian Markdown file.
    """

    frontmatter: ObsidianFrontmatter
    content: str


class MarkdownModel(BaseModel, ABC):
    """
    Abstract base class for all Markdown models.
    """

    # Each subclass must define its own regex pattern
    pattern: ClassVar[re.Pattern]

    @classmethod
    @abstractmethod
    def from_markdown(cls, markdown: str) -> None:
        """
        Parses markdown string and returns an instance of the model.
        """
        return f"Not Implemented for {cls.__name__}"

    @abstractmethod
    def to_format(self, format_type, **kwargs) -> str:
        """
        Converts the model instance to another format.
        """
        return f"Not Implemented for {format_type}"
