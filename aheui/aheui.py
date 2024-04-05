#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import

import os

from aheui import const as c
from aheui._compat import jit, unichr, ord, _unicode, bigint, PYR
from aheui import compile
from aheui.option import process_options
from aheui.warning import WarningPool


def get_location(pc, stackok, is_queue, program):
    """Add debug information.

    PYPYLOG=jit-log-opt,jit-backend,jit-summary:<filename>
    """
    op = program.get_op(pc)
    val = ('_%d' % program.get_operand(pc)) if compile.OP_USEVAL[op] else ''
    op_name = compile.OP_NAMES[op]
    assert op_name is not None
    return "#%d(s%dq%d)_%s%s" % (pc, stackok, is_queue, op_name.encode('utf-8'), val)


driver = jit.JitDriver(
    greens=['pc', 'stackok', 'is_queue', 'program'],
    reds=['stacksize', 'storage', 'selected'],
    get_printable_location=get_location)


DEBUG = False  # debug flag for `rpaheui`
MINUS1 = bigint.fromlong(-1)


class Link(object):
    """Element unit for stack and queue."""

    def __init__(self, next, value=MINUS1):
        self.value = value
        self.next = next


class LinkedList(object):
    """Common linked list for storages"""

    def __len__(self):
        return self.size

    def pop(self):
        node = self.head
        self.head = node.next
        value = node.value
        del node
        self.size -= 1
        return value

    def swap(self):
        node1 = self.head
        node2 = node1.next
        node1.value, node2.value = node2.value, node1.value

    def add(self):
        r1, r2 = self._get_2_values()
        r = bigint.add(r2, r1)
        self._put_value(r)

    def sub(self):
        r1, r2 = self._get_2_values()
        r = bigint.sub(r2, r1)
        self._put_value(r)

    def mul(self):
        r1, r2 = self._get_2_values()
        r = bigint.mul(r2, r1)
        self._put_value(r)

    def div(self):
        r1, r2 = self._get_2_values()
        r = bigint.div(r2, r1)
        self._put_value(r)

    def mod(self):
        r1, r2 = self._get_2_values()
        r = bigint.mod(r2, r1)
        self._put_value(r)

    def cmp(self):
        r1, r2 = self._get_2_values()
        r = int(bigint.ge(r2, r1))
        big_r = bigint.fromint(r)
        self._put_value(big_r)


class Stack(LinkedList):
    """Base data storage for Aheui, except for ieung and hieuh."""

    def __init__(self):
        self.head = None
        self.size = 0

    def push(self, value):
        # assert(isinstance(value, bigint.Int))
        node = Link(self.head, value)
        self.head = node
        self.size += 1

    def dup(self):
        self.push(self.head.value)

    # Tools for common methods. inline?

    def _get_2_values(self):
        return self.pop(), self.head.value

    def _put_value(self, value):
        self.head.value = value


class Queue(LinkedList):

    def __init__(self):
        self.tail = Link(None)
        self.head = self.tail
        self.size = 0

    def push(self, value):
        # assert(isinstance(value, bigint.Int))
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

    def _get_2_values(self):
        return self.pop(), self.pop()

    def _put_value(self, value):
        self.push(value)


class Port(LinkedList):

    def __init__(self):
        self.head = None
        self.size = 0
        self.last_push = bigint.fromint(0)

    def push(self, value):
        # assert(isinstance(value, bigint.Int))
        node = Link(self.head, value)
        self.head = node
        self.size += 1
        self.last_push = value

    def dup(self):
        self.push(self.last_push)

    def _get_2_values(self):
        return self.pop(), self.head.value

    def _put_value(self, value):
        self.head.value = value


class Storage(object):
    _immutable_fields = ['pools[*]']

    def __init__(self):
        pools = []
        for i in range(0, c.STORAGE_COUNT):
            if i == c.VAL_QUEUE:
                pools.append(Queue())
            elif i == c.VAL_PORT:
                pools.append(Port())
            else:
                pools.append(Stack())
        self.pools = pools

    def __getitem__(self, idx):
        return self.pools[idx]


class InputBuffer(object):

    def __init__(self, read=os.read):
        self.buf = b''
        self.read = read

    def load(self, length):
        read_length = length - len(self.buf)
        if read_length > 0:
            self.buf += self.read(0, read_length)

    def take(self, length):
        result, self.buf = self.buf[:length], self.buf[length:]
        return result

    def look(self, length):
        return self.buf[:length]


input_buffer = InputBuffer()


