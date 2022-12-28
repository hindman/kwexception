## kwexception: Better exceptions with keyword parameters

#### Motivation

Most Python exceptions consist of an error type (`ValueError`, `TypeError`,
etc.) and a message that attempts to communicate the problem. In many cases,
that message must contain one or more data values to provide context. In simple
cases, exceptions created in the classic style are not too bad.

```python
raise ValueError(f'Cannot convert value to float: {val!r}')
```

But when the data needed to create a clear exception message expands to to
multiple or more complex values, the process becomes both tedious and
ill-conceived. Tedious because the programmer must engage in a variety of ad
hoc string-formatting maneuvers. Ill-conceived because something explicit and
useful to programmers (data) is wedged into a human-readable message, making
the data less immediately accessible (for example, quickly copying it into an
editor or REPL) and less explicit (sometimes important details are lost in
stringification). Here's a lightly-edited example taken from a high quality,
widely used Python library illustrating how the typical approach to exceptions
can quickly lead to tedious string-building gynastics:

```python
raise TypeError(
    "'{name}' must be {type!r} (got {value!r} that is a "
    "{actual!r}).".format(
        name = name,
        type = self.type,
        actual = value.__class__,
        value = value,
    ),
)
```

Similar problems have long existed in even more pressing forms in the domain of
logging. The classic approach was to emit logging messages in the manner
described above: take a human-readable message and then awkwardly insert data
values into it. The end result is a logging message that is typically only
partially-parsable unless the developers on the project exercise unusually high
levels of discipline in their creation of logging messages. Seeking a better
alternative, many software engineers have switched to JSON-based logging. Under
that approach, the human-readable text is just a short message stating the
problem in general terms, and that message is just one key-value pair in a dict
that contains all other data parameters needed to make the logging entry
specific and meaningful (not only general data values like date, time, and
logging level, but also a variety of specific data values appropriate to the
case at hand).

Python exceptions are amendable to similar improvements -- hence the
kwexception library. Instead of starting with a message and shoving data into
it, the developer simply creates an exception via keyword parameters.

#### Basic usage

The first step is to define one or more exception classes for your project. If
you are satisfied with the library's default behavior, those classes simply
need to inherit from `Kwexception`:

```python
from kwexception import Kwexception

class PointError(Kwexception):
    pass
```

To create exceptions, pass both the textual message and any other keyword
parameters needed to make the error useful. By default, the message is stored
under the `msg` keyword parameter. When creating exceptions, you can pass the
message explicitly under that key or as the first positional parameter. When
writing the message, avoid the temptation to put data values inside the
message: the philosphy of the library is to keep the textual, but general,
statement of the problem separate from the specific data values relevant to the
error at hand.

```python
INVALID = 'Invalid Point coordinates'
x = 11
y = None

e = PointError(msg = INVALID, x = x, y = y)  # Pass msg explicitly.
e = PointError(INVALID, x = x, y = y)        # Or as the first positional.
```

The exception's data will be accessible via its `params` and `msg` attributes:

```python
print(e.msg)     # Invalid Point coordinates
print(e.params)  # {'msg': 'Invalid Point coordinates', 'x': 11, 'y': None}
```

When the exception is stringified, its data will be presented faithfully as a
dict:

```python
# str() representation.
{'msg': 'Invalid Point coordinates', 'x': 11, 'y': None}

# repr() representation.
PointError({'msg': 'Invalid Point coordinates', 'x': 11, 'y': None})

# Stacktrace representation.
PointError: {'msg': 'Invalid Point coordinates', 'x': 11, 'y': None}
```

Upon first exposure to such output one might balk at the aesthetics of the
stringified dict when compared to a classic exception with just a
human-readable message. But stacktraces -- and exception stringification
generally -- are the domain of software engineers, not end users, so those
aesthetics concerns are misplaced (if your end-users are seeing your
stacktraces, your project has bigger problems). For Python programmers, there
is nothing mysterious or unsightly about a dict; they are eminently clear and
beautifully practical.

#### Setting a default message

