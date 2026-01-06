from sphinxlint.utils import py2rst


def test_py2rst():
    py = '''#!/usr/bin/env python
"""Hello from the module docstring!!!"""

def foo():
    """Hello from a function docstring!!!"""
'''
    rst = """
Hello from the module docstring!!!


Hello from a function docstring!!!
"""
    assert py2rst(py) == rst
