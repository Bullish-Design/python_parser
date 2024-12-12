import os
from dataclasses import dataclass

from python_parser.src.base import (
    # ParserBase,
    # GeneratorBase,
    # ParserGeneratorBase,
    # DataShape,
    FileParserBase,
    ObsidianParserBase,
)

# from python_parser.src.parser import parse_obsidian_markdown, parse_model_directory
from python_parser.src.config import TEST_DIR, MD_MODEL_DIR

# from python_parser.src.models import MarkdownParser
from python_parser.src.parse_content import (
    document,
    block,
    front_matter,
    basic_markdown_parser,
    FrontMatter,
    Header,
    # MarkdownRule,
    # MarkdownRuleProcessor,
    # MarkdownRuleWatcher,
)  # , line


# file_objs = parse_model_directory(TEST_DIR)

# Constants ---------------------------------------------

# Tag list for directory watcher ------------------------
tag_list = ["#newModel"]


# Functions ---------------------------------------------
## Processors -------------------------------------------
def print_nodes(processed_results):
    # print(f"\nNodes:")
    # for item in processed_results.nodes:
    #    print(f"  {item.to("md")}")
    return processed_results


def create_pydantic_model(processed_results):
    print(f"\nCreating Obsidian File:")
    # print(f"\n{processed_results}\n")
    return processed_results


# def compare_shape(processed_results, input_shape: DataShape):
#    print_nodes(processed_results)
#    comparison = input_shape.compare(processed_results)
#    # print(f"\n>> Comparison result is: {comparison}")
#    return processed_results


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


# DataShape instances -----------------------------------

# pydantic_md_file = DataShape(
#    shape=[
#        # "FrontMatter",
#        Header(level=1, content="*"),
#        Header(level=2, content="Attributes:"),
#    ]
# )


## Post-processing file modification updates as decorator for MarkdownRuleProcesors?


# Parser Files in Directory ---------------------
def parse_dir(file_type: str, directory: str):
    # Get list of files in directory
    files = os.listdir(directory)
    for file in files:
        if file.endswith(file_type):
            print(
                f"\n\n\n-------------------------------- Processing {file} --------------------------------"
            )
            # print(f"\nProcessing {file} |  {filepath}\n")
            watcher.process_file(filepath)


obsidianParser = FileParserBase(file_type="md", parser=basic_markdown_parser)
full_doc_parser = ObsidianParserBase(content_parser=document)


def main():
    output_files = []
    # md_parser = MarkdownParser()
    test_dir = TEST_DIR  # MD_MODEL_DIR
    files = os.listdir(test_dir)
    print(f"Found {len(files)} files in {test_dir}:\n\nParsing results:\n")

    # watcher = MarkdownRuleWatcher()
    # rule = modified_file_rule
    # watcher.add_rule(rule)

    for file in files:
        filepath = os.path.join(test_dir, file)
        if filepath.endswith("md"):
            print(
                f"\n\n\n-------------------------------- Processing {file} --------------------------------"
            )
            # print(f"\nProcessing {file} |  {filepath}\n")
            # watcher.process_file(filepath)
            prelim_parsed_file = full_doc_parser(filepath)
            print(f"\nFrontmatter:")
            for key, value in prelim_parsed_file.frontmatter.content.items():
                print(f"  {key}: {value}")
            print(f"\nContent:")
            for item in prelim_parsed_file.content.nodes:
                print(f"  {item}")
    print("\n\nDone.")
    # print(f"\n\n{md_parser}\n\n")
