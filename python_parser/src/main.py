import os

from python_parser.src.base import ObsidianFile

from python_parser.src.parser import parse_obsidian_markdown, parse_model_directory

from python_parser.src.config import TEST_DIR

file_objs = parse_model_directory(TEST_DIR)


def main():
    print(f"Found {len(file_objs)} files in {TEST_DIR}:\n\nParsing results:\n")
    for file_obj in file_objs:
        print(file_obj)
        print("\n")
