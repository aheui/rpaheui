PyPy/RPython tutorial - Aheui JIT interpreter with pypy/rpython
====

This is a PyPy tutorial to write a JIT interpreter.

- What is Aheui? Esolang, using Hangul. See [http://aheui.github.io/specification.en/][spec]
- What is rpython? Restricted Python, for/by PyPy technology. See [Wikipedia][pypywp] or [Documentation][pypydoc]

Documentations
----
There is not much documentations for beginners.

I started with [PyPy tutorial][pypytutorial]. There also are [example-interpreter][exam1] and [example-interpreter2][exam2].

Toolchains
----

You can find rpython toolchain in [PyPy][pypy].

```
hg clone https://bitbucket.org/pypy/pypy/
```

The tutorial is outdated. `rpython` is in ```<pypy-path>/rpython/bin/rpython```.

rpython
----

First version: [tag:0.1-pure-rpython][0.1]

There is a few restriction for rpython. It is not correct description, but treating it basically as a C code with different syntax helped me. If it is not static, annotator will complain about it.

You easily can satisfy next rules if you don't forget it is statically compiled finally.

- Each variable should have same type.
- Function or class is not a first-class object.
- Containers can contain only 1 type of values.
- None(null) is available, but not with primitive types.

Other useful rules are here:

- Global variables are immutable.
- Local variables are mutable.
- You can't inherit built-in stuffs.

See details in [documentation][rpythondoc].

I coded things with normal python first and fixed it to rpython later, because normal python is easier to debug and faster than rpython.

But to build things with rpython, don't forget next things:

- [target](https://github.com/aheui/rpaheui/blob/0.1-pure-rpython/aheui.py#L497): `target` set `entry_point` for your interpreter. See tutorial for details.
- Add `if __name__ == '__main__':` for python running.

I struggled with these things:

- I used byte strings and unicode strings mixed way. Don't do it. I couldn't fully avoid it because it was Aheui.
- I didn't know how to annotate a string is not zero sized. I found I can use str[0] instead of str if I think it is 1-byte string.
- `sys.stdin` or `sys.stdout` is not available. Use `os.read` and `os.write`. Tutorial is outdated for this. First argument is the file pointer. 0 is stdin, 1 is stdout and 2 is stderr.

My basic strategy was serialization. Most of codes in normal language is serial. Normal language uses byte codes. I didn't doubt it means bytecodes make things easier than 2-dimension codespace in Aheui. This is interesting issue for me, but let's skip it here because it is not that important than JIT, yet.

JIT - JitDriver
----

Second version: [0.2][0.2].

You should add `JitDriver` to add JIT.

- [JitDriver](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L36)
- [jitpolicy](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L377)

```
from rpython.rlib.jit import JitDriver
driver = JitDriver(greens=['pc', 'program'], reds=['storage'])

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

```

You can copy and paste things but see the `greens` and `reds` fields in `JitDriver`. `greens` are used to decide if it is the same point of running or not. `reds` are result of manipulations. See [jit_merge_point](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L246).

```
def mainloop():
    # initialization codes
    while <cond>:
        driver.jit_merge_point(pc=pc, program=program, storage=storage)
        <actual codes>
```

`jit_merge_point` must be on top of the loop. `greens` and `reds` must be known there. EVERY variable above `jit_merge_point` should be one of `greens` or `reds`. Otherwise you will meet `forcelink` blah blah errors. The JIT driver automatically starts to drive JIT from here.

You should set `greens` and `reds` carefully. If you put an unrelated variable to `greens`, the driver will not find loop correctly. If you put too little variable not enough to decide how it runs, the driver cannot decide correct optimized path and cache will be missed.

First version of JIT made [logo.aheui][logo.aheui] 6x slower.

JIT - decorators for hints
----

Second version: [0.2][0.2].

There is a few decorators to hint the driver.

- `elidable`: The execution is elidable - if the input is same, the output also is same. It is `purefunction` in tutorial, but `purefunction` is deprecated.
- `unroll_safe`: Unroll the function when optimizing. Use this decorator if you want to unroll a function when optimizing.
- `dont_look_inside`: This is opposite of `unroll_safe`. Use this decorator if you don't want to optimize inside of the function.

So, `elidable` is the most powerful method. The result will be captured and cached. `unroll_safe` will be next if it is well defined by `greens` status. `dont_look_inside` if it is not very helpful to be optimized by `greens` status.

I used `elidable` to derive `op` from `pc` and `program` because it never will be changed. `unroll_safe` for methods in `Stack` and `Queue` because I captured all the status to decide it. `pc` and `program` decide `op`. `stackok` decides it branches or not. `is_queue` decides which class will be used for data. See [@elidable](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L220)

There is `@unroll_safe` in the tag, but I am not using it anymore.

JIT - assert_green
----

Second version: [0.2][0.2].

Greens also can be derived from other greens. I didn't set `op` as green but it must be green because it is derived by `pc` and `program`. I checked `op` with `assert_green` and it raises error. I added an elidable function to bring op from `pc` and `program`. See [assert_green](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L248).

```
op = program[pc][0]  # assert_green failed

@elidable
def get_op(program, pc):
    return program[pc][0]
op = get_op(program, pc)  # assert_green passed
```

JIT - logging
----

Second version: [0.2][0.2].

The [tutorial][pypytutorial] is great for this. After getting help from `#pypy` I changed the logging option like this:

```
PYPYLOG=jit-log-opt,jit-summary:<filename>
```

- jit-log-opt shows optimized codes, usually jit-log-opt-loop.
- jit-summary shows the result of optimization. It was important for me because I didn't know why tracing failed without this.

In the tutorial, only `jit-log-opt` is suggested. You will be confused if there is no optimized loop in that case. Don't miss `jit-summary` to understand what's happened when there is no optimized loop.

See [get_location](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L27) and driver.

JIT - can_enter_jit
----
Second version: [0.2][0.2].

Without `can_enter_jit`, the JIT driver regards `jit_merge_point` is enterable point. I could hint loop with `can_enter_jit`, and it helped a lot to reduce tracing cost for my case. Example code is rough and simplified one.

```
def mainloop(program, debug):
    pc = 0
    storage = init_storage()
    while pc < program.size:
        driver.jit_merge_point(pc=pc, proram=program)  # merge point here
        op, operand = program[pc]
        if needs_jump(op, operand, storage):
            driver.can_enter_jit(pc=pc, program=program)  # same arguments
            pc = operand
        else:
            # other operations
        pc += 1
```

See [example interpreter][exam1] for example.
See [rpaheui example](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L286) too.

`can_enter_jit` made [logo.aheui][logo.aheui] back to 1x speed. JIT still failed, but at least tracing didn't made it 6x slower.

JIT - immutable fields
----
Third version: [0.2][0.2].

You can add immutable fields for classes.
I changed program from raw list to a class and moved `elidable` functions to access its data.

See [Program](https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py#L213).

JIT - virtualizables
----
See [example interpreter][exam1] for this feature. I don't understand this thing not very well.

JIT - Too long to trace
----
Third version: [0.3][0.3].

I still had a problem. The common benchmark [logo.aheui][logo.aheui] still fail to trace codes. In `jit-summary`, it said the code is too long to trace.

There was `rpython.rlib.jit.set_param` and `trace_limit` parameter. I got a advice to change it from 6000 to 100000, because a loop already included 4000 IR for the loop. See [set_param](https://github.com/aheui/rpaheui/blob/0.3-world-fastest-aheui/aheui.py#L233). (Note: set_param should be in runtime context)

After that, JIT is working now. The loop is 40k ops. The speed is 6x times slower again. But at this time, it succeed to optimize the loop.

I've got a new advice to replace stacks and queue to linked list to reduce operations. I still don't know how it related - but don't use list if it is not static! It made 40k ops of optimized loop to 21k ops now.

The speed is doubled now so 3x slower than no JIT.

Optimized loop looked efficient enough... Than what is the problem? Because Aheui depends on trivial experssions to make constants. I added pre-optimization phases to help JIT driver to spend less effort to optimize things. and...

Done :D

It is 20x faster with JIT now.

BigInt
----
First rpython feature after release: [1.2.0][1.2.0].

I found it does not support bigint like pure python version. `rpython.rlib.rbigint` is a bigint library.
I replaced all of the data type to rbigint. And found it makes code 6-8 times slower.
Unfortunately aheui is so simple language - it looks hard to optimize it more for bigint.
Instead of it, I added an abstract layer of bigint. It runs under normal int system basically.
But there is bigint module and you can replace it to enable bigint support.

Unfortunately, I did not find a way to print bigint object yet. It is calculatable but not printable


So...
----
Now I have the world fastest Aheui implementation. This is 20 times faster than C implementation and 2~3 times faster than C transpile implementation for [logo.aheui][logo.aheui].

Most of trial I did here is adviced by `@fijal`(Maciej Fijalkowski) and `@arigo`(Armin Rigo). I struggled with a lot of things with wrong approach and maybe I never reached to this point without their help.

Now I understand how to create simple interpreter/vm with JIT with PyPy technology. It will be the most preferred way to write an interpreter for me. I am still interested in how to enhance it more - but yep, it is still hard to know what can I do and how each tool works. I never learned what is dont_look_inside from any documentation and will not do about most of other features, unfortunately. But there must be more things, PyPy is complicated enough and it must have hidden more things than these. :p


[spec]: http://aheui.github.io/specification.en/
[pypy]: http://pypy.org/
[pypywp]: https://en.wikipedia.org/wiki/PyPy#RPython
[pypydoc]: http://rpython.readthedocs.org
[pypytutorial]: http://morepypy.blogspot.kr/2011/04/tutorial-writing-interpreter-with-pypy.html
[rpythondoc]: http://rpython.readthedocs.org/en/latest/rpython.html
[exam1]: https://bitbucket.org/pypy/example-interpreter/
[exam2]: https://bitbucket.org/fijal/example-interpreter2/
[0.1]: https://github.com/aheui/rpaheui/blob/0.1-pure-rpython/aheui.py
[0.2]: https://github.com/aheui/rpaheui/blob/0.2-first-jit/aheui.py
[0.3]: https://github.com/aheui/rpaheui/blob/0.3-world-fastest-aheui/aheui.py
[1.2.0]: https://github.com/aheui/rpaheui/tree/1.2.0
[logo.aheui]: https://github.com/aheui/snippets/blob/master/logo/logo.aheui