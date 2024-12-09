import pytest
from python_parser.src.parse_content import (
    Text,
    # Bold,
    # Italic,
    InlineCode,
    CodeBlock,
    WikiLink,
    ExternalLink,
    Tag,
    Header,
    # ListItem,
    Callout,
    FrontMatter,
    Paragraph,
    markdown_parser,
    paragraph,
    # bold,
    # italic,
    inline_code,
    wiki_link,
    external_link,
    tag,
    header,
    front_matter,
    callout,
    code_block,
    document,
    # inline_content,
)


# --- Inline Parser Tests ---
# def test_bold():
#    """Test bold text parsing with both ** and __ syntax"""
#    assert bold.parse("**bold**") == Bold([Text("bold")])
#    assert bold.parse("__bold__") == Bold([Text("bold")])

#    # Test with multiple words
#    assert bold.parse("**bold text**") == Bold([Text("bold text")])

#    # Test with nested inline elements
#    assert bold.parse("**bold *italic***") == Bold(
#        [Text("bold "), Italic([Text("italic")])]
#    )

#    # Test failure cases
#    with pytest.raises(Exception):
#        bold.parse("**unclosed")
#    with pytest.raises(Exception):
#        bold.parse("**mismatched__")


# def test_italic():
#    """Test italic text parsing with both * and _ syntax"""
#    assert italic.parse("*italic*") == Italic([Text("italic")])
#    assert italic.parse("_italic_") == Italic([Text("italic")])

#    # Test with multiple words
#    assert italic.parse("*italic text*") == Italic([Text("italic text")])

#    # Test with nested inline elements
#    assert italic.parse("*italic **bold***") == Italic(
#        [Text("italic "), Bold([Text("bold")])]
#    )

#    # Test failure cases
#    with pytest.raises(Exception):
#        italic.parse("*unclosed")
#    with pytest.raises(Exception):
#        italic.parse("*mismatched_")

# import pytest
# from markdown_parser import (
#    Text, InlineCode, CodeBlock, WikiLink, ExternalLink,
#    Tag, Header, Callout, FrontMatter, Paragraph,
#    markdown_parser, inline_code, wiki_link, external_link,
#    tag, header, code_block, front_matter, callout, paragraph
# )

# --- Inline Element Tests ---


def test_inline_code():
    """Test inline code parsing"""
    # Simple inline code
    assert inline_code.parse("`code`") == InlineCode("code")

    # Code with spaces
    assert inline_code.parse("` code with spaces `") == InlineCode(" code with spaces ")

    # Multiple words
    assert inline_code.parse("`multiple words here`") == InlineCode(
        "multiple words here"
    )

    # With special characters
    assert inline_code.parse("`code with * and # chars`") == InlineCode(
        "code with * and # chars"
    )

    # Test failure cases
    with pytest.raises(Exception):
        inline_code.parse("`unclosed")
    with pytest.raises(Exception):
        inline_code.parse("not code")
    with pytest.raises(Exception):
        inline_code.parse("``nested``")


def test_wiki_link():
    """Test wiki link parsing"""
    # Simple wiki link
    print(f"wiki_link: {wiki_link.parse('[[page]]')}")
    assert wiki_link.parse("[[page]]") == WikiLink("page", None)

    # Wiki link with spaces
    assert wiki_link.parse("[[my page]]") == WikiLink("my page", None)

    ## Wiki link with alias
    assert wiki_link.parse("[[page|alias]]") == WikiLink("page", "alias")

    ## Wiki link with spaces in both parts
    assert wiki_link.parse("[[my page|my alias]]") == WikiLink("my page", "my alias")

    # Test failure cases
    with pytest.raises(Exception):
        wiki_link.parse("[[unclosed")
    with pytest.raises(Exception):
        wiki_link.parse("[[]]")  # Empty link
    with pytest.raises(Exception):
        wiki_link.parse("[[|]]")  # Empty page and alias


def test_external_link():
    """Test external link parsing"""
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
        external_link.parse("[text](")
    with pytest.raises(Exception):
        external_link.parse("[](url)")  # Empty text


