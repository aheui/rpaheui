
RPYTHON=../pypy/rpython/bin/rpython
RPYTHONFLAGS=--opt=jit
#RPYTHONFLAGS=

all: aheui-c
	

version:
	echo "VERSION='`git describe --tags`'" > aheui/version.py

aheui-c: version
	cd aheui && ../$(RPYTHON) $(RPYTHONFLAGS) aheui.py

clean:
	rm aheui-c

install: aheui-c
	cp aheui/aheui-c /usr/local/bin/aheui

test:
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI="../aheui/aheui-c" bash test.sh

testpy:
	py.test
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI=../aheui/aheui.py bash test.sh
