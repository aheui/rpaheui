from collections import deque
from aheui._compat import PYR


assert not PYR, 'RPython must use linkedlist'


class Stack(list):
    __slots__ = ()

    def push(self, value):
        self.append(value)

    def dup(self):
        self.append(self[-1])

    def swap(self):
        self[-1], self[-2] = self[-2], self[-1]

    def add(self):
        top = self.pop()
        self[-1] += top

    def sub(self):
        top = self.pop()
        self[-1] -= top

    def mul(self):
        top = self.pop()
        self[-1] *= top

    def div(self):
        top = self.pop()
        self[-1] /= top

    def mod(self):
        top = self.pop()
        self[-1] %= top

    def cmp(self):
        top = self.pop()
        self[-1] = self[-1] >= top


class Queue(deque):
    __slots__ = ()
    
    def push(self, value):
        self.appendleft(value)

    def dup(self):
        self.appendleft(self[0])

    def swap(self):
        self[-1], self[-2] = self[-2], self[-1]

    def add(self):
        top = self.pop()
        self.appendleft(self.pop() + top)

    def sub(self):
        top = self.pop()
        self.appendleft(self.pop() - top)

    def mul(self):
        top = self.pop()
        self.appendleft(self.pop() * top)

    def div(self):
        top = self.pop()
        self.appendleft(self.pop() / top)

    def mod(self):
        top = self.pop()
        self.appendleft(self.pop() % top)

    def cmp(self):
        top = self.pop()
        self.appendleft(self.pop() >= top)


Port = Stack
