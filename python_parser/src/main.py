# Imports ------------------------------
import os

# Library Imports -----------------------

from python_parser.src.base import (
    # ParserBase,
    # GeneratorBase,
    # ParserGeneratorBase,
    # DataShape,
    FileParserBase,
    ObsidianParserBase,
)
from python_parser.src.config import TEST_DIR, MD_MODEL_DIR
from python_parser.src.models import (
    document,
    basic_markdown_parser,
)

# Constants ---------------------------------------------

tag_list = ["#newModel"]


# Functions ---------------------------------------------
def print_nodes(processed_results):
    # print(f"\nNodes:")
    # for item in processed_results.nodes:
    #    print(f"  {item.to("md")}")
    return processed_results


def create_pydantic_model(processed_results):
    print(f"\nCreating Obsidian File:")
    # print(f"\n{processed_results}\n")
    return processed_results


## Post Processors --------------------------------------
def update_frontmatter_value(file_path: str, key: str, value: str):
    """
    Updates the status of the file to 'processed'
    """
    print(f"\nUpdating status of {file_path} to 'processed'\n")

    with open(file_path, "r") as file:
        file_contents = file.read()
    markdown_base = basic_markdown_parser.parse(file_contents)
    # print(f"\nInitial Frontmatter: \n {markdown_base.frontmatter}")
    markdown_base.frontmatter.update(key=key, value=value)

    # print(f"\nUpdated Frontmatter: \n {markdown_base.frontmatter}")
    markdown_base.write(file_path)
    # print(f"\nWrote file to disk\n")

    return True


def update_status(file_path: str, file_contents: str):
    key = "status"
    value = "processed"
    result = update_frontmatter_value(file_path, key, value)
    if result is True:
        print(f"\nStatus of {file_path} updated to 'processed'\n\n")
        return file_contents
    return result


# Classes -----------------------------------------------

obsidianParser = FileParserBase(file_type="md", parser=basic_markdown_parser)
full_doc_parser = ObsidianParserBase(content_parser=document)


# Main -------------------------------------------------
def main():
    test_dir = TEST_DIR  # MD_MODEL_DIR
    files = os.listdir(test_dir)
    print(f"Found {len(files)} files in {test_dir}:\n\nParsing results:\n")

    for file in files:
        filepath = os.path.join(test_dir, file)
        if filepath.endswith("md"):
            print(
                f"\n\n\n-------------------------------- Processing {file} --------------------------------"
            )
            prelim_parsed_file = full_doc_parser(filepath)
            print(f"\nFrontmatter:")
            for key, value in prelim_parsed_file.frontmatter.content.items():
                print(f"  {key}: {value}")
            print(f"\nContent:")
            for item in prelim_parsed_file.content.nodes:
                print(f"  {item}")
    print("\n\nDone.")
