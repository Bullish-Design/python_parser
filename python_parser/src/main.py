import os

# from python_parser.src.base import ObsidianFile
from python_parser.src.parser import parse_obsidian_markdown, parse_model_directory
from python_parser.src.config import TEST_DIR
from python_parser.src.models import MarkdownParser


# file_objs = parse_model_directory(TEST_DIR)


def main():
    output_files = []
    files = os.listdir(TEST_DIR)
    print(f"Found {len(files)} files in {TEST_DIR}:\n\nParsing results:\n")

    for file in files:
        filepath = os.path.join(TEST_DIR, file)
        if filepath.endswith(".md"):
            # print(f"\n**Parsing {file}**  |  {filepath}\n")
            parserObj = MarkdownParser()
            # print(f"**Parser: {parserObj}**\n")
            output = parserObj.parse(filepath)
            print(f"\n**Parsed: {file} | {type(output)}**\n\n{output}\n")
    print("\n\nDone.")
