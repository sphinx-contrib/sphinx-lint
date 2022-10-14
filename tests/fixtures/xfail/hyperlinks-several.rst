.. expect: missing underscore after closing backtick in hyperlink (missing-underscore-after-hyperlink)
.. expect: default role used (hint: for inline literals, use double backticks) (default-role)
.. expect: missing space before < in hyperlink (missing-space-in-hyperlink)

Several malformed hyperlinks on the same line yield several errors.

`Link text<https://example.com>`_ `Link text 2 <https://example.com>`
