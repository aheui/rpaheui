
RPYTHON=../pypy/rpython/bin/rpython
RPYTHONFLAGS=--opt=jit
#RPYTHONFLAGS=

all: aheui-c
	

aheui-c:
	$(RPYTHON) $(RPYTHONFLAGS) aheui.py

install:
	cp aheui-c /usr/local/bin/aheui

ahsembler:
	$(RPYTHON) ahsembler.py

test:
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI="../aheui-c" bash test.sh

testpy:
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI=../aheui.py bash test.sh
