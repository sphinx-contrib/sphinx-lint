from sphinxlint import interpreted_text_re


def test_shall_pass():
    assert interpreted_text_re.search("foo `bar` baz")["inline_markup"] == "`bar`"
    assert interpreted_text_re.search("foo `bar`-baz")["inline_markup"] == "`bar`"


def test_shall_not_pass():
    assert not interpreted_text_re.search("foo `bar`baz")
    assert not interpreted_text_re.search("foo '`'bar'`' baz")
    assert not interpreted_text_re.search("``")
    assert not interpreted_text_re.search("2 * x a ** b (* BOM32_* ` `` _ __ |")
    assert not interpreted_text_re.search(
        """"`" '|' (`) [`] {`} <`> ‘`’ ‚`‘ ‘`‚ ’`’ ‚`’ “`” „`“ “`„ ”`” „`” »`« ›`‹ «`» »`» ›`›"""
    )
