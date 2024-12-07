# Imports -------------------------------------------
import re
import yaml
from typing import Tuple, Dict

# Functions -----------------------------------------


def parse_obsidian_markdown(markdown_text: str) -> Tuple[Dict, str]:
    """
    Parses an Obsidian Markdown file into frontmatter and content.

    Args:
        markdown_text (str): The full content of the Markdown file.

    Returns:
        Tuple[Dict, str]: A tuple containing the frontmatter as a dictionary and the content as a string.

    Raises:
        ValueError: If the Markdown structure does not match the expected pattern.
        yaml.YAMLError: If the frontmatter is not valid YAML.
    """
    # Define the regex pattern
    pattern = re.compile(
        r"^---\s*\n"  # Start of frontmatter
        r"(?P<frontmatter>.*?)"  # Non-greedy match for frontmatter
        r"\n---\s*\n"  # End of frontmatter
        r"(?P<content>.*)",  # Capture the rest as content
        re.DOTALL,  # Make '.' match newlines
    )

    # Attempt to match the pattern
    match = pattern.match(markdown_text)
    if not match:
        raise ValueError(
            "Markdown file does not match the expected Obsidian format with frontmatter."
        )

    frontmatter_str = match.group("frontmatter").strip()
    content = match.group("content").strip()

    # Parse the YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_str) or {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML frontmatter: {e}")

    return frontmatter, content
