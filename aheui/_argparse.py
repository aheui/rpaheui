
from __future__ import absolute_import
try:
    from aheui.version import VERSION
except ImportError:
    from version import VERSION


class ParserError(Exception):
    __description__ = ''

    def __init__(self, desc=''):
        self.desc = desc

    def message(self):
        return self.__description__ + self.desc


class TooFewArgumentError(ParserError):
    __description__ = 'too few arguments: '


class TooManyArgumentError(ParserError):
    __description__ = 'too many arguments: '


class ArgumentNotInChoicesError(ParserError):
    __description__ = 'argument is not in choices: '


class InformationException(ParserError):
    __description__ = ''


class HelpException(InformationException):
    __description__ = ''


class ArgumentParser(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.arguments = []

    def add_argument(self, *names, **kwargs):
        if 'dest' not in kwargs:
            name = names[0]
            while name[0] == '-':
                name = name[1:]
            kwargs['dest'] = name
        if 'narg' not in kwargs:
            kwargs['narg'] = '1'
        if 'choices' not in kwargs:
            kwargs['choices'] = ''
        if 'description' not in kwargs:
            kwargs['description'] = ''
        if 'full_description' not in kwargs:
            kwargs['full_description'] = ''
        self.arguments.append((names, kwargs))

    def _parse_args(self, args):
        parsed = {}
        nonparsed = []
        idx = 0
        while idx < len(args):
            arg = args[idx]
            done = False
            for names, opt in self.arguments:
                dest = opt['dest']
                choices = opt['choices']
                for name in list(names):
                    if arg.startswith(name):
                        narg = int(opt['narg'])
                        if narg <= 0:
                            idx += 1
                            parsed[dest] = 'yes'
                            done = True
                            if narg < 0:
                                if opt['dest'] == 'help':
                                    raise HelpException('')
                                else:
                                    raise InformationException(opt['message'])
                        elif name.startswith('--'):
                            if '=' not in arg:
                                raise TooFewArgumentError(name)
                            argname, arg = arg.split('=', 1)
                            if choices:
                                if arg not in choices:
                                    raise ArgumentNotInChoicesError('%s (given: %s / expected: %s)' % (name, arg, choices))
                            parsed[dest] = arg
                            idx += 1
                            done = True
                        elif name.startswith('-'):
                            if name == arg:
                                arg = args[idx + 1]
                                parsed[dest] = arg
                                idx += 2
                            else:
                                parsed[dest] = arg[len(name):]
                                idx += 1
                            done = True
                    if done:
                        break
                if done:
                    break
            if not done:
                nonparsed.append(arg)
                idx += 1
        for names, opt in self.arguments:
            dest = opt['dest']
            if dest not in parsed:
                parsed[dest] = opt['default']
        return parsed, nonparsed

    def parse_args(self, args):
        import os
        try:
            return self._parse_args(args)
        except HelpException as e:
            os.write(2, 'usage: %s [option] ... file\n\n' % self.kwargs.get('prog', args[0]))
            for names, opt in self.arguments:
                name = names[0] if names[0] == names[1] else ('%s,%s' % names[0:2])
                os.write(2, '%s%s: %s' % (name, ' ' * (12 - len(name)), opt['description']))
                if int(opt['narg']) > 0 and opt['default']:
                    os.write(2, ' (default: %s)' % opt['default'])
                if opt['choices']:
                    os.write(2, ' (choices: %s)' % opt['choices'])
                if opt['full_description']:
                    os.write(2, '\n')
                    os.write(2, opt['full_description'])
                os.write(2, '\n')
        except InformationException as e:
            os.write(2, '%s\n' % e.desc)
        except ParserError as e:
            prog = self.kwargs.get('prog', args[0])
            os.write(2, '%s: error: %s\n' % (prog, e.message()))
        return {}, []

parser = ArgumentParser(prog='aheui')
parser.add_argument('--opt', '-O', default='1', choices='0,1,2', description='Set optimization level.', full_description="""\t0: No optimization.
\t1: Quickly resolve deadcode by rough stacksize emulation and merge constant operations.
\t2: Perfectly resolve deadcode by stacksize emulation, reserialize code chunks and merge constant operations.
""")
parser.add_argument('--source', '-S', default='auto', choices='auto,bytecode,asm,text', description='Set source filetype.', full_description="""\t- `auto`: Guess the source type. `bytecode` if `.aheuic` or `End of bytecode` pattern in source. `asm` is `.aheuis`. `text` if `.aheui`. `text` is default.
\t- `bytecode`: Aheui bytecode. (Bytecode representation of `ahsembly`.
\t- `asm`: See `ahsembly`.
\t- usage: `--source=asm`, `-Sbytecode` or `-S text`
""")
parser.add_argument('--target', '-T', default='run', choices='run,bytecode,asm', description='Set target filetype.', full_description="""\t- `run`: Run given code.
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
parser.add_argument('--version', '-v', narg='-1', default='no', description='Show program version', message=VERSION)
parser.add_argument('--help', '-h', narg='-1', default='no', description='Show this help text')
