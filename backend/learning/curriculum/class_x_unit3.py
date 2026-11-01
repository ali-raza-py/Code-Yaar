"""
UNIT 3 — INPUT/OUTPUT HANDLING IN C++ (printed pages 48-69).

Section outline as printed:

    3.1 Basic Structure of C++ ............ p. 49
    3.2 Comment Statement in C++ .......... pp. 50-51
    3.3 INPUT/OUTPUT Handling in C++ ...... p. 51
        3.3.1 Output Function ............. p. 52
        3.3.2 Input Function .............. pp. 53-55
        3.3.3 Statement Terminator (;) .... p. 56
        3.3.4 Escape Sequences ............ p. 56
    3.4 Operators ......................... p. 57
        3.4.1 Arithmetic .... pp. 57-59   3.4.2 Increment .... pp. 59-60
        3.4.3 Decrement ..... p. 60       3.4.4 Relational ... pp. 60-61
        3.4.5 Logical ....... pp. 62-63   3.4.6 Assignment ... pp. 63-64
        3.4.7 Arithmetic Assignment ..... p. 65
    SUMMARY p. 66 | EXERCISE pp. 67-68 | LAB ACTIVITIES p. 69

This is the unit where learners write their first working programs, so the
snippets are compiled and run for real.

Held back on purpose (see textbooks/CLASS-X-SOURCE-VERIFICATION.md):

* `getch()` and `getche()` are taught exactly as the book describes them, but
  their snippets have no Run button. They read the console device rather than
  standard input, so under the sandbox's piped stdin they hang until the
  timeout — measured, not assumed. Learners run them in Dev-C++.
* EXERCISE A items (vi) and (vii) are not published as auto-graded questions:
  the printed option sets are not legible enough in the scan to reproduce
  without inventing distractors. They are left for manual review.
"""

from .common import ref

UNIT = 'Unit 3'
CLASS = 'Class X'