In many situations, it makes sense to use one message for each exception type.
In that case, the `Kwexception` subclass can declare a `DEFAULT_MSG`, further
simplifying the process of creating the exception.

```python
class PointError(Kwexception):
    DEFAULT_MSG = 'Invalid Point coordinates'

e = PointError(x = 11, y = None)
print(e.params)  # {'msg': 'Invalid Point coordinates', 'x': 11, 'y': None}
```

#### Details on the exception data model on stringification

The underlying data model for a [Python exception][python_base_exception] is a
tuple, accessible via the `args` attribute.

```python
ve1 = ValueError('Boom')
ve1.args                        # ('Boom',)

ve2 = ValueError('Boom', 1, 2)
ve2.args                        # ('Boom', 1, 2)
```

A `Kwexception` subclass rests on that behavior, with the dict of keyword
parameters typically being the sole element in the `args` tuple. For example,
the PointError shown above would have the following tuple:

```python
({'msg': 'Invalid Point coordinates', 'x': 11, 'y': None},)
```

When a Python exception's `args` tuple has just one element (which is the
situation in the overwhelming majority of cases), stringification takes a
simplified form. One can see this by comparing the two ValueError instances
shown above:

```python
print(str(ve1))  # Boom
print(str(ve2))  # ('Boom', 1, 2)
```

The `Kwexception` library provides an analogous simplification when its instances
are stringified. If the instance has only a `msg` in its keyword parameters and
if its `args` tuple consists of nothing but the dict of those parameters, the
exception will be displayed in simple form.

```python
e1 = PointError('Foo', x = 11, y = None)
e2 = PointError('Foo')
e3 = PointError(msg = 'Foo')

print(str(e1))   # {'msg': 'Foo', 'x': 11, 'y': None}
print(repr(e1))  # PointError({'msg': 'Foo', 'x': 11, 'y': None})

print(str(e2))   # Foo
print(repr(e2))  # PointError('Foo')

print(str(e3))   # Foo
print(repr(e3))  # PointError('Foo')
```

#### Additional feature: exception handling and augmentation

The `Kwexception` class provides another primary feature: the ability to handle
other exceptions in an easier, more consistent way. This behavior is provided
via the class method `new()`, which takes an exception as its first argument
and optionally takes any other keyword parameters. Its intended usage is in a
`try-except` context:

```python
try:
    # Do something that might fail.
    ...
except Exception as e:
    # The original error might or might not be a PointError.
    # Our application wants to ensure that it is.
    e = PointError.new(e, msg = 'foo', x = x, y = y)
    ...
```

If the exception provided to `Kwexception.new()` is already an instance of a
sublcass of `Kwexception`, the method returns the same exception instance, but
updates its `params` dict with the keyword parameters supplied to `new()`.

```python
e1 = PointError('foo', a = 1, b = 2)
e2 = PointError.new(e1, a = 111, c = 3)

print(e2 is e1)  # True
print(repr(e2))  # PointError({'msg': 'foo', 'a': 111, 'b': 2, 'c': 3})
```

If the provided exception is some other type of error, the `new()` method
returns a new `Kwexception` instance with the provided keyword parameters, plus
additional parameters providing contextual information about the original
exception's type and `args`.

```python
ve1 = ValueError('foo', 99)
e3 = PointError.new(ve1, msg = 'bar', x = 1)

print(repr(e3)) # PointError({'msg': 'bar', 'x': 1,
                # 'context_error': 'ValueError', 'context_args': ('foo', 99)})
```

#### Additional feature: data-bearing messages

