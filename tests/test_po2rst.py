from sphinxlint import po2rst


def test_po2rst():
    po = """msgid "foo"
msgstr "bar"

msgid "test1"
msgstr "test2"
"""
    rst = """bar


test2
"""
    assert po2rst(po) == rst


def test_po2rst_more():
    po = """msgid "foo"
msgstr "bar"

msgid "test1"
msgstr ""
"test2"

msgid "test3"
msgstr "test4"
"""
    rst = """bar


test2



test4
"""
    assert po2rst(po) == rst
