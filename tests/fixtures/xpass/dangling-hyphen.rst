Additionally, this PEP requires that the default class definition
namespace be ordered (e.g. ``OrderedDict``) by default.  The
long-lived class namespace (``__dict__``) will remain a ``dict``.

::

    Traceback (most recent call last):
        File "<pyshell#6>", line 1, in -toplevel-
            d.pop()
    IndexError: pop from an empty deque

.. doctest::

   >>> setcontext(ExtendedContext)
   >>> Decimal(1) / Decimal(0)
   Decimal('Infinity')
   >>> getcontext().traps[DivisionByZero] = 1
   >>> Decimal(1) / Decimal(0)
   Traceback (most recent call last):
     File "<pyshell#112>", line 1, in -toplevel-
       Decimal(1) / Decimal(0)
   DivisionByZero: x / 0
