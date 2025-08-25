Download directives should not require underscores after URLs.

A basic download directive with https:
:download:`Download file <https://example.com/file.pdf>`

One with http:
:download:`Get the archive <http://downloads.example.com/archive.zip>`

An inline download:
This line contains a :download:`link to a file <https://example.com/file.txt>`.

Multiple download directives in a row:
First :download:`Download this file <https://example.com/first-file.txt>` and
then :download:`this one <https://example.com/second-file.txt>` something else

These should not trigger missing-underscore-after-hyperlink errors.
