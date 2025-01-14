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
    Section,
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
    section,
    # inline_content,
)
from python_parser.src.models.datatypes_v2 import split_content, split_sections
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
    # logger.info("Testing DB_Node_Tag Inline")
    input_text = "%%node1|v1|sample%%"
    parsed = db_node_tag.parse(input_text)
    # logger.info(f"  Parsed Tag: {parsed}")
    assert parsed.node_id == "node1"
    assert parsed.git_version == "v1"
    assert parsed.node_type == "sample"


def test_db_node_tag_no_git_version():
    # logger.info("Testing DB_Node_Tag No Git Version")
    input_text = "%%nodeOnly%%"
    parsed = db_node_tag.parse(input_text)
    # logger.info(f"  Parsed Tag: {parsed}")
    assert parsed.node_id == "nodeOnly"
    assert parsed.git_version == None
    # By default, if there's no block content or new line, it's considered inline
    assert parsed.node_type == None


def test_db_node_tag_block_node():
    # logger.info("Testing DB_Node_Tag Block Node")
    input_text = """

    %%nodeBlock|v2|sample%%
    Some multiline content
    """
    parsed = db_nodes.parse(input_text)[0]
    # logger.info(f"  Parsed Tag: {parsed}")
    assert parsed.node_tag.node_id == "nodeBlock"
    assert parsed.node_tag.git_version == "v2"
    assert parsed.node_tag.node_type == "sample"
    assert parsed.content == "\n    Some multiline content\n    "


def test_db_nodes_single_node():
    # logger.info("Testing DB_Nodes Single Node")
    input_text = "%%nodeX|123|sample%%Node content here"
    parsed_list = db_nodes.parse(input_text)
    # logger.info(f"  Parsed List: {parsed_list}")
    assert len(parsed_list) == 1
    assert parsed_list[0].node_tag.node_id == "nodeX"
    assert parsed_list[0].node_tag.git_version == "123"
    assert "Node content here" in parsed_list[0].content


def test_db_nodes_multiple_nodes():
    # logger.info("Testing DB_Nodes Multiple Nodes")
    input_text = (
        "%%nodeA|vA|sample%%Content A%%nodeB|vB|sample%%Content B\n"
        "%%nodeC|vC|sample%%Content C"
    )
    parsed_list = db_nodes.parse(input_text)
    # logger.info(f"  Parsed List: {parsed_list}")
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
    # logger.info("Testing DB_Nodes Block and Inline")
    input_text = (
        "%%inline|v1|sample%%Inline content\n"
        "%%block|v2|sample%%\n"
        "Block content on next line\n"
        "%%inline2|v3|sample%%Another inline"
    )
    parsed_list = db_nodes.parse(input_text)
    # logger.info(f"  Parsed List: {parsed_list}")
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


