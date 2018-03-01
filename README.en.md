RpAheui - Industrial-strength implementaiton of Aheui written in RPython
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

Options
----
- First parameter after removing any options is filename. If the filename is `-`, it is standard input.
- --help,-h: Show help
- --version,-v: Show version
- --opt,-O: Optimization level. Default is `1`. Any integer in `0`-`2` are available.
  - 0: No optimization.
  - 1: Quickly resolve deadcode by rough stacksize emulation and merge constant operations.
  - 2: Perfectly resolve deadcode by stacksize emulation, reserialize code chunks and merge constant operations.
  - usage: `--opt=0`, `-O1` or `-O 2`
- --source,-S: Source type. Default is `auto`. One of `auto`, `bytecode`, `asm`, `text` available.
  - `auto`: Guess the source type. `bytecode` if `.aheuic` or `End of bytecode` pattern in source. `asm` is `.aheuis`. `text` if `.aheui`. `text` is default.
  - `bytecode`: Aheui bytecode. (Bytecode representation of `ahsembly`.
  - `asm`: See `ahsembly`.
  - usage: `--source=asm`, `-Sbytecode` or `-S text`
- --target,-S: Target type. Default is `run`. One of `run`, `bytecode`, `asm` availble.
  - `run`: Run given code.
  - `bytecode`: Aheui bytecode. (Bytecode representation of `ahsembly`.
  - `asm`: See `ahsembly`.
  - usage: `--target=asm`, `-Tbytecode` or `-T run`
- --output,-o: Output file. Default is ``. See details for each target. If the value is `-`, it is standard output.
  - `run` target: This option is not availble and ignored.
  - `bytecode` target: Default value is `.aheuic`
  - `asm` target: Default value is `.aheuis`
  - `asm+comment` target: Same as `asm` with comments.
- --cmd,-c: Program passed in as string
- --no-c: Do not generate `.aheuic` file automatically.
  - Why `.aheuic` is useful: [https://github.com/aheui/snippets/commit/cbb5a12e7cd2db771538ab28dfbc9ad1ada86f35](https://github.com/aheui/snippets/commit/cbb5a12e7cd2db771538ab28dfbc9ad1ada86f35)

ahsembly, ahsembler
----
Note: `ahsembler` is now equivalent to `./aheui-c --source=asm --output=-

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
python ahsembler.py <your-aheui-code>
```

 [rpython]: http://rpython.readthedocs.org