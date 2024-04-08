from aheui._compat import bigint


class Node(object):
    """Element unit for stack and queue."""

    __slots__ = ('value', 'next')

    def __init__(self, next, value=bigint.MINUS1):
        self.value = value
        self.next = next


class LinkedList(object):
    """Common linked list for storages"""

    __slots__ = ('head', 'size')

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

    __slots__ = ('head', 'size')

    def __init__(self):
        self.head = None
        self.size = 0

    def push(self, value):
        # assert(isinstance(value, bigint.Int))
        node = Node(self.head, value)
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

    __slots__ = ('head', 'tail', 'size')

    def __init__(self):
        self.tail = Node(None)
        self.head = self.tail
        self.size = 0

    def push(self, value):
        # assert(isinstance(value, bigint.Int))
        tail = self.tail
        tail.value = value
        new = Node(None)
        tail.next = new
        self.tail = new
        self.size += 1

    def dup(self):
        head = self.head
        node = Node(head, head.value)
        self.head = node
        self.size += 1

    def _get_2_values(self):
        return self.pop(), self.pop()

    def _put_value(self, value):
        self.push(value)


class Port(LinkedList):

    __slots__ = ('head', 'size', 'last_push')

    def __init__(self):
        self.head = None
        self.size = 0
        self.last_push = bigint.fromint(0)

    def push(self, value):
        # assert(isinstance(value, bigint.Int))
        node = Node(self.head, value)
        self.head = node
        self.size += 1
        self.last_push = value

    def dup(self):
        self.push(self.last_push)

    def _get_2_values(self):
        return self.pop(), self.head.value

    def _put_value(self, value):
        self.head.value = value
