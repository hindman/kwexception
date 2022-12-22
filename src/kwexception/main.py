from __future__ import absolute_import, unicode_literals, print_function

import attr
import six
import sys

ERR_TYPE = 'attrs argument must be a str, list, tuple, or dict.'
ERR_VALUE = "value_style argument must be None, 'upper', 'lower', 'enum', or function."

def constants(name, attrs, value_style = None, bases = (object,), **attr_arguments):
    '''
    Returns a dict-like container of constants, as a frozen instance of an attrs class.

    Arguments:
    name -- Class name.
    attrs -- Dict mapping names to constant values or a tuple/list/string of names.
    value_style -- Used to create values from names (None, 'upper', 'lower', 'enum', or callable).
    bases -- Passed to attr.make_class().
    **attr_arguments -- Passed to attr.make_class().
    '''

    # Set up two parallel lists: attribute names and instance values.
    if isinstance(attrs, dict):
        # For dict, user specifies them directly.
        names = list(attrs.keys())
        vals = list(attrs.values())
    else:
        # For string or sequence, we start with the names.
        if isinstance(attrs, six.string_types):
            names = attrs.split()
        elif isinstance(attrs, (list, tuple)):
            names = attrs
        else:
            raise TypeError(ERR_TYPE)

        # Then create values based on value_style.
        if value_style is None:
            vals = names
        elif value_style == 'upper':
            vals = [nm.upper() for nm in names]
        elif value_style == 'lower':
            vals = [nm.lower() for nm in names]
        elif value_style == 'enum':
            vals = [i + 1 for i in range(len(names))]
        elif callable(value_style):
            vals = [value_style(i, nm) for i, nm in enumerate(names)]
        else:
            raise ValueError(ERR_VALUE)

    # Create the attrs class.
    attr_arguments['frozen'] = True
    cls_name = name if sys.version_info.major >= 3 else name.encode('utf-8')
    cls = attr.make_class(cls_name, names, bases, **attr_arguments)

    # Add support for iteration and getting a value by name.
    cls.__iter__ = lambda self: iter(self.__dict__.items())
    cls.__getitem__ = lambda self, k: self.__dict__[k]
    cls.__len__ = lambda self: len(self.__dict__)
    cls.__contains__ = lambda self, k: k in self.__dict__

    # If no conflicts, add support for read-only dict methods.
    if 'keys' not in names:
        cls.keys = lambda self: tuple(self.__dict__.keys())
    if 'values' not in names:
        cls.values = lambda self: tuple(self.__dict__.values())
    if 'get' not in names:
        cls.get = lambda self, *xs: self.__dict__.get(*xs)

    # Return an instance holding the constants.
    return cls(*vals)

def cons(_clsname, **kwargs):
    '''
    Returns a dict-like container of constants, as a frozen instance of an attrs class.

    Arguments:
    _clsname -- Class name.
    **kwargs -- Passed as a dict to short_con.constants()
    '''
    # A convenience function when you want to create constants via kwargs
    # and you don't need to customize `bases` or `attr_arguments`.
    return constants(_clsname, kwargs)

