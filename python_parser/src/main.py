import os

# from python_parser.src.base import ObsidianFile
from python_parser.src.parser import parse_obsidian_markdown, parse_model_directory
from python_parser.src.config import TEST_DIR
from python_parser.src.models import MarkdownParser
from python_parser.src.parse_content import document

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
            print(
                f"\n-------------------------------- {file} --------------------------------\n"
            )
            print(f"\n```\n{output.content}\n```\n")
            parsed_content = document.parse(output.content)
            print(f"\n{parsed_content}\n")
            # print(f"\n{output}\n")
    print("\n\nDone.")