@jit.dont_look_inside
def read_utf8(input_buffer=input_buffer):
    """Get a utf-8 character from standard input.

    The length of a UTF-8 character can be detected in the first byte.
    If decoding fails, it indicates that the character is broken.
    In Aheui, non-UTF-8 character input is undefined.
    In this implementation, let's assign -1.
    """
    input_buffer.load(1)
    head = input_buffer.look(1)
    if head:
        v = ord(head[0])
        if v >= 0x80:
            if (v & 0xf0) == 0xf0:
                length = 4
            elif (v & 0xe0) == 0xe0:
                length = 3
            elif (v & 0xc0) == 0xc0:
                length = 2
            else:
                length = 0
        else:
            length = 1
        if length > 0:
            input_buffer.load(length)
            buf = input_buffer.take(length)
            if len(buf) == length:
                try:
                    decoded = buf.decode('utf-8')
                    v = ord(decoded[0])
                except UnicodeDecodeError:
                    v = -1
            else:
                v = -1
    else:
        v = -1
    big_v = bigint.fromint(v)
    return big_v


@jit.dont_look_inside
def read_number(input_buffer=input_buffer):
    """Get a number from standard input."""
    input_buffer.load(1)
    numchar = input_buffer.look(1)  # for sign
    negative = numchar == b'-'
    if negative:
        input_buffer.take(1)
    numchars = []
    while True:
        input_buffer.load(1)
        numchar = input_buffer.look(1)
        if numchar not in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'0']:
            if numchar in [b' ', b'\t', b'\n']:
                input_buffer.take(1)
            break
        else:
            input_buffer.take(1)
            numchars.append(numchar)
    assert len(numchars) > 0
    if negative:
        numchars.insert(0, b'-')
    num = bigint.fromstr(b''.join(numchars))
    return num


def write_number(value_str):
    os.write(outfp, value_str)


def write_utf8(warnings, value):
    REPLACE_CHAR = unichr(0xfffd).encode('utf-8')

    if bigint.is_unicodepoint(value):
        codepoint = bigint.toint(value)
        unicode_char = unichr(codepoint)
        bytes = unicode_char.encode('utf-8')
    else:
        bytes = REPLACE_CHAR

    os.write(outfp, bytes)


def warn_utf8_range(warnings, value):
    warnings.warn(b'write-utf8-range', value)
    os.write(outfp, unichr(0xfffd).encode('utf-8'))

class Program(object):
    _immutable_fields_ = ['labels[**]', 'opcodes[*]', 'values[*]', 'size']

    def __init__(self, lines, label_map):
        self.opcodes = [line[0] for line in lines]
        self.values = [line[1] for line in lines]
        self.size = len(lines)
        self.labels = label_map

    @jit.elidable
    def get_op(self, pc):
        return self.opcodes[pc]

    @jit.elidable
    def get_operand(self, pc):
        return self.values[pc]

    @jit.elidable
    def get_req_size(self, pc):
        return c.OP_REQSIZE[self.get_op(pc)]

    @jit.elidable
    def get_label(self, pc):
        return self.labels[self.get_operand(pc)]


outfp = 1
errfp = 2
warnings = WarningPool()


