
# coding: utf-8

try:
    from rpython.rlib import jit
    from rpython.rlib.listsort import TimSort
    TRACE_LIMIT = jit.PARAMETERS['trace_limit']
except ImportError:
    """Python compatibility."""
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

    import os
    os.write(2, b"[Warning] It is running without rlib/jit.\n")


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
    def _unicode(i):
        return (b'%d' % i).decode('utf-8')
    _unicode(0)
except TypeError:
    # python3
    def _unicode(i):
        return u'%d' % i
    _unicode(0)