Perhaps you like the central idea of the kwexception library (maintaining a
separation between the textual message and the data values), but either you are
a traditionalist at heart or your project still requires data-bearing,
human-readable messages for some other purpose (for example, a situation where
you do need to assemble a user-facing message, not a stacktrace, and an
exception's data provides the most logical mechanism to do that).

The kwexception library supports that use case via the `FORMAT_MSG` attribute.
If true, the `Kwexception` subclass will treat the provided `msg` not as a
literal message by as a Python format-string. When creating a new exception
instance it will create the actual message via a `str.format()` call, passing
the exception's keyword parameters as arguments to that call.

```python
class PointError(Kwexception):
    FORMAT_MSG = True

INVALID_FMT = 'Invalid Point coordinates: x={x} y={y}'

e = PointError(INVALID_FMT, x = 11, y = None)
print(e.msg)     # Invalid Point coordinates: x=11 y=None
print(e.params)  # {'msg': 'Invalid Point coordinates: x=11 y=None', 'x': 11, 'y': None}
```

That feature can be combined with `DEFAULT_MSG`, in which the default message
serves as a default format-string.

```python
class PointError(Kwexception):
    DEFAULT_MSG = 'Invalid Point coordinates: x={x} y={y}'
    FORMAT_MSG = True

e = PointError(x = 11, y = None)
print(e.msg)     # Same as previous example.
print(e.params)
```
#### Customization

A `Kwexception` superclass offers a few customizations for users who want some,
but not all, of its default behaviors. This example lists the default settings:

```python
class PointError(Kwexception):

    # Customize object creation.
    SET_MSG = Kwexception.MOVE    # Kwexception.MOVE, Kwexception.COPY, or None.
    ADD_PARAMS_TO_ARGS = True
    SINGLE_DICT_AS_PARAMS = True
    SIMPLIFY_DISPLAY = True

    # Customize Kwexception.new().
    NEW_UPDATE = True
    NEW_CONVERT = True
    NEW_CONTEXT = True
```

**Setting the message from the first positional: `SET_MSG`**. By default, the
first positional argument is treated as the `msg` and is moved out of the tuple
of positionals and into the dict of keyword parameters. Alternatively, that
move operation can be a copy operation, or disabled entirely.

**Adding the dict of keyword parameters to the `args` tuple:
`ADD_PARAMS_TO_ARGS`**. By default, the dict of keyword parameters is appended
to the exception's `args` tuple (this occurs after the move/copy for `SET_MSG`).
If a `Kwexception` subclass wants to take advantage of keyword parameters but
also needs the `args` tuple for other purposes, this behavior can be disabled.

**Accept keyword parameters via a positional dict: `SINGLE_DICT_AS_PARAMS`**.
By default, a `Kwexception` instance is stringified for `repr()` by showing the
dict of keyword parameters. For consistency with that representation, if the
constructor is given only a dict positionally (i.e., no other positional or
keyword arguments), it will treat that dict as the exception's keyword
parameters and store them in `params` accordingly.

**Simplified display for message-only exceptions: `SIMPLIFY_DISPLAY`**. As
documented above, by default a `Kwexception` instance containing no data other
than a `msg` will stringify in a simplified way. If the behavior is disabled,
stringification will be based on the content of `args` using default Python
behavior.

**New exceptions from original exceptions: augment keyword parameters via
update or setdefault: `NEW_UPDATE`**. When given an instance of `Kwexception`,
the classmethod `new()` uses the keyword parameters to augment the original
exception's `params` dict in the manner of `dict.update()`. If `NEW_UPDATE` is
set to false, the `params` dict is augmented in the manner of
`dict.setdefault`.

**New exceptions from original exceptions: whether to convert exceptions and
add contextual information about the original: `NEW_CONVERT` and
`NEW_CONTEXT`**. When given an instance of a non-`Kwexception` type, the
classmethod `new()` returns a new exception of the relevant `Kwexception`
subclass and it includes contextual information in the `params` dict about the
original error. Alternatively, one can suppress the inclusion of contextual
information or the entire conversion process.

**Controlling the key name for the exception message: `MSG_KEY`**. The
`Kwexception` instance's message is stored under the `msg` key. To use a
different naming convention, set `MSG_KEY` to a different value and define an
alias for the `Kwexception.msg()` property. Here is an illustration for those
preferring a more verbose but explicit approach:

```python
class PointError(Kwexception):

    MSG_KEY = 'message'
    message = Kwexception.msg
```

----

[python_base_exception]: https://docs.python.org/3/library/exceptions.html#BaseException

