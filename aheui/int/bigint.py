
from aheui._compat import jit
from rpython.rlib.rbigint import rbigint


NAME = 'bigint'


Int = rbigint


def fromstr(s):
    return rbigint.fromstr(s)


def fromint(v):
    return rbigint.fromint(v)


def fromlong(v):
    return rbigint.fromlong(v)


def toint(big):
    return big.toint()


def tolonglong(big):
    return big.tolonglong()


def str(big):
    return big.str()


@jit.elidable
def add(r1, r2):
    return r1.add(r2)


@jit.elidable
def sub(r1, r2):
    return r1.sub(r2)


@jit.elidable
def mul(r1, r2):
    return r1.mul(r2)


@jit.elidable
def div(r1, r2):
    return r1.div(r2)


@jit.elidable
def mod(r1, r2):
    return r1.mod(r2)


@jit.elidable
def ge(r1, r2):
    return r1.ge(r2)


@jit.elidable
def is_zero(r):
    # return r.sign == 0
    return r._size == 0  # pypy 7.3.15


@jit.elidable
def is_unicodepoint(r):
    return 0 <= r._size and r.int_le(0x110000)
