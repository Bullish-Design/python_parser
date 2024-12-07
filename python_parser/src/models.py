# Imports -----------------------------------------------
import re
from typing import ClassVar
from python_parser.src.base import MarkdownModel


# Classes -----------------------------------------------


class ExampleModel(MarkdownModel):
    """
    Example model representing a specific Markdown structure.
    """

    # Define the regex pattern to match the desired Markdown structure
    pattern: ClassVar[re.Pattern] = re.compile(
        r"^# Example Header\s+Content:\s+(?P<content>.+)$", re.MULTILINE
    )

    content: str

    @classmethod
    def from_markdown(cls, markdown: str):
        """
        Parses markdown and initializes the ExampleModel.
        """
        match = cls.pattern.search(markdown)
        if not match:
            raise ValueError("Markdown does not match ExampleModel pattern.")
        return cls(content=match.group("content"))

    def to_html(self):
        """
        Converts the model instance to HTML format.
        """
        return f"<h1>Example Header</h1>\n<p>Content: {self.content}</p>"

    def to_json(self):
        """
        Converts the model instance to JSON format.
        """
        return self.json()
