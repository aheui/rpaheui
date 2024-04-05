# coding: utf-8
from __future__ import absolute_import
import os


try:
    from rpython.rlib import jit
    from rpython.rlib.listsort import TimSort

    PYR = True
    PY2 = False
    PY3 = False
    PY = -1

    try:
        USE_BIGINT = os.environ["RPAHEUI_BIGINT"]
    except (KeyError, ValueError):
        USE_BIGINT = ''

except ImportError:
    # Python compatibility

    import sys

    PY = sys.version_info.major
    PYR = False
    PY2 = PY == 2
    PY3 = PY == 3

    USE_BIGINT = False

    def omnipotent(*args, **kw):
        return args and args[0]

    class Omnipotent(object):
        def __getattr__(self, name):
            return omnipotent

        def __call__(self, *args, **kw):
            return self

    class JitModule(Omnipotent):
        JitDriver = Omnipotent()

    jit = JitModule()

    class TimSort(object):
        def __init__(self, list):
            self.list = list

        def sort(self):
            self.list.sort()


try:
    unichr(0)
    unichr = unichr
    ord = ord
except NameError:
    long = int

    def unichr(n):  # not rpython but python3
        return chr(n)

    ord3 = ord

    def ord(n):
        if type(n) == int:  # noqa: E721
            return n
        return ord3(n)


try:
    # rpython, python2
    @jit.elidable
    def _unicode(i):
        return (b'%d' % i).decode('utf-8')
    _unicode(0)

    @jit.elidable
    def _bytestr(i):
        return b'%d' % i
except TypeError:
    # python3
    def _unicode(i):
        return u'%d' % i
    _unicode(0)

    def _bytestr(i):
        return b'%d' % i


try:
    USE_BIGINT = os.environ["RPAHEUI_BIGINT"]
except (KeyError, ValueError):
    USE_BIGINT = ''


if USE_BIGINT:
    from aheui.int import bigint  # Enable bigint in rpython build
else:
    from aheui.int import smallint as bigint  # noqa: F401 smallint or python support