def test_tag():
    """Test tag parsing"""
    # Simple tag
    assert tag.parse("#tag") == Tag("tag")

    # Tag with numbers
    assert tag.parse("#tag123") == Tag("tag123")

    # Tag with hyphens and underscores
    assert tag.parse("#tag-with_symbols") == Tag("tag-with_symbols")

    # Test failure cases
    with pytest.raises(Exception):
        tag.parse("#")  # Empty tag
    with pytest.raises(Exception):
        tag.parse("#invalid tag")  # Space in tag
    with pytest.raises(Exception):
        tag.parse("#!invalid")  # Invalid character


# --- Block Level Tests ---


def test_header():
    """Test header parsing"""
    # Different header levels
    assert header.parse("# Header\n") == Header(1, "Header")
    assert header.parse("## Header\n") == Header(2, "Header")
    assert header.parse("### Header\n") == Header(3, "Header")

    # Header with multiple words
    assert header.parse("# Multiple words here\n") == Header(1, "Multiple words here")

    # Test failure cases
    with pytest.raises(Exception):
        header.parse("#Invalid\n")  # No space after #
    with pytest.raises(Exception):
        header.parse("# Header")  # No newline
    with pytest.raises(Exception):
        header.parse("####### Header\n")  # Too many #s


def test_code_block():
    """Test code block parsing"""
    # Simple code block
    assert code_block.parse("```\ncode\n```\n") == CodeBlock("code\n", None)

    # Code block with language
    assert code_block.parse("```python\ncode\n```\n") == CodeBlock("code\n", "python")

    # Multiple lines
    multi_line = """```
line 1
line 2
```
"""
    assert code_block.parse(multi_line) == CodeBlock("line 1\nline 2\n", None)

    # Test failure cases
    with pytest.raises(Exception):
        code_block.parse("```\nunclosed")
    with pytest.raises(Exception):
        code_block.parse("```\n```")  # No newline after closing


def test_front_matter():
    """Test front matter parsing"""
    simple_front_matter = """---
title: Test
---
"""
    result = front_matter.parse(simple_front_matter)
    assert isinstance(result, FrontMatter)

    # Test failure cases
    with pytest.raises(Exception):
        front_matter.parse("---\nunclosed")
    with pytest.raises(Exception):
        front_matter.parse("---")  # No content and no closing


def test_callout():
    """Test callout parsing"""
    # Simple callout
    simple_callout = """> [!NOTE]
> This is a note
"""
    assert callout.parse(simple_callout) == Callout("NOTE", ["This is a note"])

    # Multiple lines
    multi_line = """> [!WARNING]
> Line 1
> Line 2
"""
    assert callout.parse(multi_line) == Callout("WARNING", ["Line 1", "Line 2"])

    # Test failure cases
    with pytest.raises(Exception):
        callout.parse("> Invalid")  # No callout type
    with pytest.raises(Exception):
        callout.parse("> [!NOTE] Invalid")  # Invalid format


def test_paragraph():
    """Test paragraph parsing"""
    # Simple paragraph
    assert paragraph.parse("This is a paragraph\n") == Paragraph("This is a paragraph")

    # With special characters
    assert paragraph.parse("Para with *special* chars\n") == Paragraph(
        "Para with *special* chars"
    )

    # Test failure cases
    with pytest.raises(Exception):
        paragraph.parse("# Not a paragraph\n")
    with pytest.raises(Exception):
        paragraph.parse("> Not a paragraph\n")


# --- Integration Tests ---


def test_complete_document():
    """Test parsing a complete document"""
    doc = """---
title: Test Document
---

# Header

This is a paragraph with `code` and [[wiki-link]].

```python
def hello():
    print("world")
```

> [!NOTE]
> This is a callout
> With multiple lines
"""
    result = markdown_parser.parse(doc)

    # Verify structure
    assert len(result) > 0
    assert isinstance(result[0], FrontMatter)
    # print(f"Result: {result}")
    assert isinstance(result[1], Header)
    assert isinstance(result[2], Paragraph)
    assert isinstance(result[3], CodeBlock)
    assert isinstance(result[4], Callout)


def test_document_without_front_matter():
    """Test parsing a document without front matter"""
    doc = """# Header

Paragraph here.
"""
    result = markdown_parser.parse(doc)
    assert len(result) == 2
    assert isinstance(result[0], Header)
    assert isinstance(result[1], Paragraph)


def test_minimal_document():
    """Test parsing a minimal document"""
    doc = "Just a paragraph\n"
    result = markdown_parser.parse(doc)
    assert len(result) == 1
    assert isinstance(result[0], Paragraph)


if __name__ == "__main__":
    pytest.main([__file__])
