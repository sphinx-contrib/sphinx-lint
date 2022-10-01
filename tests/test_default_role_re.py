from sphinxlint import default_role_re


def test_shall_pass():
    assert default_role_re.search("foo `bar` baz")['default_role'] == '`bar`'
    assert default_role_re.search("foo `bar`-baz")['default_role'] == '`bar`'


def test_shall_not_pass():
    assert not default_role_re.search("foo `bar`baz")
    assert not default_role_re.search("foo '`'bar'`' baz")
    assert not default_role_re.search("``")
    assert not default_role_re.search("2 * x a ** b (* BOM32_* ` `` _ __ |")
    assert not default_role_re.search('''"`" '|' (`) [`] {`} <`> ‘`’ ‚`‘ ‘`‚ ’`’ ‚`’ “`” „`“ “`„ ”`” „`” »`« ›`‹ «`» »`» ›`›''')
