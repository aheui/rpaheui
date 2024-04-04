# flake8: noqa: E501

from __future__ import absolute_import


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
        except HelpException:
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
