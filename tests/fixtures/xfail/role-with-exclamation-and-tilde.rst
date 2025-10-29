.. expect: Found a role with both `!` and `~` in ':meth:`!~list.pop`'. (exclamation-and-tilde)
.. expect: Found a role with both `!` and `~` in ':meth:`~!list.pop`'. (exclamation-and-tilde)

:meth:`!~list.pop` cannot be used to display ``pop()`` and avoid
reference warnings; instead, it renders as ``~list.pop()``.
We should instead write :meth:`!pop` to correctly display ``pop()``.
:meth:`~!list.pop` doesn’t work either.
