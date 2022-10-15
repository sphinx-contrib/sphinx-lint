.. expect: 15: superfluous backtick in front of role (backtick-before-role)
.. expect: 23: superfluous backtick in front of role (backtick-before-role)

.. and as erroneous roles may greatly looks like default roles, sphinx-lint sees:
.. expect: default role used
.. expect: default role used


Right:

:c:func:`PyFrame_GetLocals` instead.

Wrong:

`:c:func:`PyFrame_GetLocals` instead.

Right:

:func:`max` instead.

Wrong:

`:func:`max` instead.
