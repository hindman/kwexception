import pytest

from kwexception import Kwexception, __version__

####
# Constants and customized Kwexception classes.
####

MSG = 'blort-blort'
SUFFIX = '-default'

VALUE_ERROR_CONTEXT = {
    'context_error': 'ValueError',
    'context_args': (MSG,),
}

class KwDefault(Kwexception):
    pass

class KwNoNewConvert(Kwexception):
    NEW_CONVERT = False

class KwNoNewUpdate(Kwexception):
    NEW_UPDATE = False
    NEW_CONTEXT = False

class KwNoSingleDict(Kwexception):
    SINGLE_DICT_AS_PARAMS = False

class KwDifferentMessageKey(Kwexception):
    MSG_KEY = 'message'
    message = Kwexception.msg

class KwDefaultMessage(Kwexception):
    DEFAULT_MSG = MSG + SUFFIX

####
# Tests for object creation.
####

def test_construct_default(tr):
    kws = dict(a = 1, b = 2)
    exp = dict(msg = MSG, **kws)
    e = KwDefault(MSG, **kws)
    assert e.args == (exp,)
    assert e.params == exp
    assert e.msg == MSG
    assert tuple(e.params)[0] == 'msg'
    assert str(e) == str(exp)
    assert repr(e) == f'KwDefault({repr(exp)})'
    assert isinstance(e, KwDefault)
    assert isinstance(e, Kwexception)

def test_construct_just_dict(tr):
    kws = dict(msg = MSG, a = 1, b = 2)

    e = KwDefault(kws)
    assert e.args == (kws,)
    assert e.params == kws
    assert e.msg == MSG

    kws = dict(a = 1, b = 2)
    exp_params = {'msg': kws}
    e = KwNoSingleDict(kws)
    assert e.msg == kws
    assert e.params == exp_params
    assert e.args == (exp_params,)

def test_construct_simple(tr):
    e = KwDefault(MSG)
    exp_params = {'msg': MSG}
    assert e.params == exp_params
    assert e.args == (exp_params,)
    assert e.msg == MSG
    assert str(e) == MSG
    assert repr(e) == f'KwDefault({MSG!r})'

def test_construct_default_msg(tr):

    # A helper to check a KwDefaultMessage instance.
    def check(e, exp_msg, exp_params):
        # Params, msg, and args.
        assert e.params == exp_params
        assert e.args == (exp_params,)
        assert e.msg == exp_msg
        # In params, msg is first key.
        assert tuple(e.params)[0] == 'msg'
        # Stringification.
        assert str(e) == str(exp_params)
        assert repr(e) == f'KwDefaultMessage({exp_params!r})'

    # Some params and the default msg of the subclass.
    kws = dict(a = 1, b = 2)
    def_msg = KwDefaultMessage.DEFAULT_MSG

    # If you don't pass any msg args/params, you'll get default.
    e = KwDefaultMessage(**kws)
    check(e, def_msg, {'msg': def_msg, **kws})

    # If you pass msg explicitly or positionally, you'll get it rather than default.
    exp = {'msg': MSG, **kws}
    e1 = KwDefaultMessage(msg = MSG, **kws)
    e2 = KwDefaultMessage(MSG, **kws)
    check(e1, MSG, exp)
    check(e2, MSG, exp)

####
# Tests for Kwexception.new().
####

def test_default_new(tr):
    kws = dict(a = 1, b = 2)
    extra = dict(c = 33, d = 44)

    exp = dict(msg = MSG, **kws, **extra)
    exp.update(a = -1)
    e1 = KwDefault(MSG, **kws)
    e2 = KwDefault.new(e1, **extra, a = -1)
    assert e2 is e1
    assert e2.params == exp

    exp = {**extra, **VALUE_ERROR_CONTEXT}
    e1 = ValueError(MSG)
    e2 = KwDefault.new(e1, **extra)
    assert isinstance(e2, KwDefault)
    assert e2 is not e1
    assert e2.params == exp

def test_new_no_convert(tr):
    e1 = ValueError(MSG)
    e2 = KwNoNewConvert.new(e1, a = 1)
    prev = tuple(e1.args)
    assert e2 is e1
    assert e2.args == prev

def test_new_no_update(tr):
    kws = dict(a = 1, b = 2)
    extra = dict(c = 33, d = 44)
    exp = dict(msg = MSG, **kws)

    e1 = KwNoNewUpdate(MSG, **kws)
    e2 = KwNoNewUpdate.new(e1, **extra, a = -1)
    assert e2 is e1
    assert e2.params == {**exp, **extra}

    e1 = ValueError(MSG)
    e2 = KwNoNewUpdate.new(e1, **extra)
    assert e2 is not e1
    assert isinstance(e2, KwNoNewUpdate)
    assert e2.params == extra

####
# Other tests.
####

def test_version(tr):
    v = __version__
    assert v
    assert isinstance(v, str)

def test_different_message_name(tr):
    kws = dict(a = 1, b = 2)
    exp = dict(message = MSG, **kws)
    e = KwDifferentMessageKey(MSG, **kws)

    assert e.args == (exp,)
    assert e.params == exp
    assert e.msg == MSG
    assert str(e) == str(exp)
    assert repr(e) == f'KwDifferentMessageKey({repr(exp)})'
    assert isinstance(e, KwDifferentMessageKey)
    assert isinstance(e, Kwexception)

