#!/usr/bin/env python
# coding: utf-8


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


def target(*args):
    from aheui.aheui import entry_point
    return entry_point, None


if __name__ == '__main__':
    """Python compatibility."""
    import sys
    from aheui.aheui import entry_point
    sys.exit(entry_point(sys.argv))
