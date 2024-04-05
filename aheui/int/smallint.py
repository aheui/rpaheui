from __future__ import absolute_import

try:
    import builtins
except ImportError:
    builtins = __builtins__
from aheui._compat import _bytestr


NAME = 'smallint'


Int = int


def fromstr(s):
    return int(s)


def fromint(v):
    return v


def fromlong(v):
    return v


def toint(v):
    return v


def tolonglong(v):
    return v


def str(r):
    return _bytestr(r)


def hex(r):
    return hex(r)


def add(r1, r2):
    return r1 + r2


def sub(r1, r2):
    return r1 - r2


def mul(r1, r2):
    return r1 * r2


def div(r1, r2):
    return r1 // r2


def mod(r1, r2):
    return r1 % r2


def ge(r1, r2):
    return r1 >= r2


def is_zero(r):
    return r == 0


def is_unicodepoint(r):
    return 0 < r <= 0x110000
