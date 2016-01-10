#!/usr/bin/env python


def entry_point(argv):
    from aheui.aheui import entry_point
    return entry_point(argv + ['--target=asm', '--output=-'])


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    import sys
    entry_point(sys.argv)
