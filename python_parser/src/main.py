import os
from dataclasses import dataclass

# from python_parser.src.base import ObsidianFile
from python_parser.src.parser import parse_obsidian_markdown, parse_model_directory
from python_parser.src.config import TEST_DIR, MD_MODEL_DIR
from python_parser.src.models import MarkdownParser
from python_parser.src.parse_content import (
    document,
    block,
    front_matter,
    MarkdownRule,
    MarkdownRuleProcessor,
    MarkdownRuleWatcher,
)  # , line

# file_objs = parse_model_directory(TEST_DIR)

# Constants ---------------------------------------------

# Tag list for directory watcher ------------------------
tag_list = ["#newModel"]


# Functions ---------------------------------------------
## Processors -------------------------------------------
def print_nodes(processed_results):
    print(f"\nNodes:")
    for item in processed_results.nodes:
        print(f"  {item}")
    return processed_results


def create_pydantic_model(processed_results):
    print(f"\nCreating Obsidian File:")
    print(f"\n{processed_results}\n")
    return processed_results


# Classes -----------------------------------------------

# MarkdownRule Classes ----------------------------------


# A Class to process files with a status of "modified"
class ModifiedFileRule(MarkdownRule):
    frontmatter_conditions = {"status": "modified"}
    parser = document
    processor = print_nodes


def main():
    output_files = []
    test_dir = MD_MODEL_DIR
    files = os.listdir(test_dir)
    print(f"Found {len(files)} files in {test_dir}:\n\nParsing results:\n")

    watcher = MarkdownRuleWatcher()
    watcher.add_rule(ModifiedFileRule)

    for file in files:
        filepath = os.path.join(test_dir, file)
        if filepath.endswith(".md"):
            print(
                f"\n\n\n-------------------------------- {file} --------------------------------\n"
            )
            print(f"\nProcessing {file} |  {filepath}\n")
            watcher.process_file(filepath)
            # print(f"\n**Parsing {file}**  |  {filepath}\n")
            # parserObj = MarkdownParser()
            # parserObj = document
            # print(f"**Parser: {parserObj}**\n")
            # output = parserObj.parse(filepath)
            # print(
            #    f"\n-------------------------------- {file} --------------------------------\n"
            # )
            # print(f"Frontmatter:")
            # for item in output.frontmatter.parameters:
            #    print(f"  {item}")
            # print(f"\nContent:")
            # parsed_content = document.parse(output.content)
            # for item in parsed_content.nodes:
            #    print(f"  {item}")
            # print(f"\n{parsed_content}\n")
            # print(f"\n{output}\n")
    print("\n\nDone.")
