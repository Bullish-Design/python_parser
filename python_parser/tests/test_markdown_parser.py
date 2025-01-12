import pytest
from python_parser.src.models import (
    Text,
    # Bold,
    # Italic,
    InlineCode,
    CodeBlock,
    WikiLink,
    ExternalLink,
    ImageLink,
    Tag,
    Header,
    ListItem,
    Callout,
    FrontMatter,
    Paragraph,
    DB_Node,
    DB_Node_Tag,
    list_item,
    markdown_parser,
    basic_markdown_parser,
    paragraph,
    # bold,
    # italic,
    inline_code,
    wiki_link,
    external_link,
    image_link,
    image_external_link,
    image_wiki_link,
    tag,
    header,
    front_matter,
    callout,
    code_block,
    document,
    parse_references,
    db_node_tag,
    db_nodes,
    # inline_content,
)
# from python_parser.logs.logger import get_logger

# logger = get_logger(__name__)

# from python_parser.src.models import *

"""
from python_parser.src.models.datatypes import (
    Text,
    # Bold,
    # Italic,
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
)
from python_parser.src.models.parse_primitives import (
    list_item,
    markdown_parser,
    basic_markdown_parser,
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
"""

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


# --- Test DB_Node functionality ---


def test_db_node_tag_inline():
    logger.info("Testing DB_Node_Tag Inline")
    input_text = "%%node1|v1|sample%%"
    parsed = db_node_tag.parse(input_text)
    logger.info(f"  Parsed Tag: {parsed}")
    assert parsed.node_id == "node1"
    assert parsed.git_version == "v1"
    assert parsed.node_type == "sample"


def test_db_node_tag_no_git_version():
    logger.info("Testing DB_Node_Tag No Git Version")
    input_text = "%%nodeOnly%%"
    parsed = db_node_tag.parse(input_text)
    logger.info(f"  Parsed Tag: {parsed}")
    assert parsed.node_id == "nodeOnly"
    assert parsed.git_version == None
    # By default, if there's no block content or new line, it's considered inline
    assert parsed.node_type == None


def test_db_node_tag_block_node():
    logger.info("Testing DB_Node_Tag Block Node")
    input_text = """

    %%nodeBlock|v2|sample%%
    Some multiline content
    """
    parsed = db_nodes.parse(input_text)[0]
    logger.info(f"  Parsed Tag: {parsed}")
    assert parsed.node_tag.node_id == "nodeBlock"
    assert parsed.node_tag.git_version == "v2"
    assert parsed.node_tag.node_type == "sample"
    assert parsed.content == "\n    Some multiline content\n    "


def test_db_nodes_single_node():
    logger.info("Testing DB_Nodes Single Node")
    input_text = "%%nodeX|123|sample%%Node content here"
    parsed_list = db_nodes.parse(input_text)
    logger.info(f"  Parsed List: {parsed_list}")
    assert len(parsed_list) == 1
    assert parsed_list[0].node_tag.node_id == "nodeX"
    assert parsed_list[0].node_tag.git_version == "123"
    assert "Node content here" in parsed_list[0].content


def test_db_nodes_multiple_nodes():
    logger.info("Testing DB_Nodes Multiple Nodes")
    input_text = (
        "%%nodeA|vA|sample%%Content A%%nodeB|vB|sample%%Content B\n"
        "%%nodeC|vC|sample%%Content C"
    )
    parsed_list = db_nodes.parse(input_text)
    logger.info(f"  Parsed List: {parsed_list}")
    assert len(parsed_list) == 3

    assert parsed_list[0].node_tag.node_id == "nodeA"
    assert parsed_list[0].node_tag.git_version == "vA"
    assert "Content A" in parsed_list[0].content

    assert parsed_list[1].node_tag.node_id == "nodeB"
    assert parsed_list[1].node_tag.git_version == "vB"
    assert "Content B" in parsed_list[1].content

    assert parsed_list[2].node_tag.node_id == "nodeC"
    assert parsed_list[2].node_tag.git_version == "vC"
    assert "Content C" in parsed_list[2].content


