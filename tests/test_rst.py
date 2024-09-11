from sphinxlint.utils import escape2null as e2n
from sphinxlint.rst import inline_markup_gen


def test_inline_literals_can_end_with_escaping_backslash():
    """See https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html
    paragraph: Inline markup recognition rules
    """
    inline_markup_re = inline_markup_gen("``", "``")
    assert inline_markup_re.findall(e2n(r"``\``")) == [e2n(r"``\``")]
    assert inline_markup_re.findall(e2n(r"``\\``")) == [e2n(r"``\\``")]
    assert inline_markup_re.findall(e2n(r"``\\\``")) == [e2n(r"``\\\``")]
    assert inline_markup_re.findall(e2n(r"``\\\\``")) == [e2n(r"``\\\\``")]


def test_emphasis_cannot_end_with_escaping_backslash():
    """See https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html
    paragraph: Inline markup recognition rules
    """
    emphasis_re = inline_markup_gen(r"\*", r"\*")
    assert emphasis_re.findall(e2n(r"*\*")) == []
    assert emphasis_re.findall(e2n(r"*\\*")) == [e2n(r"*\\*")]
    assert emphasis_re.findall(e2n(r"*\\\*")) == []
    assert emphasis_re.findall(e2n(r"*\\\\*")) == [e2n(r"*\\\\*")]

    assert emphasis_re.findall(
        e2n(r"Tous les *\*args* et *\*\*kwargs* fournis à cette fonction sont")
    ) == [e2n(r"*\*args*"), e2n(r"*\*\*kwargs*")]
