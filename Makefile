
RPYTHON?=../pypy/rpython/bin/rpython
RPYTHONFLAGS?=--opt=jit
#RPYTHONFLAGS=

all: aheui-c
	

version:
	echo "VERSION='`git describe --tags`'" > version.py

aheui-c: version
	$(RPYTHON) $(RPYTHONFLAGS) aheui.py

clean:
	rm aheui-c

install: aheui-c
	cp aheui-c /usr/local/bin/aheui

ahsembler: version
	$(RPYTHON) ahsembler.py

test:
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI="../aheui-c" bash test.sh

testpy:
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI=../aheui.py bash test.sh
