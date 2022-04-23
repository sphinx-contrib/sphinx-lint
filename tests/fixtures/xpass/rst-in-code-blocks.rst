Presented with the :term:`expression` ``obj[x]``, the Python interpreter
follows something like the following process to decide whether
:meth:`~object.__getitem__` or :meth:`~object.__class_getitem__` should be
called::

   from inspect import isclass

   def subscribe(obj, x):
       """Return the result of the expression `obj[x]`"""

       class_of_obj = type(obj)

       # If the class of `obj` defines `__getitem__()`,
       # call `type(obj).__getitem__()`
       if hasattr(class_of_obj, '__getitem__'):
           return class_of_obj.__getitem__(obj, x)

       # Else, if `obj` is a class and defines `__class_getitem__()`,
       # call `obj.__class_getitem__()`
       elif isclass(obj) and hasattr(obj, '__class_getitem__'):
           return obj.__class_getitem__(x)

       # Else, raise an exception
       else:
           raise TypeError(
               f"'{class_of_obj.__name__}' object is not subscriptable"
           )
