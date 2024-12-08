# Imports -------------------------------------------
import os
import re
import yaml
from typing import Tuple, Dict, List
import parsy
from parsy import regex, string, generate

# Module Imports ------------------------------------
from python_parser.src.base import (
    # MarkdownModel,
    ObsidianFrontmatterParameter,
    ObsidianFrontmatter,
    ObsidianFile,
)
from python_parser.src.config import MD_MODEL_DIR


# Parsing Primitives --------------------------------
from python_parser.src.parse_primitives import (
    delimiter,
    frontmatter_content,
    content,
    lines_parser,
    newline,
    obsidian_start,
    indent,
    line,
)

# Constants -----------------------------------------

test_file = MD_MODEL_DIR + "/ObsidianFile.md"

markdown_file_content = """
---
title: Sample Document
author: John Doe
tags:
  - example
  - test
---

# Introduction

This is a sample Obsidian Markdown file.

- Point 1
- Point 2
"""

frontmatter_delim = obsidian_start.desc("Obsidian File Opening Delimiter")
bullet = (parsy.string("-") >> parsy.whitespace >> line).desc("Bullet")
list_property_val = (
    indent >> parsy.string("-") >> parsy.whitespace >> parsy.string << newline
)
# Full parser for the Obsidian Markdown file
basic_markdown_parser = parsy.seq(
    frontmatter_delim.skip(newline)
    >> frontmatter_content,  # .map(lambda x: x.strip().split("\n")),
    frontmatter_delim.skip(newline)
    >> content,  # .map(lambda x: x.strip().split("\n")),
)


@generate
def parse_content():
    pass


# Functions -----------------------------------------


def parse_misc():
    pass


def parse_frontmatter(frontmatter_dict: Dict) -> ObsidianFrontmatter:
    """
    Parses the frontmatter of an Obsidian Markdown file.
    Args:
        frontmatter_dict: The preliminarily parsed frontmatter and content after yaml.safe_load().
    Returns:
        ObsidianFrontmatter: A Pydantic model representing the frontmatter.
    """

    frontmatter_list = []

    # Parse the YAML frontmatter
    for key, value in frontmatter_dict.items():
        frontmatter_parameter = ObsidianFrontmatterParameter(name=key, value=value)
        frontmatter_list.append(frontmatter_parameter)
    frontmatter = ObsidianFrontmatter(parameters=frontmatter_list)

    return frontmatter


def parse_obsidian_markdown(markdown_text: str) -> ObsidianFile:
    """
    Parses an Obsidian Markdown file into frontmatter and content using Parsy.

    Args:
        markdown_text (str): The full content of the Markdown file.

    Returns:
        Tuple[Dict, str]: A tuple containing the frontmatter as a dictionary and the content as a string.

    Raises:
        parsy.ParseError: If the Markdown structure does not match the expected pattern.
        yaml.YAMLError: If the frontmatter is not valid YAML.
    """
    try:
        # Parse the markdown text to extract frontmatter and content
        frontmatter_str, content_str = basic_markdown_parser.parse(markdown_text)

        frontmatter = yaml.safe_load(frontmatter_str) or {}
        print(f"\n**Frontmatter **\n\n{frontmatter}\n")
        frontmatter = parse_frontmatter(frontmatter)
        obsidian_file = ObsidianFile(frontmatter=frontmatter, content=content_str)
        return obsidian_file
    except parsy.ParseError as pe:
        raise ValueError(
            "Markdown file does not match the expected Obsidian format with frontmatter."
        ) from pe
    except yaml.YAMLError as ye:
        raise yaml.YAMLError(f"Error parsing YAML frontmatter: {ye}") from ye


def parse_model_directory(file_dir: str) -> List[ObsidianFile]:
    """
    Parses all markdown files in the directory specified by MD_MODEL_DIR.
    """
    print(f"\nParsing Markdown files in directory: {file_dir}\n")
    # List all files in the directory
    output_files = []
    files = os.listdir(file_dir)
    for file in files:
        if file.endswith(".md"):
            with open(os.path.join(file_dir, file), "r") as f:
                markdown_text = f.read()
            print(
                f"-------------------------------- {file} --------------------------------\n"
            )
            # frontmatter, content = parse_obsidian_markdown(markdown_text)
            # parsed_frontmatter = parse_frontmatter(frontmatter)
            parsed_file = parse_obsidian_markdown(markdown_text)
            output_files.append(parsed_file)
            # print(f"**Frontmatter for {file}: [{type(parsed_file.frontmatter)}] **")
            # for parameter in parsed_file.frontmatter.parameters:
            #    print(f"    {parameter.name}: {parameter.value}")
            print(f"{parsed_file.frontmatter}")
            print(
                f"\n**Content for {file}: [{type(parsed_file.content)}] **\n{parsed_file.content}\n"
            )
    print("\n\nParsing complete.\n")
    return output_files
