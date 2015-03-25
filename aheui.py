#!/usr/bin/env python
# coding: utf-8

import os

from const import *
import compile
try:
    from rpython.rlib.jit import JitDriver
    from rpython.rlib.jit import elidable, dont_look_inside
    from rpython.rlib.jit import assert_green
    from rpython.rlib.jit import set_param, PARAMETERS
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
    os.write(2, "[Warning] It is running without rlib/jit.\n")


def get_location(pc, stackok, is_queue, program):
    """Add debug information.

    PYPYLOG=jit-log-opt,jit-backend,jit-summary:<filename>
    """
    op = program.get_op(pc)
    val = program.get_operand(pc)
    return "#%d(s%d)_%s_%d" % (pc, stackok, compile.OPCODE_NAMES[op], val)

driver = JitDriver(greens=['pc', 'stackok', 'is_queue', 'program'], reds=['stacksize', 'storage', 'selected'], get_printable_location=get_location)


DEBUG = False


class Link(object):
    """Element unit for stack and queue."""

    def __init__(self, next, value=-1):
        self.value = value
        self.next = next

class Stack(object):
    """Base data storage for Aheui, except for ieung and hieuh."""

    def __init__(self):
        self.head = None
        self.size = 0

    def push(self, value):
        node = Link(self.head, value)
        self.head = node
        self.size += 1

    def pop(self):
        node = self.head
        self.head = node.next
        value = node.value
        del node
        self.size -= 1
        return value

    def dup(self):
        self.push(self.head.value)

    def swap(self):
        node1 = self.head
        node2 = node1.next
        node1.value, node2.value = node2.value, node1.value

    # Tools for common methods. inline?

    def get_2_values(self):
        return self.pop(), self.head.value

    def put_value(self, value):
        self.head.value = value

    # Common methods from here

    def __len__(self):
        return self.size

    def add(self):
        r1, r2 = self.get_2_values()
        r = r2 + r1
        self.put_value(r)

    def sub(self):
        r1, r2 = self.get_2_values()
        r = r2 - r1
        self.put_value(r)

    def mul(self):
        r1, r2 = self.get_2_values()
        r = r2 * r1
        self.put_value(r)

    def div(self):
        r1, r2 = self.get_2_values()
        r = r2 / r1
        self.put_value(r)

    def mod(self):
        r1, r2 = self.get_2_values()
        r = r2 % r1
        self.put_value(r)

    def cmp(self):
        r1, r2 = self.get_2_values()
        r = int(r2 >= r1)
        self.put_value(r)


class Queue(Stack):

    def __init__(self):
        self.tail = Link(None)
        self.head = self.tail
        self.size = 0

    def push(self, value):
        tail = self.tail
        tail.value = value
        new = Link(None)
        tail.next = new
        self.tail = new
        self.size += 1

    def dup(self):
        head = self.head
        node = Link(head, head.value)
        self.head = node
        self.size += 1

    def get_2_values(self):
        return self.pop(), self.pop()

    def put_value(self, value):
        self.push(value)


class Port(Stack):
    pass


class Storage(object):
    _immutable_fields = ['pools[*]']

    def __init__(self):
        pools = []
        for i in range(0, 28):
            if i == VAL_QUEUE:
                pools.append(Queue())
            elif i == VAL_PORT:
                pools.append(Port())
            else:
                pools.append(Stack())
        self.pools = pools

    def __getitem__(self, idx):
        return self.pools[idx]


@dont_look_inside
def get_utf8():
    """Get a utf-8 character from standard input.

    The length of utf-8 character is detectable in first byte.
    If decode fails, it means it is a broken character.
    Non-utf-8 character input is undefined in aheui.
    Let's put -1 in this implementaion.
    """
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
    else:
         v = -1
    return v

@dont_look_inside
def get_number():
    """Get a number from standard input."""
    numchars = []
    while True:
        numchar = os.read(0, 1)
        if numchar not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            break
        else:
            numchars.append(numchar)
    assert len(numchars) > 0
    num = int(''.join(numchars))
    return num



class Program(object):
    _immutable_fields_ = ['labels[*]', 'opcodes[*]', 'values[*]', 'size']

    def __init__(self, lines, label_map):
        self.opcodes = [l[0] for l in lines]
        self.values = [l[1] for l in lines]
        self.size = len(lines)
        self.labels = label_map

    @elidable
    def get_op(self, pc):
        return self.opcodes[pc]

    @elidable
    def get_operand(self, pc):
        return self.values[pc]

    @elidable
    def get_req_size(self, pc):
        return OP_REQSIZE[self.get_op(pc)]

    @elidable
    def get_label(self, pc):
        return self.labels[self.get_operand(pc)]


