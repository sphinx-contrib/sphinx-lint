.. expect: directive should start with two dots, not three. (directive-with-three-dots)

... versionchanged:: 3.11
    Raises :exc:`TypeError` instead of :exc:`AttributeError` if *cm*
    is not a context manager.
