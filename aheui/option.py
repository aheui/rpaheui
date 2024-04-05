# flake8: noqa: E501

from __future__ import absolute_import

import os
from aheui._argparse import ArgumentParser
from aheui._compat import bigint, PY3
from aheui.version import VERSION
from aheui import compile


parser = ArgumentParser(prog='aheui')
parser.add_argument('--opt', '-O', default='1', choices='0,1,2', description='Set optimization level.', full_description="""\t0: No optimization.
\t1: Quickly resolve deadcode by rough stacksize emulation and merge constant operations.
\t2: Perfectly resolve deadcode by stacksize emulation, reserialize code chunks and merge constant operations.
""")
parser.add_argument('--source', '-S', default='auto', choices='auto,bytecode,asm,text', description='Set source filetype.', full_description="""\t- `auto`: Guess the source type. `bytecode` if `.aheuic` or `End of bytecode` pattern in source. `asm` is `.aheuis`. `text` if `.aheui`. `text` is default.
\t- `bytecode`: Aheui bytecode. (Bytecode representation of `ahsembly`.
\t- `asm`: See `ahsembly`.
\t- `asm+comment`: Same as `asm` with comments.
\t- usage: `--source=asm`, `-Sbytecode` or `-S text`
""")
parser.add_argument('--target', '-T', default='run', choices='run,bytecode,asm,asm+comment', description='Set target filetype.', full_description="""\t- `run`: Run given code.
\t- `bytecode`: Aheui bytecode. (Bytecode representation of `ahsembly`.
\t- `asm`: See `ahsembly`.
\t- usage: `--target=asm`, `-Tbytecode` or `-T run`
""")
parser.add_argument('--output', '-o', default='', description='Output file. Default is ``. See details for each target. If the value is `-`, it is standard output.', full_description="""\t- `run` target: This option is not availble and ignored.
\t- `bytecode` target: Default value is `.aheuic`
\t- `asm` target: Default value is `.aheuis`
""")
parser.add_argument('--cmd', '-c', default='', description='Program passed in as string')
parser.add_argument('--no-c', '--no-c', narg='0', default='no', description='Do not generate `.aheuic` file automatically.', full_description='\tWhat is .aheuic? https://github.com/aheui/snippets/commit/cbb5a12e7cd2db771538ab28dfbc9ad1ada86f35\n')
parser.add_argument('--warning-limit', '--warning-limit', default='', description='Set repetitive warning limit. '' fallbacks to environment variable `RPAHEUI_WARNING_LIMIT`. 0 means no warning. -1 means no limit. Default is 3.')
parser.add_argument('--trace-limit', '--trace-limit', default='', description='Set JIT trace limit. '' fallbacks to environment variable `RPAHEUI_TRACE_LIMIT`.')
parser.add_argument('--version', '-v', narg='-1', default='no', description='Show program version', message=('%s %s' % (VERSION, bigint.NAME)).encode('utf-8'))
parser.add_argument('--help', '-h', narg='-1', default='no', description='Show this help text')


def kwarg_or_environ(kwargs, environ, arg_key, env_key):
    if arg_key in kwargs and kwargs[arg_key] != '':
        return (1, kwargs[arg_key])
    try:
        return (2, environ[env_key])
    except KeyError:
        return (0, '')


def kwarg_or_environ_int(kwargs, environ, arg_key, env_key, default):
    source, arg = kwarg_or_environ(kwargs, environ, arg_key, env_key)
    if source == 0:
        return default
    try:
        value = int(arg)
    except ValueError:
        if source == 1:
            msg = b'The value of --%s="%s" is not a valid integer\n' % (arg_key, arg)
        elif source == 2:
            msg = b'The value %s="%s" is not a valid integer\n' % (env_key, arg)
        else:
            assert False
        os.write(2, msg)
        raise
    return value


def process_options(argv, environ):
    def open_r(filename):
        return os.open(filename, os.O_RDONLY, 0o777)

    kwargs, args = parser.parse_args(argv)
    if not args:
        raise SystemExit()

    cmd = kwargs['cmd']
    if cmd == '':
        if len(args) != 2:
            os.write(2, b'aheui: error: no input files\n')
            raise SystemExit()
        filename = args[1]
        if filename == '-':
            fp = 0
            contents = compile.read(fp)
        else:
            fp = open_r(filename)
            contents = compile.read(fp)
            os.close(fp)
    else:
        if len(args) != 1:
            os.write(2, b'aheui: error: --cmd,-c but input file found\n')
            raise SystemExit()
        if PY3:
            cmd = cmd.encode('utf-8')
        contents = cmd
        filename = '-'

    source = kwargs['source']
    if source == 'auto':
        if filename.endswith('.aheui'):
            source = 'text'
        elif filename.endswith('.aheuic'):
            source = 'bytecode'
        elif filename.endswith('.aheuis'):
            source = 'asm'
        elif b'\xff\xff\xff\xff' in contents:
            source = 'bytecode'
        else:
            source = 'text'

    opt_level = kwargs['opt']

    target = kwargs['target']
    need_aheuic = target == 'run' and kwargs['no-c'] == 'no'\
        and filename != '-' and not filename.endswith('.aheuic')

    if need_aheuic:
        aheuic_output = filename
        if aheuic_output.endswith('.aheui'):
            aheuic_output += 'c'
        else:
            aheuic_output += '.aheuic'
    else:
        aheuic_output = None

    output = kwargs['output']
    comment_aheuis = False
    if output == '':
        if target == 'bytecode':
            output = filename
            if output.endswith('.aheui'):
                output += 'c'
            else:
                output += '.aheuic'
        elif target in ['asm', 'asm+comment']:
            output = filename
            if output != '-':
                if output.endswith('.aheui'):
                    output += 's'
                else:
                    output += '.aheuis'
            comment_aheuis = target == 'asm+comment'
        elif target == 'run':
            output = '-'
        else:
            os.write(2, b'aheui: error: --target,-t must be one of "bytecode", "asm", "asm+comment", "run"\n')  # noqa: E501
            raise SystemExit()

    warning_limit = kwarg_or_environ_int(kwargs, environ, 'warning-limit', 'RPAHEUI_WARNING_LIMIT', 3)
    trace_limit = kwarg_or_environ_int(kwargs, environ, 'trace-limit', 'RPAHEUI_TRACE_LIMIT', -1)

    return cmd, source, contents, opt_level, target, aheuic_output, comment_aheuis, output, warning_limit, trace_limit
