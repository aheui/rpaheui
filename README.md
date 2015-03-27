RpAheui - Aheui rpython implementation
====

* What is rpython?: [http://rpython.readthedocs.org][rpython]

```
git clone https://github.com/aheui/rpaheui
make # set RPYTHON in Makefile. You can get pypy by: hg clone http://bitbucket.org/pypy/pypy
./aheui-c <your-aheui-code>
```

How to pronounce
----
- / a _r_ p a h i /
- R-pa-hee
- 알파희 (Because it is written in rpython or 알파희썬)

JIT speedup
----
PyPy technology advanced PyPy faster than CPython. (See [http://speed.pypy.org/](http://speed.pypy.org/))

It also boosts RpAheui too. RpAheui is 20x faster than caheui!

```
$ time AHEUI=../rpaheui/aheui-c ./test.sh logo/
testset: logo/
  test logo...success!
test status: 1/1

real	0m1.795s
user	0m1.087s
sys	0m1.262s
```

```
$ time AHEUI=../caheui/aheui ./test.sh logo/
testset: logo/
  test logo...success!
test status: 1/1

real	0m23.953s
user	0m23.843s
sys	0m0.058s
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
- sel $v: ㅅ. $v is always an integer order of final consonants.
- mov $v: ㅆ. $v is always an integer order of final consonants.
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