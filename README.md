알파희 - 알파희썬(rpython)으로 만든 엔터프라이즈급 고성능 아희
====

[![Build Status](https://github.com/aheui/rpaheui/workflows/CI/badge.svg)](https://github.com/aheui/rpaheui/actions?query=workflow%3ACI)

* English: [README.en.md](https://github.com/aheui/rpaheui/blob/master/README.en.md)
* Working log (English): [LOG.md](https://github.com/aheui/rpaheui/blob/master/LOG.md)

* 빌드 및 실행 영상: [Youtube](https://www.youtube.com/watch?v=mjoj69i_f8s)
* 2015 한국 파이콘: [PyPy/RPython으로 20배 빨라지는 JIT 아희 인터프리터](http://www.slideshare.net/YunWonJeong/pypyrpython-20-jit)

알파희썬(RPython)은 PyPy를 개발하기 위해 개발/사용된 python의 방언으로서 정적 언어로 컴파일되고 tracing-JIT를 지원하기 위한 라이브러리를 내장하고 있습니다.
알파희썬으로 개발한 언어는 손쉽게 파이썬으로 실행하거나 바이너리로 빌드할 수 있고, JIT를 적용하기도 쉽습니다.

이 프로젝트는 RPython으로 JIT 인터프리터를 개발하는 예제로 활용할 수 있습니다. 위의 링크에서 LOG.md를 확인해 더 알아보세요.

* 파이썬이란?

아직 파이썬을 모르세요? [알파희 개발자가 번역한 책](http://www.yes24.com/24/Goods/15240210?Acode=101)으로 파이썬을 공부해 봅시다.

* 알파희썬이란?: [http://rpython.readthedocs.org][rpython]


```
git clone https://github.com/aheui/rpaheui
make # RPYTHON 환경변수 설정 필요. rpython은 pypy 소스코드를 내려받으면 포함되어 있습니다. 버전은 github actions 설정을 참고해 주세요.
./bin/aheui-c <아희 코드 파일>
./bin/aheui-bigint-c <큰 정수가 필요한 아희 코드 파일>
```

JIT로 속도 올리기
----

PyPy 기술은 PyPy를 CPython보다 빠르게 동작하게 만듭니다. ([http://speed.pypy.org/](http://speed.pypy.org/) 참고)

알파희도 이 기술을 이용해 JIT로 빨라지고 있습니다. 벤치마크에 널리 쓰이는 로고 실행이 caheui보다 30배 이상 더 빠릅니다!

```
$ time ./rpaheui-c snippets/logo/logo.aheui > /dev/null

real    0m0.915s
user    0m0.640s
sys 0m0.269s
```

```
$ time ../caheui/aheui snippets/logo/logo.aheui > /dev/null

real    0m26.026s
user    0m25.970s
sys 0m0.035s
```

실행 옵션
----
- 옵션을 제외한 첫 인자는 파일 이름입니다. 파일이름이 `-`면 표준 입력입니다.
- --help,-h: 도움말
- --version,-v: 버전
- --opt,-O: 최적화 수준. 기본값은 `1`입니다. `0`과 `2` 사이의 정수를 쓸 수 있습니다.
  - 0: 최적화 없음.
  - 1: 간단한 스택크기 추정으로 빠르게 쓰이지 않는 코드를 제거하고 상수 연산을 병합합니다.
  - 2: 스택크기 추정으로 완벽하게 쓰이지 않는 코드를 제거하고, 코드 조각을 직렬화해 재배치하고, 상수 연산을 병합합니다.
  - usage: `--opt=0`, `-O1` or `-O 2`
- --source,-S: 소스 유형. 기본 값은 `auto`입니다. `auto`, `bytecode`, `asm`, `text` 가운데 하나를 쓸 수 있습니다.
  - `auto`: 소스 유형을 추측합니다. 파일이름이 `.aheuic`이거나 바이트코드 종료 패턴이 담겨 있으면 `bytecode`로 추측합니다. 파일이름이 `.aheuis`이면 `asm`으로 추측합니다. 파일이름이 `.aheui`이면 `text`로 추정합니다. 추정할 수 없으면 `text`로 추정합니다.
  - `bytecode`: 아희 바이트코드. (`앟셈블리`의 바이트코드 표현형)
  - `asm`: `앟셈블리` 참고
  - usage: `--source=asm`, `-Sbytecode` or `-S text`
- --target,-T: 결과물 유형. 기본값은 `run`입니다. `run`, `bytecode`, `asm` 가운데 하나를 쓸 수 있습니다.
  - `run`: 주어진 코드를 실행합니다.
  - `bytecode`: 아희 바이트코드. (`앟셈블리`의 바이트코드 표현형)
  - `asm`: `앟셈블리` 참고
  - usage: `--target=asm`, `-Tbytecode` or `-T run`
- --output,-o: 결과물 파일. 기본값은 아래와 같습니다. 각 결과물 유형에 따라 자세한 내용을 확인하세요. `-`이면 표준 출력입니다.
  - --target=run: 이 옵션은 무시됩니다.
  - --target=bytecode: 기본 값은 `.aheuic` 파일입니다.
  - --target=asm: 기본 값은 `.aheuis` 파일입니다.
  - --target=asm+comment: `asm`에 주석이 추가됩니다.
- --cmd,-c: 코드를 파일 대신 문자열로 받아 넘겨줍니다.
- --no-c: `.aheuic` 파일을 자동으로 생성하지 않습니다.
  - `.aheuic` 파일은 왜 생성되나요?: [https://github.com/aheui/snippets/commit/cbb5a12e7cd2db771538ab28dfbc9ad1ada86f35](https://github.com/aheui/snippets/commit/cbb5a12e7cd2db771538ab28dfbc9ad1ada86f35)

앟셈블리와 ahsembler
----

* 알림: `ahsembler`는 `./aheui-c --source=asm --output=-`와 같은 명령입니다.

앟셈블러로 아희 코드를 컴파일해 직렬화 된 앟셈블리로 만드세요!
아희 코드를 선형으로 디버그할 수 있습니다!

원시 명령

- halt: ㅎ
- add: ㄷ
- mul: ㄸ
- sub: ㅌ
- div: ㄴ
- mod: ㄹ
- pop: ㅁ without ㅇ/ㅎ
- popnum: ㅁ with ㅇ
- popchar: ㅁ with ㅎ
- push $v: ㅂ without ㅇ/ㅎ. Push THE VALUE $v. $v is not an index of consonants.
- pushnum: ㅂ with ㅇ
- pushchar: ㅂ with ㅎ
- dup: ㅃ
- swap: ㅍ
- sel $v: ㅅ. $v is always an integer order of final consonants.
- mov $v: ㅆ. $v is always an integer order of final consonants.
- cmp: ㅈ
- brz $v: ㅊ. If a popped value is zero, program counter is set to $v; otherwise +1.

확장 명령 (선형 코드는 위치 정보를 잃고 일부 명령이 스택 크기 점검을 하지 않으므로 추가 명령이 필요합니다)

- brpop2 $v: If current stack doesn't have 2 values to pop, program counter is set to $v; otherwise +1.
- brpop1 $v: If current stack doesn't have 1 values to pop, program counter is set to $v; otherwise +1.
- jmp $v: Program counter is set to $v.

사용법

```
git clone https://github.com/aheui/rpaheui
python ahsembler.py <your-aheui-code>
```

 [rpython]: http://rpython.readthedocs.org