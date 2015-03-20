#!/usr/bin/env python
# coding: utf-8
import os
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

OPCODE_NAMES = [None, None, 'div', 'add', 'mul', 'mod', 'pop', 'push', 'dup', 'sel', 'mov', None, 'cmp', None, 'brz', None, 'sub', 'swap', 'halt', 'popnum', 'popchar', 'pushnum', 'pushchar', 'brpop2', 'brpop1', 'jmp']

def get_location(pc, stacksize, program):
    return "#%d_stack%d_%s_%d" % (pc, stacksize, OPCODE_NAMES[program[pc][0]], program[pc][1])

jitdriver = JitDriver(greens=['pc', 'stacksize', 'program'], reds=['storage', 'selected'], get_printable_location=get_location)


DEBUG = False
class Debug(object):
    ENABLED = DEBUG

    def __init__(self, primitive, serialized, code_map):
        self.primitive = primitive
        self.serialized = serialized
        self.code_map = code_map
        self.inv_map = {}
        for k, v in self.code_map.items():
            try:
                self.inv_map[v].append(k)
            except:
                self.inv_map[v] = [k]

    def show(self, pc):
        if not self.ENABLED: return

        op, value = self.serialized[pc]
        positions = self.inv_map.get(pc, [])
        if not positions:
            os.write(2, 'No instruction information for pc %s\n' % pc)
        for position in positions:
            char = self.primitive.pane[position[0]]
            os.write(2, (u'%s %s(%s) %s # %s\n' % (char, OPCODE_NAMES[op], unichr(0x1100 + op), value, position)).encode('utf-8'))

    def dump(self):
        keys = sorted(self.inv_map.keys())
        for k in keys:
            pos = self.inv_map[k]
            char = self.primitive.pane[pos[0][0]]
            os.write(2, (u'%d %s\n' % (k, char)).encode('utf-8'))

    def storage(self, storage, selected=None):
        for i, l in enumerate(storage.lists):
            marker = u':' if l == selected else u' '
            os.write(2, (u'%s (%d):%s' % (unichr(0x11a8 + i - 1), i, marker)).encode('utf-8'))
            os.write(2, ('%s\n' % l.list))


class Assembler(object):
    def __init__(self):
        self.lines = []
        self.debug = None

    def compile(self, program):
        """Compile to aheui-assembly representation."""
        primitive = PrimitiveProgram(program)

        code_map = {}
        self.serialize(primitive, code_map, (0, 0), DIR_DOWN)
        self.debug = Debug(primitive, self.lines, code_map)

    def serialize(self, primitive, code_map, position, direction, depth=0):
        while True:
            if not position in primitive.pane:
                position = primitive.advance_position(position, direction)
                continue

            op, mv, val = primitive.decode(position)
            new_direction, step = dir_from_mv(mv, direction)
            
            if (position, direction) in code_map:
                index = code_map[position, direction]
                code_map[position, direction + 10] = len(self.lines)
                self.lines.append((OP_JMP, index))
                break

            code_map[position, direction] = len(self.lines)

            direction = new_direction
            if OP_HASOP[op]:
                if op == OP_POP:
                    if val == VAL_NUMBER:
                        op = OP_POPNUM
                    elif val == VAL_UNICODE:
                        op = OP_POPCHAR
                    else:
                        pass
                elif op == OP_PUSH:
                    if val == VAL_NUMBER:
                        op = OP_PUSHNUM
                    elif val == VAL_UNICODE:
                        op = OP_PUSHCHAR
                    else:
                        pass
                else:
                    pass

                if op == OP_PUSH:
                    self.lines.append((op, VAL_CONSTS[val]))
                elif op == OP_BRZ:
                    idx = len(self.lines)
                    code_map[position, direction + 10] = idx
                    self.lines.append((OP_BRZ, -1))
                    position1 = primitive.advance_position(position, direction, step)
                    self.serialize(primitive, code_map, position1, direction, depth + 1)
                    self.lines[idx] = OP_BRZ, len(self.lines)
                    position2 = primitive.advance_position(position, -direction, step)
                    self.serialize(primitive, code_map, position2, -direction, depth + 1)
                else:
                    req_size = OP_REQSIZE[op]
                    if req_size > 0:
                        brop = OP_BRPOP1 if req_size == 1 else OP_BRPOP2
                        idx = len(self.lines)
                        code_map[position, direction + 10] = idx
                        code_map[position, direction] = idx + 1
                        self.lines.append((brop, -1))
                        if OP_USEVAL[op]:
                            self.lines.append((op, val))
                        else:
                            self.lines.append((op, -1))
                        position1 = primitive.advance_position(position, direction, step)
                        self.serialize(primitive, code_map, position1, direction, depth + 1)
                        self.lines[idx] = brop, len(self.lines)
                        position2 = primitive.advance_position(position, -direction, step)
                        self.serialize(primitive, code_map, position2, -direction, depth + 1)
                    else:
                        if OP_USEVAL[op]:
                            self.lines.append((op, val))
                        else:
                            self.lines.append((op, -1))
                            if op == OP_HALT:
                                break

            position = primitive.advance_position(position, direction, step)


    def export(self):
        for i, (op, val) in enumerate(self.lines):
            code = OPCODE_NAMES[op]
            if code is None:
                code = 'inst' + str(op)
            if val != -1:
                print '%s %s; L%d' % (code, val, i)
            else:
                print '%s; L%d' % (code, i)


