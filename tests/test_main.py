import pytest

from kwexception import Kwexception, __version__

class KwDefault(Kwexception):
    pass

class KwNoNewConvert(Kwexception):
    NEW_CONVERT = False

class KwNoNewUpdate(Kwexception):
    NEW_UPDATE = False
    NEW_CONTEXT = False

MSG = 'blort-blort'

VALUE_ERROR_CONTEXT = {
    'context_error': 'ValueError',
    'context_args': (MSG,),
    'context_str': MSG,
}

def test_version(tr):
    v = __version__
    assert v
    assert isinstance(v, str)

def test_default_construct(tr):
    kws = dict(a = 1, b = 2)
    exp = dict(msg = MSG, **kws)
    e = KwDefault(MSG, **kws)
    assert e.args == (exp,)
    assert e.params == exp
    assert e.msg == MSG
    assert str(e) == str(exp)
    assert repr(e) == f'KwDefault({repr(exp)})'
    assert isinstance(e, KwDefault)
    assert isinstance(e, Kwexception)

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

