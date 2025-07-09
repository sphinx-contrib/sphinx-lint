.. expect: Extra backtick in role: ':mod:`!cgi``' (role-with-extra-backtick)
.. expect: Extra backtick in role: ':mod:``!cgitb`' (role-with-extra-backtick)
.. expect: Extra backtick in role: ':func:`foo``' (role-with-extra-backtick)
.. expect: Extra backtick in role: ':class:`MyClass``' (role-with-extra-backtick)
.. expect: Extra backtick in role: ':meth:``method`' (role-with-extra-backtick)

This file contains roles with extra backtick that should be detected.

* :pep:`594`: Remove the :mod:`!cgi`` and :mod:``!cgitb` modules

* :func:`foo`` should be :func:`foo`

* :class:`MyClass`` is wrong

* :meth:``method` should be fixed
