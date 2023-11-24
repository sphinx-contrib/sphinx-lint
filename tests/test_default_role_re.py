from sphinxlint import rst


def test_shall_pass():
    assert rst.INTERPRETED_TEXT_RE.search("foo `bar` baz")["inline_markup"] == "`bar`"
    assert rst.INTERPRETED_TEXT_RE.search("foo `bar`-baz")["inline_markup"] == "`bar`"


def test_shall_not_pass():
    assert not rst.INTERPRETED_TEXT_RE.search("foo `bar`baz")
    assert not rst.INTERPRETED_TEXT_RE.search("foo '`'bar'`' baz")
    assert not rst.INTERPRETED_TEXT_RE.search("``")
    assert not rst.INTERPRETED_TEXT_RE.search("2 * x a ** b (* BOM32_* ` `` _ __ |")
    assert not rst.INTERPRETED_TEXT_RE.search(
        """"`" '|' (`) [`] {`} <`> ‘`’ ‚`‘ ‘`‚ ’`’ ‚`’ “`” „`“ “`„ ”`” „`” »`« ›`‹ «`» »`» ›`›"""  # noqa: E501
    )
