.. expect: Found a role starting with `!~` in ':meth:`!~list.pop`'. (exclamation-and-tilde)

:meth:`!~list.pop` cannot be used to display ``pop()`` and avoid
reference warnings; instead, it renders as ``~list.pop()``.
We should instead write :meth:`!pop` to correctly display ``pop()``.
