#!/usr/bin/env python
# coding: utf-8
import os
#import rpython.rlib import jit

class Debug(object):
    ENABLED = False
    OPCODES = [None, None, 'div', 'add', 'mul', 'mod', 'pop', 'push', 'dup', 'sel', 'mov', None, 'cmp', None, 'brz', None, 'sub', 'swap', 'halt', 'outnum', 'outchar', 'innum', 'inchar', 'jmp']

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
        opcode, value = self.serialized[pc]
        positions = self.inv_map[pc]
        char = self.primitive.pane[positions[0][0]]
        os.write(2, (u'%s %s(%s) %s # %s\n' % (char, self.OPCODES[opcode], unichr(0x1100 + opcode), value, self.inv_map[pc])).encode('utf-8'))

    def dump(self):
        if not self.ENABLED: return
        keys = sorted(self.inv_map.keys())
        for k in keys:
            pos = self.inv_map[k]
            char = self.primitive.pane[pos[0][0]]
            os.write(2, (u'%d %s\n' % (k, char)).encode('utf-8'))

    def export(self):
        if not self.ENABLED: return
        for op, val in self.serialized:
            code = self.OPCODES[op]
            if code is None:
                code = 'inst' + str(op)
            if val != -1:
                print code, val
            else:
                print code

    def storage(self, storage):
        for i, l in enumerate(storage.lists):
            marker = ':' if l == storage.selected else ' '
            os.write(2, (u'%s (%2d):%s%s\n' % (unichr(0x11a8 + i - 1), i, marker, l.list)).encode('utf-8'))

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
OP_OUTNUM = 19
OP_OUTCHAR = 20
OP_INNUM = 21
OP_INCHAR = 22
OP_BRPOP = -2 # special
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

OP_HASOP = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
OP_USEVAL = [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
OP_REQSIZE = [0, 0, 2, 2, 2, 2, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 2, 2, 0, 1, 1, 0, 0, 0, 0]
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


class Storage(object):
    def __init__(self):
        storage = []
        for i in range(0, 28):
            if i == VAL_QUEUE:
                storage.append(Queue())
            else:
                storage.append(Stack())
        self.lists = storage
        self.selected = self.lists[0]

    def select(self, index):
        self.selected = self.lists[index]


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

def serialize(primitive, code_map, serialized, position, direction):
    while True:
        posdir = position, direction
        if posdir in code_map:
            index = code_map[posdir]
            code_map[position, -direction] = len(serialized)
            serialized.append((OP_JMP, index))
            break

        code_map[posdir] = len(serialized)
        if not position in primitive.pane:
            position = primitive.advance_position(position, direction)
            continue

        op, mv, val = primitive.decode(position)
        direction, step = dir_from_mv(mv, direction)
        if OP_HASOP[op]:
            if op == OP_POP:
                if val == VAL_NUMBER:
                    op = OP_OUTNUM
                elif val == VAL_UNICODE:
                    op = OP_OUTCHAR
                else:
                    pass
            elif op == OP_PUSH:
                if val == VAL_NUMBER:
                    op = OP_INNUM
                elif val == VAL_UNICODE:
                    op = OP_INCHAR
                else:
                    pass
            else:
                pass

            if op == OP_PUSH:
                serialized.append((op, VAL_CONSTS[val]))
            elif op == OP_BRZ:
                idx = len(serialized)
                serialized.append((OP_BRZ, -1))
                position1 = primitive.advance_position(position, direction, step)
                serialize(primitive, code_map, serialized, position1, direction)
                serialized[idx] = OP_BRZ, len(serialized)
                position2 = primitive.advance_position(position, -direction, step)
                serialize(primitive, code_map, serialized, position2, -direction)
            else:
                req_size = OP_REQSIZE[op]
                #if req_size > 0:
                #    serialized.append((OP_BRPOP, req_size))
                if OP_USEVAL[op]:
                    serialized.append((op, val))
                else:
                    serialized.append((op, -1))

        position = primitive.advance_position(position, direction, step)

def parse(program):
    primitive = PrimitiveProgram(program)

    code_map = {}
    serialized = []
    serialize(primitive, code_map, serialized, (0, 0), DIR_DOWN)

    debug = Debug(primitive, serialized, code_map)
    return serialized, debug

def mainloop(program, debug):
    debug.export()
    s = Storage()
    pc = 0
    while pc < len(program):
        debug.show(pc)
        op, value = program[pc]
        if op == OP_ADD:
            r1, r2 = s.selected.pop(), s.selected.pop()
            s.selected.push(r2 + r1)
        elif op == OP_SUB:
            r1, r2 = s.selected.pop(), s.selected.pop()
            s.selected.push(r2 - r1)
        elif op == OP_MUL:
            r1, r2 = s.selected.pop(), s.selected.pop()
            s.selected.push(r2 * r1)
        elif op == OP_DIV:
            r1, r2 = s.selected.pop(), s.selected.pop()
            s.selected.push(r2 / r1)
        elif op == OP_MOD:
            r1, r2 = s.selected.pop(), s.selected.pop()
            s.selected.push(r2 % r1)
        elif op == OP_POP:
            s.selected.pop()
        elif op == OP_PUSH:
            s.selected.push(value)
        elif op == OP_DUP:
            s.selected.dup()
        elif op == OP_SWAP:
            s.selected.swap()
        elif op == OP_SEL:
            s.select(value)
        elif op == OP_MOV:
            r = s.selected.pop()
            s.lists[value].push(r)
        elif op == OP_CMP:
            r1, r2 = s.selected.pop(), s.selected.pop()
            r = 1 if r2 >= r1 else 0
            s.selected.push(r)
        elif op == OP_BRZ:
            r = s.selected.pop()
            if r == 0:
                pc = value
                continue
        elif op == OP_OUTNUM:
            r = s.selected.pop()
            os.write(1, str(r))
        elif op == OP_OUTCHAR:
            r = s.selected.pop()
            os.write(1, unichr(r).encode('utf-8'))
        elif op == OP_INNUM:
            numchars = []
            while True:
                numchar = os.read(0, 1)
                if numchar not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                    break
                else:
                    numchars.append(numchar)
            assert len(numchars) > 0
            num = int(''.join(numchars))
            s.selected.push(num)
        elif op == OP_INCHAR:
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
                s.selected.push(v)
            else:
                s.selected.push(-1)
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
        #debug.storage(s)
        #raw_input()

import os
def run(fp):
    program_contents = ''
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    program, debug = parse(program_contents)
    mainloop(program, debug)

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print 'filename'
        return 1
    fp = os.open(filename, os.O_RDONLY, 0777)
    run(fp)
    return 0

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    import sys
    entry_point(sys.argv)


