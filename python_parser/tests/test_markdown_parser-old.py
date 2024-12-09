import pytest

from python_parser.src.parse_content import (
    document,
    line,
    header_line,
    bullet_line,
    code_block,
    tag,
    link,
)


@pytest.mark.parametrize(
    "input_text,expected",
    [
        # Simple lines without markup
        (
            "Hello world\n",
            [{"type": "line", "content": [{"type": "text", "content": "Hello world"}]}],
        ),
        (
            "Just some text",
            [
                {
                    "type": "line",
                    "content": [{"type": "text", "content": "Just some text"}],
                }
            ],
        ),
        # Lines with tags and links
        (
            "Check this out #cool\n",
            [
                {
                    "type": "line",
                    "content": [
                        {"type": "text", "content": "Check this out "},
                        {"type": "tag", "name": "cool"},
                    ],
                }
            ],
        ),
        (
            "A link [[http://example.com|Example]] here\n",
            [
                {
                    "type": "line",
                    "content": [
                        {"type": "text", "content": "A link "},
                        {
                            "type": "link",
                            "address": "http://example.com",
                            "text": "Example",
                        },
                        {"type": "text", "content": " here"},
                    ],
                }
            ],
        ),
    ],
)
def test_line_parsing(input_text, expected):
    assert line.parse(input_text) == expected


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("# Heading 1\n", {"type": "header", "level": 1, "title": "Heading 1"}),
        ("## Subheading\n", {"type": "header", "level": 2, "title": "Subheading"}),
        (
            "### Another level\n",
            {"type": "header", "level": 3, "title": "Another level"},
        ),
    ],
)
def test_header_line_parsing(input_text, expected):
    assert header_line.parse(input_text) == expected


@pytest.mark.parametrize(
    "input_text,expected",
    [
        (
            "- A bullet point\n",
            {"type": "bullet", "indent": 0, "content": "A bullet point"},
        ),
        (
            "    - An indented bullet\n",
            {"type": "bullet", "indent": 4, "content": "An indented bullet"},
        ),
    ],
)
def test_bullet_line_parsing(input_text, expected):
    assert bullet_line.parse(input_text) == expected


def test_code_block_parsing():
    # Multi-line code block sample
    code_text = """```
print("Hello")
# comment
"""
    parsed = code_block.parse(code_text)
    expected = {
        "type": "code_block",
        "content": [
            {"type": "code_line", "content": 'print("Hello")'},
            {"type": "code_line", "content": "# comment"},
        ],
    }
    assert parsed == expected


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("#cool", {"type": "tag", "name": "cool"}),
        ("#tag123", {"type": "tag", "name": "tag123"}),
    ],
)
def test_tag_parsing(input_text, expected):
    assert tag.parse(input_text) == expected


@pytest.mark.parametrize(
    "input_text,expected",
    [
        (
            "[[http://example.com]]",
            {"type": "link", "address": "http://example.com", "text": None},
        ),
        (
            "[[http://example.com|Example]]",
            {"type": "link", "address": "http://example.com", "text": "Example"},
        ),
    ],
)
def test_link_parsing(input_text, expected):
    assert link.parse(input_text) == expected


def test_document_parsing_simple():
    md = """# Title Some text here

item 1
item 2
Subsection
Another line
"""
    parsed = document.parse(md)
    # Expected structure: a document with one section and a subsection
    expected = {
        "type": "document",
        "children": [
            {
                "type": "section",
                "level": 1,
                "title": "Title",
                "children": [
                    {
                        "type": "line",
                        "content": [{"type": "text", "content": "Some text here"}],
                    },
                    {"type": "bullet", "indent": 0, "content": "item 1"},
                    {"type": "bullet", "indent": 0, "content": "item 2"},
                    {
                        "type": "section",
                        "level": 2,
                        "title": "Subsection",
                        "children": [
                            {
                                "type": "line",
                                "content": [
                                    {"type": "text", "content": "Another line"}
                                ],
                            },
                        ],
                    },
                ],
            }
        ],
    }
    assert parsed == expected


def test_document_parsing_with_code_and_links():
    md = """# Top Section Check out this link [[http://example.com|Example]]

def foo():
    return "bar"

Next Section
A line with #atag and another [[link]] here
"""
    parsed = document.parse(md)
    # Expected structure includes code block, link, and tags in lines
    expected = {
        "type": "document",
        "children": [
            {
                "type": "section",
                "level": 1,
                "title": "Top Section",
                "children": [
                    {
                        "type": "line",
                        "content": [
                            {"type": "text", "content": "Check out this link "},
                            {
                                "type": "link",
                                "address": "http://example.com",
                                "text": "Example",
                            },
                        ],
                    },
                    {
                        "type": "code_block",
                        "content": [
                            {"type": "code_line", "content": "def foo():"},
                            {"type": "code_line", "content": '    return "bar"'},
                        ],
                    },
                    {
                        "type": "section",
                        "level": 2,
                        "title": "Next Section",
                        "children": [
                            {
                                "type": "line",
                                "content": [
                                    {"type": "text", "content": "A line with "},
                                    {"type": "tag", "name": "atag"},
                                    {"type": "text", "content": " and another "},
                                    {"type": "link", "address": "link", "text": None},
                                    {"type": "text", "content": " here"},
                                ],
                            },
                        ],
                    },
                ],
            }
        ],
    }
    assert parsed == expected
