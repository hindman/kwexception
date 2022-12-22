
class Kwexception(Exception):
    '''
    Richer exceptions with keyword parameters.
    '''

    # Key name for the Kwexception message in self.params. To customize this
    # name, the subclass should set a value for MSG and also define an alias
    # for Kwexception.msg. For example, to change 'msg' to 'message' configure
    # the subclass with: MSG = 'message'; message = Kwexception.msg.
    MSG = 'msg'

    # Customize object creation: if SET_MSG is Kwexception.MOVE or
    # Kwexception.COPY, the constructor's first positional argument will be
    # moved or copied into the self.params under the MSG key.
    MOVE = 'move'
    COPY = 'copy'
    SET_MSG = MOVE

    # Customize object creation: if SUPER_PARAMS is True, the self.params dict
    # will be appended to the tuple passed to the super().__init__() call.
    SUPER_PARAMS = True

    # Customize object creation. If SINGLE_DICT is True, one can create a
    # Kwexception by passing a single dict positionally. That dict will be
    # treated as self.params. This behavior is consistent with the default
    # repr() output for Kwexception instances.
    SINGLE_DICT = True

    # Customize str() and repr() for Kwexception instances. If SIMPLIFY_DISPLAY
    # is True, Kwexception instances having nothing more than a message will be
    # stringified like basic Python exceptions.
    SIMPLIFY_DISPLAY = True

    # Customize Kwexception.new() in cases where the method receives an error
    # whose type is a Kwexception subclass. If NEW_UPDATE is True, the keyword
    # arguments passed to new() will be applied to self.params in the manner
    # of dict.update(). If NEW_UPDATE is False, they will be applied in the
    # manner of dict.setdefault().
    NEW_UPDATE = True

    # Customize Kwexception.new() in cases where the method receives an error
    # whose type is not a Kwexception subclass. If NEW_CONVERT is True, the
    # method will return a new instance of the relevant Kwexception subclass
    # (cls); if NEW_CONVERT is False, the method will simply return the
    # original exception unchanged. In the True case, and if NEW_CONTEXT is
    # also True, the new instance of cls will have contextual information about
    # the original error added to self.params (its class name, its self.args,
    # and its str() representation).
    NEW_CONVERT = True
    NEW_CONTEXT = True

    def __init__(self, *xs, **kws):

        # To remain faithful to repr(), if the constructor receives
        # only a dict positionally, treat it as the params.
        xs_is_params = (
            self.SINGLE_DICT and
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
            self.MSG not in kws
        )
        if should_set_msg:
            d = {self.MSG: xs[0]}
            d.update(kws)
            kws = d
            if self.SET_MSG == self.MOVE:
                xs = xs[1:]

        # Add kws to xs so that it will be included in the super() call.
        if self.SUPER_PARAMS:
            xs = xs + (kws,)

        # Set params and make the super() call.
        self.params = kws
        super().__init__(*xs)

    @property
    def msg(self):
        return self.params.get(self.MSG, None)

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
                context_str = str(e),
            )
        return cls(**kws)

    def __str__(self):
        if self._use_simplified_display:
            return self.msg
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
            self.MSG in self.params
        )

