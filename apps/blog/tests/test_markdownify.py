from apps.blog.templatetags.blog_extras import markdownify


def test_renders_header():
    result = markdownify("#### A Heading")
    assert "<h4>A Heading</h4>" in result


def test_renders_table():
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    result = markdownify(md)
    assert "<table>" in result
    assert "<th>A</th>" in result


def test_renders_bold():
    result = markdownify("This is **bold** text")
    assert "<strong>bold</strong>" in result


def test_empty_input_returns_empty_string():
    assert markdownify("") == ""
    assert markdownify(None) == ""


def test_no_raw_markdown_syntax_leaks_through():
    md = "#### Heading\n\n**bold** and a table:\n\n| A | B |\n|---|---|\n| 1 | 2 |\n"
    result = markdownify(md)
    assert "####" not in result
    assert "**" not in result
