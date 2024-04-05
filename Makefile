
RPYTHON?=../pypy/rpython/bin/rpython
RPYTHONFLAGS?=--opt=jit --translation-jit_opencoder_model=big


.PHONY: all rpaheui-c rpaheui-bigint-c test-bigint test-smallint test-py clean install


all: aheui-bigint-c aheui-c aheui-py ahsembler-py

version:
	echo "VERSION = '`git describe --tags`'" > aheui/version.py

aheui-py: version
	cp rpaheui.py bin/aheui-py
	cp rpaheui.py bin/aheui

ahsembler-py:
	cp ahsembler.py bin/ahsembler

rpaheui-bigint-c: 
	RPAHEUI_BIGINT=1 $(RPYTHON) $(RPYTHONFLAGS) --output rpaheui-bigint-c rpaheui.py

rpaheui-c:
	$(RPYTHON) $(RPYTHONFLAGS) rpaheui.py

ahsembler-c:
	$(RPYTHON) ahsembler.py  # No JIT

aheui-bigint-c: rpaheui-bigint-c
	cp rpaheui-bigint-c bin/aheui-bigint-c

aheui-c: rpaheui-c
	cp rpaheui-c bin/aheui-c

clean:
	rm rpaheui-smallint rpaheui-bigint

install: rpaheui-c rpaheui-bigint-c
	cp rpaheui-bigint-c /usr/local/bin/rpaheui-bigint
	cp rpaheui-c /usr/local/bin/rpaheui
	ln -s /usr/local/bin/rpaheui /usr/local/bin/aheui

test-bigint-c:
	cd snippets && AHEUI="../rpaheui-bigint-c" bash test.sh

test-c:
	cd snippets && AHEUI="../rpaheui-c" bash test.sh --disable integer

test-py:
	pytest
	cd snippets && AHEUI=../bin/aheui bash test.sh --disable logo
