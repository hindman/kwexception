
class Kwexception(Exception):
    '''
    Better exceptions with keyword parameters.
    '''

    # Key name for the Kwexception message in self.params.
    MSG_KEY = 'msg'

    # Specify a default msg for instances of the class.
    DEFAULT_MSG = None

    # Whether and how to set msg from the first positional.
    MOVE = 'move'
    COPY = 'copy'
    SET_MSG = MOVE

    # Whether to add params to args.
    ADD_PARAMS_TO_ARGS = True

    # Whether to treat a single positional dict as the keyword params.
    SINGLE_DICT_AS_PARAMS = True

    # Whether to simplify stringification for message-only exceptions.
    SIMPLIFY_DISPLAY = True

    # Whether new() should use update or setdefault when augmenting params.
    NEW_UPDATE = True

    # Whether new() should convert errors of another type to the relevant
    # Kwexception subclass and, if so, whether to include contexutal
    # information in params.
    NEW_CONVERT = True
    NEW_CONTEXT = True

    # Whether to use the msg as format string or as a lookup
    # into a FORMATS dict of format strings.
    FORMAT_MSG = False
    FORMATS = None

    def __init__(self, *xs, **kws):
        # To remain faithful to repr(), if the constructor receives
        # only a dict positionally, treat it as the params.
        xs_is_params = (
            self.SINGLE_DICT_AS_PARAMS and
            len(xs) == 1 and
            isinstance(xs[0], dict) and
            not kws
        )
        if xs_is_params:
            kws = xs[0]
            xs = ()

        # Copy/move the msg from xs[0] into the kws dict as the first key.
        should_set_msg = (
            self.SET_MSG in (self.MOVE, self.COPY) and
            xs and
            self.MSG_KEY not in kws
        )
        if should_set_msg:
            d = {self.MSG_KEY: xs[0]}
            d.update(kws)
            kws = d
            if self.SET_MSG == self.MOVE:
                xs = xs[1:]

        # Set a default msg.
        if self.DEFAULT_MSG is not None and self.MSG_KEY not in kws:
            d = {self.MSG_KEY: self.DEFAULT_MSG}
            d.update(kws)
            kws = d

        # Format the msg. If msg is a str (neither None nor an unusual value
        # from user), first set fmt, either directly from msg or via FORMATS
        # (where msg is key). Then set the msg in kws via a format() call.
        msg = kws.get(self.MSG_KEY, None)
        if self.FORMAT_MSG and isinstance(msg, str):
            if self.FORMATS is None:
                fmt = msg
            else:
                fmt = self.FORMATS.get(msg, msg)
            kws[self.MSG_KEY] = fmt.format(**kws)

        # Add kws to xs so that it will be included in the super() call.
        if self.ADD_PARAMS_TO_ARGS:
            xs = xs + (kws,)

        # Set params and make the super() call.
        self.params = kws
        super().__init__(*xs)

    @property
    def msg(self):
        return self.params.get(self.MSG_KEY, None)

    @classmethod
    def new(cls, e, **kws):
        # If the exception is already an instance of cls, just augment
        # it with additional keyword params and return it.
        if isinstance(e, cls):
            if cls.NEW_UPDATE:
                e.params.update(kws)
            else:
                for k, v in kws.items():
                    e.params.setdefault(k, v)
            return e

        # If the exception is some other type and if the user
        # does not want new() to convert exceptions, just
        # return the original error.
        if not cls.NEW_CONVERT:
            return e

        # Otherwise, return a new exception of type cls (optionally augmented
        # with contextual information about the original error).
        if cls.NEW_CONTEXT:
            kws.update(
                context_error = type(e).__name__,
                context_args = e.args,
            )
        return cls(**kws)

    def __str__(self):
        if self._use_simplified_display:
            return str(self.msg)
        else:
            return super().__str__()

    def __repr__(self):
        if self._use_simplified_display:
            cls_name = type(self).__name__
            return f'{cls_name}({self.msg!r})'
        else:
            return super().__repr__()

    @property
    def _use_simplified_display(self):
        # Helper to determine whether str() and repr() behavior should be
        # simplified to mimic default Python behavior. Is applicable only if
        # the exception's data attributes (self.args and self.params) consist
        # of nothing but a message.
        return (
            self.SIMPLIFY_DISPLAY and
            len(self.args) == 1 and
            self.args[0] == self.params and
            len(self.params) == 1 and
            self.MSG_KEY in self.params
        )

