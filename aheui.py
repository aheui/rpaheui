#!/usr/bin/env python
# coding: utf-8

import os

from const import *
import serializer
try:
    from rpython.rlib.jit import JitDriver
    from rpython.rlib.jit import purefunction
    from rpython.rlib.jit import assert_green
except ImportError:
    class JitDriver(object):
        def __init__(self, **kw): pass
        def jit_merge_point(self, **kw): pass
        def can_enter_jit(self, **kw): pass
    def purefunction(f): return f


def get_location(pc, stacksize, program):
    return "#%d(s%d)_%s_%d" % (pc, stacksize, serializer.OPCODE_NAMES[program[pc][0]], program[pc][1])

jitdriver = JitDriver(greens=['pc', 'stacksize', 'program'], reds=['storage', 'selected'], get_printable_location=get_location)


DEBUG = False



class Stack(object):
    def __init__(self):
        self.list = []

    def push(self, value):
        assert value is not None
        self.list.append(value)

    def pop(self):
        return self.list.pop()

    def dup(self):
        last = self.list[-1]
        self.push(last)

    def swap(self):
        l = self.list
        l[-1], l[-2] = l[-2], l[-1]

    def last(self):
        return self.list[-1]

    def __len__(self):
        return len(self.list)


class Queue(Stack):
    def pop(self):
        return self.list.pop(0)

    def swap(self):
        l = self.list
        l[0], l[1] = l[1], l[0]


def init_storage():
    storage = []
    for i in range(0, 28):
        if i == VAL_QUEUE:
            storage.append(Queue())
        else:
            storage.append(Stack())
    return storage

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

@purefunction
def get_op_val(program, pc):
    return program[pc]

@purefunction
def get_req_size(program, pc):
    return OP_REQSIZE[program[pc][0]]

def mainloop(program, debug):
    pc = 0
    stacksize = 0
    storage = init_storage()
    selected = storage[0]
    #debug.export()
    while pc < len(program):
        #debug.storage(s)
        #if DEBUG: raw_input()
        #debug.show(pc)
        stacksize = min(get_req_size(program, pc), len(selected))
        jitdriver.jit_merge_point(pc=pc, stacksize=stacksize, program=program, storage=storage, selected=selected)
        op, value = get_op_val(program, pc)
        if op == OP_ADD:
            r1, r2 = selected.pop(), selected.pop()
            selected.push(r2 + r1)
        elif op == OP_SUB:
            r1, r2 = selected.pop(), selected.pop()
            selected.push(r2 - r1)
        elif op == OP_MUL:
            r1, r2 = selected.pop(), selected.pop()
            selected.push(r2 * r1)
        elif op == OP_DIV:
            r1, r2 = selected.pop(), selected.pop()
            selected.push(r2 / r1)
        elif op == OP_MOD:
            r1, r2 = selected.pop(), selected.pop()
            selected.push(r2 % r1)
        elif op == OP_POP:
            selected.pop()
        elif op == OP_PUSH:
            selected.push(value)
        elif op == OP_DUP:
            selected.dup()
        elif op == OP_SWAP:
            selected.swap()
        elif op == OP_SEL:
            selected = storage[value]
        elif op == OP_MOV:
            r = selected.pop()
            storage[value].push(r)
        elif op == OP_CMP:
            r1, r2 = selected.pop(), selected.pop()
            r = 1 if r2 >= r1 else 0
            selected.push(r)
        elif op == OP_BRZ:
            r = selected.pop()
            if r == 0:
                pc = value
                continue
        elif op == OP_BRPOP1:
            if len(selected) < 1:
                pc = value
                continue
        elif op == OP_BRPOP2:
            if len(selected) < 2:
                pc = value
                continue
        elif op == OP_POPNUM:
            r = selected.pop()
            os.write(1, str(r))
        elif op == OP_POPCHAR:
            r = selected.pop()
            os.write(1, unichr(r).encode('utf-8'))
        elif op == OP_PUSHNUM:
            numchars = []
            while True:
                numchar = os.read(0, 1)
                if numchar not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                    break
                else:
                    numchars.append(numchar)
            assert len(numchars) > 0
            num = int(''.join(numchars))
            selected.push(num)
        elif op == OP_PUSHCHAR:
            buf = os.read(0, 1)
            if buf:
                v = ord(buf[0])
                if v >= 0x80:
                    if (v & 0xf0) == 0xf0:
                        length = 4
                    elif (v & 0xe0) == 0xe0:
                        length = 3
                    elif (v & 0xc0) == 0xc0:
                        length = 2
                    else:
                        length = 0
                    if length > 0:
                        buf += os.read(0, length - 1)
                        if len(buf) == length:
                            try:
                                v = ord((buf).decode('utf-8')[0])
                            except:
                                v = -1
                        else:
                            v = -1
                selected.push(v)
            else:
                selected.push(-1)
        elif op == OP_JMP:
            pc = value
            continue
        elif op == OP_HALT:
            break
        elif op == OP_NONE:
            pass
        else:
            os.write(2, 'Missing operator: %d' % op)
            assert False
        pc += 1

    if len(selected) > 0:
        return selected.pop()
    else:
        return 0

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print 'aheui: error: no input files'
        return 1
    
    assembler = serializer.Serializer()
    fp = os.open(filename, os.O_RDONLY, 0777)
    if filename.endswith('.aheuic'):
        assembler.read(fp)
        os.close(fp)
    else:
        program_contents = ''
        while True:
            read = os.read(fp, 4096)
            if len(read) == 0:
                break
            program_contents += read
        os.close(fp)
            
        assembler.compile(program_contents)
        assembler.optimize()

        binname = filename
        if binname.endswith('.aheui'):
            binname += 'c'
        else:
            binname += '.aheuic'
        try:
            bfp = os.open(binname, os.O_WRONLY|os.O_CREAT, 0644)
            assembler.write(bfp)
            os.write(bfp, '\n\n')
            assembler.dump(bfp)
            os.close(bfp)
        except:
            pass
    exitcode = mainloop(assembler.lines, assembler.debug)
    return exitcode

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    import sys
    sys.exit(entry_point(sys.argv))


