import pytest
from types import SimpleNamespace

from kwexception import Kwexception, __version__

####
# Constants, a default Kwexception subclass, and a function
# to create various customized subclasses.
####

MSG = 'blort-blort'

DEFAULT_CLS_NAME = 'KwDefault'
CUSTOM_CLS_NAME = 'KwCustom'

class KwDefault(Kwexception):
    pass

class KwCustom(Kwexception):
    pass

def custom_kwex(**kws):
    return type(CUSTOM_CLS_NAME, (KwCustom,), kws)

####
# Helpers to check an exception instance.
####

def do_checks(e,
              msg,
              params,
              args = None,
              cls = KwDefault,
              msg_key = Kwexception.MSG_KEY,
              skip_str = False):

    # Type.
    assert isinstance(e, cls)
    assert isinstance(e, Kwexception)

    # Params, msg, and args.
    assert e.msg == msg
    assert e.params == params
    assert e.args == (params,) if args is None else args

    # In params, msg is first key.
    if e.params:
        assert tuple(e.params)[0] == msg_key

    # Stringification.
    if not skip_str:
        cls_name = cls.__name__
        assert str(e) == str(params)
        assert repr(e) == f'{cls_name}({params})'

def do_custom_checks(e, msg, params, **kws):
    do_checks(e, msg, params, cls = KwCustom, **kws)

####
# Tests for object creation.
####

def test_construct_default(tr):
    # Default behavior.
    kws = dict(a = 1, b = 2)
    exp_params = dict(msg = MSG, **kws)
    e = KwDefault(MSG, **kws)
    do_checks(e, MSG, exp_params)

def test_construct_message_only(tr):
    # Default behavior for a message-only Kwexception.
    e = KwDefault(MSG)
    exp_params = {'msg': MSG}
    do_checks(e, MSG, exp_params, skip_str = True)
    assert str(e) == MSG
    assert repr(e) == f'{DEFAULT_CLS_NAME}({MSG!r})'

def test_construct_just_dict(tr):
    # Checks behavior when the only arg/param is a positional dict.

    # Basic use case: user intends for the keyword params
    # to be the Kwexception params, and they include a msg.
    kws = dict(msg = MSG, a = 1, b = 2)
    e = KwDefault(kws)
    do_checks(e, MSG, kws)

    # Reasonable use case, albeit one that doesn't take direct advantage of
    # Kwexception behaviors. User wants a single dict to be the args, not the
    # params, so they disable SINGLE_DICT_AS_PARAMS and SET_MSG.
    d = dict(x = 1, y = 2)
    cls = custom_kwex(
        SINGLE_DICT_AS_PARAMS = False,
        SET_MSG = None,
    )
    e = cls(d)
    do_custom_checks(e, None, {}, args = (d,), skip_str = True)
    assert str(e) == str(d)
    assert repr(e) == f'{CUSTOM_CLS_NAME}({d})'

    # Strange use case. Same as above, but user did not disable SET_MSG,
    # so the dict itself will be treated as the msg.
    kws = dict(a = 1, b = 2)
    cls = custom_kwex(SINGLE_DICT_AS_PARAMS = False)
    exp_msg = kws
    exp_params = {'msg': kws}
    e = cls(kws)
    do_custom_checks(e, exp_msg, exp_params, skip_str = True)
    assert str(e) == str(kws)
    assert repr(e) == f'{CUSTOM_CLS_NAME}({kws})'

def test_construct_default_msg(tr):
    # Some params and the default msg of the subclass.
    cls = custom_kwex(DEFAULT_MSG = MSG + '-fubb')
    def_msg = cls.DEFAULT_MSG
    kws = dict(a = 1, b = 2)

    # If you don't pass any msg args/params, you'll get default.
    e = cls(**kws)
    do_custom_checks(e, def_msg, {'msg': def_msg, **kws})

    # If you pass msg explicitly or positionally, you'll get it rather than default.
    exp = {'msg': MSG, **kws}
    e1 = cls(msg = MSG, **kws)
    e2 = cls(MSG, **kws)
    do_custom_checks(e1, MSG, exp)
    do_custom_checks(e2, MSG, exp)

