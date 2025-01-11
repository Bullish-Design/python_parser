from typing import List, Dict, Union, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime, date
import parsy
from pathlib import Path

from dataclasses import dataclass

from pydantic import BaseModel


# Datashape classes --------------------------------
class ParsyBase(BaseModel):
    """
    Base Pydantic model for creating parsers. Sets configs for everything else.
    """

    class Config:
        arbitrary_types_allowed = True


class DataType(BaseModel, ABC):
    """
    Base Pydantic model for a parsed node.
    """

    class Config:
        # Allow arbitrary types to be converted to JSON
        arbitrary_types_allowed = True

        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
        # This ensures you can use the model with ORMs
        from_attributes = True
        # Allow extra fields when deserializing
        extra = "allow"

    def dict(self, *args, **kwargs):
        """Override dict method to ensure all nested objects are serializable"""

        def convert_to_serializable(obj: Any) -> Any:
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, BaseModel):
                return obj.dict(*args, **kwargs)
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {
                    key: convert_to_serializable(value) for key, value in obj.items()
                }
            elif hasattr(obj, "__dict__"):
                return convert_to_serializable(obj.__dict__)
            return obj

        data = super().dict(*args, **kwargs)
        serialized_obj = convert_to_serializable(data)
        # print(f"Serialized object: \n{serialized_obj}\n")
        return serialized_obj

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


# TODO: Can I move all DB node/tag related stuff out into the ObsidianDB library?
#          - Import this library, create the DB parsers from primitives
#          - Have all parsing/generation and database handling there.


# TODO:  Make class for content_type obj
@dataclass
class ContentType:
    name: str
    parser: parsy.Parser


# --- AST Node Definitions ---
class DB_Node_Tag(DataType):
    """
    Pydantic model that recognizes a DB Node tag (Hidden obsidian tag - %%{DB_ID}|{Git_VersionMajor.Minor.Patch}|{node_type: i.e.-is_block}%%)
    """

    node_id: str
    git_version: str
    node_type: str
    # is_inline: bool = False  # Is this necessary? Nested content would be easier to handle with an explicit inline/block tag callout. Does it need more node types?

    def to_string(self) -> str:
        return f"%%{self.node_id}|{self.git_version}|{self.node_type}%%"


class ContentNode(DataType):
    """
    A Pydantic model that represents a content node in the AST. A content node consists of an id, content_type (which drives parsing), and content str
    """

    id: str
    content_str: str
    content_type: Optional[ContentType]  # For parsing to/generating from the database.

    # TODO: Look at making the DataType obj require a "parse" function? And include a Parsy parser attribute in the class definition?
    #          - Could make it easier for handling database operations, would just store everything as strings, and parse into MarkdownNode objects after database lookup
    #          - Could have secondary parse that identifies nested DB_Node tags, performs recursive parsing/generation as needed.

    def detect_type(self):
        # parse the content_str to determine what type it is TODO: figure out how to return Parsy parser type based on sucessful parsing
        pass

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass


class DB_Node(DataType):
    """
    Pydantic model that represents the DB Node in the database. consists of a DB_Node_Tag, node_parameters, and content.
    """

    # id: str
    node_tag: DB_Node_Tag
    content: Optional[str]
    # node_parameters: Dict[
    #    str, Any
    # ]  # File Frontmatter - block comment if code file, frontmatter if markdown
    # content: List[
    #    ContentNode
    # ]  # TODO: Have another relationship lookup for a one-to-many relationship between the node and the list of contentNodes?

    ## Relationships:
    # TODO: relationship: For linking the db node to the content node - many to many for reusing nodes across different files (configs, constants, envvars, todo lists, etc.)
    # TODO: relationship: For linking the db_node to the db_node_tag - one to one - would there be any situation where I'd want a one-to-many or a many-to-many relationship here??

    def to_string(self) -> str:
        # node_tag = f"%%{self.node_tag.node_id}|{self.node_tag.git_version}%%"
        node_tag = self.node_tag.to_string()
        # node_parameters = "\n".join(
        #    [f"{key}: {value}" for key, value in self.node_parameters.items()]
        # )
        # if self.node_tag.is_block:
        #    content = f"{node_tag}\n{self.content}\n"
        # else:
        #    content = f"{node_tag} {self.content}"
        file = f"---\n{node_tag}\n---\n{self.content}"
        return file

    def from_file(self, filepath: Path):
        # Parse a file into a DB object
        pass


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


class ImageLink(DataType):
    """
    Represents an image link in Obsidian markdown.
    Can be either a local image (wiki-style) or external URL.

    Examples:
    - Local image: ![[image.png]]
    - External image: ![alt text](https://example.com/image.png)
    """

    path: str  # Either the local path or URL
    is_external: bool  # True for external URLs, False for local wiki-style links
    alt_text: Optional[str] = None  # Optional alt text/alias

    def to_string(self) -> str:
        if self.is_external:
            return f"![{self.alt_text}]({self.path})"
        elif self.alt_text is None:
            return f"![[{self.path}]]"
        else:
            return f"![[{self.path}|{self.alt_text}]]"


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

    type: Optional[str]
    content: List[str]

    def to_string(self) -> str:
        if not self.type:
            return f"[!]\n" + "\n".join(self.content)
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

    def date_to_string(self) -> None:
        for key, value in self.content.items():
            if isinstance(value, datetime):
                # print(f"    Found datetime: {value}, converting to string...")
                self.content[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(value, date):
                # print(f"    Found date: {value}, converting to string...")
                self.content[key] = value.strftime("%Y-%m-%d")


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


class PythonFrontMatter(DataType):
    """
    Base Pydantic model for a Python file's frontmatter. Same structure as Obsidian frontmatter, but using triple quotes as the delimiter.

    parameters: Dict[str, Any]

    """

    parameters: Dict[str, Any]

    def to_string(self) -> str:
        return (
            '"""\n'
            + "\n".join([f"{key}: {value}" for key, value in self.parameters.items()])
            + '\n"""'
        )

    def add(self, key: str, value: Any) -> None:
        self.parameters[key] = value

    def remove(self, key: str) -> None:
        if key in self.parameters:
            del self.parameters[key]

    def update(self, key: str, value: Any) -> None:
        if key in self.parameters:
            self.parameters[key] = value

    def date_to_string(self) -> None:
        for key, value in self.parameters.items():
            if isinstance(value, datetime):
                # print(f"    Found datetime: {value}, converting to string...")
                self.parameters[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(value, date):
                # print(f"    Found date: {value}, converting to string...")
                self.parameters[key] = value.strftime("%Y-%m-%d")


class PythonFileBase(DataType):
    """
    Base Pydantic model for a Python file.
    """

    frontmatter: PythonFrontMatter
    content: str

    def to_string(self) -> str:
        return f"{self.frontmatter.to_string()}\n{self.content}"

    def write(self, file_path: str) -> None:
        with open(file_path, "w") as file:
            file.write(self.to_string())


class FileBase(DataType):
    """
    Base Pydantic model for a file. Contains a frontmatter and a content attribute.
    """

    frontmatter: Union[FrontMatter, PythonFrontMatter]
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
    ImageLink,
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
