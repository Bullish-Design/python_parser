from typing import List, Dict, Union, Optional, Any
from abc import ABC, abstractmethod

from parsy import (
    seq,
    generate,
    regex,
    string,
    string_from,
    whitespace,
    forward_declaration,
    eof,
    Parser,
)
from python_parser.src.parse_primitives import (
    content,
)
from pydantic import BaseModel

import yaml


# Datashape classes --------------------------------
class ParsyBase(BaseModel):
    """
    Base Pydantic model for creating parsers. Sets configs for everything else.
    """

    class Config:
        arbitrary_types_allowed = True


class DataType(ParsyBase, ABC):
    """
    Base Pydantic model for a parsed node.
    """

    @abstractmethod
    def to_string(self) -> str:
        """
        Convert the parsed node to a string.
        """
        return "Not implemented"

    def to_python(self):
        pass

    def to(self, file_type: str) -> str:
        """
        Matches a file type string to the conversion function in question.

        Args:
            file_type: String indicating desired output format

        Returns:
            Converted string in requested format

        Raises:
            ValueError: If file_type is not supported
        """
        match file_type.lower():
            case "string" | "str":
                return self.to_string()
            case "python" | "py":
                return self.to_python()
            case "json":
                return self.to_json()
            case "yaml" | "yml":
                return self.to_yaml()
            case "markdown" | "md":
                return self.to_string()
            case "html":
                return self.to_html()
            case _:
                raise ValueError(f"Unsupported file type: {file_type}")


# --- AST Node Definitions ---


class Text(DataType):
    """
    Pydantic model for a text node in a Markdown file.
    """

    content: str

    def to_string(self) -> str:
        return self.content


class ListItem(DataType):
    """
    Pydantic model for a list item.
    """

    level: int
    content: str

    def to_string(self) -> str:
        spaces = "  " * self.level
        return f"{spaces}- {self.content}"


class InlineCode(DataType):
    """
    Pydantic model for an inline code block in a Markdown file.
    """

    content: str

    def to_string(self) -> str:
        return f"`{self.content}`"


class CodeBlock(DataType):
    """
    Pydantic model for a code block in a Markdown file.
    """

    content: str
    language: Optional[str]

    def to_string(self) -> str:
        return f"```{self.language}\n{self.content}\n```"


class WikiLink(DataType):
    """
    Pydantic model for a wiki link in a Markdown file.
    """

    target: str
    alias: Optional[str]

    def to_string(self) -> str:
        return f"[[{self.target}|{self.alias}]]"


class ExternalLink(DataType):
    """
    Pydantic model for an external link in a Markdown file.
    """

    url: str
    text: Optional[str]

    def to_string(self) -> str:
        return f"[{self.text}]({self.url})"


class Tag(DataType):
    """
    Pydantic model for a tag in a Markdown file.
    """

    name: str

    def to_string(self) -> str:
        return f"#{self.name}"


class Header(DataType):
    """
    Pydantic model for a header in a Markdown file.
    """

    level: int
    content: str

    def to_string(self) -> str:
        return f"{'#' * self.level} {self.content}"


class Callout(DataType):
    """
    Pydantic model for a callout in a Markdown file.
    """

    type: str
    content: List[str]

    def to_string(self) -> str:
        return f">[!{self.type}]\n" + "\n".join(self.content)


class Paragraph(DataType):
    """
    Pydantic model for a paragraph in a Markdown file.
    """

    content: str

    def to_string(self) -> str:
        return self.content


class FrontMatter(DataType):
    """
    Pydantic model for the frontmatter of a Markdown file.
    """

    content: Dict[str, Any]

    def to_string(self) -> str:
        return (
            "---\n"
            + "\n".join([f"{key}: {value}" for key, value in self.content.items()])
            + "\n---"
        )

    def add(self, key: str, value: Any) -> None:
        self.content[key] = value

    def remove(self, key: str) -> None:
        if key in self.content:
            del self.content[key]

    def update(self, key: str, value: Any) -> None:
        if key in self.content:
            self.content[key] = value


class ObsidianFileBase(DataType):
    """
    Base Pydantic model for an Obsidian Markdown file.
    """

    frontmatter: FrontMatter
    content: str

    def to_string(self) -> str:
        return f"{self.frontmatter.to_string()}\n{self.content}"

    def write(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            file.write(self.to_string())


MarkdownNode = Union[
    FrontMatter,
    Text,
    ListItem,
    InlineCode,
    CodeBlock,
    WikiLink,
    ExternalLink,
    Tag,
    Header,
    Callout,
    FrontMatter,
    Paragraph,
]


# @dataclass
class ObsidianMarkdownContent(DataType):
    """
    Represents an Obsidian Markdown file.
    """

    nodes: List[MarkdownNode]

    def to_string(self) -> str:
        return "\n".join([node.to_string() for node in self.nodes])


class ObsidianFile(DataType):
    """
    Represents an Obsidian Markdown file.
    """

    frontmatter: FrontMatter
    content: ObsidianMarkdownContent

    def to_string(self) -> str:
        return f"{self.frontmatter.to_string()}\n{self.content.to_string()}"

    def write(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            file.write(self.to_string())
