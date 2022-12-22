## kwexception: Richer exceptions with keyword parameters

#### Motivation

Blah blah blah. Blah blah blah. Blah blah blah. Blah blah blah. Blah blah blah.
Blah blah blah. Blah blah blah.

```python
for x in xs:
    print(x)
```

#### An easier way

Blah blah blah. Blah blah blah. Blah blah blah. Blah blah blah. Blah blah blah.
Blah blah blah. Blah blah blah.

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

raise TypeError(
    "'{name}' must be {type!r} (got {value!r} that is a "
    "{actual!r}).".format(
        name=attr.name,
        type=self.type,
        actual=value.__class__,
        value=value,
    ),
    attr,
    self.type,
    value,
)

# Django
raise ValidationError(self.message, code=self.code, params={"value": value})
raise ValueError("The protocol '%s' is unknown. Supported: %s" % (protocol, list(ip_address_validator_map)))
raise TypeError("Page indices must be integers or slices, not %s." % type(index).__name__)

----

[stackoverflow_url]: https://stackoverflow.com/questions/2682745

