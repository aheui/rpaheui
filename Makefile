
RPYTHON?=../pypy/rpython/bin/rpython
RPYTHONFLAGS?=--opt=jit


all: aheui-c aheui-py

version:
	echo "VERSION = '`git describe --tags`'" > aheui/version.py

aheui-py:
	cp rpaheui.py bin/aheui-py
	cp rpaheui.py bin/aheui

aheui-c: version
	$(RPYTHON) $(RPYTHONFLAGS) rpaheui.py

clean:
	rm rpaheui-c

install: aheui-c
	cp rpaheui-c /usr/local/bin/rpaheui
	ln -s /usr/local/bin/rpaheui /usr/local/bin/aheui

test:
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI="../rpaheui-c" bash test.sh

testpy:
	py.test
	if [ -e snippets ]; then cd snippets && git pull; else git clone https://github.com/aheui/snippets; fi
	cd snippets && AHEUI=../rpaheui.py bash test.sh
