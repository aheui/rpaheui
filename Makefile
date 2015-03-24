
RPYTHON=../pypy/rpython/bin/rpython
RPYTHONFLAGS=--opt=jit
#RPYTHONFLAGS=

all: build
	

build:
	$(RPYTHON) $(RPYTHONFLAGS) aheui.py

ahsembler:
	$(RPYTHON) ahsembler.py

test:
	cd snippets && AHEUI=../aheui-c bash test.sh

testpy:
	cd snippets && AHEUI=../aheui.py bash test.sh
