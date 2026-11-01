"""
UNIT 5 — FUNCTIONS (printed pages 93-106).

Section outline as printed:

    5.1 Introduction to Functions ................ p. 94
        5.1.1 Pre-defined Functions .............. p. 94
        5.1.2 User-defined Function .............. pp. 95-96
        Function call ............................ p. 97
        Definition vs call (table) ............... p. 98
        Different Ways to Use a Function ......... pp. 98-99
        Worked programs (sqrt, average) .......... pp. 99-100
        Pre-define vs User-define (table) ........ p. 100
        Local variable and global variable ....... pp. 101-102
    SUMMARY p. 103 | EXERCISE pp. 104-105 | LAB ACTIVITIES pp. 105-106

Every function form in this unit was compiled and run with MinGW g++
(`-std=c++17`) before being published as a runnable sample; the four
return/argument combinations and the pre-defined functions (`sqrt`, `pow`,
`strcpy`, `toupper`) all execute honestly in the sandbox.

EXERCISE A (pp. 104-105) is published as the book's own MCQs; EXERCISE B Q7
(the `void Table(void)` find-the-errors program) and the six LAB ACTIVITIES
(pp. 105-106) are implemented as graded exercises with real output checks.
"""

from .common import ref

UNIT = 'Unit 5'
CLASS = 'Class X'