# ㄱ
# ㄲ
OP_DIV = 2 # ㄴ
OP_ADD = 3 # ㄷ
OP_MUL = 4 # ㄸ
OP_MOD = 5 # ㄹ
OP_POP = 6 # ㅁ
OP_PUSH= 7 # ㅂ
OP_DUP = 8 # ㅃ
OP_SEL = 9 # ㅅ
OP_MOV = 10 # ㅆ
OP_NONE= 11 # ㅇ
OP_CMP = 12 # ㅈ
# ㅉ
OP_BRZ = 14
# ㅋ
OP_SUB = 16 # ㅌ
OP_SWAP= 17 # ㅍ
OP_HALT= 18 # ㅎ
## end of primitive
OP_POPNUM = 19
OP_POPCHAR = 20
OP_PUSHNUM = 21
OP_PUSHCHAR = 22
OP_BRPOP2 = -3 # special
OP_BRPOP1 = -2 # special
OP_JMP = -1 # special

MV_RIGHT = 0 # ㅏ
# ㅐ
MV_RIGHT2 = 2 # ㅑ
# ㅒ
MV_LEFT = 4 # ㅓ
# ㅔ
MV_LEFT2 = 6 # ㅕ
# ㅖ
MV_UP = 8 # ㅗ
# ㅘ
# ㅙ
# ㅚ
MV_UP2 = 12 # ㅛ
MV_DOWN = 13 # ㅜ
# ㅝ
# ㅞ
# ㅟ
MV_DOWN2 = 17 # ㅠ
MV_HWALL = 18 # ㅡ
MV_WALL = 19 # ㅢ
MV_VWALL = 20 # ㅣ

VAL_QUEUE = 21
VAL_NUMBER = 21
VAL_UNICODE = 27

OP_HASOP = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
OP_USEVAL = [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
OP_REQSIZE = [0, 0, 2, 2, 2, 2, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 2, 2, 0, 1, 1, 0, 0, 2, 1, 0]
VAL_CONSTS = [0, 2, 4, 4, 2, 5, 5, 3, 5, 7, 9, 9, 7, 9, 9, 8, 4, 4, 6, 2, 4, 1, 3, 4, 3, 4, 4, 3]

DIR_DOWN = 1
DIR_RIGHT = 2
DIR_UP = -1
DIR_LEFT = -2



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

class PrimitiveProgram(object):
    def __init__(self, text):
        self.text = text.decode('utf-8')
        self.pane = {}

        pc_row = 0
        pc_col = 0
        max_col = 0
        for char in self.text:
            if char == '\n':
                pc_row += 1
                max_col = max(max_col, pc_col)
                pc_col = 0
                continue
            if u'가' <= char <= u'힣':
                self.pane[pc_row, pc_col] = char
            pc_col += 1
        max_col = max(max_col, pc_col)

        self.max_row = pc_row
        self.max_col = max_col

    def decode(self, position):
        code = self.pane[position]
        base = ord(code) - ord(u'가')
        op_code = base / 588
        mv_code = (base / 28) % 21
        val_code = base % 28
        return op_code, mv_code, val_code

    def advance_position(self, position, direction, step=1):
        r, c = position
        d = direction
        if d == DIR_DOWN:
            r += step
            if r > self.max_row:
                r = 0
            p = r, c
            return p
        elif d == DIR_RIGHT:
            c += step
            if c > self.max_col:
                c = 0
            p = r, c
            return p
        elif d == DIR_UP:
            r -= step
            if r < 0:
                r = self.max_row
            p = r, c
            return p
        elif d == DIR_LEFT:
            c -= step
            if c < 0:
                c = self.max_col
            p = r, c
            return p
        else:
            assert False


def dir_from_mv(mv_code, direction):
    if mv_code == MV_RIGHT:
        return DIR_RIGHT, 1
    elif mv_code == MV_RIGHT2:
        return DIR_RIGHT, 2
    elif mv_code == MV_LEFT:
        return DIR_LEFT, 1
    elif mv_code == MV_LEFT2:
        return DIR_LEFT, 2
    elif mv_code == MV_UP:
        return DIR_UP, 1
    elif mv_code == MV_UP2:
        return DIR_UP, 2
    elif mv_code == MV_DOWN:
        return DIR_DOWN, 1
    elif mv_code == MV_DOWN2:
        return DIR_DOWN, 2
    elif mv_code == MV_WALL:
        if direction == DIR_RIGHT:
            return DIR_LEFT, 1
        elif direction == DIR_LEFT:
            return DIR_RIGHT, 1
        elif direction == DIR_UP:
            return DIR_DOWN, 1
        elif direction == DIR_DOWN:
            return DIR_UP, 1
        else:
            assert False
    elif mv_code == MV_HWALL:
        if direction == DIR_UP:
            return DIR_DOWN, 1
        elif direction == DIR_DOWN:
            return DIR_UP, 1
        else:
            return direction, 1
    elif mv_code == MV_VWALL:
        if direction == DIR_RIGHT:
            return DIR_LEFT, 1
        elif direction == DIR_LEFT:
            return DIR_RIGHT, 1
        else:
            return direction, 1
    else:
        return direction, 1

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

import os
def run(fp):
    program_contents = ''
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    assembler = Assembler()
    assembler.compile(program_contents)
    return mainloop(assembler.lines, assembler.debug)

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print 'filename'
        return 1
    fp = os.open(filename, os.O_RDONLY, 0777)
    exitcode = run(fp)
    return exitcode

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    import sys
    entry_point(sys.argv)


