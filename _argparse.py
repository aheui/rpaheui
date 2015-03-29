
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
                        if opt['narg'] == '0':
                            idx += 1
                            parsed[dest] = 'yes'
                            done = True
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
        try:
            return self._parse_args(args)
        except ParserError, e:
            prog = self.kwargs.get('prog', args[0])
            import os
            os.write(2, '%s: error: %s\n' % (prog, e.message()))
            return {}, []

parser = ArgumentParser(prog='aheui')
parser.add_argument('--opt', '-O', default='1', choices='0,1,2')
parser.add_argument('--source', '-S', default='auto', choices='auto,bytecode,asm,text')
parser.add_argument('--target', '-T', default='run', choices='run,bytecode,asm')
parser.add_argument('--output', '-o', default='')
parser.add_argument('--no-c', '--no-c', narg='0', default='no', choices='yes,no')
