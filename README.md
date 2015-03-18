aheui rpython implementation
====

* What is rpython?: [http://rpython.readthedocs.org][rpython]

```
git clone https://github.com/aheui/rpaheui
make # set RPYTHON in Makefile. You can get pypy by: hg clone http://bitbucket.org/pypy/pypy
./aheui-c <your-aheui-code>
```

ahsembler
----
Aheui assembler: Compile aheui code to linear ahsembly.
Debug your aheui code LINEARLY!

Primitives

- halt: ㅎ
- add: ㄷ
- mul: ㄸ
- sub: ㅌ
- div: ㄴ
- mod: ㄹ
- pop: ㅁ without ㅇ/ㅎ
- popnum: ㅁ with ㅇ
- popchar: ㅁ with ㅎ
- push $v: ㅂ without ㅇ/ㅎ. Push THE VALUE $v. $v is not an index of consonants.
- pushnum: ㅂ with ㅇ
- pushchar: ㅂ with ㅎ
- dup: ㅃ
- swap: ㅍ
- sel: ㅅ
- mov: ㅆ
- cmp: ㅈ
- brz $v: ㅊ. If a popped value is zero, program counter is set to $v; otherwise +1.

Extensions (because linear codes loses a little informations)

- brpop2 $v: If current stack doesn't have 2 values to pop, program counter is set to $v; otherwise +1.
- brpop1 $v: If current stack doesn't have 1 values to pop, program counter is set to $v; otherwise +1.
- jmp $v: Program counter is set to $v.

How-to

```
git clone https://github.com/aheui/rpaheui
make ahsembler
./ahsembler-c <your-aheui-code>
```

 [rpython]: http://rpython.readthedocs.org