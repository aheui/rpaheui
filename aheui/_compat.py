
# coding: utf-8

try:
    from rpython.rlib.jit import JitDriver
    from rpython.rlib.jit import elidable, dont_look_inside
    from rpython.rlib.jit import assert_green
    from rpython.rlib.jit import set_param, PARAMETERS
    from rpython.rlib.listsort import TimSort
    TRACE_LIMIT = PARAMETERS['trace_limit']
except ImportError:
    """Python compatibility."""
    class JitDriver(object):
        def __init__(self, **kw): pass
        def jit_merge_point(self, **kw): pass
        def can_enter_jit(self, **kw): pass
    def elidable(f): return f
    def dont_look_inside(f): return f
    def unroll_safe(f): return f
    def hint(v, **kw): return v
    def assert_green(x): pass
    def set_param(driver, name, value): pass

    class TimSort(object):
        def __init__(self, list):
            self.list = list

        def sort(self):
            self.list.sort()

    import os
    os.write(2, b"[Warning] It is running without rlib/jit.\n")


try:
    unichr(0)
except NameError:
    def unichr(n):  # not rpython but python3
        return chr(n)
    ord3 = ord

    def ord(n):
        if type(n) == int:
            return n
        return ord3(n)

try:
    long(0)
except NameError:
    long = int


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
