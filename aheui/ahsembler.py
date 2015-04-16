#!/usr/bin/env python

import aheui

def entry_point(argv):
    return aheui.entry_point(argv + ['--target=asm', '--output=-'])

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    import sys
    entry_point(sys.argv)

