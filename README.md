## kwexception: Richer exceptions with keyword parameters

#### Motivation

Most Python exceptions consist of error type (`ValueError`, `TypeError`, etc.)
and a message that attempts to communicate the problem. In many cases, that
message must contain one or more data values to provide context. In simple
cases, exceptions created in the classic style are not too bad.

    raise ValueError(f'Cannot convert value to float: {val!r}')

But when the data needed to create a clear exception message expands to to
multiple or more complex values, the process becomes both tedious and
ill-conceived. Tedious because the programmer must engage in a variety of ad
hoc string-formatting maneuvers. Ill-conceived because something explicit and
useful to programmers (data) is wedged into a human-readable message, making
the data less immediately accessible (for example, quickly copying into an
editor or REPL) and less explicit (sometimes important details are lost in
stringification). Here's a lightly-edited example taken from a widely used
Python library illustrating how the typical approach to exceptions can quickly
lead to tedious string-building gynastics:

    raise TypeError(
        "'{name}' must be {type!r} (got {value!r} that is a "
        "{actual!r}).".format(
            name = name,
            type = self.type,
            actual = value.__class__,
            value = value,
        ),
    )

Similar problems exist in even more pressing forms in the domain of logging.
The classic approach was to emit logging messages in the manner described
above: take a human-readable message and then awkwardly insert data values into
it. The end result is a logging message that is typically only
partially-parsable unless the developers on the project exercise unusually high
levels of discipline in their creation of logging messages. Seeking a better
alternative, many software engineers have switched to JSON-based logging. Under
that approach, the human-readable text is just a short message stating the
problem in general terms, and that message is just one key-value pair in a dict
that contains all other data parameters needed to make the logging entry
specific and meaningful (not only general data values like date, time, and
logging level but also a variety of specific data values appropriate to the
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
under the `msg` keyword parameter. When creating exceptions you can pass the
message explicitly under that key or as the first positional parameter.

```python
INVALID = 'Invalid Point coordinates'
x = 11
y = 0

e = PointError(msg = INVALID, x = x, y = y)  # Pass msg explicitly.
e = PointError(INVALID, x = x, y = y)        # Or as the first positional.
```

The exception's data will be accessible via its `params` and `msg` attributes:

```python
print(e.msg)     # Invalid Point coordinates
print(e.params)  # {'msg': 'Invalid Point coordinates', 'x': 11, 'y': 0}
```

When the exception is stringified, its data will be presented faithfully as a
dict:

```python
# Representation via str().

{'msg': 'Invalid Point coordinates', 'x': 11, 'y': 0}

# Representation via repr().

PointError({'msg': 'Invalid Point coordinates', 'x': 11, 'y': 0})

# Representation in a stacktrace.

PointError: {'msg': 'Invalid Point coordinates', 'x': 11, 'y': 0}
```

Upon first exposure to such output one might balk at the aesthetics of the
stringified dict when compared to a classic exception with just a
human-readable message. But stacktraces -- and exception stringification
generally -- are the domain of software engineers, not end users, so those
aesthetics concerns are misplaced (if your end-users are seeing your
stacktraces, your project has bigger problems). For Python programmers, there
is nothing mysterious about a dict; they are eminently clear and practical.

#### Details

The underlying data model for a Python exception is a tuple, accessible via the
`args` attribute.

```python
e1 = ValueError('Boom')
e1.args                          # ('Boom',)

e2 = ValueError('Boom', 1, 2)
e2.args                          # ('Boom', 1, 2)
```

During creation, a Kwexception subclass ends up having the keyword parameters
dict as an element in that `args` tuple.

    ...

Although the `args` tuple can hold multiple values, in the vast majority of
cases, Python exceptions contain a single argument (the hand-crafted,
data-bearing message). In those cases, the stringified exception is simplified
to show only the first element of the tuple.

```python
e = ValueError('Boom')
print(e.args)                   # ('Boom',)
print(str(e))                   # Boom
print(repr(e))                  # ValueError('Boom')

e = ValueError('Boom', 1, 2)
print(e.args)                   # ('Boom', 1, 2)
print(str(e))                   # ('Boom', 1, 2)
print(repr(e))                  # ValueError('Boom', 1, 2)
```

The Kwexception library provides the same simplification when its instances
are stringified.

    ...

#### Details and customization

#### Examples

The purposes of Kwexception.new():

    - Convert another error type to the error-type known by your project.
      [see NEW_CONVERT]

    - Augment a Kwexception instance with more keyword args, either in the
      fashion of dict.update or dict.setdefault. [see NEW_UPDATE]

    - Add some attributes from the initial Exception to the params. [see
      NEW_INITIAL]

    - But its purposes do not include, replacing or improving upon Python's
      traceback generation or handling of __context__ and __cause__. Let
      the user raise-with as needed.

Is STRINGIFY really needed? Defer for now.

    There might be one valid use case: someone who wants stringification to
    be just the self.msg (or less compellingly, self.params), but they need
    the underlying self.args to be a tuple with multiple elements (maybe a
    named tuple).

    But this could be added later without changing anything else.


raise ValueError(f"Cannot convert value to bool: {val}")

raise UnannotatedAttributeError(
    "The following `attr.ib`s lack a type annotation: "
    + ", ".join(
        sorted(unannotated, key=lambda n: cd.get(n).counter)
    )
    + "."
)

raise ValueError(f"No mandatory attributes allowed after an attribute with a default value or factory.  Attribute in question: {a!r}")

raise AttrsAttributeNotFoundError(f"{k} is not an attrs attribute on {new.__class__}.")

# Django
raise ValidationError(self.message, code=self.code, params={"value": value})
raise ValueError("The protocol '%s' is unknown. Supported: %s" % (protocol, list(ip_address_validator_map)))
raise TypeError("Page indices must be integers or slices, not %s." % type(index).__name__)

----

[stackoverflow_url]: https://stackoverflow.com/questions/2682745

