from __future__ import absolute_import

import os
from aheui._compat import jit


class Warning(object):
    def format(self, *args):
        return self.MESSAGE % args
    

class NoRpythonWarning(Warning):
    MESSAGE = b"[Warning:VirtualMachine] Running without rlib/jit."


class CommandLineArgumentWarning(Warning):
    MESSAGE = b"[Warning:CommandLine] Invalid command line argument is ignored: %s."


class WriteUtf8RangeWarning(Warning):
    MESSAGE = b'[Warning:UndefinedBehavior:write-utf8-range] value %x is out of unicode codepoint range.'


WARNING_LIST = [
    NoRpythonWarning(),
    CommandLineArgumentWarning(),
    WriteUtf8RangeWarning(),
]


class WarningPool(object):
    def __init__(self):
        self.limit = -1
        self.counters = {}
        for w in WARNING_LIST:
            self.counters[type(w).__name__] = 0

    @jit.dont_look_inside
    def warn(self, warning, *args):
        name = warning.__name__
        if self.limit != -1 and self.limit <= self.counters[name]:
            return
        self.counters[name] = self.counters[name] + 1
        os.write(2, warning().format(*args))
        os.write(2, b'\n')
        if self.limit != -1 and self.limit <= self.counters[name]:
            os.write(2, b"[Warning:Meta] The warning '%s' has reached the limit %d and will be suppressed\n" % (name, self.limit))


warnings = WarningPool()