CHAPTER = {
    'slug': 'unit-3-input-output-handling-in-cpp',
    'title': 'Unit 3 — Input/Output Handling in C++',
    'description': (
        'The structure of a C++ program, comments, printing with cout and '
        'puts, reading with cin, escape sequences, and all seven families of '
        'operators — with the textbook\'s own formula practicals.'
    ),
    'order': 2,
    'xp_reward': 600,
    'reference': ref(UNIT, 'Input/Output Handling in C++', '48-69', CLASS),
    'lessons': [
        # ── 3.1 ────────────────────────────────────────────────────────────
        {
            'slug': 'basic-structure-of-a-cpp-program',
            'title': 'The Basic Structure of a C++ Program',
            'content_type': 'interactive',
            'learning_objective': (
                'Name the three parts of a C++ program and explain what each '
                'line of the standard skeleton does.'
            ),
            'order': 1,
            'duration_minutes': 18,
            'xp_reward': 60,
            'reference': ref(UNIT, '3.1 Basic Structure of C++', '49-50', CLASS),
            'content_body': '''# The Basic Structure of C++

Section 3.1 (p. 49) divides every C++ program into **three parts**: the **Preprocessor Directives**, the **Main Function Header** and the **Body of the Program/Function**. Fig 3.1 prints the skeleton:

```cpp
#include<iostream>
using namespace std;
int main(void)
{
    Statements;
    return 0;
}
```

Run it as it stands — the textbook's own shape of a program, and it already works:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Pakistan Zindabad";
    return 0;
}
```

**Expected output:**

```output
Pakistan Zindabad
```

## The seven lines, one by one

The book explains the skeleton line by line in a seven-row table (pp. 49-50):

- `#include<iostream>` — the `#` marks a **preprocessor directive**. It links the external header file `iostream` into your program, bringing in the code for input and output. (`#define` is the other directive, used for defining constants.)
- `using namespace std;` — a **namespace** is a collection of identifiers; `std` is the **Standard Library of C++**. This line lets you write `cout` instead of `std::cout`.
- `int main(void)` — `main()` is the function used for execution; the program starts here. The table also mentions `void main(void)`, which returns nothing.
- `{` — the opening curly brace marks where the body begins.
- `Statement;` — one instruction, ended by the **statement terminator** `;`. The example in the table is `cout << "Pakistan Zindabad";`.
- `return 0;` — the **exit code**. `main()` returns an `int` to the operating system; `0` means "finished normally".
- `}` — the closing curly brace ends the body.

## One thing to know before you copy from the book

The table offers `void main(void)` as a valid alternative. Measured with the modern C++ compiler this course runs, it is **rejected**:

```output
error: '::main' must return 'int'
```

Older teaching compilers (including the version Dev-C++ on your classroom machine may ship) accept it. Standard C++ does not. Write `int main()` and keep the `return 0;` — it works everywhere, and now you know why the two forms you will see in the book and in the sandbox differ.
''',
            'exercises': [
                {
                    'slug': 'which-header-for-io',
                    'title': 'Which Header File for Input and Output?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which header file must be included to use `cin` and `cout`?'
                    ),
                    'explain': (
                        '`#include<iostream>` links the input/output stream '
                        'library. Sindh Board Class X, Unit 3, EXERCISE A (i), p. 67.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '<iostream>', 'is_correct': True},
                        {'id': 'b', 'text': '<stdio.h>', 'is_correct': False},
                        {'id': 'c', 'text': '<conio.h>', 'is_correct': False},
                        {'id': 'd', 'text': '<math.h>', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A (i)', '67', CLASS),
                },
                {
                    'slug': 'purpose-of-using-namespace-std',
                    'title': 'What Does `using namespace std;` Do?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Why does the textbook put `using namespace std;` in the program structure?'
                    ),
                    'explain': (
                        '`std` is the Standard Library of C++ and a namespace is '
                        'a collection of identifiers; the directive lets the '
                        'program use those names such as `cout` directly. Sindh '
                        'Board Class X, Unit 3, 3.1, pp. 49-50.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'It makes the names of the Standard Library available without qualifying them', 'is_correct': True},
                        {'id': 'b', 'text': 'It reserves memory for the variables', 'is_correct': False},
                        {'id': 'c', 'text': 'It starts the program execution', 'is_correct': False},
                        {'id': 'd', 'text': 'It marks the end of every statement', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, '3.1 Basic Structure of C++', '49-50', CLASS),
                },
                {
                    'slug': 'statement-terminator',
                    'title': 'The Missing Semicolon',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'What happens if a C++ statement is not followed by a semicolon?'
                    ),
                    'context': 'Section 3.3.3, "Statement Terminator (;)", p. 56.',
                    'explain': (
                        'Every statement must end with `;`; without it the '
                        'compiler produces an error message. Sindh Board Class '
                        'X, Unit 3, 3.3.3, p. 56.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'The compiler gives an error message', 'is_correct': True},
                        {'id': 'b', 'text': 'The program runs but ignores that line', 'is_correct': False},
                        {'id': 'c', 'text': 'The statement is joined with the next one', 'is_correct': False},
                        {'id': 'd', 'text': 'The program runs twice as fast', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 3,
                    'reference': ref(UNIT, '3.3.3 Statement Terminator (;)', '56', CLASS),
                },
                {
                    'slug': 'return-zero-explained',
                    'title': 'Why `return 0;`?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'According to the structure table, what does `return 0;` at the end of `main()` mean?'
                    ),
                    'explain': (
                        '`main()` returns an `int` to the operating system; the '
                        'value it returns is the exit code of the program. Sindh '
                        'Board Class X, Unit 3, 3.1, p. 50.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'It hands the exit code of the program back to the operating system', 'is_correct': True},
                        {'id': 'b', 'text': 'It prints the number 0 on the screen', 'is_correct': False},
                        {'id': 'c', 'text': 'It restarts the program from the first line', 'is_correct': False},
                        {'id': 'd', 'text': 'It deletes the value of every variable', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 4,
                    'reference': ref(UNIT, '3.1 Basic Structure of C++', '50', CLASS),
                },
            ],
        },

        # ── 3.2 ────────────────────────────────────────────────────────────
        {
            'slug': 'comments-in-cpp',
            'title': 'Comment Statements in C++',
            'content_type': 'text',
            'learning_objective': 'Write single-line and multi-line comments that the compiler ignores.',
            'order': 2,
            'duration_minutes': 8,
            'xp_reward': 40,
            'reference': ref(UNIT, '3.2 Comment Statement in C++', '50-51', CLASS),
            'content_body': '''# Comments

A **comment** is a line of text for the reader of the program. The book states plainly (pp. 50-51) that comments are **ignored by the compiler** — they change nothing about how the program runs.

C++ has two types.

## Single line comment — `//`

Everything from `//` to the end of that line is ignored. One comment per line.

## Multi line comment — `/* ... */`

Everything between `/*` and `*/` is ignored, even across several lines.

```cpp
#include <iostream>
using namespace std;

// This program prints a greeting
// Written by a Class X student

int main() {
    /* A multi-line comment can cover
       as many lines as you need,
       and the compiler skips all of it. */

    cout << "Hello";   // this part of the line still runs
    return 0;
}
```

**Expected output:**

```output
Hello
```

Notice the last line: `// this part of the line still runs` follows real code. `cout << "Hello";` executes, and only the text after `//` is ignored.

## When to write which

- Use `//` above a statement to say what it does.
- Use `/* ... */` to temporarily switch off a block of code while you are testing, or for a longer note.

Comments are not decoration — the next unit of exercises (Unit 4 lab) asks you to explain a program's behaviour, and the students who write comments are the ones who can.
''',
            'exercises': [
                {
                    'slug': 'which-lines-are-ignored',
                    'title': 'What Does This Program Print?',
                    'exercise_type': 'output_prediction',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Read the program and write exactly what it prints.'
                    ),
                    'context': 'Section 3.2: comments are ignored by the compiler (pp. 50-51).',
                    'expected_output': 'C++',
                    'explain': (
                        'Both comment lines disappear before compiling, and the '
                        'text after `//` on the third line is ignored too. Only '
                        '`cout << "C++";` produces output. Sindh Board Class X, '
                        'Unit 3, 3.2, pp. 50-51.'
                    ),
                    'starter_code': (
                        '// Predict the output, then run it to check yourself\n'
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    // cout << "Programming";\n'
                        '    /* cout << "language"; */\n'
                        '    cout << "C++"; // the comment is not printed\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'xp_reward': 60,
                    'order': 1,
                    'reference': ref(UNIT, '3.2 Comment Statement in C++', '50-51', CLASS),
                },
                {
                    'slug': 'comment-a-program',
                    'title': 'Add Comments to an Existing Program',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'This program adds two numbers. Add one `//` comment '
                        'above the lines that matter, keeping the calculation '
                        'and the printed result exactly as they are.'
                    ),
                    'context': 'Practice for section 3.2 (pp. 50-51).',
                    'constraints': 'Do not change the statements that produce the output.',
                    'expected_behavior': 'The program still prints 30, with comments added.',
                    'explain': (
                        'A comment runs from `//` to the end of the line and is '
                        'ignored by the compiler, so the output stays 30. Sindh '
                        'Board Class X, Unit 3, 3.2.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int a = 10;\n'
                        '    int b = 20;\n'
                        '    int sum = a + b;\n'
                        '    cout << sum;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int a = 10;   // first number\n'
                        '    int b = 20;   // second number\n'
                        '    int sum = a + b;   // add them\n'
                        '    cout << sum;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '30'},
                    ],
                    'xp_reward': 80,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.2 Comment Statement in C++ — practice', '50-51', CLASS,
                        source_type='supplementary',
                    ),
                },
            ],
        },

        # ── 3.3.1 ──────────────────────────────────────────────────────────
        {
            'slug': 'output-functions-cout-and-puts',
            'title': 'Output: cout and puts()',
            'content_type': 'interactive',
            'learning_objective': (
                'Print text, expressions and variables with `cout` and `puts()`.'
            ),
            'order': 3,
            'duration_minutes': 15,
            'xp_reward': 60,
            'reference': ref(UNIT, '3.3.1 Output Function', '52', CLASS),
            'content_body': '''# Output Functions

Section 3.3 (p. 51) explains that C++ moves data through **streams**, and that the header `<iostream>` must be included at the very beginning of the program for input and output to work. Printing is handled by two functions the book gives in 3.3.1 (p. 52).

## `cout`

`cout` is a **predefined object** of the output stream class. You push things into it with the **insertion operator** `<<`. The syntax forms printed in the book:

```cpp
cout << variable;
cout << expression;
cout << string << variable;
```

The book's own example:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "MY FIRST PROGRAM";
    return 0;
}
```

**Expected output:**

```output
MY FIRST PROGRAM
```

Because `<<` can be chained, one statement can print several things one after another:

```cpp
#include <iostream>
using namespace std;

int main() {
    int marks = 85;

    cout << "Marks = " << marks;
    return 0;
}
```

**Expected output:**

```output
Marks = 85
```

Note what the quotes do: `"Marks = "` is printed exactly as written, `marks` is printed as its **value**.

## `puts()`

`puts()` prints a string and then moves to a **new line automatically**. Its syntax (p. 52):

```cpp
int puts(const char *str);
```

```cpp
#include <cstdio>

int main() {
    puts("Hello from puts");
    puts("on its own line");
    return 0;
}
```

**Expected output:**

```output
Hello from puts
on its own line
```

The return value is a number telling you whether the write succeeded, so you do not have to look at it. The book notes that `puts()` is defined in `<cstdio>`, so you include that header rather than `<iostream>` when you use it. (The Teachers Note on the same page points to `putc()`, which writes a single character.)

## Choosing between them

- Printing several values of different types in one line: `cout`, because it chains and understands numbers.
- Printing one plain string and moving to the next line: `puts()`.
''',
            'exercises': [
                {
                    'slug': 'extraction-vs-insertion',
                    'title': 'Which Operator Does `cin` Use?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        '`cout` uses the insertion operator `<<`. Which operator does `cin` use to read a value?'
                    ),
                    'explain': (
                        '`cin` is the predefined input object and uses the '
                        '**extraction** operator `>>`. Sindh Board Class X, '
                        'Unit 3, EXERCISE A (ii), p. 67.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '>>', 'is_correct': True},
                        {'id': 'b', 'text': '<<', 'is_correct': False},
                        {'id': 'c', 'text': '=', 'is_correct': False},
                        {'id': 'd', 'text': '&', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A (ii)', '67', CLASS),
                },
                {
                    'slug': 'print-a-line-with-cout',
                    'title': 'Print a Label and a Value',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Store the number `10` in an `int` variable named `a` '
                        'and print exactly: `Value is 10`'
                    ),
                    'context': 'Chaining with the insertion operator, section 3.3.1 (p. 52).',
                    'constraints': 'One `cout` statement, chained with `<<`. No trailing newline needed.',
                    'expected_behavior': 'Prints: Value is 10',
                    'explain': (
                        '`cout << "Value is " << a;` prints the string, then the '
                        'value stored in `a`. Sindh Board Class X, Unit 3, 3.3.1.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    // declare a and print "Value is 10"\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int a = 10;\n'
                        '    cout << "Value is " << a;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': 'Value is 10'},
                    ],
                    'xp_reward': 90,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.3.1 Output Function — practice', '52', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Declare the variable first: int a = 10;',
                        'Chain two pieces with << : cout << "text " << a;',
                        'Solution: cout << "Value is " << a;',
                    ],
                },
                {
                    'slug': 'puts-two-lines',
                    'title': 'Two Lines with puts()',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Using `puts()`, print the two lines `First line` and '
                        '`Second line` in that order.'
                    ),
                    'context': 'Section 3.3.1 — `puts()` adds the new line itself (p. 52).',
                    'constraints': (
                        'Use `puts()` only, and do not add any `\\n` of your own.'
                    ),
                    'expected_behavior': 'Two lines of output.',
                    'explain': (
                        '`puts()` prints the string and moves to a new line by '
                        'itself, which is why no `\\n` is needed and why one `int` '
                        'per call is not printed. Sindh Board Class X, Unit 3, '
                        '3.3.1, p. 52.'
                    ),
                    'starter_code': (
                        '#include <cstdio>\n'
                        '\n'
                        'int main() {\n'
                        '    // print the two lines with puts()\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <cstdio>\n'
                        '\n'
                        'int main() {\n'
                        '    puts("First line");\n'
                        '    puts("Second line");\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': 'First line\nSecond line'},
                    ],
                    'xp_reward': 90,
                    'order': 3,
                    'reference': ref(
                        UNIT, '3.3.1 Output Function — puts()', '52', CLASS,
                        source_type='supplementary',
                    ),
                },
            ],
        },

        # ── 3.3.2 ──────────────────────────────────────────────────────────
        {
            'slug': 'input-functions-cin-getch-getche-getchar-gets',
            'title': 'Input: cin, getch(), getche(), getchar() and gets()',
            'content_type': 'interactive',
            'learning_objective': (
                'Read numbers, single characters and whole lines from the user, '
                'and say which input function waits for the Enter key.'
            ),
            'order': 4,
            'duration_minutes': 20,
            'xp_reward': 60,
            'reference': ref(UNIT, '3.3.2 Input Function', '53-55', CLASS),
            'content_body': '''# Input Functions

Section 3.3.2 (pp. 53-55) gives five ways to bring data into a program. Choosing between them is one of the most examined things in this unit.

## 1. `cin` — the standard input object

`cin` is a **predefined object** of the input stream, and it uses the **extraction operator** `>>` to take a value out of the keyboard and put it into a variable:

```cpp
cin >> variable;
```

```cpp
#include <iostream>
using namespace std;

int main() {
    int a, b;

    cout << "Enter two numbers";
    cin >> a >> b;

    cout << a + b;
    return 0;
}
```

`>>` can be chained, so one statement can fill several variables. `cin` waits for the **Enter** key, then extracts the values in order.

Type into the box that appears when you run this, one line: `15 27`

```cpp
#include <iostream>
using namespace std;

int main() {
    int x;

    cin >> x;
    cout << x * 2;
    return 0;
}
```

**Expected output** (for the input `20`): `40`

## 2. `getch()` — one character, not echoed (pp. 53-54)

`getch()` comes from **`<conio.h>`**. It reads a **single character** from the keyboard and **does not display it** on the screen, and it **holds the output screen** until a key is pressed. It is the function the book uses when a program must pause before the window closes.

```cpp
#include <iostream>
#include <conio.h>
using namespace std;

int main() {
    char ch;

    cout << "Press any key";
    ch = getch();
    cout << "You pressed " << ch;
    return 0;
}
```

**This snippet has no Run button, on purpose.** `getch()` reads the keyboard through the console, not through the normal input stream, and the sandbox has no console — so the program would sit waiting until it timed out. Run this one in Dev-C++ instead, exactly as the textbook intends.

## 3. `getche()` — one character, echoed (p. 54)

`getche()` stands for "**get character echo**". Like `getch()` it takes one character from `<conio.h>` and returns immediately, but it **shows the character on the screen** as it is typed. The book's example asks "Do you want to continue(Y/N)..", reads the reply and prints the addition:

```cpp
#include <iostream>
#include <conio.h>
using namespace std;

int main() {
    char c;

    cout << "Do your want to continue(Y/N)..";
    c = getche();
    cout << "\nthe addition is…. 20";
    return 0;
}
```

**Expected output** (as printed in the book, after typing `Y`):

```output
Do your want to continue(Y/N)..Y
the addition is…. 20
```

Also console-only, so no Run button here either.

## 4. `getchar()` — one character from standard input (p. 54)

`getchar()` is from `<stdio.h>`. It reads **one character from the standard input** and, unlike `getch()`/`getche()`, **requires you to press Enter** before the character is passed to the program. Because it uses the ordinary input stream, it runs in the sandbox:

```cpp
#include <cstdio>

int main() {
    char ch;

    ch = getchar();
    printf("%c", ch);
    return 0;
}
```

Run it with the input `A` (then Enter) to get the output `A`.

## 5. `gets()` — a whole line of text (p. 55)

`gets()` reads characters from the standard input **until you press Enter**, storing the whole line in a character array. This is how you read a multi-word string, which plain `cin >>` cannot do (it stops at the first space).

```cpp
#include <cstdio>

int main() {
    char ch[20];

    gets(ch);
    printf("%s", ch);
    return 0;
}
```

Run it with the input `Pakistan` to get back `Pakistan`.

## The comparison the exam asks for

| Function | Header | Reads | Echoed? | Needs Enter? |
|---|---|---|---|---|
| `cin >>` | `<iostream>` | a value matching the variable's type | yes | yes |
| `getch()` | `<conio.h>` | one character | **no** | no |
| `getche()` | `<conio.h>` | one character | yes | no |
| `getchar()` | `<stdio.h>` | one character | yes | **yes** |
| `gets()` | `<stdio.h>` / `<cstdio>` | a whole line | yes | yes |

The Teachers Note on p. 55 mentions `getsc()` as an additional function to demonstrate.
''',
            'exercises': [
                {
                    'slug': 'which-header-for-getch',
                    'title': 'Which Header for getch()?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'The function `getch()` is declared in which header file?'
                    ),
                    'explain': (
                        '`getch()` comes from `conio.h` (console input/output). '
                        'Sindh Board Class X, Unit 3, EXERCISE A (iv), p. 67.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '<conio.h>', 'is_correct': True},
                        {'id': 'b', 'text': '<iostream>', 'is_correct': False},
                        {'id': 'c', 'text': '<stdio.h>', 'is_correct': False},
                        {'id': 'd', 'text': '<string>', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A (iv)', '67', CLASS),
                },
                {
                    'slug': 'purpose-of-gets',
                    'title': 'What Is gets() For?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': 'What is the `gets()` function used for?',
                    'explain': (
                        '`gets()` reads a line of characters from the standard '
                        'input into a character array — in other words, it is '
                        'used to get a string. Sindh Board Class X, Unit 3, '
                        'EXERCISE A (iii), p. 67.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'To get a string', 'is_correct': True},
                        {'id': 'b', 'text': 'To get a single number', 'is_correct': False},
                        {'id': 'c', 'text': 'To clear the screen', 'is_correct': False},
                        {'id': 'd', 'text': 'To end the program', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A (iii)', '67', CLASS),
                },
                {
                    'slug': 'echo-or-not',
                    'title': 'Which Character Does Not Show On Screen?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Which input function reads a single character **without** '
                        'displaying it on the screen?'
                    ),
                    'context': 'Section 3.3.2 contrasts getch() with getche() (pp. 53-54).',
                    'explain': (
                        '`getch()` stands for get character and does not echo the '
                        'key to the screen; `getche()` is "get character **echo**" '
                        'and does show it. Sindh Board Class X, Unit 3, 3.3.2, '
                        'pp. 53-54.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'getch()', 'is_correct': True},
                        {'id': 'b', 'text': 'getche()', 'is_correct': False},
                        {'id': 'c', 'text': 'getchar()', 'is_correct': False},
                        {'id': 'd', 'text': 'gets()', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 3,
                    'reference': ref(UNIT, '3.3.2 Input Function', '53-54', CLASS),
                },
                {
                    'slug': 'add-two-inputs',
                    'title': 'Add Two Numbers Entered by the User',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read two integers with a single `cin` statement and '
                        'print their sum.'
                    ),
                    'context': 'Section 3.3.2, `cin` with the extraction operator (pp. 53-54).',
                    'constraints': 'Print only the sum — no labels.',
                    'expected_behavior': 'For the input `12 8` it prints 20.',
                    'explain': (
                        '`cin >> a >> b;` chains the extraction operator to fill '
                        'both variables from one line of input, then '
                        '`cout << a + b;` prints the result. Sindh Board Class '
                        'X, Unit 3, 3.3.2.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int a, b;\n\n'
                        '    // read both values, then print their sum\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int a, b;\n\n'
                        '    cin >> a >> b;\n'
                        '    cout << a + b;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '12 8\n', 'expected_output': '20'},
                        {'input': '45 55\n', 'expected_output': '100'},
                    ],
                    'xp_reward': 110,
                    'order': 4,
                    'reference': ref(
                        UNIT, '3.3.2 Input Function — cin', '53', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'One statement can fill both variables: cin >> a >> b;',
                        'Then print the expression: cout << a + b;',
                    ],
                },
                {
                    'slug': 'read-a-line',
                    'title': 'Read a Whole Line of Text',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read one full line of text entered by the user and '
                        'print it back unchanged.'
                    ),
                    'context': 'Section 3.3.2 — `gets()` reads until Enter is pressed (p. 55).',
                    'constraints': (
                        'The line contains spaces, so a plain `cin >>` is not '
                        'enough. Declare a `char` array large enough for the '
                        'text.'
                    ),
                    'expected_behavior': 'It repeats exactly what was typed.',
                    'explain': (
                        '`char line[40]; gets(line); puts(line);` reads the whole '
                        'line including its spaces and prints it back. '
                        '`cin >> line` would stop at the first space. Sindh '
                        'Board Class X, Unit 3, 3.3.2, p. 55.'
                    ),
                    'starter_code': (
                        '#include <cstdio>\n'
                        '\n'
                        'int main() {\n'
                        '    // declare an array, read a line, print it back\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <cstdio>\n'
                        '\n'
                        'int main() {\n'
                        '    char line[40];\n\n'
                        '    gets(line);\n'
                        '    puts(line);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': 'Karachi Sindh\n', 'expected_output': 'Karachi Sindh'},
                    ],
                    'xp_reward': 110,
                    'order': 5,
                    'reference': ref(
                        UNIT, '3.3.2 Input Function — gets()', '55', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'You need an array of char, not a single char.',
                        'gets(line) reads up to the Enter key, and puts(line) prints it.',
                        'Solution: char line[40]; gets(line); puts(line);',
                    ],
                },
            ],
        },

        # ── 3.3.4 ──────────────────────────────────────────────────────────
        {
            'slug': 'escape-sequences',
            'title': 'Escape Sequences',
            'content_type': 'interactive',
            'learning_objective': (
                "Use \\n, \\t, \\\\, ' and \" to control spacing and quoting in output."
            ),
            'order': 5,
            'duration_minutes': 14,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.3.4 Escape Sequences', '56', CLASS),
            'content_body': '''# Escape Sequences

Escape sequences are **non-printing characters** used with `cout`. Each one starts with a **backslash** `\\` followed by a letter, and the pair means one thing (p. 56).

The table from p. 56:

- `\\a` — alert / beep
- `\\b` — backspace
- `\\t` — horizontal tab
- `\\n` — new line (line feed)
- `\\r` — carriage return
- `\\\\` — backslash
- `\\'` — single quote
- `\\"` — double quote

## Spacing inside one statement

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "C++\tProgramming\tLanguage";
    return 0;
}
```

**Expected output:**

```output
C++	Programming	Language
```

The three `\\t` produce tab stops, which is why `\\t` is used for columns instead of a run of spaces.

## Two lines from one statement

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "First line\nSecond line";
    return 0;
}
```

**Expected output:**

```output
First line
Second line
```

## Printing the characters that are normally markers

A double quote ends a string, and a backslash starts an escape sequence — so to print them you must escape them:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "She said \"Hello\"";
    cout << "\nPath: C:\\temp";
    return 0;
}
```

**Expected output:**

```output
She said "Hello"
Path: C:\temp
```

The short exercise in EXERCISE B (p. 68) asks you to use `\\a` and `\\r` in a program. `\\a` makes the machine beep, and `\\r` sends the cursor back to the start of the line — the following line therefore **overwrites** what was printed there:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "12345\r67";
    return 0;
}
```

**Expected output:** `67345` — `\\r` moves the cursor to column one, and `67` is written over `12`, leaving `67345`.
''',
            'exercises': [
                {
                    'slug': 'output-with-tab-and-newline',
                    'title': 'Predict the Output: \\t and \\n',
                    'exercise_type': 'output_prediction',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'What does this program print? Answer with the text only '
                        '(a single space where the tab is).'
                    ),
                    'expected_output': 'A B\nC',
                    'explain': (
                        '`\\t` inserts a horizontal tab and `\\n` moves to a new '
                        'line, so the output is `A<tab>B` then `C` on the next '
                        'line. Sindh Board Class X, Unit 3, 3.3.4, p. 56.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    cout << "A\\tB\\nC";\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'xp_reward': 70,
                    'order': 1,
                    'reference': ref(UNIT, '3.3.4 Escape Sequences', '56', CLASS),
                },
                {
                    'slug': 'escape-quote-and-backslash',
                    'title': 'Print Quotes and a Backslash',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Print exactly this line, including the double quotes and '
                        'the single backslash:\n\n'
                        '`Say "Hi" now\\`'
                    ),
                    'context': 'Section 3.3.4 — escaping `\\"`, `\\\\` (p. 56).',
                    'constraints': 'Use escape sequences; do not build the line out of separate strings.',
                    'expected_behavior': 'Prints: Say "Hi" now\\',
                    'explain': (
                        'A double quote inside a string is written `\\"`, and a '
                        'backslash is written `\\\\` because a single `\\` would '
                        'begin an escape sequence. Sindh Board Class X, Unit 3, '
                        '3.3.4, p. 56.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    // print: Say "Hi" now\\\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    cout << "Say \\"Hi\\" now\\\\";\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': 'Say "Hi" now\\'},
                    ],
                    'xp_reward': 110,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.3.4 Escape Sequences — practice', '56', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'The two quotes must each be written as \\"',
                        'A literal backslash needs two of them: \\\\',
                        'Solution: cout << "Say \\"Hi\\" now\\\\";',
                    ],
                },
                {
                    'slug': 'carriage-return-effect',
                    'title': 'What Does \\r Do?',
                    'exercise_type': 'output_prediction',
                    'language': 'cpp',
                    'difficulty': 'hard',
                    'instructions': (
                        'The program below writes some text, moves the cursor '
                        'back to the start of the line with `\\r`, then writes '
                        '`89`. On the screen `89` is drawn over the first two '
                        'letters. Predict the final text the learner sees '
                        'displayed on that line.'
                    ),
                    'context': (
                        'EXERCISE B (p. 68) asks for a program that uses `\\a` '
                        'and `\\r`. This checks the carriage-return behaviour: '
                        'the cursor returns to column 0 without erasing what is '
                        'already on the line, so later characters overwrite '
                        'earlier ones. (The overwrite only shows on a real '
                        'terminal, so this is a reasoning question rather than '
                        'an auto-run test.)'
                    ),
                    'expected_output': '89CDE',
                    'explain': (
                        '`\\r` returns the cursor to the beginning of the line '
                        'without erasing it, so the next characters written '
                        'replace the ones already there: `89` overwrites `AB` '
                        'and `CDE` remains, giving `89CDE`. Sindh Board Class X, '
                        'Unit 3, 3.3.4, p. 56.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    cout << "ABCDE\\r89";\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'xp_reward': 110,
                    'order': 3,
                    'reference': ref(
                        UNIT, 'EXERCISE B — use \\a and \\r', '68', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Read ABCDE first, then the cursor jumps back over A.',
                        '89 is written over the top of AB; the rest (CDE) is untouched.',
                    ],
                },
            ],
        },
    ],
}
