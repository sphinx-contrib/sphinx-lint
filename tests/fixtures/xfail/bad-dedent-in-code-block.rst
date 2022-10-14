.. expect: Bad dedent in block (bad-dedent)

Here's a single big code block, but the author intent was to write two::

    >>> from enum import Enum
    >>> class Weekday(Enum):
    ...     MONDAY = 1
    ...     TUESDAY = 2
    ...     WEDNESDAY = 3
    ...     THURSDAY = 4
    ...     FRIDAY = 5
    ...     SATURDAY = 6
    ...     SUNDAY = 7

 Here's the line starting with a space (so it's inside the code block instead of starting another)::

    >>> from enum import Enum
    >>> class Color(Enum):
    ...     RED = 1
    ...     GREEN = 2
    ...     BLUE = 3
