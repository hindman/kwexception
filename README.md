## kwexception: Richer exceptions with keyword parameters

#### Motivation

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


```python
for x in xs:
    print(x)
```

#### An easier way

Blah blah blah. Blah blah blah. Blah blah blah. Blah blah blah. Blah blah blah.
Blah blah blah. Blah blah blah.

----

[stackoverflow_url]: https://stackoverflow.com/questions/2682745