def mainloop(program, debug):
    program = jit.promote(program)
    jit.assert_green(program)
    pc = 0
    stacksize = 0
    is_queue = False
    storage = Storage()
    storage = jit.promote(storage)
    selected = storage[0]
    jit.assert_green(selected)

    # debug_skip = 0
    # runtime_counter = 0
    while pc < program.size:
        '''
        #  debug.storage(storage, selected)
        runtime_counter += 1
        os.write(errfp, b'%8d\t' % runtime_counter)
        debug.show(pc)
        if debug_skip <= 0:
            raw_debug_skip = raw_input()
            if not raw_debug_skip:
                raw_debug_skip = '0'
            debug_skip = int(raw_debug_skip)
        else:
            debug_skip -= 1
        '''
        stackok = program.get_req_size(pc) <= stacksize
        driver.jit_merge_point(
            pc=pc, stackok=stackok, is_queue=is_queue, program=program,
            stacksize=stacksize, storage=storage, selected=selected)
        op = program.get_op(pc)
        jit.assert_green(op)
        stacksize += - c.OP_STACKDEL[op] + c.OP_STACKADD[op]
        if op == c.OP_ADD:
            selected.add()
        elif op == c.OP_SUB:
            selected.sub()
        elif op == c.OP_MUL:
            selected.mul()
        elif op == c.OP_DIV:
            selected.div()
        elif op == c.OP_MOD:
            selected.mod()
        elif op == c.OP_POP:
            selected.pop()
        elif op == c.OP_PUSH:
            value = program.get_operand(pc)
            big_value = bigint.fromint(value)
            selected.push(big_value)
        elif op == c.OP_DUP:
            selected.dup()
        elif op == c.OP_SWAP:
            selected.swap()
        elif op == c.OP_SEL:
            value = program.get_operand(pc)
            selected = storage[value]
            stacksize = len(selected)
            is_queue = value == c.VAL_QUEUE
        elif op == c.OP_MOV:
            r = selected.pop()
            value = program.get_operand(pc)
            targeted = storage[value]
            targeted.push(r)
            if selected == targeted:
                stacksize += 1
        elif op == c.OP_CMP:
            selected.cmp()
        elif op == c.OP_BRPOP1 or op == c.OP_BRPOP2 or op == c.OP_JMP or op == c.OP_BRZ:
            if op == c.OP_BRPOP1 or op == c.OP_BRPOP2:
                jump = not stackok
            elif op == c.OP_JMP:
                jump = True
            elif op == c.OP_BRZ:
                top = selected.pop()
                jump = bigint.is_zero(top)
            else:
                assert False
            if jump:
                value = program.get_label(pc)
                pc = value
                stackok = program.get_req_size(pc) <= stacksize
                driver.can_enter_jit(
                    pc=pc, stackok=stackok, is_queue=is_queue, program=program,
                    stacksize=stacksize, storage=storage, selected=selected)
                continue
        elif op == c.OP_POPNUM:
            r = selected.pop()
            write_number(bigint.str(r))
        elif op == c.OP_POPCHAR:
            r = selected.pop()
            write_utf8(warnings, r)
        elif op == c.OP_PUSHNUM:
            num = read_number()
            selected.push(num)
        elif op == c.OP_PUSHCHAR:
            char = read_utf8()
            selected.push(char)
        elif op == c.OP_NONE:
            pass
        elif op == c.OP_HALT:
            break
        else:
            os.write(errfp, (u'Missing operator: %s' % _unicode(op)).encode('utf-8'))
            assert False
        pc += 1

    if len(selected) > 0:
        return bigint.toint(selected.pop())
    else:
        return 0


def open_w(filename):
    return os.open(filename, os.O_WRONLY | os.O_CREAT, 0o644)


def prepare_compiler(contents, opt_level=2, source='code', aheuic_output=None, add_debug_info=False):
    compiler = compile.Compiler()
    if source == 'bytecode':
        compiler.read_bytecode(contents)
    elif source == 'asm':
        compiler.read_asm(contents.decode('utf-8'))
    else:
        contents = contents.decode('utf-8')
        compiler.compile(contents, add_debug_info=add_debug_info)

    if opt_level == 0:
        pass
    elif opt_level == 1:
        compiler.optimize1()
    elif opt_level == 2:
        compiler.optimize2()
    else:
        assert False

    if aheuic_output is not None:
        try:
            bfp = open_w(aheuic_output)
            bytecode = compiler.write_bytecode()
            asm = compiler.write_asm().encode('utf-8')
            os.write(bfp, bytecode)
            os.write(bfp, '\n\n')
            os.write(bfp, asm)
            os.close(bfp)
        except Exception:
            pass
    return compiler


def entry_point(argv):
    try:
        cmd, source, contents, str_opt_level, target, aheuic_output, comment_aheuis, output, warning_limit, trace_limit = process_options(argv, os.environ)
    except SystemExit:
        return 1

    warnings.limit = warning_limit
    if trace_limit >= 0:
        jit.set_param(driver, 'trace_limit', trace_limit)

    add_debug_info = DEBUG or target != 'run'  # debug flag for user program
    compiler = prepare_compiler(contents, int(str_opt_level), source, aheuic_output, add_debug_info)
    outfp = 1 if output == '-' else open_w(output)
    if target == 'run':
        if not PYR:
            warnings.warn(b'no-rpython')
        program = Program(compiler.lines, compiler.label_map)
        exitcode = mainloop(program, compiler.debug)
    elif target in ['asm', 'asm+comment']:
        asm = compiler.write_asm(commented=comment_aheuis).encode('utf-8')
        os.write(outfp, asm)
        os.close(outfp)
        exitcode = 0
    elif target == 'bytecode':
        bytecode = compiler.write_bytecode()
        os.write(outfp, bytecode)
        os.close(outfp)
        exitcode = 0
    else:
        assert False
    return exitcode
