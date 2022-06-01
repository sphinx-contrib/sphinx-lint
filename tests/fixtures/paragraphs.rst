====================
Paragraphs test file
====================

Introduction
============

This is a test rst used to check
that the ``paragraphs`` function
works properly and returns the correct
line numbers.

This issue was initially reported in
https://github.com/sphinx-contrib/sphinx-lint/issues/32
by Hugo.



Bug
===

The function was bugged because
it set the line number after one
paragraph ended, instead of waiting
for the beginning of the new one.


This is why I'm putting several
empty lines between paragraphs
in this test file.


I also wonder if the function should
skip lines that contain only whitespace
since they don't belong to the paragraph
and the function might fail to parse
files that use `\r\n` as newlines.




Fix Description
===============

This fix:
* adds this test file
* adds a test for the
  `paragraphs` function
* adds a test to check
  the lno in error msgs
* fixes the code of the
  `paragraphs` function



lno check
=========

This section has a few markup errors,
to ensure that the checkers now
return the correct line number.



This ``markup``will raise an error at line 65!


This error is on the third line
of this very long paragraph
i.e. at :line:``70``!


Note that the errors report the exact
line, not the first line of the paragraph
so for example an error like
:foo`missing colon` will be reported
at line 76 and not at line 73!


.. note:
   One of the tests in :file:`test_sphinxlint.py`
   relies on exact line numbers, so if you edit
   this section of the file you might break the test
