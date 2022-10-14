.. expect: missing space before default role: 'e \ufeff``i would like to be an inline literal``'. (missing-space-before-default-role)
.. expect: found an unbalanced inline literal markup. (unbalanced-inline-literals-delimiters)
.. expect: found an unbalanced inline literal markup. (unbalanced-inline-literals-delimiters)

See https://github.com/spyder-ide/spyder-docs/pull/332 for context.

Some words then a ZWNBSP here ﻿``i would like to be an inline literal``
(but it is not).

This inline literal will **not** be parsed by docutils because of the
ZERO WIDTH NO-BREAK SPACE that you may don't see, place right before
the opening double backticks.
