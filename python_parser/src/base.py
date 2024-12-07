# Imports -----------------------------------------

import re
from abc import ABC, abstractmethod
from typing import ClassVar, Optional
from pydantic import BaseModel


# BaseModel ---------------------------------------


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