CHAPTER = {
    'slug': 'unit-5-functions',
    'title': 'Unit 5 — Functions',
    'description': (
        'Grouping code into named, reusable blocks: pre-defined library '
        'functions, writing your own user-defined functions, the four ways to '
        'pass arguments and return values, and local versus global variables.'
    ),
    'order': 4,
    'xp_reward': 650,
    'reference': ref(UNIT, 'Functions', '93-106', CLASS),
    'lessons': [
        # ── 5.1 ────────────────────────────────────────────────────────────
        {
            'slug': 'introduction-to-functions',
            'title': 'What Is a Function?',
            'content_type': 'text',
            'learning_objective': (
                'Define a function and name the two kinds: pre-defined and '
                'user-defined.'
            ),
            'order': 1,
            'duration_minutes': 10,
            'xp_reward': 45,
            'reference': ref(UNIT, '5.1 Introduction to Functions', '94', CLASS),
            'content_body': '''# What Is a Function?

Section 5.1 (p. 94) defines a function as **a set of statements with a unique name that performs a specific task** — a *subprogram* you can call whenever you need it. Instead of rewriting the same five lines everywhere, you write them once, give them a name, and *call* that name.

Two facts the book insists on:

- **Every** C++ program has at least one function: `main()`. Your program is itself a function the operating system calls.
- Functions are called **subprograms** because they do a sub-task of the whole program.

## The two types (p. 94)

| Type | Who writes it | Example |
|---|---|---|
| **Pre-defined** (system-defined / library) | already written for you, declared in a header file | `sqrt()`, `pow()`, `strcpy()`, `toupper()` |
| **User-defined** | you write it | `int add(int a, int b) { return a + b; }` |

You never have to define a pre-defined function — you only `#include` its header and call it. A user-defined function needs *you* to declare and define it. EXERCISE A (1), p. 104 asks exactly this: a function **you** write is the user-defined kind.
''',
            'exercises': [
                {
                    'slug': 'function-is-a-set-of-statements',
                    'title': 'Defining a Function',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'According to section 5.1, what is a function?'
                    ),
                    'explain': (
                        'A function is a set of statements with a unique name '
                        'that performs a specific task — a subprogram. Sindh '
                        'Board Class X, Unit 5, EXERCISE A (1), p. 104.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'A set of statements with a unique name that performs a specific task', 'is_correct': True},
                        {'id': 'b', 'text': 'A variable that holds a number', 'is_correct': False},
                        {'id': 'c', 'text': 'A special symbol that ends a statement', 'is_correct': False},
                        {'id': 'd', 'text': 'The name of the program file', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A (1)', '104', CLASS),
                },
                {
                    'slug': 'every-program-has-main',
                    'title': 'The Function Every Program Has',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which function must be present in every C++ program?'
                    ),
                    'explain': (
                        'Every program has at least one function, `main()`; '
                        'execution begins there. Sindh Board Class X, Unit 5, '
                        '5.1, p. 94.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'main()', 'is_correct': True},
                        {'id': 'b', 'text': 'sqrt()', 'is_correct': False},
                        {'id': 'c', 'text': 'printf()', 'is_correct': False},
                        {'id': 'd', 'text': 'start()', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '5.1 Introduction to Functions', '94', CLASS),
                },
                {
                    'slug': 'predefined-vs-userdefined',
                    'title': 'Who Writes the Function?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        '`sqrt()` is ready to use after including its header, '
                        'with no code you had to write. Which kind of function '
                        'is it?'
                    ),
                    'explain': (
                        'Pre-defined (system-defined / library) functions are '
                        'declared in header files and need no definition by '
                        'you. Sindh Board Class X, Unit 5, 5.1.1, p. 94.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Pre-defined (library) function', 'is_correct': True},
                        {'id': 'b', 'text': 'User-defined function', 'is_correct': False},
                        {'id': 'c', 'text': 'A global variable', 'is_correct': False},
                        {'id': 'd', 'text': 'A statement terminator', 'is_correct': False},
                    ],
                    'xp_reward': 45,
                    'order': 3,
                    'reference': ref(UNIT, '5.1.1 Pre-defined Functions', '94', CLASS),
                },
            ],
        },

        # ── 5.1.1 ──────────────────────────────────────────────────────────
        {
            'slug': 'using-predefined-functions',
            'title': 'Calling Pre-defined Functions',
            'content_type': 'interactive',
            'learning_objective': (
                'Call library functions such as `sqrt()` and `pow()` after '
                'including the right header.'
            ),
            'order': 2,
            'duration_minutes': 12,
            'xp_reward': 55,
            'reference': ref(UNIT, '5.1.1 Pre-defined Functions', '94-99', CLASS),
            'content_body': '''# Pre-defined Functions in Action

A pre-defined function is already written and declared in a header file — you just `#include` the header and call it (p. 94). The book names `sqrt()`, `strcpy()`, `toupper()` and `pow()`, and points to `<cmath>` and `<cstdlib>` for the maths ones.

## The worked sqrt program (p. 99)

The textbook prints a program that reads a number and shows its square root; with `a = 16` the OUTPUT is `4`:

```cpp
#include <iostream>
#include <cmath>
using namespace std;

int main() {
    float a;
    cout << "Enter a number: ";
    cin >> a;
    cout << sqrt(a);
    return 0;
}
```

Run it with `16` — `sqrt` does all the work; you never wrote how to compute a root. That is the whole advantage of the library.

## A few you will meet

- `sqrt(x)` — square root (`<cmath>`). `sqrt(16)` → `4`.
- `pow(base, exp)` — power (`<cmath>`). `pow(2, 5)` → `32`.
- `toupper(c)` — upper-case a character (`<cctype>`).
- `strcpy(dest, src)` — copy a string (`<cstring>`).

> EXERCISE A (8), p. 105 lists `time()` among pre-defined functions too — it returns the current time. All of these are **system-defined**: you call them, you do not write them.
''',
            'exercises': [
                {
                    'slug': 'sqrt-of-a-number',
                    'title': 'Print a Square Root',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Read a number and print its square root using '
                        '`sqrt()`. With `25` the output is `5`.'
                    ),
                    'context': 'Section 5.1.1, worked sqrt program, p. 99.',
                    'constraints': 'Include `<cmath>` and call `sqrt`.',
                    'expected_behavior': 'For input 25 the program prints: 5',
                    'explain': (
                        '`sqrt(25)` returns 5; the library function does the '
                        'work. Sindh Board Class X, Unit 5, 5.1.1, p. 99.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        '#include <cmath>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    float a;\n'
                        '    cin >> a;\n'
                        '    // print the square root of a\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        '#include <cmath>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    float a;\n'
                        '    cin >> a;\n'
                        '    cout << sqrt(a);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '25\n', 'expected_output': '5'},
                        {'input': '16\n', 'expected_output': '4'},
                    ],
                    'xp_reward': 80,
                    'order': 1,
                    'reference': ref(UNIT, '5.1.1 Pre-defined — sqrt program', '99', CLASS),
                    'hints': [
                        'The function is sqrt(a); print it with cout.',
                        'cout << sqrt(a);',
                    ],
                },
                {
                    'slug': 'which-header-for-sqrt',
                    'title': 'Which Header for sqrt()?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Pre-defined functions are declared in files with which '
                        'extension? (EXERCISE A (2), p. 104.)'
                    ),
                    'explain': (
                        'Pre-defined functions are declared in **header files** '
                        'with the `.h` extension (or C++ headers like <cmath>). '
                        'Sindh Board Class X, Unit 5, EXERCISE A (2), p. 104.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '.h (header files)', 'is_correct': True},
                        {'id': 'b', 'text': '.cpp (source files)', 'is_correct': False},
                        {'id': 'c', 'text': '.exe (executable files)', 'is_correct': False},
                        {'id': 'd', 'text': '.txt (text files)', 'is_correct': False},
                    ],
                    'xp_reward': 45,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A (2)', '104', CLASS),
                },
            ],
        },

        # ── 5.1.2 + call ───────────────────────────────────────────────────
        {
            'slug': 'writing-user-defined-functions',
            'title': 'Writing a User-defined Function',
            'content_type': 'interactive',
            'learning_objective': (
                'Declare a prototype, define a function with a return type and '
                'parameters, and call it.'
            ),
            'order': 3,
            'duration_minutes': 18,
            'xp_reward': 65,
            'reference': ref(UNIT, '5.1.2 User-defined Function', '95-98', CLASS),
            'content_body': '''# User-defined Functions

A user-defined function is one **you** write. Section 5.1.2 (pp. 95-96) breaks it into three steps.

## 1. Declaration (the prototype)

Announced **before `main()`** so the compiler knows the function exists. Figure 5.1 annotates `float avg (int val1, int val2, int val3);` into four parts:

- **Return Data Type** — `float` (what the function hands back; `void` if nothing).
- **Name of Function** — `avg`.
- **Parameters** — `int val1, int val2, int val3` (comma-separated).
- **Statement Terminator** — the `;`.

## 2. Definition

The actual work: a **header** plus a **body** in braces. The book\'s example (p. 96):

```cpp
int add (int a, int b)
{
    int c;
    c = a + b;
    return c;
}
```

## 3. Call

You *use* the function from `main()`. Syntax (p. 97): `function_name();`, e.g. `add();` or `x = add(y, z);`.

- **Actual parameters** are the real values you pass at the call site; **formal parameters** are the names in the definition that receive them. EXERCISE A (4), p. 104 tests this.
- `return` sends a value back to the caller and ends the function.

## Putting it together — the average program (p. 100)

The textbook works a `float average(int x, int y)` example; with `24` and `34` the OUTPUT is `29`:

```cpp
#include <iostream>
using namespace std;

int average(int x, int y)      // definition (return type int, two parameters)
{
    return (x + y) / 2;
}

int main() {
    int a, b;
    cout << "Enter two numbers: ";
    cin >> a >> b;
    cout << average(a, b);     // call
    return 0;
}
```

**Expected output** with input `24 34`:

```output
Enter two numbers: 29
```

> **Definition vs call** (p. 98): the *definition* is where you write what the function does (`int sum(int p, int q) { … }`); the *call* is where you use it (`a = sum(x, y);`). EXERCISE A (5), p. 104 confirms the declaration/prototype comes before `main()`.
''',
            'exercises': [
                {
                    'slug': 'write-a-sum-function',
                    'title': 'Write and Call a Function',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Define a function `int add(int a, int b)` that returns '
                        'the sum of its two arguments. In `main()`, read two '
                        'integers, call `add`, and print the result. Input '
                        '`20 22` prints `42`.'
                    ),
                    'context': 'Section 5.1.2, add() definition (p. 96) and call (p. 97).',
                    'constraints': 'The function must be defined with a return type of int and two int parameters.',
                    'expected_behavior': 'For input `20 22` the program prints: 42',
                    'explain': (
                        '`add` returns `a + b`; `main` reads the two numbers, '
                        'calls `add(a, b)` and prints the returned value. Sindh '
                        'Board Class X, Unit 5, 5.1.2, pp. 95-97.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        '// define int add(int a, int b) here\n\n\n\n\n'
                        'int main() {\n'
                        '    int a, b;\n'
                        '    cin >> a >> b;\n'
                        '    // call add and print the result\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int add(int a, int b) {\n'
                        '    return a + b;\n'
                        '}\n'
                        '\n'
                        'int main() {\n'
                        '    int a, b;\n'
                        '    cin >> a >> b;\n'
                        '    cout << add(a, b);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '20 22\n', 'expected_output': '42'},
                        {'input': '5 7\n', 'expected_output': '12'},
                    ],
                    'xp_reward': 110,
                    'order': 1,
                    'reference': ref(UNIT, '5.1.2 User-defined Function', '95-97', CLASS),
                    'hints': [
                        'Write the definition above main: int add(int a, int b) { return a + b; }',
                        'Then call it: cout << add(a, b);',
                    ],
                },
                {
                    'slug': 'average-two-numbers',
                    'title': 'The Average Function',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Reproduce the worked program (p. 100): a function that '
                        'takes two integers and returns their average, called '
                        'from `main`. Input `24 34` prints `29`.'
                    ),
                    'context': 'Section 5.1.2 worked average program, p. 100.',
                    'constraints': 'Define the function separately from main and call it.',
                    'expected_behavior': 'For input `24 34` the program prints: 29',
                    'explain': (
                        'The function returns `(x + y) / 2`; (24+34)/2 = 29. '
                        'Sindh Board Class X, Unit 5, 5.1.2, p. 100.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        '// int average(int x, int y) returns (x + y) / 2\n\n\n\n\n'
                        'int main() {\n'
                        '    int a, b;\n'
                        '    cin >> a >> b;\n'
                        '    cout << average(a, b);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int average(int x, int y) {\n'
                        '    return (x + y) / 2;\n'
                        '}\n'
                        '\n'
                        'int main() {\n'
                        '    int a, b;\n'
                        '    cin >> a >> b;\n'
                        '    cout << average(a, b);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '24 34\n', 'expected_output': '29'},
                        {'input': '10 20\n', 'expected_output': '15'},
                    ],
                    'xp_reward': 100,
                    'order': 2,
                    'reference': ref(UNIT, '5.1.2 — average program', '100', CLASS),
                    'hints': [
                        'int average(int x, int y) { return (x + y) / 2; }',
                    ],
                },
                {
                    'slug': 'prototype-comes-before-main',
                    'title': 'Where Does the Prototype Go?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'In the book\'s three steps, the function declaration '
                        '(prototype) is placed…'
                    ),
                    'explain': (
                        'The declaration/prototype comes **before `main()`** so '
                        'the compiler knows the function before it is called. '
                        'Sindh Board Class X, Unit 5, EXERCISE A (5), p. 104.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Before main()', 'is_correct': True},
                        {'id': 'b', 'text': 'Inside another function body', 'is_correct': False},
                        {'id': 'c', 'text': 'After the closing brace of main', 'is_correct': False},
                        {'id': 'd', 'text': 'Only inside the function it describes', 'is_correct': False},
                    ],
                    'xp_reward': 45,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE A (5)', '104', CLASS),
                },
                {
                    'slug': 'formal-vs-actual-parameters',
                    'title': 'Formal vs Actual Parameters',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'hard',
                    'instructions': (
                        'In `int add(int a, int b)` used by `x = add(3, 4);`, '
                        'the names `a` and `b` in the definition are called the…'
                    ),
                    'explain': (
                        '`a` and `b` are the **formal parameters** (in the '
                        'definition); the values `3` and `4` at the call are the '
                        'actual parameters. Sindh Board Class X, Unit 5, '
                        'EXERCISE A (4), p. 104.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Formal parameters', 'is_correct': True},
                        {'id': 'b', 'text': 'Actual parameters', 'is_correct': False},
                        {'id': 'c', 'text': 'Return values', 'is_correct': False},
                        {'id': 'd', 'text': 'Global variables', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 4,
                    'reference': ref(UNIT, 'EXERCISE A (4)', '104', CLASS),
                },
            ],
        },
        # ── Different Ways (pp. 98-99) ─────────────────────────────────────
        {
            'slug': 'four-ways-to-use-a-function',
            'title': 'Four Ways to Use a Function',
            'content_type': 'interactive',
            'learning_objective': (
                'Combine arguments and return values four ways: with/without '
                'arguments crossed with with/without a return value.'
            ),
            'order': 4,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, 'Different Ways to Use User-Defined Function', '98-99', CLASS),
            'content_body': '''# Four Ways to Use a User-defined Function

Pages 98-99 list every combination of the two independent choices — *do you pass arguments?* and *do you return a value?* — giving **four** forms.

| # | Arguments? | Returns? | Prototype the book gives |
|---|---|---|---|
| 1 | No | No | `void functionName(void);` |
| 2 | No | Yes | `int/float/char functionName(void);` |
| 3 | Yes | No | `void functionName(int, float, char);` |
| 4 | Yes | Yes | `int/float/char functionName(int, float, char);` |

`void` in the return-type slot means "returns nothing". `void` inside the parameter list means "takes nothing".

## Form 3 — arguments but no return (a `void` function)

```cpp
#include <iostream>
using namespace std;

void showDouble(int n)      // takes an int, returns nothing
{
    cout << n * 2;
}

int main() {
    int v;
    cin >> v;
    showDouble(v);          // call; nothing is received back
    return 0;
}
```

**Expected output** with input `6`:

```output
12
```

## Form 2 — a return value but no arguments

```cpp
int answer() { return 42; }   // hands back 42, needs nothing
```

Forms 1 and 4 are just the remaining crossings: form 1 neither receives nor returns (`void name(void)`), form 4 does both — exactly like the `add(int a, int b)` from the previous lesson.
''',
            'exercises': [
                {
                    'slug': 'void-function-with-argument',
                    'title': 'A void Function that Takes an Argument',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Write `void showDouble(int n)` that prints `n * 2` and '
                        'returns nothing. In `main`, read one integer and call '
                        'the function. Input `6` prints `12`.'
                    ),
                    'context': 'Form 3 (arguments, no return), pp. 98-99.',
                    'constraints': 'The function returns void and takes one int.',
                    'expected_behavior': 'For input 6 the program prints: 12',
                    'explain': (
                        'A `void` function performs an action (printing) without '
                        'returning a value; the argument is passed in. Sindh '
                        'Board Class X, Unit 5, Different Ways (form 3), pp. 98-99.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        '// void showDouble(int n) prints n * 2\n\n\n\n\n'
                        'int main() {\n'
                        '    int v;\n'
                        '    cin >> v;\n'
                        '    showDouble(v);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'void showDouble(int n) {\n'
                        '    cout << n * 2;\n'
                        '}\n'
                        '\n'
                        'int main() {\n'
                        '    int v;\n'
                        '    cin >> v;\n'
                        '    showDouble(v);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '6\n', 'expected_output': '12'},
                        {'input': '10\n', 'expected_output': '20'},
                    ],
                    'xp_reward': 100,
                    'order': 1,
                    'reference': ref(UNIT, 'Different Ways — form 3', '98-99', CLASS),
                    'hints': [
                        'void showDouble(int n) { cout << n * 2; }',
                    ],
                },
                {
                    'slug': 'how-many-combinations',
                    'title': 'How Many Ways to Use a Function?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Counting the presence or absence of arguments and of a '
                        'return value, how many ways does the book list for '
                        'using a user-defined function?'
                    ),
                    'explain': (
                        'Four: no-arg/no-return, no-arg/return, arg/no-return, '
                        'arg/return. Sindh Board Class X, Unit 5, Different '
                        'Ways to Use User-Defined Function, pp. 98-99.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Four', 'is_correct': True},
                        {'id': 'b', 'text': 'Two', 'is_correct': False},
                        {'id': 'c', 'text': 'Three', 'is_correct': False},
                        {'id': 'd', 'text': 'Five', 'is_correct': False},
                    ],
                    'xp_reward': 45,
                    'order': 2,
                    'reference': ref(UNIT, 'Different Ways to Use User-Defined Function', '98-99', CLASS),
                },
            ],
        },

        # ── Local / Global (pp. 101-102) ───────────────────────────────────
        {
            'slug': 'local-and-global-variables',
            'title': 'Local and Global Variables',
            'content_type': 'interactive',
            'learning_objective': (
                'Tell a local variable from a global (external) one and predict '
                'where each can be seen.'
            ),
            'order': 5,
            'duration_minutes': 14,
            'xp_reward': 55,
            'reference': ref(UNIT, 'Local variable and global variable', '101-102', CLASS),
            'content_body': '''# Local vs Global Variables

Pages 101-102 sort variables by **where they are declared**.

- A **local variable** is declared *inside* a function (or block). Only that function can see it, and it disappears when the function ends. The comment in the book reads `int a = 10; // Local Variable`.
- A **global variable** is declared *outside* `main()`. The book also calls it an **external variable**: it keeps its value for the whole run and is shared by every function.

## The worked program (p. 102)

```cpp
#include <iostream>
using namespace std;

int a = 20;          // Global Variable — visible everywhere

void add(int c)      // c is a local variable (and a received argument)
{
    cout << a + c;   // uses the global a and the local c
}

int main() {
    int v;
    cin >> v;
    add(v);
    return 0;
}
```

**Expected output** with input `5`:

```output
25
```

`a` lives outside `main()`, so `add()` can read it without it being passed in. `c` (and the `v` in `main`) exist only inside their own function — a local in one function is invisible to another. Note the received argument `c` is itself **local** to `add`.

> EXERCISE A (7), p. 104: a variable declared inside a function is the **local variable**. Two functions each declaring `int x;` have two separate, unrelated `x`s.
''',
            'exercises': [
                {
                    'slug': 'global-plus-local-sum',
                    'title': 'Use a Global Inside a Function',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'The starter has a global `int a = 20;`. Complete '
                        '`void add(int c)` so it prints `a + c`. In `main` an '
                        'integer is read and passed to `add`. Input `5` prints '
                        '`25`.'
                    ),
                    'context': 'Section 5.1 worked global-variable program, p. 102.',
                    'constraints': 'Read the global `a` inside `add`; do not redeclare it locally.',
                    'expected_behavior': 'For input 5 the program prints: 25',
                    'explain': (
                        '`a` is global so `add` sees it without being passed it; '
                        '`c` is the local received argument. 20 + 5 = 25. Sindh '
                        'Board Class X, Unit 5, local/global, p. 102.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int a = 20;          // Global Variable\n'
                        '\n'
                        'void add(int c) {\n'
                        '    // print a + c\n\n\n'
                        '}\n'
                        '\n'
                        'int main() {\n'
                        '    int v;\n'
                        '    cin >> v;\n'
                        '    add(v);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int a = 20;          // Global Variable\n'
                        '\n'
                        'void add(int c) {\n'
                        '    cout << a + c;\n'
                        '}\n'
                        '\n'
                        'int main() {\n'
                        '    int v;\n'
                        '    cin >> v;\n'
                        '    add(v);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '5\n', 'expected_output': '25'},
                        {'input': '3\n', 'expected_output': '23'},
                    ],
                    'xp_reward': 100,
                    'order': 1,
                    'reference': ref(UNIT, 'Local and global variable', '102', CLASS),
                    'hints': [
                        'Just add: cout << a + c;',
                        'a is global — no need to pass it in.',
                    ],
                },
                {
                    'slug': 'variable-inside-function',
                    'title': 'Local or Global?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'A variable declared inside a function is called a… '
                        '(EXERCISE A (7), p. 104.)'
                    ),
                    'explain': (
                        'A variable declared inside a function is a local '
                        'variable, visible only there. Sindh Board Class X, '
                        'Unit 5, EXERCISE A (7), p. 104.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Local variable', 'is_correct': True},
                        {'id': 'b', 'text': 'Global (external) variable', 'is_correct': False},
                        {'id': 'c', 'text': 'Constant', 'is_correct': False},
                        {'id': 'd', 'text': 'Formal parameter', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A (7)', '104', CLASS),
                },
            ],
        },

        # ── LAB ACTIVITIES (pp. 105-106) ───────────────────────────────────
        {
            'slug': 'unit-5-function-lab-practicals',
            'title': 'Function Lab Practicals',
            'content_type': 'interactive',
            'learning_objective': (
                'Solve the textbook\'s Unit 5 lab practicals as real functions.'
            ),
            'order': 6,
            'duration_minutes': 22,
            'xp_reward': 70,
            'reference': ref(UNIT, 'LAB ACTIVITIES', '105-106', CLASS),
            'content_body': '''# Unit 5 Lab Practicals

The LAB ACTIVITIES (pp. 105-106) turn the theory into programs you must actually write:

1. Print the series `0, 5, 10, 15, 20, 25, 30, 35` with a `for` loop, using **no return value and no passed parameters** (form 1/3).
2. Check **even or odd** using **return value and passed parameters** (form 4).
3. A function that takes kilograms as a parameter and **returns grams** (1 kg = 1000 g).
4. A function taking length and height that prints a **box of stars** (form: return value but not passed parameters in the book\'s wording).
5. A function that **returns the factorial** of a number.
6. Formula programs as functions: Area of Rectangle (`a = l b`), Area of Circle (`a = pi * r * r`, pi = 3.14), Pythagorean Theorem.

The graded exercises below implement items 5 (factorial) and 3 (kg → grams) — both are form-4 functions: they take an argument and return a value.

## Factorial (item 5)

`5!` means 5 × 4 × 3 × 2 × 1 = 120. A loop inside a function multiplies the running product, then `return`s it.
''',
            'exercises': [
                {
                    'slug': 'factorial-function',
                    'title': 'LAB 5: A Factorial Function',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'hard',
                    'instructions': (
                        'Write `int factorial(int n)` that returns n! (the '
                        'product 1 × 2 × … × n). In `main`, read a number, call '
                        'it and print the result. Input `5` prints `120`; '
                        'input `0` prints `1`.'
                    ),
                    'context': 'LAB ACTIVITIES 5, p. 106.',
                    'constraints': 'Use a loop inside the function; return the product. 0! is 1.',
                    'expected_behavior': 'For input 5 the program prints: 120',
                    'explain': (
                        'Start the product at 1 and multiply by every integer 1..n; '
                        'returning hands the result to main. 5! = 120, 0! = 1. '
                        'Sindh Board Class X, Unit 5, LAB ACTIVITIES 5, p. 106.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        '// int factorial(int n) using a loop\n\n\n\n\n\n'
                        'int main() {\n'
                        '    int n;\n'
                        '    cin >> n;\n'
                        '    cout << factorial(n);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int factorial(int n) {\n'
                        '    int f = 1;\n'
                        '    for (int i = 1; i <= n; i++) {\n'
                        '        f = f * i;\n'
                        '    }\n'
                        '    return f;\n'
                        '}\n'
                        '\n'
                        'int main() {\n'
                        '    int n;\n'
                        '    cin >> n;\n'
                        '    cout << factorial(n);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '5\n', 'expected_output': '120'},
                        {'input': '0\n', 'expected_output': '1'},
                        {'input': '6\n', 'expected_output': '720'},
                    ],
                    'xp_reward': 130,
                    'order': 1,
                    'reference': ref(UNIT, 'LAB ACTIVITIES 5', '106', CLASS),
                    'hints': [
                        'Start f at 1 so 0! naturally returns 1.',
                        'int f = 1; for (int i = 1; i <= n; i++) f = f * i; return f;',
                    ],
                },
                {
                    'slug': 'kg-to-grams-function',
                    'title': 'LAB 3: Kilograms to Grams',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Write a function that takes kilograms as a parameter '
                        'and returns the number of grams (1 kg = 1000 g). Read '
                        'an integer kg in `main` and print the returned grams. '
                        'Input `2` prints `2000`.'
                    ),
                    'context': 'LAB ACTIVITIES 3, p. 105.',
                    'constraints': 'The function takes one int and returns an int.',
                    'expected_behavior': 'For input 2 the program prints: 2000',
                    'explain': (
                        'The function returns kg × 1000; main prints the returned '
                        'value. Sindh Board Class X, Unit 5, LAB ACTIVITIES 3, '
                        'p. 105.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        '// int toGrams(int kg) returns kg * 1000\n\n\n\n\n'
                        'int main() {\n'
                        '    int kg;\n'
                        '    cin >> kg;\n'
                        '    cout << toGrams(kg);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int toGrams(int kg) {\n'
                        '    return kg * 1000;\n'
                        '}\n'
                        '\n'
                        'int main() {\n'
                        '    int kg;\n'
                        '    cin >> kg;\n'
                        '    cout << toGrams(kg);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '2\n', 'expected_output': '2000'},
                        {'input': '7\n', 'expected_output': '7000'},
                    ],
                    'xp_reward': 100,
                    'order': 2,
                    'reference': ref(UNIT, 'LAB ACTIVITIES 3', '105', CLASS),
                    'hints': [
                        'int toGrams(int kg) { return kg * 1000; }',
                    ],
                },
                {
                    'slug': 'predefined-vs-userdefined-table',
                    'title': 'Pre-defined vs User-defined',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Which statement about a pre-defined function is true? '
                        '(The p. 100 comparison table.)'
                    ),
                    'explain': (
                        'Pre-defined (library) functions are already written and '
                        'declared in a header; you only call them, you do not '
                        'define them. Sindh Board Class X, Unit 5, Pre-define vs '
                        'User-define table, p. 100.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'It is already written and you only call it after including its header', 'is_correct': True},
                        {'id': 'b', 'text': 'You must write its body yourself', 'is_correct': False},
                        {'id': 'c', 'text': 'It can never return a value', 'is_correct': False},
                        {'id': 'd', 'text': 'It only works inside main()', 'is_correct': False},
                    ],
                    'xp_reward': 45,
                    'order': 3,
                    'reference': ref(UNIT, 'Differentiate Pre-define vs User-define Function', '100', CLASS),
                },
            ],
        },
    ],
}
