# coding: utf-8
# flake8: noqa: E501

OP_REQSIZE = [0, 0, 2, 2, 2, 2, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 2, 2, 0, 1, 1, 0, 0, 2, 1, 0]
OP_STACKDEL = [0, 0, 2, 2, 2, 2, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 2, 2, 0, 1, 1, 0, 0, 0, 0, 0]
OP_STACKADD = [0, 0, 1, 1, 1, 1, 0, 1, 2, 0, 0, 0, 1, 0, 0, 0, 1, 2, 0, 0, 0, 1, 1, 0, 0, 0]
#              ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ ln lc pn pc b2 b1 j
VAL_QUEUE = 21
VAL_PORT = 27
STORAGE_COUNT = 28

# ㄱ
# ㄲ
OP_DIV = 2  # ㄴ
OP_ADD = 3  # ㄷ
OP_MUL = 4  # ㄸ
OP_MOD = 5  # ㄹ
OP_POP = 6  # ㅁ
OP_PUSH = 7  # ㅂ
OP_DUP = 8  # ㅃ
OP_SEL = 9  # ㅅ
OP_MOV = 10  # ㅆ
OP_NONE = 11  # ㅇ
OP_CMP = 12  # ㅈ
# ㅉ
OP_BRZ = 14
# ㅋ
OP_SUB = 16  # ㅌ
OP_SWAP = 17  # ㅍ
OP_HALT = 18  # ㅎ

# end of primitive
OP_POPNUM = 19
OP_POPCHAR = 20
OP_PUSHNUM = 21
OP_PUSHCHAR = 22
OP_BRPOP2 = -3  # special
OP_BRPOP1 = -2  # special
OP_JMP = -1  # special

OP_BRANCHES = [OP_BRZ, OP_BRPOP1, OP_BRPOP2]
OP_JUMPS = OP_BRANCHES + [OP_JMP]
OP_BINARYOPS = [OP_DIV, OP_ADD, OP_MUL, OP_MOD, OP_CMP, OP_SUB]
