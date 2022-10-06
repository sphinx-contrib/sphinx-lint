:class:`subprocess.Popen` destructor now emits a :exc:`ResourceWarning` warning
if the child process is still running. Use the context manager protocol (``with
proc: ...``) or explicitly call the :meth:`~subprocess.Popen.wait` method to
read the exit status of the child process. (Contributed by Victor Stinner in
:issue:`26741`.)

A new :data:`~html.entities.html5` dictionary that maps HTML5 named character
references to the equivalent Unicode character(s) (e.g. ``html5['gt;'] ==
'>'``) has been added to the :mod:`html.entities` module.  The dictionary is
now also used by :class:`~html.parser.HTMLParser`.  (Contributed by Ezio
Melotti in :issue:`11113` and :issue:`15156`.)

``-X importtime`` to show how long each import takes. It shows module
name, cumulative time (including nested imports) and self time (excluding
nested imports).  Note that its output may be broken in multi-threaded
application.  Typical usage is ``python3 -X importtime -c 'import
asyncio'``.  See also :envvar:`PYTHONPROFILEIMPORTTIME`.
