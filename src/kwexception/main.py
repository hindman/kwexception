
class Kwexception(Exception):
    '''
    Richer exceptions with keyword parameters.
    '''

    MSG = 'msg'
    MOVE = 'move'
    COPY = 'copy'

    SET_MSG = MOVE
    SUPER_PARAMS = True

    NEW_UPDATE = True
    NEW_CONVERT = True
    NEW_CONTEXT = True

    def __init__(self, *xs, **kws):

        # Copy or move the msg from xs[0] into the kws dict as the first key.
        should_set = (
            xs and
            self.MSG not in kws and
            self.SET_MSG in (self.MOVE, self.COPY)
        )
        if should_set:
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
        if isinstance(e, cls):
            if cls.NEW_UPDATE:
                e.params.update(kws)
            else:
                for k, v in kws.items():
                    e.params.setdefault(k, v)
            return e
        elif cls.NEW_CONVERT:
            if cls.NEW_CONTEXT:
                kws.update(
                    context_error = type(e).__name__,
                    context_args = e.args,
                    context_str = str(e),
                )
            return cls(**kws)
        else:
            return e

