
import os
import serializer

def run(fp):
    program_contents = ''
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    assembler = serializer.Serializer()
    assembler.compile(program_contents)
    assembler.export()
    return 0

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print 'filename'
        return 1
    fp = os.open(filename, os.O_RDONLY, 0777)
    exitcode = run(fp)
    return exitcode

def target(*args):
    return entry_point, None

if __name__ == '__main__':
    import sys
    entry_point(sys.argv)

