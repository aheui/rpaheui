#!/usr/bin/env python
# coding: utf-8

try:
    import settings
    DEBUG = settings.DEBUG
except ImportError:
    DEBUG = False

import os
from const import *
try:
    from rpython.rlib.listsort import TimSort
except ImportError:
    class TimSort(object):
        def __init__(self, list):
            self.list = list

        def sort(self):
            self.list.sort()


OPCODE_NAMES = [None, None, 'DIV', 'ADD', 'MUL', 'MOD', 'POP', 'PUSH', 'DUP', 'SEL', 'MOV', None, 'CMP', None, 'BRZ', None, 'SUB', 'SWAP', 'HALT', 'POPNUM', 'POPCHAR', 'PUSHNUM', 'PUSHCHAR', 'BRPOP2', 'BRPOP1', 'JMP']

OP_HASOP = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
OP_USEVAL = [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
VAL_CONSTS = [0, 2, 4, 4, 2, 5, 5, 3, 5, 7, 9, 9, 7, 9, 9, 8, 4, 4, 6, 2, 4, 1, 3, 4, 3, 4, 4, 3]


VAL_NUMBER = 21
VAL_UNICODE = 27


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

    def show(self, pc, fp=2):
        op, value = self.serialized[pc]
        positions = self.inv_map.get(pc, [])
        if not positions:
            os.write(fp, (u'%d X %s(%s) %s\n' % (pc, OPCODE_NAMES[op], unichr(0x1100 + op), value)).encode('utf-8'))
        for position in positions:
            char = self.primitive.pane[position[0]]
            os.write(fp, (u'%d %s %s(%s) %s # %s\n' % (pc, char, OPCODE_NAMES[op], unichr(0x1100 + op), value, position)).encode('utf-8'))

    def dump(self, fp=2):
        keys = sorted(self.inv_map.keys())
        for k in keys:
            pos = self.inv_map[k]
            char = self.primitive.pane[pos[0][0]]
            os.write(fp, (u'%d %s\n' % (k, char)).encode('utf-8'))

    def _list(self, list):
        items = []
        node = list.head
        while node.next:
            items.append(str(node.value))
            node = node.next
        return '[' + ', '.join(items) + ']'

    def storage(self, storage, selected=None):
        for i, l in enumerate(storage):
            marker = u':' if l == selected else u' '
            os.write(2, (u'%s (%d):%s' % (unichr(0x11a8 + i - 1), i, marker)).encode('utf-8'))
            os.write(2, ('%s\n' % self._list(l)))


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

        
DIR_DOWN = 1
DIR_RIGHT = 2
DIR_UP = -1
DIR_LEFT = -2

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


class Compiler(object):
    """Compiler manipulate any kinds of aheui related code representation.

    1. `compile` accepts raw aheui code text and generate serialized bytecodes.
    2. `optimize` optimizes loaded bytecodes.
    3. `read` and `write` read and write bytecodes.
    3. `dump` writes assembly.
    """

    def __init__(self):
        self.lines = []
        self.debug = None
        self.label_map = {}

    def compile(self, program):
        """Compile to aheui-assembly representation."""
        primitive = PrimitiveProgram(program)

        self.lines, self.label_map, code_map = self.serialize(primitive)
        self.debug = Debug(primitive, self.lines, code_map)

    def serialize(self, primitive):
        """Serialize Aheui primitive codes.

        1. Start to trace the code pane from (0, 0)
        2. If there is branchable code,
            1. Add a label
            2. Set the label as target of jump.
            3. Add branch point to `job_queue`
            4. When it is dequeued, add the address to `label_map` and trace it.
        3. If serializer passes same code with same direction,
            1. Add `OP_JMP` to serialized address to connect.
            2. Stop the job and go to next job in the queue.
        4. If there is `OP_HALT`, go to next job in the queue.
        5. If `job_queue` is empty, drop any other instructions not on the path.
        """
        job_queue = [((0, 0), DIR_DOWN, -1)]

        lines = []
        label_map = {}
        code_map = {}
        while job_queue:
            position, direction, marker = job_queue.pop()
            if marker >= 0:
                label_map[marker] = len(lines)
            while True:
                if not position in primitive.pane:
                    position = primitive.advance_position(position, direction)
                    continue

                op, mv, val = primitive.decode(position)
                new_direction, step = dir_from_mv(mv, direction)

                if (position, direction) in code_map:
                    index = code_map[position, direction]
                    posdir = position, direction + 10
                    code_map[position, direction + 20] = len(lines)
                    if posdir in code_map:
                        target = code_map[posdir]
                    else:
                        target = index
                    label_id = len(lines)
                    label_map[label_id] = target
                    lines.append((OP_JMP, label_id))
                    break

                code_map[position, direction] = len(lines)

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
                        lines.append((op, VAL_CONSTS[val]))
                    elif op == OP_BRZ:
                        idx = len(lines)
                        code_map[position, direction + 10] = idx
                        lines.append((OP_BRZ, idx))
                        alt_position = primitive.advance_position(position, -direction, step)
                        job_queue.append((alt_position, -direction, idx))
                    else:
                        req_size = OP_REQSIZE[op]
                        if req_size > 0:
                            brop = OP_BRPOP1 if req_size == 1 else OP_BRPOP2
                            idx = len(lines)
                            code_map[position, direction + 10] = idx
                            code_map[position, direction] = idx + 1
                            lines.append((brop, idx))
                            if OP_USEVAL[op]:
                                lines.append((op, val))
                            else:
                                lines.append((op, -1))
                            alt_position = primitive.advance_position(position, -direction, step)
                            job_queue.append((alt_position, -direction, idx))
                        else:
                            if OP_USEVAL[op]:
                                lines.append((op, val))
                            else:
                                lines.append((op, -1))
                                if op == OP_HALT:
                                    break
                position = primitive.advance_position(position, direction, step)
        return lines, label_map, code_map

    def optimize_reachability(self):
        """Optimize codes by removing unreachable codes.

        Because unreachable path is already removed by `serialize`, this path
        mainly remove useless OP_BRPOPs and its branches.

        1. Trace current stack size from first line.
        2. If there is enough stack, do not trace OP_BRPOPs' jumps.
        3. If optimizer met OP_SEL, assume stacksize is 0 from there.
        3. If optimizer passes same codes,
            1. If assumed stacksize is smaller than before, keep going to trace.
            2. Otherwise it is not worth to do. Stop.
        4. Stop if OP_HALT.
        5. Drop useless OP_BRPOPs and any codes out of path.
        """
        minstack_map = [-1] * len(self.lines)
        job_queue = [(0, 0)]
        while len(job_queue) > 0:
            pc, stacksize = job_queue.pop(0) 
            while pc < len(self.lines):
                assert stacksize >= 0
                op, val = self.lines[pc]
                if minstack_map[pc] >= 0:
                    if minstack_map[pc] <= stacksize:
                        break
                if op == OP_BRPOP1 or op == OP_BRPOP2:
                    reqsize = OP_REQSIZE[op]
                    if stacksize >= reqsize:
                        pc += 1
                        continue
                    else:
                        minstack_map[pc] = stacksize
                        job_queue.append((self.label_map[val], stacksize))
                elif op == OP_BRZ:
                    stacksize -= 1
                    if stacksize < 0: stacksize = 0
                    minstack_map[pc] = stacksize
                    job_queue.append((self.label_map[val], stacksize))
                elif op == OP_JMP:
                    minstack_map[pc] = stacksize
                    pc = self.label_map[val]
                    continue
                else:
                    minstack_map[pc] = stacksize
                    stacksize -= OP_STACKDEL[op]
                    if stacksize < 0: stacksize = 0
                    stacksize += OP_STACKADD[op]
                    if op == OP_SEL:
                        stacksize = 0
                    elif op == OP_HALT:
                        break
                pc += 1

        reachability = [int(minstack >= 0) for minstack in minstack_map]
        return reachability

    def optimize_operation(self):
        """Optimize codes by removing constant operation.

        Because constants in aheui usuallly is generated by codes, aheui codes
        are normally full of OP_PUSH and operations. This path merge constants
        operations.

        1. Trace the code is passing when it is using queue or stack.
        2. If there is OP_SEL with ieung, suppose it is potential queue code.
        3. If tracer passes same codes,
            1. If current guess is queue but it was stack before, keep going.
            2. Otherwise stop.
        4. Repeat 2-3 until there is no jobs in queue.
        5. Let's start to optimize the code from the start to the end.
        6. Pick 3 consecutive instructions. If there is OP_NONE, ignore it.
        7. If 3 instructions don't includes labels for jump, potential queue
            codes and consists of only constants instructions, merge it.
        """
        job_queue = [(0, 0)]

        lines = self.lines
        queue_map = [-1] * len(lines)
        while len(job_queue) > 0:
            pc, in_queue = job_queue.pop(0)
            while pc < len(lines):
                op, val = lines[pc]
                if queue_map[pc] >= 0:
                    if in_queue == 0 or queue_map[pc] == 1:
                        break
                queue_map[pc] = in_queue
                if op in [OP_BRZ, OP_BRPOP1, OP_BRPOP2]:
                    job_queue.append((pc + 1, in_queue))
                    job_queue.append((self.label_map[val], in_queue))
                    break
                elif op == OP_JMP:
                    job_queue.append((self.label_map[val], in_queue))
                    break
                else:
                    pc += 1
                    if op == OP_SEL:
                        in_queue = int(val == VAL_QUEUE or val == VAL_PORT)
                    elif op == OP_HALT:
                        break
        assert -1 not in queue_map

        reachability = [1] * len(lines)
        for i in range(2, len(lines)):
            op, val = lines[i]
            if op not in [OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD, OP_CMP]:
                continue
            i1 = i - 1
            while lines[i1][0] == OP_NONE and i1 >= 1:
                i1 -= 1
            i2 = i1 - 1
            while lines[i1][0] == OP_NONE and i2 >= 0:
                i2 -= 1
            if queue_map[i] or queue_map[i1] or queue_map[i2]:
                continue
            inst1 = lines[i1]
            inst2 = lines[i2]
            if not inst2[0] == OP_PUSH:
                continue
            v2 = inst2[1]
            if inst1[0] == OP_PUSH:
                v1 = inst1[1]
            elif inst1[0] == OP_DUP:
                v1 = v2
            else:
                continue
            if op == OP_ADD:
                v = v2 + v1
            elif op == OP_SUB:
                v = v2 - v1
            elif op == OP_MUL:
                v = v2 * v1
            elif op == OP_DIV:
                v = v2 / v1
            elif op == OP_MOD:
                v = v2 % v1
            elif op == OP_CMP:
                v = int(v2 >= v1)
            else:
                assert False
            lines[i] = (OP_PUSH, v)
            lines[i1] = (OP_NONE, -1)
            lines[i2] = (OP_NONE, -1)
            reachability[i1] = 0
            reachability[i2] = 0
        return reachability


    def optimize_adjust(self, reachability):
        useless_map = [0] * len(reachability)
        count = 0
        for i, reachable in enumerate(reachability):
            useless_map[i] = count
            if not reachable:
                count += 1
        
        new = []
        code_map = {}
        new_label_map = {}
        for i, (op, val) in enumerate(self.lines):
            if not reachability[i]:
                continue
            new.append((op, val))
            if op in OP_JUMPS:
                target_idx = self.label_map[val]
                new_label_map[val] = target_idx - useless_map[target_idx]
            if i in self.debug.inv_map:
                keys = self.debug.inv_map[i]
                useless_count = useless_map[i]
                for key in keys:
                    code_map[key] = i - useless_count

        new_debug = Debug(self.debug.primitive, new, code_map) # wrong
        self.lines = new
        self.label_map = new_label_map
        self.debug = new_debug


    def optimize(self):
        """Optimize generated codes.

        Do not decouple each steps or change the order. It is important.
        """
        reachability = self.optimize_reachability()
        self.optimize_adjust(reachability)

        reachability = self.optimize_operation()
        self.optimize_adjust(reachability)


    def write(self, fp=1):
        """Write bytecodes down for given fp."""
        for op, val in self.lines:
            if op in OP_JUMPS:
                val = self.label_map[val]
            if val >= 0: 
                p_val = chr(val & 0xff) + chr((val & 0xff00) >> 8) + chr((val & 0xff0000) >> 16)
            else:
                p_val = '\0\0\0'
            if op < 0:
                op = 256 + op
            p_op = chr(op)
            p = p_val + p_op
            assert len(p) == 4
            os.write(fp, p)
        os.write(fp, '\xff\xff\xff\xff')


    def read(self, fp=0):
        """Read bytecodes from given fp."""
        self.debug = None
        self.lines = []
        self.label_map = {}
        while True:
            buf = os.read(fp, 4)
            assert len(buf) == 4
            if buf == '\xff\xff\xff\xff':
                break
            val = ord(buf[0]) + (ord(buf[1]) << 8) + (ord(buf[2]) << 16)
            op = ord(buf[3])
            if op > 128:
                op -= 256
            self.lines.append((op, val))
            if op in OP_JUMPS:
                self.label_map[val] = val 


    def write_asm(self, fp=1):
        """Write assembly representation with comments."""
        label_revmap = {}
        for i, (op, val) in enumerate(self.lines):
            if i in self.label_map.values():
                os.write(fp, 'L%d:' % i)
            code = OPCODE_NAMES[op]
            if code is None:
                code = 'inst' + str(op)
            if val != -1:
                if op in OP_JUMPS:
                    code_val = '%s L%s' % (code, self.label_map[val])
                else:
                    code_val = '%s %s' % (code, val)
            else:
                code_val = code
            if self.debug and i in self.debug.inv_map:
                debug_infos = []
                for posdir in self.debug.inv_map[i]:
                    position, direction = posdir
                    syllable = self.debug.primitive.pane[position].encode('utf-8')
                    debug_infos.append(' %s %s %d' % (syllable, position, direction))
                debug_info = ''.join(debug_infos)
            else:
                debug_info = ''
            os.write(fp, '\t%s\t; L%d%s\n' % (code_val, i, debug_info))

    def read_asm(self, fp=0):
        """Read assembly representation."""
        OPCODE_MAP = {}
        for opcode, name in enumerate(OPCODE_NAMES):
            if name is None:
                continue
            if name in ['BRPOP1', 'BRPOP2', 'JMP']:
                opcode -= len(OPCODE_NAMES)
            OPCODE_MAP[name] = opcode
        label_name_map = {}
        label_map = {}
        
        text_fragments = []
        while True:
            buf = os.read(fp, 1024)
            if buf == '':
                break
            text_fragments.append(buf)
        text = ''.join(text_fragments)

        lines = []
        for row in text.split('\n'):
            main = row.split(';')[0]
            if ':' in main:
                label, main = main.split(':')
                label = label.strip()
                label_name_map[label] = len(lines)
            main = main.strip(' \t')
            if not main:
                continue
            parts = main.split(' ')
            opcode = OPCODE_MAP[parts[0].upper()]
            val = parts[-1]
            if opcode in OP_JUMPS:
                if val in label_map:
                    target = label_map[val]
                else:
                    target = len(lines)
                    label_map[val] = target
                lines.append((opcode, target))
            elif OP_USEVAL[opcode]:
                lines.append((opcode, int(val)))
            else:
                lines.append((opcode, -1))
        self.debug = None
        self.lines = lines
        self.label_map = {}
        for key in label_map.keys():
            self.label_map[label_map[key]] = label_name_map[key]

