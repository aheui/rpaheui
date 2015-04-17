#!/usr/bin/env python
# coding: utf-8

try:
    import settings
    DEBUG = settings.DEBUG
except ImportError:
    DEBUG = False

import os
try:
    from aheui.const import *
except ImportError:
    from const import *
try:
    from rpython.rlib.listsort import TimSort
except ImportError:
    class TimSort(object):
        def __init__(self, list):
            self.list = list

        def sort(self):
            self.list.sort()


OP_NAMES = [None, None, u'DIV', u'ADD', u'MUL', u'MOD', u'POP', u'PUSH', u'DUP', u'SEL', u'MOV', None, u'CMP', None, u'BRZ', None, u'SUB', u'SWAP', u'HALT', u'POPNUM', u'POPCHAR', u'PUSHNUM', u'PUSHCHAR', u'BRPOP2', u'BRPOP1', u'JMP']

OP_HASOP = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
OP_USEVAL = [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
VAL_CONSTS = [0, 2, 4, 4, 2, 5, 5, 3, 5, 7, 9, 9, 7, 9, 9, 8, 4, 4, 6, 2, 4, 1, 3, 4, 3, 4, 4, 3]
#             () ㄱ ㄲ ㄳ ㄴ ㄵ ㄶ ㄷ ㄹ ㄺ ㄻ ㄼ ㄽ ㄾ ㄿ ㅀ ㅁ ㅂ ㅄ ㅅ ㅆ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ

VAL_NUMBER = 21
VAL_UNICODE = 27


MV_RIGHT = 0  # ㅏ
# ㅐ
MV_RIGHT2 = 2  # ㅑ
# ㅒ
MV_LEFT = 4  # ㅓ
# ㅔ
MV_LEFT2 = 6  # ㅕ
# ㅖ
MV_UP = 8  # ㅗ
# ㅘ
# ㅙ
# ㅚ
MV_UP2 = 12  # ㅛ
MV_DOWN = 13  # ㅜ
# ㅝ
# ㅞ
# ㅟ
MV_DOWN2 = 17  # ㅠ
MV_HWALL = 18  # ㅡ
MV_WALL = 19  # ㅢ
MV_VWALL = 20  # ㅣ

MV_DETERMINISTICS = [MV_DOWN, MV_DOWN2, MV_UP, MV_UP2, MV_LEFT, MV_LEFT2, MV_RIGHT, MV_RIGHT2]

DIR_NAMES = [None, u'DOWN', u'RIGHT', u'LJMP', u'UJMP', None, u'DJMP', u'RJMP', u'LBR', u'UBR', None, u'DBR', u'RBR', u'LEFT', u'UP']

DIR_DOWN = 1
DIR_RIGHT = 2
DIR_UP = -1
DIR_LEFT = -2


def padding(s, l, left=True):
    spaces = u' ' * max(0, l - len(s))
    padded = (s + spaces) if left else (spaces + s)
    return padded


def read(fp=0):
    text_fragments = []
    while True:
        buf = os.read(fp, 1024)
        if len(buf) == 0:
            break
        text_fragments.append(buf)
    text = b''.join(text_fragments)
    return text


class Debug(object):
    ENABLED = DEBUG

    def __init__(self, lines, comments=None):
        self.lines = lines
        self.comments = comments

    def build_comments(self, primitive, code_map):
        self.comments = []
        for i in range(0, len(self.lines)):
            self.comments.append([])
        for (pos, dir, step), i in code_map.items():
            if dir >= 3:
                continue
            self.comments[i].append(primitive.pane[pos])
            srow = padding(u'%d' % pos[0], 3, left=False)
            scol = padding(u'%d' % pos[1], 3, left=False)
            sdir = padding(DIR_NAMES[dir], 5)
            self.comments[i].append(u'[%s,%s] %s%s' % (srow, scol, sdir, step))

    def comment(self, i):
        return u' / '.join(self.comments[i])

    def show(self, pc, fp=2):
        op, value = self.lines[pc]
        os.write(fp, (u'L%d %s(%s) %s ;' % (pc, OP_NAMES[op], unichr(0x1100 + op), value if OP_USEVAL[op] else '')).encode('utf-8'))
        os.write(fp, self.comment(pc))
        os.write(fp, '\n')

    def storage(self, storage, selected=None):
        def _list(list):
            items = []
            node = list.head
            while node:
                items.append(str(node.value))
                node = node.next
            return '[' + ', '.join(items) + ']'
        for i, l in enumerate(storage):
            marker = u':' if l == selected else u' '
            os.write(2, (u'%s (%d):%s' % (unichr(0x11a8 + i - 1), i, marker)).encode('utf-8'))
            os.write(2, ('%s\n' % _list(l)))


class PrimitiveProgram(object):
    def __init__(self, text):
        self.text = text
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
        op_code = base // 588
        mv_code = (base // 28) % 21
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
        elif d == DIR_RIGHT:
            c += step
            if c > self.max_col:
                c = 0
            p = r, c
        elif d == DIR_UP:
            r -= step
            if r < 0:
                r = self.max_row
            p = r, c
        elif d == DIR_LEFT:
            c -= step
            if c < 0:
                c = self.max_col
            p = r, c
        else:
            assert False
        #  print 'move:', position, '->', p, DIR_NAMES[direction], step
        return p


def dir_from_mv(mv_code, direction, step):
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
        return -direction, step
    elif mv_code == MV_HWALL:
        if direction in [DIR_UP, DIR_DOWN]:
            return -direction, step
        else:
            return direction, step
    elif mv_code == MV_VWALL:
        if direction in [DIR_RIGHT, DIR_LEFT]:
            return -direction, step
        else:
            return direction, step
    else:
        return direction, step


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
        self.debug = Debug(self.lines)
        self.debug.build_comments(primitive, code_map)

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
        job_queue = [((0, 0), DIR_DOWN, 1, -1)]

        lines = []
        label_map = {}
        code_map = {}

        def add(lines, op, operand, debug='unknown'):
            idx = len(lines)
            lines.append((op, operand))
            #  print idx, OP_NAMES[op], operand, debug
            return idx

        while job_queue:
            position, direction, step, marker = job_queue.pop(0)
            #  print 'dequeue:', position, DIR_NAMES[direction], step, marker
            if marker >= 0:
                label_map[marker] = len(lines)
            while True:
                if position not in primitive.pane:
                    position = primitive.advance_position(position, direction)
                    continue

                op, mv, val = primitive.decode(position)
                new_direction, new_step = dir_from_mv(mv, direction, step)
                if mv in MV_DETERMINISTICS:
                    direction = new_direction
                    step = new_step
                if (position, direction, step) in code_map:
                    index = code_map[position, direction, step]
                    posdir = position, direction + 10, step
                    code_map[position, direction + 5, step] = len(lines)
                    if posdir in code_map:
                        target = code_map[posdir]
                    else:
                        target = index
                    label_id = len(lines)
                    label_map[label_id] = target
                    add(lines, OP_JMP, label_id, 'jump label for %s %s' % (position, direction))
                    break

                code_map[position, direction, step] = len(lines)

                direction = new_direction
                step = new_step
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
                        add(lines, op, VAL_CONSTS[val])
                    else:
                        req_size = OP_REQSIZE[op]
                        if req_size > 0:
                            brop = OP_BRPOP1 if req_size == 1 else OP_BRPOP2
                            idx = len(lines)
                            code_map[position, direction + 10, step] = idx  # mark branch
                            add(lines, brop, idx, 'brpop')
                            code_map[position, direction, step] = idx + 1  # mark code
                            if OP_USEVAL[op]:
                                if op == OP_BRZ:
                                    add(lines, op, idx, 'brpop-brz')
                                    alt_position = primitive.advance_position(position, -direction, step)
                                    #  print 'enqueue:', alt_position, DIR_NAMES[-direction], step, idx
                                    job_queue.append((alt_position, -direction, step, idx))
                                else:
                                    add(lines, op, val, 'brpop-useval')
                            else:
                                add(lines, op, -1, 'brpop-noval')

                            alt_position = primitive.advance_position(position, -direction, step)
                            #  print 'enqueue:', alt_position, DIR_NAMES[-direction], step, idx
                            job_queue.append((alt_position, -direction, step, idx))
                        else:
                            if OP_USEVAL[op]:
                                add(lines, op, val, 'safe-useval')
                            else:
                                add(lines, op, -1, 'safe-noval')
                                if op == OP_HALT:
                                    break
                position = primitive.advance_position(position, direction, step)
        return lines, label_map, code_map

    def optimize1(self):
        self.optimize_jump()
        reachability = self.optimize_deadcode1()
        self.optimize_adjust(reachability)

        reachability = self.optimize_operation(True)
        self.optimize_jump()
        self.optimize_adjust(reachability)

    def optimize2(self):
        """Optimize generated codes.

        Do not decouple each steps or change the order. It is important.
        """
        self.optimize_jump()
        reachability = self.optimize_deadcode2()
        self.optimize_adjust(reachability)

        self.optimize_order()

        reachability = self.optimize_operation(True)
        self.optimize_jump()
        self.optimize_adjust(reachability)

    def optimize_adjust(self, reachability):
        useless_map = [0] * len(reachability)
        count = 0
        for i, reachable in enumerate(reachability):
            useless_map[i] = count
            if not reachable:
                count += 1

        new = []
        new_comments = []
        new_label_map = {}
        comments_buffer = []
        for i, (op, val) in enumerate(self.lines):
            if not reachability[i]:
                if self.debug:
                    comments_buffer += self.debug.comments[i]
                continue
            new.append((op, val))
            new_comments.append([])
            if op in OP_JUMPS:
                target_idx = self.label_map[val]
                new_target_idx = target_idx - useless_map[target_idx]
                new_label_map[val] = new_target_idx
                #  print 'remap:', target_idx, '->', new_target_idx
            if self.debug:
                comments = []
                for comment in comments_buffer:
                    if u'JMP' in comment:
                        pass
                    comments.append(comment)
                new_comments[-1] += comments + self.debug.comments[i]
                comments_buffer = []

        self.lines = new
        self.label_map = new_label_map
        if self.debug:
            new_debug = Debug(new, new_comments)
            self.debug = new_debug

    def optimize_jump(self):
        for label, direct_target in self.label_map.items():
            op, operand = self.lines[direct_target]
            if op == OP_JMP:
                indirect_target = self.label_map[operand]
                self.label_map[label] = indirect_target

    def optimize_deadcode1(self):
        """Optimize codes by removing unreachable codes.

        Because unreachable path is already removed by `serialize`, this path
        mainly remove useless OP_BRPOPs and its branches.

        1. Trace current stack size from first line.
        2. If there is enough stack, do not trace OP_BRPOPs' jumps.
        3. If optimizer met OP_SEL, assume stacksize is 0 from there.
        4. If optimizer passes same codes,
            1. If assumed stacksize is smaller than before, keep going to trace.
            2. Otherwise it is not worth to do. Stop.
        5. Stop if OP_HALT.
        6. Drop useless OP_BRPOPs and any codes out of path.
        """
        minstacksize_map = [-1] * len(self.lines)
        job_queue = [(0, 0)]

        while len(job_queue) > 0:
            pc, stacksize = job_queue.pop(0)
            while pc < len(self.lines):
                op, val = self.lines[pc]
                minstacksize = minstacksize_map[pc]
                if minstacksize >= 0:
                    if minstacksize <= stacksize - OP_STACKDEL[op] + OP_STACKADD[op]:
                        break
                if op == OP_BRPOP1 or op == OP_BRPOP2:
                    reqsize = OP_REQSIZE[op]
                    if stacksize >= reqsize:
                        pc += 1
                        continue
                    else:
                        minstacksize_map[pc] = stacksize
                        job_queue.append((self.label_map[val], stacksize))
                else:
                    minstacksize_map[pc] = stacksize
                    stacksize -= OP_STACKDEL[op]
                    if stacksize < 0:
                        stacksize = 0
                    stacksize += OP_STACKADD[op]
                    if op == OP_BRZ:
                        job_queue.append((self.label_map[val], stacksize))
                    elif op == OP_JMP:
                        pc = self.label_map[val]
                        continue
                    elif op == OP_SEL:
                        minstacksize_map[pc] = stacksize
                        stacksize = 0
                    elif op == OP_MOV:
                        pass
                    elif op == OP_HALT:
                        break
                pc += 1

        reachability = [int(minstacksize >= 0) for minstacksize in minstacksize_map]
        return reachability

    def optimize_deadcode2(self):
        minstacksize_map = [[-1] * STORAGE_COUNT] * len(self.lines)
        job_queue = [(0, 0, [0] * STORAGE_COUNT)]

        def min_list(l1, l2):
            if l1[0] == -1:
                return l2[:]
            return [min(l1[i], l2[i]) for i in range(0, STORAGE_COUNT)]

        while len(job_queue) > 0:
            pc, selected, stacksizes = job_queue.pop(0)
            while pc < len(self.lines):
                stacksize = stacksizes[selected]
                assert stacksize >= 0
                op, val = self.lines[pc]
                minstacksizes = minstacksize_map[pc]
                if minstacksizes[selected] >= 0:
                    if minstacksizes[selected] <= stacksizes[selected] - OP_STACKDEL[op] + OP_STACKADD[op] and min_list(minstacksizes, stacksizes) == minstacksizes:
                        break
                if op == OP_BRPOP1 or op == OP_BRPOP2:
                    reqsize = OP_REQSIZE[op]
                    if stacksize >= reqsize:
                        pc += 1
                        continue
                    else:
                        minstacksize_map[pc] = min_list(minstacksizes, stacksizes)
                        job_queue.append((self.label_map[val], selected, stacksizes[:]))
                else:
                    minstacksize_map[pc] = min_list(minstacksizes, stacksizes)
                    stacksize -= OP_STACKDEL[op]
                    if stacksize < 0:
                        stacksize = 0
                    stacksize += OP_STACKADD[op]
                    stacksizes[selected] = stacksize
                    if op == OP_BRZ:
                        job_queue.append((self.label_map[val], selected, stacksizes[:]))
                    elif op == OP_JMP:
                        pc = self.label_map[val]
                        continue
                    elif op == OP_SEL:
                        minstacksize_map[pc] = min_list(minstacksizes, stacksizes)
                        selected = val
                    elif op == OP_MOV:
                        stacksizes[val] += 1
                    elif op == OP_HALT:
                        break
                pc += 1

        reachability = [int(minstacksizes[0] >= 0) for minstacksizes in minstacksize_map]
        return reachability

    def optimize_order(self):
        lines = self.lines
        hints = [x for x in range(0, len(lines))]
        c = 0
        while True:
            jump_map = {}
            jump_rmap = {}
            for dep, (op, v) in enumerate(lines):
                if op == OP_JMP:
                    dest = self.label_map[v]
                    jump_map[dep] = dest
                    if dest in jump_rmap:
                        jump_rmap[dest] = -1
                    else:
                        jump_rmap[dest] = dep

            for i in range(1, len(lines)):

                if i not in jump_rmap:
                    continue
                f = jump_rmap[i]
                if f == -1:
                    continue
                if i - 1 not in jump_map:
                    continue
                ix = i
                while ix + 1 < len(lines):
                    ix += 1
                    if ix in jump_map:
                        break
                    if ix in jump_rmap:
                        ix = -1
                        break
                    if lines[ix][0] in OP_BRANCHES:
                        ix = -1
                        break
                else:
                    ix = -1
                if ix < 0:
                    continue
                if ix == f:
                    continue

                assert f > 0  # rpython hint
                if ix < f:
                    """
                    ... JMP(i-1) | XXX(i) ... JMP(ix) | ... | JMP->i(f) | ...
                       b1                  b2           b3        x       b4
                    """
                    size = ix - i + 1
                    diff = f - size
                    for label, dest in self.label_map.items():
                        if i <= dest <= ix:  # b2
                            self.label_map[label] += diff - 1
                        elif ix < dest <= f:  # b3
                            self.label_map[label] -= size
                        elif f < dest:  # b4
                            self.label_map[label] -= 1
                    b1 = lines[:i]
                    b2 = lines[i:ix + 1]
                    b3 = lines[ix + 1:f]
                    b4 = lines[f + 1:]
                    lines = b1 + b3 + b2 + b4
                    hints = hints[:i] + hints[ix + 1:f] + hints[i:ix + 1] + hints[f + 1:]
                else:
                    """
                    ... | JMP->i(f) | ... JMP(i-1) | XXX(i) ... JMP(ix) | ...
                     b1      x            b2                 b3            b4
                    """
                    size = ix - i + 1
                    diff = i - f
                    for label, dest in self.label_map.items():
                        if i <= dest <= ix:  # b3
                            self.label_map[label] -= diff
                        elif f <= dest < i:  # b2
                            self.label_map[label] += size - 1
                        elif ix < dest:  # b4
                            self.label_map[label] -= 1
                    b1 = lines[:f]
                    b2 = lines[f + 1:i]
                    b3 = lines[i:ix + 1]
                    b4 = lines[ix + 1:]
                    lines = b1 + b3 + b2 + b4
                    hints = hints[:f] + hints[i:ix + 1] + hints[f + 1:i] + hints[ix + 1:]
                break
            else:
                break
        labels = []
        for op, v in lines:
            if op in OP_JUMPS:
                labels.append(v)
        for label in self.label_map.keys():
            if label not in labels:
                del self.label_map[label]
        self.lines = lines
        if self.debug:
            new_comments = [self.debug.comments[h] for h in hints]
            self.debug = Debug(lines, new_comments)

    def optimize_operation(self, optimize_dup=False):
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

        if self.debug:
            for pc, queueable in enumerate(queue_map):
                if queueable and u'QUEUE' not in self.debug.comments[pc]:
                    self.debug.comments[pc].append(u'QUEUE')

        label_targets = self.label_map.values()
        label_rmap = {}
        for k, v in self.label_map.items():
            if v in label_rmap:
                label_rmap[v] = -1
            else:
                label_rmap[v] = k

        reachability = [int(queue_map[i] >= 0) for i in range(0, len(lines))]

        if optimize_dup:
            for i in range(1, len(lines)):
                op, val = lines[i]
                i1 = i - 1
                while lines[i1][0] == OP_NONE and i1 >= 0:
                    i1 -= 1
                if queue_map[i] or queue_map[i1]:
                    continue
                if i in label_targets:
                    continue
                if op == OP_DUP:
                    inst1 = lines[i1]
                    if inst1[0] == OP_PUSH:
                        lines[i] = lines[i1]
                    continue

        for i in range(2, len(lines)):
            op, v = lines[i]
            i1 = i - 1

            while lines[i1][0] == OP_NONE and i1 >= 1:
                i1 -= 1
            i2 = i1 - 1
            while lines[i1][0] == OP_NONE and i2 >= 0:
                i2 -= 1
            op1, v1 = lines[i1]
            op2, v2 = lines[i2]
            if not op2 == OP_PUSH:
                continue

            if op1 == OP_PUSH:
                pass
            elif op1 == OP_DUP:
                v1 = v2
            else:
                continue

            #  print '----'
            #  print i, OP_NAMES[op2], OP_NAMES[op1], OP_NAMES[op]
            #  self.debug.show(i2)
            #  self.debug.show(i1)
            #  self.debug.show(i)

            if queue_map[i] or queue_map[i1] or queue_map[i2]:
                #  print 'in queue'
                continue
            if i1 in label_targets or i in label_targets:
                #  print 'has jump label'
                continue
            is_jmp = op == OP_JMP
            if is_jmp:
                target = self.label_map[v]
                #  print v, target, label_rmap[target]
                if label_rmap[target] == v:
                    op, v = lines[target]
            if op not in OP_BINARYOPS:
                #  print 'not binops'
                continue

            if op == OP_ADD:
                v = v2 + v1
            elif op == OP_SUB:
                v = v2 - v1
            elif op == OP_MUL:
                v = v2 * v1
            elif op == OP_DIV:
                v = v2 // v1
            elif op == OP_MOD:
                v = v2 % v1
            elif op == OP_CMP:
                v = int(v2 >= v1)
            else:
                assert False

            #  print 'optimized!'
            if is_jmp:
                lines[i1] = (OP_PUSH, v)
                lines[i2] = (OP_NONE, -1)
                reachability[i2] = 0
                jv = lines[i][1]
                target = self.label_map[jv]
                self.label_map[jv] += 1
                del label_rmap[target]
                if target + 1 in label_rmap:
                    label_rmap[target + 1] = -1
                else:
                    label_rmap[target + 1] = jv
                if self.debug:
                    self.debug.comments[i1] += self.debug.comments[target]
                #  self.debug.show(i1)
                #  self.debug.show(i)
            else:
                lines[i] = (OP_PUSH, v)
                lines[i1] = (OP_NONE, -1)
                lines[i2] = (OP_NONE, -1)
                reachability[i1] = 0
                reachability[i2] = 0
                #  self.debug.show(i)

        return reachability

    def write_bytecode(self):
        """Write bytecodes data text."""
        codes = []
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
            codes.append(p)
        codes.append('\xff\xff\xff\xff')
        return ''.join(codes)

    def read_bytecode(self, text):
        """Read bytecodes from data text."""
        self.debug = None
        self.lines = []
        self.label_map = {}
        idx = 0
        while idx < len(text):
            buf = text[idx:idx + 4]
            assert len(buf) == 4
            if buf == '\xff\xff\xff\xff':
                break
            idx += 4

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
        codes = []
        for i, (op, val) in enumerate(self.lines):
            if i in self.label_map.values():
                label_str = u'L%d:' % i
                codes.append(padding(label_str, 8))
            else:
                codes.append(u' ' * 8)
            code = OP_NAMES[op]
            if len(code.encode('utf-8')) == 3:
                code += u' '
            if code is None:
                code = u'inst%d' % op
            if OP_USEVAL[op]:
                if op in OP_JUMPS:
                    slabel = padding(u'%d' % self.label_map[val], 3)
                    code_val = u'%s L%s' % (code, slabel)
                else:
                    sval = padding(u'%d' % val, 4)
                    code_val = u'%s %s' % (code, sval)
            else:
                code_val = code
            code_val = padding(code_val, 10)
            comment = self.debug.comment(i) if self.debug else u''
            sline = padding(u'%d' % i, 3)
            codes.append(u'%s ; L%s %s\n' % (code_val, sline, comment))
        return u''.join(codes)

    def read_asm(self, text):
        """Read assembly representation."""
        OPCODE_MAP = {}
        for opcode, name in enumerate(OP_NAMES):
            if name is None:
                continue
            if name in [u'BRPOP1', u'BRPOP2', u'JMP']:
                opcode -= len(OP_NAMES)
            OPCODE_MAP[name] = opcode
        label_name_map = {}
        label_map = {}

        lines = []
        comments = []
        for row in text.split(u'\n'):
            if u';' in row:
                main, comment = row.split(u';', 1)
            else:
                main, comment = row, u''
            if u':' in main:
                label, main = main.split(u':')
                label_name_map[label] = len(lines)
                label = label.strip(' \t')
            main = main.strip(' \t')
            if not main:
                continue
            parts = main.split(u' ')
            opname = parts[0].encode('utf-8').upper().decode('utf-8')
            opcode = OPCODE_MAP[opname]
            val = parts[-1]
            try:
                if opcode in OP_JUMPS:
                    if val in label_map:
                        target = label_map[val]
                    else:
                        target = len(lines)
                        label_map[val] = target
                    lines.append((opcode, target))
                elif OP_USEVAL[opcode]:
                    val = int(val)
                    lines.append((opcode, int(val)))
                else:
                    lines.append((opcode, -1))
                comments.append([comment])
            except Exception as e:
                os.write(2, b'parsing error: ln%d %s\n' % (len(lines), main.encode('utf-8')))
                raise
        self.lines = lines
        self.label_map = {}
        for key in label_map.keys():
            self.label_map[label_map[key]] = label_name_map[key]
        self.debug = Debug(lines, comments)
