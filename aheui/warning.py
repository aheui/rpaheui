from __future__ import absolute_import

import os
from aheui._compat import jit


class Warning(object):
    def __init__(self, name, message):
        self.name = name
        self.message = message

    def format(self, *args):
        return self.message % args


WARNING_LIST = [
    Warning(b'no-rpython', b"[Warning:VirtualMachine] Running without rlib/jit.\n"),
    Warning(b'write-utf8-range', b'[Warning:UndefinedBehavior:write-utf8-range] value %x is out of unicode codepoint range.'),
]


class WarningPool(object):
    def __init__(self):
        self.limit = -1
        self.warnings = {}
        self.counters = {}
        for w in WARNING_LIST:
            self.warnings[w.name] = w
            self.counters[w.name] = 0

    @jit.dont_look_inside
    def warn(self, name, *args):
        warning = self.warnings[name]
        if self.limit != -1 and self.limit <= self.counters[name]:
            return
        self.counters[name] = self.counters[name] + 1
        os.write(2, warning.format(*args))
        os.write(2, b'\n')
        if self.limit != -1 and self.limit <= self.counters[name]:
            os.write(2, b"[Warning:Meta] The warning '%s' has reached the limit %d and will be suppressed\n" % (warning.name, self.limit))