def test_sample_files():
    file_1 = """---
id: Notes
aliases: []
tags: []
---
%%mYvdWaq9ogP627SSqfFffP|0.0.0|ObsidianFile%%
# Python_Parser

# What:
A parsing library that utilizes Obsidian based markdown templates as a source to generate the to/from regex based parsing models. 



# Why:
A flexible starting point to "self-bootstrap" an obsidian based development environment. 

Utilize LLM agents as semi-smart "text-expander" functionality. 



# Goals:


# Outline:


# My Questions:


# Learnings:


# Resources:


# Tasks:


# Log:
 - [[Projects/python_parser/Daily/24-49-1.md|24-49-1]]
 - [[Projects/python_parser/Daily/24-49-2.md|24-49-2]]
 - [[Projects/python_parser/Daily/24-49-3.md|24-49-3]]
 - [[Projects/python_parser/Daily/24-49-5.md|24-49-5]]
 - [[Projects/python_parser/Daily/24-50-3.md|24-50-3]]
 - [[Projects/python_parser/Daily/24-50-4.md|24-50-4]]
 - [[Projects/python_parser/Daily/24-50-7.md|24-50-7]]
 - [[Projects/python_parser/Daily/24-51-2.md|24-51-2]]
 - [[Projects/python_parser/Daily/25-01-6.md|25-01-6]]
 - [[Projects/python_parser/Daily/25-01-7.md|25-01-7]]
 - [[Projects/python_parser/Daily/_index.md|_index]]
"""
    file_2 = """---
id: bGa9Dj5rrKMoobFou6T2vJ
vault_path: z-archive/Design-inspiration-the-best-projects-from-December.md
---
%%nBWaanUtQAXX22VDzGFhBb|0.0.0|ObsidianFile%%
### Black Lines brand identity, by Test & Smith

Black Lines wants it to be as easy to serve a Negroni as it is a pint of lager. The drinks company is seeking to revolutionise the bar experience by serving cocktails by draught with a changing menu of drinks (as well as same favourite stand-bys). A pink grapefruit spritz was served through the summer while a new pear and white tea fizz joins the line-up for winter.

1. ROFL means Rolling on floor laughing.
2. STFU means Shut the *freak* up.
3. LMK means Let me know.
4. ILY means I love you.
5. YOLO means You only live once.
6. SMH means Shaking my head.

![[images/Design-inspiration-the-best-projects-from-December-1.png]]

The company was previously known as Hingston + Co. but has been given a complete rebrand — including a new logo, tap badges, website and branded material — by London-based design studio & Smith. The new identity is based on the Kandinsky abstract painting, Black Lines, and true to its name, is mostly black and white with a few flashes of colour. According to & Smith, the identity brings together “art and science” and has been brought to life through collaborations with nine illustrators.

1. ROFL means Rolling on floor laughing.
2. STFU means Shut the *freak* up.
3. LMK means Let me know.
4. ILY means I love you.
5. YOLO means You only live once.
6. SMH means Shaking my head.

![blog-details-image-02](https://user-images.githubusercontent.com/16266381/71399826-2009b380-264f-11ea-9bc3-59d7fa9a9994.jpg)

Black Lines wants it to be as easy to serve a Negroni as it is a pint of lager. The drinks company is seeking to revolutionise the bar experience by serving cocktails by draught with a changing menu of drinks (as well as same favourite stand-bys). A pink grapefruit spritz was served through the summer while a new pear and white tea fizz joins the line-up for winter.

> "The public is more familiar with bad design than good design. It is, in effect, conditioned to prefer bad design, because that is what it lives with. The new becomes threatening, the old reassuring."


> Paul Rand, graphic designer

"""
    file_3 = """---
title: OSEN CLOCK
date: 2019-12-23 15:56:43+06:00
type: portfolio
image: images/projects/project-thumb-two.jpg
category: ['PRODUCT DESIGN', 'REBRAND']
project_images: ['images/projects/project-details-image-one.jpg', 'images/projects/project-details-image-two.jpg']
id: RUspmRy5iw9cqkL2KJFsot
vault_path: z-archive/osen-clock.md
---
%%DphAAcJ6iFzNksbbsGYMCs|0.0.0|ObsidianFile%%
# Title Test
## Multi category test
The “Seamless Watch” watch has all the features that users expect in a digital watch, and some unusual features.


The watch has the following features:

Time and date displayed on the screen. Current time is in large numbers, date is in small numbers above it.

Light: Pressing the light button on the side of the watch activates a light while the button is pressed. Pressing and holding that button for 3 seconds turns on the light and keeps it on, until the button is held again for 3 seconds or up to 2 hours. After 2 hours, it will automatically turn off.

Alarm. A daily alarm may be set for a given time. The alarm may be enabled or disabled. When the alarm is enabled and the alarm time is reached, the watch will beep fast for 5 seconds, then slowly for 30 seconds, then fast for another 5 seconds. Pressing any button stops the alarm sound (in addition to performing its normal function).

Timer. Timer mode shows a count-up timer that starts at 00:00. When the timer is started, it counts up. Pressing the start/stop button will pause the timer, pressing it again continues counting up. Pressing and holding the button for 3 seconds resets the timer to 00:00 and stops counting.

Mystery answer. After entering this mode, the screen initially displays “ask now”. The user may ask a yes-or-no question aloud and press the start/stop button, this will display a randomly selected answer that is one of the following: “yeah”, “yeah right”, “no”, “no doubt”, “keep trying”, “keep dreaming”. Whenever the display has more than one word, only one word is displayed for 2 seconds, then the other word is displayed for 2 seconds, alternately. The answer is displayed until the user leaves this mode, or he/she presses start/stop again for a new answer. 


Note: these strings are for the English version of the watch, we will need to use completely different strings in other countries without reprogramming the logic of the watch.

The user may cycle among all modes (date/time, timer, mystery answer) by pressing the mode button."""
    file_4 = """---
id: XKgQGLKYMxpyrkC9EhWN9Z
vault_path: Thoughts/Research/Web/16elt.com /Ideas from A Philosophy of Software Design 2.md
---
%%SZSTe8fGmMLfCeMj6EtQrz|0.0.0|ObsidianFile%%
# My Thoughts:


# Related:


# Content:

![SETI (The Search for Extraterrestrial Intelligence) Temporary Exhibit at the National Cryptologic Museum](https://media.defense.gov/2024/Oct/28/2003571989/1920/1080/0/241028-D-IM742-1111.JPG)

PHOTO INFORMATION

From psychics to extraterrestrial communication, new temporary and permanent exhibits at the National Cryptologic Museum will have you scratching your head.

With exhibit labels like "Mind over Matter" and "What the What?"—museum visitors will go from, “What in the world?” to “What if?” The exhibits explore the extraordinary practice of using psychics to gain information from the enemy.

#### New Temporary Exhibits

 

Project Star Gate was used by the U.S. Government during the Cold War. Many of the psychic spies were at Ft. Meade, tasked with collecting intelligence, locating enemy agents and determining American vulnerabilities by using “remote viewing.” Remote viewing is mentally viewing a distant location they have never visited to gather insights on a person, site, or specific information. As outrageous as it sounds, the secret program was very successful and was in use until 1995.

A standout in the remote viewing field, Agent 001 of Project Star Gate Joe McMoneagle has been involved in over 200 intelligence missions utilizing his unique set of skills. His distinct collection of drawings (as a result of his remote viewing missions) were used to assist in combat and are a part of the current exhibit.

The exhibit even explores the brief moments in history that the U.S and Russia’s relationship wasn’t quite as contentious. See astounding sketches and the landscapes they match up to!

Plus, see the machine, altered by the mind to change its output! Don’t believe us? Come see for yourself, only at the NCM!

Psychics aren’t the only twilight zoneish content this fall.

SETI (The Search for Extraterrestrial Intelligence) also makes its debut at the NCM. The museum created a theatre room for guests to watch a video about the search for alien life and how researchers go under the sea to make connections.

Using anticryptography methods (a cryptographic message that is easy to decipher), the scientists detail their use of radio signals in their search for intelligent life in the universe. See a circuit board that digitized cosmic signals and more in the quest to communicate with alien life.

Be sure to plan your next visit soon as these temporary exhibits will only be on display through mid-December!

#### New Permanent Exhibits

 

The Museum has also added several permanent new exhibits as well.

The Language Whiteboard is a linguists’ delight!  It’s a compilation of all the languages we make use of at the agency. It came from the National Cryptologic University’s College of Language and Area Studies, where instructors created the artwork to use a teaching tool. It hung in a language classroom for many years before being “retired” to the National Cryptologic Museum.

While the museum has had several pieces of the Berlin Wall in its collection, the “You Are Leaving the American Sector” sign is a new addition. It was acquired by an American after the fall of the Berlin Wall. The iconic symbol of the Cold War is on display now.

*The National Cryptologic Museum is open Mon-Sat from 10am-4pm. Admission is free, reservations are not required.  For more information on scheduling a visit or a field trip visit [nsa.gov/museum/](https://www.nsa.gov/Press-Room/News-Highlights/Article/Article/3946210/new-exhibits-at-the-national-cryptologic-museum-unlock-your-curiosity/udroot$/gh1/vol20454/medusak/Transfers/20241010%20MED/nsa.gov/museum/)*

# Highlights:



# Notes:



"""
    file_5 = """---
title: OpenAI o3 Breakthrough High Score on ARC-AGI-Pub
source: https://arcprize.org/blog/oai-o3-pub-breakthrough
author: ['[[ARC Prize]]']
published: None
created: 2024-12-22
description: OpenAI o3 scores 75.7% on ARC-AGI public leaderboard.
tags: ['AI']
domain: arcprize.org
from: ['Mobile']
id: JCBMmSFJv3rVfzr3SUCvNj
vault_path: Thoughts/Research/Web/arcprize.org /OpenAI o3 Breakthrough High Score on ARC-AGI-Pub.md
---
%%Y6Jh5Z8yoERYMG3k2PW64J|0.0.0|ObsidianFile%%

Here we're going to test out a bumch of random lines

Just to see how it handles it

And another one

Last one is going to sit right above a header...
# My Thoughts:


# Related:


# Content:

## ARC Prize remains undefeated.  
New ideas still needed.

OpenAI's new o3 system - trained on the ARC-AGI-1 Public Training set - has scored a breakthrough **75.7%** on the Semi-Private Evaluation set at our stated public leaderboard $10k compute limit. A high-compute (172x) o3 configuration scored **87.5%**.

![o Series Performance](https://arcprize.org/media/images/blog/o-series-performance.jpg)

This is a surprising and important step-function increase in AI capabilities, showing novel task adaptation ability never seen before in the GPT-family models. For context, ARC-AGI-1 took 4 years to go from 0% with GPT-3 in 2020 to 5% in 2024 with GPT-4o. All intuition about AI capabilities will need to get updated for o3.

The mission of ARC Prize goes beyond our first benchmark: to be a North Star towards AGI. And we're excited to be working with the OpenAI team and others next year to continue to design next-gen, enduring AGI benchmarks.

ARC-AGI-2 (same format - verified easy for humans, harder for AI) will launch alongside ARC Prize 2025. We're committed to running the Grand Prize competition until a high-efficiency, open-source solution scoring 85% is created.

Read on for the full testing report.

---

## OpenAI o3 ARC-AGI Results

We tested o3 against two ARC-AGI datasets:

- **Semi-Private Eval**: 100 private tasks used to assess overfitting
- **Public Eval**: 400 public tasks

At OpenAI's direction, we tested at two levels of compute with variable sample sizes: 6 (high-efficiency) and 1024 (low-efficiency, 172x compute).

Here are the results.

| Set | Tasks | Efficiency | Score | Retail Cost | Samples | Tokens | Cost/Task | Time/Task (mins) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Semi-Private | 100 | High | 75.7% | $2,012 | 6 | 33M | $20 | 1.3 |
| Semi-Private | 100 | Low | 87.5% | \- | 1024 | 5.7B | \- | 13.8 |
| Public | 400 | High | 82.8% | $6,677 | 6 | 111M | $17 | N/A |
| Public | 400 | Low | 91.5% | \- | 1024 | 9.5B | \- | N/A |

Note: o3 high-compute costs not available as pricing and feature availability is still TBD. The amount of compute was roughly 172x the low-compute configuration.

Note on "tuned": OpenAI shared they trained the o3 we tested on 75% of the Public Training set. They have not shared more details. We have not yet tested the ARC-untrained model to understand how much of the performance is due to ARC-AGI data.

Due to variable inference budget, efficiency (e.g., compute cost) is now a required metric when reporting performance. We've documented both the total costs and the cost per task as an initial proxy for efficiency. As an industry, we'll need to figure out [what metric best tracks efficiency](https://x.com/mikeknoop/status/1868760635716386864), but directionally, cost is a solid starting point.

The high-efficiency score of 75.7% is within the budget rules of ARC-AGI-Pub (costs <$10k) and therefore qualifies as 1st place on the public leaderboard!

The low-efficiency score of 87.5% is quite expensive, but still shows that performance on novel tasks does improve with increased compute (at least up to this level.)

Despite the significant cost per task, these numbers aren't just the result of applying brute force compute to the benchmark. OpenAI's new o3 model represents a significant leap forward in AI's ability to adapt to novel tasks. This is not merely incremental improvement, but a genuine breakthrough, marking a qualitative shift in AI capabilities compared to the prior limitations of LLMs. o3 is a system capable of adapting to tasks it has never encountered before, arguably approaching human-level performance in the ARC-AGI domain.

Of course, such generality comes at a steep cost, and wouldn't quite be economical yet: you could pay a human to solve ARC-AGI tasks for roughly $5 per task (we know, we did that), while consuming mere cents in energy. Meanwhile o3 requires $17-20 per task in the low-compute mode. But cost-performance will likely improve quite dramatically over the next few months and years, so you should plan for these capabilities to become competitive with human work within a fairly short timeline.

o3's improvement over the GPT series proves that architecture is everything. You couldn't throw more compute at GPT-4 and get these results. Simply scaling up the things we were doing from 2019 to 2023 – take the same architecture, train a bigger version on more data – is not enough. Further progress is about new ideas.

---

### So is it AGI?

ARC-AGI serves as a critical benchmark for detecting such breakthroughs, highlighting generalization power in a way that saturated or less demanding benchmarks cannot. However, it is important to note that ARC-AGI is not an acid test for AGI – as we've repeated dozens of times this year. It's a research tool designed to focus attention on the most challenging unsolved problems in AI, a role it has fulfilled well over the past five years.

Passing ARC-AGI does not equate to achieving AGI, and, as a matter of fact, I don't think o3 is AGI yet. o3 still fails on some very easy tasks, indicating fundamental differences with human intelligence.

Furthermore, early data points suggest that the upcoming ARC-AGI-2 benchmark will still pose a significant challenge to o3, potentially reducing its score to under 30% even at high compute (while a smart human would still be able to score over 95% with no training). This demonstrates the continued possibility of creating challenging, unsaturated benchmarks without having to rely on expert domain knowledge. You'll know AGI is here when the exercise of creating tasks that are easy for regular humans but hard for AI becomes simply impossible.

### What's different about o3 compared to older models?

Why does o3 score so much higher than o1? And why did o1 score so much higher than GPT-4o in the first place? I think this series of results provides invaluable data points for the ongoing pursuit of AGI.

My mental model for LLMs is that they work as [a repository of vector programs](https://fchollet.substack.com/p/how-i-think-about-llm-prompt-engineering). When prompted, they will fetch the program that your prompt maps to and "execute" it on the input at hand. LLMs are a way to store and operationalize millions of useful mini-programs via passive exposure to human-generated content.

This "memorize, fetch, apply" paradigm can achieve arbitrary levels of skills at arbitrary tasks given appropriate training data, but it cannot adapt to novelty or pick up new skills on the fly (which is to say that there is no fluid intelligence at play here.) This has been exemplified by the low performance of LLMs on ARC-AGI, the only benchmark specifically designed to measure adaptability to novelty – GPT-3 scored 0, GPT-4 scored near 0, GPT-4o got to 5%. Scaling up these models to the limits of what's possible wasn't getting ARC-AGI numbers anywhere near what basic brute enumeration could achieve years ago (up to 50%).

To adapt to novelty, you need two things. First, you need knowledge – a set of reusable functions or programs to draw upon. LLMs have more than enough of that. Second, you need the ability to recombine these functions into a brand new program when facing a new task – a program that models the task at hand. Program synthesis. LLMs have long lacked this feature. The o series of models fixes that.

For now, we can only speculate about the exact specifics of how o3 works. But o3's core mechanism appears to be natural language program search and execution within token space – at test time, the model searches over the space of possible Chains of Thought (CoTs) describing the steps required to solve the task, in a fashion perhaps not too dissimilar to AlphaZero-style Monte-Carlo tree search. In the case of o3, the search is presumably guided by some kind of evaluator model. To note, Demis Hassabis hinted back in [a June 2023 interview](https://www.wired.com/story/google-deepmind-demis-hassabis-chatgpt/) that DeepMind had been researching this very idea – this line of work has been a long time coming.

So while single-generation LLMs struggle with novelty, o3 overcomes this by generating and executing its own programs, where the program itself (the CoT) becomes the artifact of knowledge recombination. Although this is not the only viable approach to test-time knowledge recombination (you could also do test-time training, or search in latent space), it represents the current state-of-the-art as per these new ARC-AGI numbers.

Effectively, o3 represents a form of *deep learning-guided program search*. The model does test-time search over a space of "programs" (in this case, natural language programs – the space of CoTs that describe the steps to solve the task at hand), guided by a deep learning prior (the base LLM). The reason why solving a single ARC-AGI task can end up taking up tens of millions of tokens and cost thousands of dollars is because this search process has to explore an enormous number of paths through program space – including backtracking.

There are however two significant differences between what's happening here and what I meant when I previously described "deep learning-guided program search" as the best path to get to AGI. Crucially, the programs generated by o3 are *natural language instructions* (to be "executed" by a LLM) rather than *executable symbolic programs*. This means two things. First, that they cannot make contact with reality via execution and direct evaluation on the task – instead, they must be evaluated for fitness via another model, and the evaluation, lacking such grounding, might go wrong when operating out of distribution. Second, the system cannot autonomously acquire the ability to generate and evaluate these programs (the way a system like AlphaZero can learn to play a board game on its own.) Instead, it is reliant on expert-labeled, human-generated CoT data.

It's not yet clear what the exact limitations of the new system are and how far it might scale. We'll need further testing to find out. Regardless, the current performance represents a remarkable achievement, and a clear confirmation that intuition-guided test-time search over program space is a powerful paradigm to build AI systems that can adapt to arbitrary tasks.

### What comes next?

First of all, open-source replication of o3, facilitated by the ARC Prize competition in 2025, will be crucial to move the research community forward. A thorough analysis of o3's strengths and limitations is necessary to understand its scaling behavior, the nature of its potential bottlenecks, and anticipate what abilities further developments might unlock.

Moreover, ARC-AGI-1 is now saturating – besides o3's new score, the fact is that a large ensemble of low-compute Kaggle solutions can now score 81% on the private eval.

We're going to be raising the bar with a new version – ARC-AGI-2 - which has been in the works since 2022. It promises a major reset of the state-of-the-art. We want it to push the boundaries of AGI research with hard, high-signal evals that highlight current AI limitations.

Our early ARC-AGI-2 testing suggests it will be useful and extremely challenging, even for o3. And, of course, ARC Prize's objective is to produce a *high-efficiency* and *open-source* solution in order to win the Grand Prize. We currently intend to launch ARC-AGI-2 alongside ARC Prize 2025 (estimated launch: late Q1).

Going forward, the ARC Prize Foundation will continue to create new benchmarks to focus the attention of researchers on the hardest unsolved problems on the way to AGI. We've started work on a third-generation benchmark which departs completely from the 2019 ARC-AGI format and incorporates some exciting new ideas.

---

## Get Involved: Open-Source Analysis

Today, we're also releasing data (results, attempts, and prompt) from our high-compute o3 testing and would like your help to analyze the results. In particular, we are very curious about the ~9% set of Public Eval tasks o3 was unable to solve, even with lots of compute, yet are straightforward for humans.

We invite the community to help us assess the characteristics of both solved and unsolved tasks.

To get your ideas flowing, here are 3 examples of tasks unsolved by high-compute o3.

![ARC-AGI Task Id: c6e1b8da](https://arcprize.org/media/images/blog/arc-agi-task-c6e1b8da.png)

ARC-AGI Task ID: c6e1b8da

![ARC-AGI Task Id: 0d87d2a6](https://arcprize.org/media/images/blog/arc-agi-task-0d87d2a6.png)

ARC-AGI Task ID: 0d87d2a6

![ARC-AGI Task Id: b457fec5](https://arcprize.org/media/images/blog/arc-agi-task-b457fec5.png)

ARC-AGI Task ID: b457fec5

[See our full set of o3 testing data.](https://github.com/arcprizeorg/model_baseline/tree/main/results)

[Here's the prompt that was used in testing.](https://github.com/arcprizeorg/model_baseline/blob/main/prompt_example_o3.md)

We've also created a new channel in our Discord named `oai-analysis` and we'd love to hear your analysis and insights there. Or tag us on X/Twitter [@arcprize](https://x.com/arcprize).

---

## Conclusions

To sum up – o3 represents a significant leap forward. Its performance on ARC-AGI highlights a genuine breakthrough in adaptability and generalization, in a way that no other benchmark could have made as explicit.

o3 fixes the fundamental limitation of the LLM paradigm – the inability to recombine knowledge at test time – and it does so via a form of LLM-guided natural language program search. This is not just incremental progress; it is new territory, and it demands serious scientific attention.

[Sign up to get updates](https://arcprize.org/blog/#)

# Highlights:



# Notes:



"""
    from python_parser.logs.logger import get_logger

    logger = get_logger(__name__)
    file_count = 0
    for file in [file_1, file_2, file_3, file_4, file_5]:
        sections = split_content(file)
        file_count += 1
        logger.info(f"File {file_count}:")
        section_count = 0
        for sec in sections:
            section_count += 1
            logger.info(f"    Section {section_count}:")
            try:
                node = section.parse(sec)
                logger.info(f"       {type(node).__name__}: {node}")
            except Exception as e:
                logger.error(f"       Error: {e}")
            # groups = split_sections(section)
            # for

            # node = section.parse(file)

            # print(f"\nMixed tag nodes:")
            # for node in result:
            # logger.info(f"   {type(node).__name__}: {node}")
            # assert isinstance(node, Header)
            # assert isinstance(node, Paragraph)
            # assert isinstance(node, Header)
            # assert isinstance(node, Paragraph)


if __name__ == "__main__":
    pytest.main([__file__])
