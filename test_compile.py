
#coding: utf-8
import compile

def test_compiler():
    compiler = compile.Compiler()
    compiler.compile(u'반맣희')
    code1 = compiler.lines[:]
    asm = compiler.write_asm()
    compiler.read_asm(asm)
    code2 = compiler.lines[:]
    bytecode = compiler.write_bytecode()
    compiler.read_bytecode(bytecode)
    code3 = compiler.lines[:]
    assert list(map(lambda t: t[0], code1)) == list(map(lambda t: t[0], code2))
    assert list(map(lambda t: t[0], code1)) == list(map(lambda t: t[0], code3))