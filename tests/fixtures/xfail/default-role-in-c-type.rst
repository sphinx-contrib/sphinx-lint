.. expect: default role used (hint: for inline literals, use double backticks) (default-role)

.. c:type:: int (*PyCode_WatchCallback)(PyCodeEvent event, PyCodeObject* co)

   If *event* is ``PY_CODE_EVENT_CREATE``, then the callback is invoked
   after `co` has been fully initialized. Otherwise, the callback is invoked
   before the destruction of *co* takes place, so the prior state of *co*
   can be inspected.
