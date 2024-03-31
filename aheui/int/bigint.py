
from rpython.rlib.jit import elidable
from rpython.rlib.rbigint import rbigint


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


@elidable
def add(r1, r2):
    return r1.add(r2)


@elidable
def sub(r1, r2):
    return r1.sub(r2)


@elidable
def mul(r1, r2):
    return r1.mul(r2)


@elidable
def div(r1, r2):
    return r1.div(r2)


@elidable
def mod(r1, r2):
    return r1.mod(r2)


@elidable
def ge(r1, r2):
    return r1.ge(r2)