def test_db_nodes_block_and_inline():
    logger.info("Testing DB_Nodes Block and Inline")
    input_text = (
        "%%inline|v1|sample%%Inline content\n"
        "%%block|v2|sample%%\n"
        "Block content on next line\n"
        "%%inline2|v3|sample%%Another inline"
    )
    parsed_list = db_nodes.parse(input_text)
    logger.info(f"  Parsed List: {parsed_list}")
    assert len(parsed_list) == 3

    assert parsed_list[0].node_tag.node_type == "sample"
    assert "Inline content" in parsed_list[0].content

    assert parsed_list[1].node_tag.node_type == "sample"
    assert "Block content on next line" in parsed_list[1].content

    assert parsed_list[2].node_tag.node_type == "sample"
    assert "Another inline" in parsed_list[2].content


# --- Inline Element Tests ---


def test_list_item():
    """Test list item parsing"""
    assert list_item.parse("- test") == ListItem(level=0, content="test")
    assert list_item.parse("  - test") == ListItem(level=1, content="test")
    assert list_item.parse("    - test") == ListItem(level=2, content="test")


def test_inline_code():
    """Test inline code parsing"""
    # Simple inline code
    assert inline_code.parse("`code`") == InlineCode(content="code")

    # Code with spaces
    assert inline_code.parse("` code with spaces `") == InlineCode(
        content=" code with spaces "
    )

    # Multiple words
    assert inline_code.parse("`multiple words here`") == InlineCode(
        content="multiple words here"
    )

    # With special characters
    assert inline_code.parse("`code with * and # chars`") == InlineCode(
        content="code with * and # chars"
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
    assert wiki_link.parse("[[page]]") == WikiLink(target="page", alias=None)

    # Wiki link with spaces
    assert wiki_link.parse("[[my page]]") == WikiLink(target="my page", alias=None)

    ## Wiki link with alias
    assert wiki_link.parse("[[page|alias]]") == WikiLink(target="page", alias="alias")

    ## Wiki link with spaces in both parts
    assert wiki_link.parse("[[my page|my alias]]") == WikiLink(
        target="my page", alias="my alias"
    )

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
    assert external_link.parse("[text](url)") == ExternalLink(url="url", text="text")

    # Link with spaces in text
    assert external_link.parse("[link text](url)") == ExternalLink(
        url="url", text="link text"
    )

    # Link with full URL
    assert external_link.parse("[text](https://example.com)") == ExternalLink(
        url="https://example.com", text="text"
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
    assert tag.parse("#tag") == Tag(name="tag")

    # Tag with numbers
    assert tag.parse("#tag123") == Tag(name="tag123")

    # Tag with hyphens and underscores
    assert tag.parse("#tag-with_symbols") == Tag(name="tag-with_symbols")

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
    assert header.parse("# Header\n") == Header(level=1, content="Header")
    assert header.parse("## Header\n") == Header(level=2, content="Header")
    assert header.parse("### Header\n") == Header(level=3, content="Header")

    # Header with multiple words
    assert header.parse("# Multiple words here\n") == Header(
        level=1, content="Multiple words here"
    )

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
    assert code_block.parse("```\ncode\n```\n") == CodeBlock(
        content="code\n", language=None
    )

    # Code block with language
    assert code_block.parse("```python\ncode\n```\n") == CodeBlock(
        content="code\n", language="python"
    )

    # Multiple lines
    multi_line = """```
line 1
line 2
```
"""
    assert code_block.parse(multi_line) == CodeBlock(
        content="line 1\nline 2\n", language=None
    )

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
    assert callout.parse(simple_callout) == Callout(
        type="NOTE", content=["This is a note"]
    )

    # Multiple lines
    multi_line = """> [!WARNING]
> Line 1
> Line 2
"""
    assert callout.parse(multi_line) == Callout(
        type="WARNING", content=["Line 1", "Line 2"]
    )

    # Test failure cases
    with pytest.raises(Exception):
        callout.parse("> Invalid")  # No callout type
    with pytest.raises(Exception):
        callout.parse("> [!NOTE] Invalid")  # Invalid format


def test_paragraph():
    """Test paragraph parsing"""
    # Simple paragraph
    assert paragraph.parse("This is a paragraph\n") == Paragraph(
        content="This is a paragraph"
    )

    # With special characters
    assert paragraph.parse("Para with *special* chars\n") == Paragraph(
        content="Para with *special* chars"
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
    result = document.parse(doc)
    # Verify structure
    # assert len(result) > 0
    assert isinstance(result[0], FrontMatter)
    body_result = result[1].nodes

    # print(f"Result: {result}")
    assert isinstance(body_result[0], Header)
    assert isinstance(body_result[1], Paragraph)
    assert isinstance(body_result[2], CodeBlock)
    assert isinstance(body_result[3], Callout)


def test_document_without_front_matter():
    """Test parsing a document without front matter"""
    doc = """# Header

Paragraph here.
"""
    result = markdown_parser.parse(doc)
    result = result.nodes

    assert len(result) == 2
    assert isinstance(result[0], Header)
    assert isinstance(result[1], Paragraph)


def test_minimal_document():
    """Test parsing a minimal document"""
    doc = "Just a paragraph\n"
    result = markdown_parser.parse(doc)
    result = result.nodes
    assert len(result) == 1
    assert isinstance(result[0], Paragraph)


# Tests for individual image link parsers
def test_local_image_basic():
    """Test basic local image parsing"""
    result = image_wiki_link.parse("![[image.png]]")
    assert isinstance(result, ImageLink)
    assert result.path == "image.png"
    assert result.is_external is False
    assert result.alt_text is None


def test_local_image_with_alt():
    """Test local image with alt text"""
    result = image_wiki_link.parse("![[photo.jpg|My vacation photo]]")
    assert isinstance(result, ImageLink)
    assert result.path == "photo.jpg"
    assert result.is_external is False
    assert result.alt_text == "My vacation photo"


def test_local_image_with_spaces():
    """Test local image with spaces in filename"""
    result = image_wiki_link.parse("![[my summer photo.jpg|Holiday 2023]]")
    assert isinstance(result, ImageLink)
    assert result.path == "my summer photo.jpg"
    assert result.alt_text == "Holiday 2023"


def test_external_image_basic():
    """Test basic external image parsing"""
    result = image_external_link.parse("![alt text](https://example.com/image.jpg)")
    assert isinstance(result, ImageLink)
    assert result.path == "https://example.com/image.jpg"
    assert result.is_external is True
    assert result.alt_text == "alt text"


def test_external_image_empty_alt():
    """Test external image with empty alt text"""
    result = image_external_link.parse("![](https://example.com/image.jpg)")
    assert isinstance(result, ImageLink)
    assert result.path == "https://example.com/image.jpg"
    assert result.is_external is True
    assert result.alt_text is None


def test_combined_image_parser():
    """Test that combined parser handles both types"""
    local = image_link.parse("![[local.png]]")
    assert isinstance(local, ImageLink)
    assert local.is_external is False

    external = image_link.parse("![alt](https://example.com/pic.jpg)")
    assert isinstance(external, ImageLink)
    assert external.is_external is True


# Tests for invalid inputs
def test_invalid_local_image():
    """Test that invalid local image syntax raises ParseError"""
    with pytest.raises(Exception):
        image_wiki_link.parse("[[image.png]]")  # Missing !
    with pytest.raises(Exception):
        image_wiki_link.parse("![[image.png")  # Unclosed brackets


def test_invalid_external_image():
    """Test that invalid external image syntax raises ParseError"""
    with pytest.raises(Exception):
        image_external_link.parse("[alt](image.jpg)")  # Missing !
    with pytest.raises(Exception):
        image_external_link.parse("![alt](image.jpg")  # Unclosed parenthesis


# Tests for images in complete markdown documents
def test_image_in_document():
    """Test parsing images within a complete markdown document"""
    markdown = """# My Document

This is a paragraph with a local image ![[photo.jpg|Holiday]] embedded in it.

Here's another paragraph with an external image ![sunset](https://example.com/sunset.jpg).

```python
# This is a code block
print("Hello")
```

And here's a final local image:
![[diagram.png]]
"""
    result = markdown_parser.parse(markdown)
    result = result.nodes

    # Find all ImageLink instances in the parsed result
    images = [node for node in result if isinstance(node, ImageLink)]

    assert any(img.path == "photo.jpg" and img.alt_text == "Holiday" for img in images)
    assert any(
        img.path == "https://example.com/sunset.jpg" and img.alt_text == "sunset"
        for img in images
    )
    assert any(img.path == "diagram.png" and img.alt_text is None for img in images)
    assert len(images) == 3


def test_complex_document_with_images():
    """Test parsing a more complex document with various elements including images"""
    markdown = """# Photo Gallery

## Local Images
Here's a local image: ![[vacation.jpg|Summer 2023]]

## External Images
And an external one: ![winter scene](https://example.com/winter.jpg)

```text
This is a code block that mentions images
![[not-an-image.png]]
![not-an-image](url)
```

### Mixed Content
- List item with ![[inline-image.png]]
- Another with ![external](https://example.com/pic.jpg)

Final paragraph with multiple images:
![[local1.png]] and ![external2](https://example.com/ext2.jpg)
"""
    result = markdown_parser.parse(markdown)
    result = result.nodes

    # Verify overall structure
    assert isinstance(result[0], Header)  # # Photo Gallery

    # Find all images
    images = [node for node in result if isinstance(node, ImageLink)]

    # Should find 5 images (not counting the ones in the code block)
    assert len(images) == 5

    # Verify specific images are found
    local_images = [img for img in images if not img.is_external]
    external_images = [img for img in images if img.is_external]

    assert len(local_images) == 2
    assert len(external_images) == 3

    # Verify specific image properties
    assert any(
        img.path == "vacation.jpg" and img.alt_text == "Summer 2023"
        for img in local_images
    )
    assert any(
        img.path == "https://example.com/winter.jpg" and img.alt_text == "winter scene"
        for img in external_images
    )


def test_document_edge_cases():
    """Test edge cases in document parsing with images"""
    # ![[]]  # Empty local image

    markdown = """# Edge Cases

![](https://example.com/img.jpg)  # Empty alt text
![[image with spaces.jpg|alt with spaces]]
![alt with spaces](https://example.com/spaces in url.jpg)

![[nested/path/image.png]]  # Image in subfolder
![](https://example.com/path?param=value#fragment)  # URL with query and fragment
"""

    result = markdown_parser.parse(markdown)
    result = result.nodes
    images = [node for node in result if isinstance(node, ImageLink)]

    # Verify specific edge cases
    paths = [img.path for img in images]
    assert "nested/path/image.png" in paths
    assert "https://example.com/path?param=value#fragment" in paths
    assert "image with spaces.jpg" in paths
    # assert "https://example.com/spaces in url.jpg" in paths
    assert len(images) == 5


def test_parse_references():
    """Test that references are parsed correctly"""
    markdown = """# References

Just testing ![](https://example.com/img.jpg) that this thing works. # Empty alt text ![[image with spaces.jpg|alt with spaces]]

Maybe this works too? ![alt with spaces](https://example.com/spaces in url.jpg) And again, lets see what's what.

![[nested/path/image.png]]  # Image in subfolder
![](https://example.com/path?param=value#fragment)  # URL with query and fragment
"""
    result = markdown_parser.parse(markdown)
    result = result.nodes

    links = []
    for node in result:
        node_links = parse_references(node.to_string())
        links.extend(node_links)

    for link in links:
        print(f"Link: {link}")
    assert (
        links[0] == "![](https://example.com/img.jpg)"
    )  # "https://example.com/img.jpg"


def test_mixed_tag_quotes():
    """Test that tags with mixed quotes are parsed correctly"""
    markdown = """### Tip

`pkgs.fetchFrom*` helpers retrieve *snapshots* of version-controlled sources, as opposed to the entire version history, which is more efficient. `pkgs.fetchgit` by default also has the same behaviour, but can be changed through specific attributes given to it.

## Caveats

Because Nixpkgs fetchers are fixed-output derivations, an [output hash](https://nixos.org/manual/nix/stable/language/advanced-attributes#adv-attr-outputHash) has to be specified, usually indirectly through a `hash` attribute. This hash refers to the derivation output, which can be different from the remote source itself!

This has the following implications that you should be aware of:

- Use Nix (or Nix-aware) tooling to produce the output hash.
- When changing any fetcher parameters, always update the output hash. Use one of the methods from [the section called “Updating source hashes”](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-fetchers-updating-source-hashes "Updating source hashes"). Otherwise, existing store objects that match the output hash will be re-used rather than fetching new content.
"""
    result = markdown_parser.parse(markdown)
    result = result.nodes
    print(f"\nMixed tag nodes:")
    for node in result:
        print(f"   {type(node).__name__}: {node}")

    assert isinstance(result[0], Header)
    assert isinstance(result[1], Paragraph)
    assert isinstance(result[2], Header)
    assert isinstance(result[3], Paragraph)


if __name__ == "__main__":
    pytest.main([__file__])