def test_construct_format_msg(tr):
    # Some params and format strings.
    kws = dict(a = 1, b = 2)
    fmt1 = 'Got {a} expected {b}'
    exp_msg = fmt1.format(**kws)
    exp_params = {'msg': exp_msg, **kws}

    # Just set FORMAT_MSG to True.
    cls = custom_kwex(FORMAT_MSG = True)
    e = cls(fmt1, **kws)
    do_custom_checks(e, exp_msg, exp_params)

    # Set FORMAT_MSG and a DEFAULT_MSG. In this case, user does not
    # need to pass a msg/format at all.
    cls = custom_kwex(FORMAT_MSG = True, DEFAULT_MSG = fmt1)
    e = cls(**kws)
    do_custom_checks(e, exp_msg, exp_params)

    # Set FORMAT_MSG and MSGS. Now the user can just pass a MSGS key
    formats = dict(
        regular = 'Got {a} expected {b}',
        reverse = 'Expected {b} got {a}',
    )
    cls = custom_kwex(FORMAT_MSG = True, MSGS = formats)
    for k in formats:
        exp_msg = formats[k].format(**kws)
        exp_params = {'msg': exp_msg, **kws}
        e = cls(k, **kws)
        do_custom_checks(e, exp_msg, exp_params)

    # If the user supplies an invalid MSGS key, they will
    # get a KeyError from Python.
    bad_key = 'fubb'
    with pytest.raises(KeyError) as einfo:
        e = cls(bad_key, **kws)
    assert repr(einfo.value) == f"KeyError({bad_key!r})"

    # Or if the user fails to supply the params needed by the
    # relevant format string, they will get a KeyError from Python.
    missing_key = 'b'
    with pytest.raises(KeyError) as einfo:
        e = cls(k, a = 1)
    assert repr(einfo.value) == f"KeyError({missing_key!r})"

    # If the user supplies an invalid MSGS attribute, they will
    # get an AttributeError from Python.
    bad_key = 'fubb'
    formats = SimpleNamespace(**formats)
    cls = custom_kwex(FORMAT_MSG = True, MSGS = formats)
    with pytest.raises(AttributeError) as einfo:
        e = cls(bad_key, **kws)
    assert bad_key in repr(einfo.value)

def test_different_message_name(tr):
    # The user switches msg to message.
    kws = dict(a = 1, b = 2)
    exp_params = dict(message = MSG, **kws)
    msg_key = 'message'
    cls = custom_kwex(
        MSG_KEY = msg_key,
        message = Kwexception.msg,
    )
    e = cls(MSG, **kws)
    do_custom_checks(e, MSG, exp_params, msg_key = msg_key)

####
# Tests for Kwexception.new().
####

def test_default_new(tr):
    # Checks (mostly) default behavior for Kwexception.new().

    # Some params.
    kws = dict(a = 1, b = 2)
    extra = dict(c = 33, d = 44)

    # Initial error is already a Kwexception.
    exp = dict(msg = MSG, **kws, **extra)
    exp.update(a = -1)
    e1 = KwDefault(MSG, **kws)
    e2 = KwDefault.new(e1, **extra, a = -1)
    assert e2 is e1
    assert e2.params == exp

    # Initial error is something else.
    context = {
        Kwexception.CONTEXT_ERROR: 'ValueError',
        Kwexception.CONTEXT_ARGS: (MSG,),
    }
    exp = {**extra, **context}
    e1 = ValueError(MSG)
    e2 = KwDefault.new(e1, **extra)
    assert isinstance(e2, KwDefault)
    assert e2 is not e1
    assert e2.params == exp

    # Initial error is something else and user customized the context keys.
    cls = custom_kwex(
        CONTEXT_ERROR = 'orig_error',
        CONTEXT_ARGS = 'orig_args',
    )
    context = {
        'orig_error': 'ValueError',
        'orig_args': (MSG,),
    }
    exp = {**extra, **context}
    e1 = ValueError(MSG)
    e2 = cls.new(e1, **extra)
    assert isinstance(e2, KwCustom)
    assert e2 is not e1
    assert e2.params == exp

def test_new_no_convert(tr):
    # Checks Kwexception.new() without conversion.
    cls = custom_kwex(NEW_CONVERT = False)
    e1 = ValueError(MSG)
    e2 = cls.new(e1, a = 1)
    prev = tuple(e1.args)
    assert e2 is e1
    assert e2.args == prev

def test_new_no_update_or_context(tr):
    # Checks Kwexception.new() without conversion or context.

    # Params and a cls to use.
    kws = dict(a = 1, b = 2)
    extra = dict(c = 33, d = 44)
    exp = dict(msg = MSG, **kws)
    cls = custom_kwex(
        NEW_UPDATE = False,
        NEW_CONTEXT = False,
    )

    # Original error is a Kwexception.
    e1 = cls(MSG, **kws)
    e2 = cls.new(e1, **extra, a = -1)
    assert e2 is e1
    assert e2.params == {**exp, **extra}

    # Original error is something else.
    e1 = ValueError(MSG)
    e2 = cls.new(e1, **extra)
    assert e2 is not e1
    assert isinstance(e2, cls)
    assert e2.params == extra

####
# Other tests.
####

def test_version(tr):
    v = __version__
    assert v
    assert isinstance(v, str)

