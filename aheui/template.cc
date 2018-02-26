#include <cstdint>
#include <memory>
#include <vector>
#include <deque>
#include <algorithm>
#include <string>

namespace aheui {

typedef int64_t int_t;
typedef std::vector<int_t> SpaceVector;

const size_t SPACE_QUEUE_INDEX = 21;
const size_t SPACE_PORT_INDEX = 27;
const size_t SPACE_COUNT = 28;

struct int_pair {
    int_t first;
    int_t second;
};

void print_unicode(uint32_t codepoint) {
    if (codepoint <= 0x7f) {
        putchar(codepoint);
    }
    else if (codepoint <= 0x7ff) {
        putchar(0xc0 | ((codepoint >> 6) & 0x1f));
        putchar(0x80 | (codepoint & 0x3f));
    }
    else if (codepoint <= 0xffff) {
        putchar(0xe0 | ((codepoint >> 12) & 0x0f));
        putchar(0x80 | ((codepoint >> 6) & 0x3f));
        putchar(0x80 | (codepoint & 0x3f));
    }
    else {
        putchar(0xf0 | ((codepoint >> 18) & 0x07));
        putchar(0x80 | ((codepoint >> 12) & 0x3f));
        putchar(0x80 | ((codepoint >> 6) & 0x3f));
        putchar(0x80 | (codepoint & 0x3f));
    }
}

class Space {
protected:
    inline virtual void _put_value(int_t v) = 0;
    inline virtual int_pair _get_2_values() = 0;
public:
    inline virtual size_t size() = 0;
    inline virtual void push(int_t v) = 0;
    inline virtual int_t pop() = 0;
    inline virtual void swap() = 0;
    inline virtual void dup() = 0;
    inline void add() {
        auto values = this->_get_2_values();
        auto r = values.second + values.first;
        this->_put_value(r);
    }
    inline void sub() {
        auto values = this->_get_2_values();
        auto r = values.second - values.first;
        this->_put_value(r);
    }
    inline void mul() {
        auto values = this->_get_2_values();
        auto r = values.second * values.first;
        this->_put_value(r);
    }
    inline void div() {
        auto values = this->_get_2_values();
        auto r = values.second / values.first;
        this->_put_value(r);
    }
    inline void mod() {
        auto values = this->_get_2_values();
        auto r = values.second % values.first;
        this->_put_value(r);
    }
    inline void cmp() {
        auto values = this->_get_2_values();
        auto r = values.second >= values.first;
        this->_put_value((int_t)r);
    }
};

class Stack: public Space, std::vector<int_t> {
protected:
    inline void _put_value(int_t v) {
        this->back() = v;
    }
    inline int_pair _get_2_values() {
        int_pair r;
        r.first = this->back();
        this->pop_back();
        r.second = this->back();
        return r;
    }
public:
    inline size_t size() {
        return std::vector<int_t>::size();
    }
    inline virtual void push(int_t v) {
        this->push_back(v);
    }
    inline virtual int_t pop() {
        auto v = this->back();
        this->pop_back();
        return v;
    }
    inline void swap() {
        std::iter_swap(this->end() - 1, this->end() - 2);
    }
    inline void dup() {
        auto r = this->back();
        this->push_back(r);
    }
};

class Queue: public Space, std::deque<int_t> {
protected:
    inline void _put_value(int_t v) {
        this->push_back(v);
    }
    inline int_pair _get_2_values() {
        int_pair r;
        r.first = this->back();
        this->pop_back();
        r.second = this->back();
        this->pop_back();
        return r;
    }
public:
    inline size_t size() {
        return std::deque<int_t>::size();
    }
    inline virtual void push(int_t v) {
        this->push_back(v);
    }
    inline virtual int_t pop() {
        auto v = this->front();
        this->pop_front();
        return v;
    }
    inline void swap() {
        std::iter_swap(this->end() - 1, this->end() - 2);
    }
    inline void dup() {
        auto r = this->back();
        this->push_back(r);
    }
};

class Runtime {
    std::unique_ptr<Space> spaces[28];
    Space *space;
public:
    int_t exitcode = 0;
    Runtime() {
        for (auto i = 0; i < SPACE_COUNT; i++) {
            if (i ==  SPACE_QUEUE_INDEX) {
                this->spaces[i] = std::make_unique<Queue>();
            } else {
                this->spaces[i] = std::make_unique<Stack>();
            }
        }
        this->sel(0);
    }
    // generation resource
    inline void add() {
        this->space->add();
    }
    inline void sub() {
        this->space->sub();
    }
    inline void mul() {
        this->space->mul();
    }
    inline void div() {
        this->space->div();
    }
    inline void mod() {
        this->space->mod();
    }
    inline void pop() {
        this->space->pop();
    }
    inline void push(int_t v) {
        this->space->push(v);
    }
    inline void dup() {
        this->space->dup();
    }
    inline void swap() {
        this->space->swap();
    }
    inline void sel(size_t i) {
        this->space = spaces[i].get();
    }
    inline void mov(size_t i) {
        auto r = this->space->pop();
        this->spaces[i]->push(r);
    }
    inline void cmp() {
        this->space->cmp();
    }
    inline void popnum() {
        auto r = this->space->pop();
        printf("%lld", r);
    }
    inline void popchar() {
        auto r = this->space->pop();
        if (r < 0 || r > 0x10ffff) {
            this->exitcode = r;
            exit(-1);
        }
        print_unicode((uint32_t)r);
    }
    inline void pushnum() {
        int_t i;
        scanf("%lld", &i);
        this->space->push(i);
    }
    inline void pushchar() {
        
    }
    inline void halt() {
        if (this->space->size() > 0) {
            this->exitcode = this->space->pop();
        } else {
            this->exitcode = 0;
        }
        exit((int)this->exitcode);
    }
    inline bool jump_brpop1() {
        return this->space->size() < 1;
    }
    inline bool jump_brpop2() {
        return this->space->size() < 2;
    }
    inline bool jump_brz() {
        return this->space->pop() == 0;
    }
};

void _main_run(Runtime *r);
int _main() {
    auto runtime = std::make_unique<aheui::Runtime>();
    _main_run(runtime.get());
    return (int)runtime->exitcode;
}

void _main_run(Runtime *r) {
///GENERATED_CODE///
}

}

int main() {
    return aheui::_main();
}

