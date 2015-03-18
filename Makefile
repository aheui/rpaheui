
RPYTHON=../pypy/rpython/bin/rpython

build:
	$(RPYTHON) aheui.py

ahsembler:
	$(RPYTHON) ahsembler.py

test:
	cd snippets && AHEUI=../aheui-c bash test.sh