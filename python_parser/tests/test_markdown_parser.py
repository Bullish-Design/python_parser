import pytest
from python_parser.src.parse_content import (
    Text,
    Bold,
    Italic,
    InlineCode,
    CodeBlock,
    WikiLink,
    ExternalLink,
    Tag,
    Header,
    ListItem,
    Callout,
    FrontMatter,
    Paragraph,
    bold,
    italic,
    inline_code,
    wiki_link,
    external_link,
    tag,
    header,
    front_matter,
    callout,
    document,
    inline_content,
)

# --- Inline Parser Tests ---


def test_bold():
    """Test bold text parsing with both ** and __ syntax"""
    assert bold.parse("**bold**") == Bold([Text("bold")])
    assert bold.parse("__bold__") == Bold([Text("bold")])

    # Test with multiple words
    assert bold.parse("**bold text**") == Bold([Text("bold text")])

    # Test with nested inline elements
    assert bold.parse("**bold *italic***") == Bold(
        [Text("bold "), Italic([Text("italic")])]
    )

    # Test failure cases
    with pytest.raises(Exception):
        bold.parse("**unclosed")
    with pytest.raises(Exception):
        bold.parse("**mismatched__")


def test_italic():
    """Test italic text parsing with both * and _ syntax"""
    assert italic.parse("*italic*") == Italic([Text("italic")])
    assert italic.parse("_italic_") == Italic([Text("italic")])

    # Test with multiple words
    assert italic.parse("*italic text*") == Italic([Text("italic text")])

    # Test with nested inline elements
    assert italic.parse("*italic **bold***") == Italic(
        [Text("italic "), Bold([Text("bold")])]
    )

    # Test failure cases
    with pytest.raises(Exception):
        italic.parse("*unclosed")
    with pytest.raises(Exception):
        italic.parse("*mismatched_")


def test_inline_code():
    """Test inline code parsing"""
    assert inline_code.parse("`code`") == InlineCode("code")

    # Test with spaces
    assert inline_code.parse("` code with spaces `") == InlineCode(" code with spaces ")

    # Test failure cases
    with pytest.raises(Exception):
        inline_code.parse("`unclosed")


def test_wiki_link():
    """Test Obsidian wiki link parsing"""
    # Simple wiki link
    assert wiki_link.parse("[[page]]") == WikiLink("page", None)

    # Wiki link with alias
    assert wiki_link.parse("[[page|alias]]") == WikiLink("page", "alias")

    # Wiki link with spaces
    assert wiki_link.parse("[[my page]]") == WikiLink("my page", None)

    # Test failure cases
    with pytest.raises(Exception):
        wiki_link.parse("[[unclosed")
    with pytest.raises(Exception):
        wiki_link.parse("[[invalid|alias|extra]]")


def test_external_link():
    """Test markdown link parsing"""
    # Simple link
    assert external_link.parse("[text](url)") == ExternalLink("url", "text")

    # Link with spaces in text
    assert external_link.parse("[link text](url)") == ExternalLink("url", "link text")

    # Link with full URL
    assert external_link.parse("[text](https://example.com)") == ExternalLink(
        "https://example.com", "text"
    )

    # Test failure cases
    with pytest.raises(Exception):
        external_link.parse("[unclosed](url")
    with pytest.raises(Exception):
        external_link.parse("[text](unclosed")


def test_tag():
    """Test Obsidian tag parsing"""
    # Simple tag
    assert tag.parse("#tag") == Tag("tag")

    # Tag with numbers
    assert tag.parse("#tag123") == Tag("tag123")

    # Tag with hyphens and underscores
    assert tag.parse("#tag-with_symbols") == Tag("tag-with_symbols")

    # Test failure cases
    with pytest.raises(Exception):
        tag.parse("#")
    with pytest.raises(Exception):
        tag.parse("#invalid tag")


# --- Block Parser Tests ---


def test_header():
    """Test header parsing"""
    # Different header levels
    assert header.parse("# Header 1\n") == Header(1, [Text("Header 1")])
    assert header.parse("## Header 2\n") == Header(2, [Text("Header 2")])
    assert header.parse("### Header 3\n") == Header(3, [Text("Header 3")])

    # Header with inline elements
    assert header.parse("# Header with *italic*\n") == Header(
        1, [Text("Header with "), Italic([Text("italic")])]
    )

    # Test failure cases
    with pytest.raises(Exception):
        header.parse("#Invalid")  # No space after #
    with pytest.raises(Exception):
        header.parse("# Unclosed")  # No newline


def test_front_matter():
    """Test YAML front matter parsing"""
    simple_front_matter = """---
title: Test
date: 2024-01-01
---
"""
    result = front_matter.parse(simple_front_matter)
    assert isinstance(result, FrontMatter)

    # Test failure cases
    with pytest.raises(Exception):
        front_matter.parse("---\nunclosed")
    with pytest.raises(Exception):
        front_matter.parse("--invalid--")


def test_callout():
    """Test Obsidian callout parsing"""
    simple_callout = """> [!NOTE]
> This is a note
> Second line
"""
    result = callout.parse(simple_callout)
    assert result == Callout("NOTE", [[Text("This is a note")], [Text("Second line")]])

    # Test failure cases
    with pytest.raises(Exception):
        callout.parse("> Invalid")
    with pytest.raises(Exception):
        callout.parse("> [!NOTE] Invalid")


# --- Integration Tests ---


def test_inline_content():
    """Test parsing of mixed inline content"""
    text = "Normal text with **bold** and *italic* and `code` and [[wiki]] and #tag"
    result = inline_content.parse(text)
    assert result == [
        Text("Normal text with "),
        Bold([Text("bold")]),
        Text(" and "),
        Italic([Text("italic")]),
        Text(" and "),
        InlineCode("code"),
        Text(" and "),
        WikiLink("wiki", None),
        Text(" and "),
        Tag("tag"),
    ]


def test_complete_document():
    """Test parsing a complete Obsidian document"""
    doc = """---
title: Test Document
---

# Header 1

Normal paragraph with **bold** and *italic*.

> [!NOTE]
> This is a callout
> With multiple lines

[[wiki-link]] and #tag
"""
    result = document.parse(doc)
    # Assert based on expected structure
    assert isinstance(result[0], FrontMatter)
    assert isinstance(result[1], Header)
    assert isinstance(result[2], Paragraph)
    assert isinstance(result[3], Callout)
    assert isinstance(result[4], Paragraph)


# --- Helper Function Tests ---


def test_nested_formatting():
    """Test handling of nested formatting elements"""
    text = "**Bold with *italic* inside**"
    result = inline_content.parse(text)
    assert result == [
        Bold([Text("Bold with "), Italic([Text("italic")]), Text(" inside")])
    ]


def test_edge_cases():
    """Test various edge cases and potential problem areas"""
    # Empty elements
    assert bold.parse("****") == Bold([])
    assert italic.parse("**") == Italic([])

    # Escaped characters
    # Note: Add these tests after implementing escape character handling

    # Mixed nested elements
    text = "**Bold _italic_ `code`**"
    result = inline_content.parse(text)
    assert isinstance(result[0], Bold)

    # Unicode content
    text = "**Bold 你好**"
    result = bold.parse(text)
    assert result == Bold([Text("Bold 你好")])


if __name__ == "__main__":
    pytest.main([__file__])