def mainloop(program, debug):
    set_param(None, 'trace_limit', 30000)
    assert_green(program)
    pc = 0
    stacksize = 0
    is_queue = False
    storage = Storage()
    selected = storage[0]
    while pc < program.size:
        #debug.storage(storage, selected)
        #raw_input()
        #debug.show(pc)
        stackok = program.get_req_size(pc) <= stacksize
        driver.jit_merge_point(pc=pc, stackok=stackok, is_queue=is_queue, program=program, stacksize=stacksize, storage=storage, selected=selected)
        op = program.get_op(pc)
        assert_green(op)
        stacksize += - OP_STACKDEL[op] + OP_STACKADD[op]
        if op == OP_ADD:
            selected.add()
        elif op == OP_SUB:
            selected.sub()
        elif op == OP_MUL:
            selected.mul()
        elif op == OP_DIV:
            selected.div()
        elif op == OP_MOD:
            selected.mod()
        elif op == OP_POP:
            selected.pop()
        elif op == OP_PUSH:
            value = program.get_operand(pc)
            selected.push(value)
        elif op == OP_DUP:
            selected.dup()
        elif op == OP_SWAP:
            selected.swap()
        elif op == OP_SEL:
            value = program.get_operand(pc)
            selected = storage[value]
            stacksize = len(selected)
            is_queue = value == VAL_QUEUE
        elif op == OP_MOV:
            r = selected.pop()
            value = program.get_operand(pc)
            storage[value].push(r)
        elif op == OP_CMP:
            selected.cmp()
        elif op == OP_BRZ:
            r = selected.pop()
            if r == 0:
                value = program.get_label(pc)
                pc = value
                stackok = program.get_req_size(pc) <= stacksize
                driver.can_enter_jit(pc=pc, stackok=stackok, is_queue=is_queue, program=program, stacksize=stacksize, storage=storage, selected=selected)
                continue
        elif op == OP_BRPOP1 or op == OP_BRPOP2:
            if not stackok:
                value = program.get_label(pc)
                pc = value
                stackok = program.get_req_size(pc) <= stacksize
                driver.can_enter_jit(pc=pc, stackok=stackok, is_queue=is_queue, program=program, stacksize=stacksize, storage=storage, selected=selected)
                continue
        elif op == OP_POPNUM:
            r = selected.pop()
            os.write(1, str(r))
        elif op == OP_POPCHAR:
            r = selected.pop()
            os.write(1, unichr(r).encode('utf-8'))
        elif op == OP_PUSHNUM:
            num = get_number()
            selected.push(num)
        elif op == OP_PUSHCHAR:
            c = get_utf8()
            selected.push(c)
        elif op == OP_JMP:
            value = program.get_label(pc)
            pc = value
            stackok = program.get_req_size(pc) <= stacksize
            driver.can_enter_jit(pc=pc, stackok=stackok, is_queue=is_queue, program=program, stacksize=stacksize, storage=storage, selected=selected)
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
    
    compiler = compile.Compiler()

    if filename == '-':
        fp = 0
    else:
        fp = os.open(filename, os.O_RDONLY, 0777)
    if filename.endswith('.aheuic'):
        compiler.read(fp)
    elif filename.endswith('.aheuis'):
        compiler.read_asm(fp)
    else:
        program_contents = ''
        while True:
            read = os.read(fp, 4096)
            if len(read) == 0:
                break
            program_contents += read
 
        compiler.compile(program_contents)
        compiler.optimize()

        if filename != '-':
            binname = filename
            if binname.endswith('.aheui'):
                binname += 'c'
            else:
                binname += '.aheuic'
            try:
                bfp = os.open(binname, os.O_WRONLY|os.O_CREAT, 0644)
                compiler.write(bfp)
                os.write(bfp, '\n\n')
                compiler.write_asm(bfp)
                os.close(bfp)
            except:
                pass
    os.close(fp)

    program = Program(compiler.lines, compiler.label_map)
    exitcode = mainloop(program, compiler.debug)
    return exitcode


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    """Python compatibility."""
    import sys
    sys.exit(entry_point(sys.argv))

