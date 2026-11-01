"""
UNIT 2 — BASICS OF PROGRAMMING IN C++ (printed pages 20-47).

Section outline as it is actually printed in the textbook:

    2.1 Introduction ................ p. 21
        2.1.1 Computer Program ...... p. 21  (syntax, p. 22)
        2.1.2 Classification of Programming Languages .. pp. 22-24
        2.1.3 Translators ........... pp. 25-26
        2.1.4 Types of Errors ....... pp. 27-28
    2.2 Programming Environment of C++  pp. 28-38
    2.3 C++ Programming Language .... pp. 39-41
    2.4 Constants and Variables ..... pp. 41-44
    SUMMARY ......................... pp. 44-45
    EXERCICE A (10 MCQs) / B (8 questions)  pp. 46-47
    LAB ACTIVITIES .................. p. 47

Two honesty notes about this module:

1. Unit 2 does **not** contain a section on program structure, header files,
   `main()`, operators or expressions. Those live in Unit 3. The brief's
   candidate lesson list suggested otherwise; following it would have
   published invented syllabus, so the outline above is what is implemented.

2. The multiple-choice questions are the book's own EXERCISE A items
   (pp. 46-47) — the concept, the options and the answer are as printed. The
   textbook is a scan with no text layer, so the wording is re-typed by hand
   from the page rather than copied from a file. The page reference in each
   `explain` tells a learner where to check it.
"""

from .common import ref

UNIT = 'Unit 2'
CLASS = 'Class X'

CHAPTER = {
    'slug': 'unit-2-basics-of-programming-in-cpp',
    'title': 'Unit 2 — Basics of Programming in C++',
    'description': (
        'What a program is, how languages and translators differ, the three '
        'kinds of errors, the C++ environment, and the words, types, constants '
        'and variables every C++ program is built from.'
    ),
    'order': 1,
    'xp_reward': 500,
    'reference': ref(UNIT, 'Basics of Programming in C++', '20-47', CLASS),
    'lessons': [
        # ── 2.1.1 ──────────────────────────────────────────────────────────
        {
            'slug': 'what-is-a-computer-program',
            'title': 'What Is a Computer Program?',
            'content_type': 'text',
            'learning_objective': (
                'Define a computer program, explain why syntax matters, and run '
                'a first C++ statement that prints text.'
            ),
            'order': 1,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '2.1.1 Computer Program', '21-22', CLASS),
            'content_body': '''# What Is a Computer Program?

The textbook defines a computer program as a **collection of instructions** that tells a computer what to do. A computer has no judgement of its own: it carries out exactly what you write, in the order you write it, and it stops when the instructions run out.

That definition has two halves worth remembering for the exam:

- **Instruction** — one single step the computer can perform.
- **Collection** — the steps are put together, and their order is part of the program.

## Syntax is the grammar of a language

Natural languages let you say "hello" or "hi" and still be understood. Programming languages do not. Every statement must follow the exact rules of the language, or the translator refuses it. The book calls these rules the **syntax** of the programming language.

The first C++ statement almost everyone meets prints a message:

```cpp
cout << "Hello World";
```

Read it as three pieces:

- `cout` — the standard output stream, the "console outlet" the book uses for printing.
- `<<` — the insertion operator, which pushes whatever is on its right into `cout`.
- `"Hello World"` — a string: text held inside double quotes.

Two details decide whether this compiles: `cout` is spelled with a small **c**, and the statement is finished with a **semicolon**. The book's own example is written without the semicolon on p. 22 because it is showing the printing statement by itself; a real program must terminate every statement with `;` (that rule is taught formally in Unit 3, section 3.3.3).

## Why the machine needs a translator

A computer's own hardware only understands patterns of 0s and 1s. `cout << "Hello World";` is human-readable; the machine cannot execute it directly. Something has to convert the program into machine instructions — and what does the converting is called a **translator** (section 2.1.3, next lesson but one).

## Check the idea before moving on

- A program is a *collection of instructions*, not a single instruction.
- Syntax errors happen because the rules are exact, not flexible.
- Text inside double quotes is a string; the quotes are not printed.
''',
            'exercises': [
                {
                    'slug': 'print-a-message',
                    'title': 'Print a Message of Your Own',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'The starter program prints "Hello World". Change the '
                        'text so that the program prints exactly: '
                        'I am learning C++'
                    ),
                    'context': (
                        'Section 2.1.1 introduces `cout << "Hello World";` as '
                        'the syntax example. This applies the same statement to '
                        'different text.'
                    ),
                    'constraints': (
                        'Use `cout` with the insertion operator `<<`, keep the '
                        'semicolon, and print nothing else — no extra words, '
                        'spaces or punctuation.'
                    ),
                    'expected_behavior': 'The program prints exactly: I am learning C++',
                    'explain': (
                        'The string inside the double quotes is copied to the '
                        'output exactly as written. `cout` performs the printing '
                        'and `<<` inserts the string into the output stream. '
                        'Sindh Board Class X, Unit 2, 2.1.1, p. 22.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    // Replace the text inside the quotes\n'
                        '    cout << "Hello World";\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    cout << "I am learning C++";\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'expected_output': 'I am learning C++',
                    'test_cases': [
                        {'input': '', 'expected_output': 'I am learning C++'},
                    ],
                    'xp_reward': 100,
                    'order': 1,
                    'reference': ref(
                        UNIT, '2.1.1 Computer Program — syntax', '22', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Keep the statement exactly as it is and change only the text between the double quotes.',
                        'The quotes themselves are not printed — they only mark where the text starts and ends.',
                        'Solution: cout << "I am learning C++";',
                    ],
                },
                {
                    'slug': 'program-is-a-collection',
                    'title': 'A Program Is a Collection of …',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'According to section 2.1.1, a computer program is a '
                        'collection of what?'
                    ),
                    'explain': (
                        'The textbook defines a computer program as a '
                        'collection of instructions that a computer can carry '
                        'out. Sindh Board Class X, Unit 2, EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Instructions', 'is_correct': True},
                        {'id': 'b', 'text': 'Languages', 'is_correct': False},
                        {'id': 'c', 'text': 'Translators', 'is_correct': False},
                        {'id': 'd', 'text': 'Screens', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
            ],
        },

        # ── 2.1.2 ──────────────────────────────────────────────────────────
        {
            'slug': 'classification-of-programming-languages',
            'title': 'Low-Level, Middle-Level and High-Level Languages',
            'content_type': 'text',
            'learning_objective': (
                'Classify programming languages by level and explain what each '
                'level is readable by.'
            ),
            'order': 2,
            'duration_minutes': 14,
            'xp_reward': 50,
            'reference': ref(UNIT, '2.1.2 Classification of Programming Languages', '22-24', CLASS),
            'content_body': '''# Low-Level, Middle-Level and High-Level Languages

The book classifies programming languages into three groups by how close they are to the machine.

## Low-Level Languages (pp. 22-23)

Two kinds:

- **Machine-level language (1GL)** — pure binary codes, 0s and 1s. This is the only language the processor understands directly, so it is **easily readable by machines** and extremely hard for people to write. Every instruction is a number.
- **Assembly language (2GL)** — replaces those numbers with short mnemonics such as `ADD` or `MOV`, so a programmer can write in abbreviations instead of raw binary. It still maps one-to-one onto machine instructions and still needs an assembler to be translated.

## Middle-Level Languages (p. 23)

The textbook lists a middle category for languages that sit between assembly and high level — closer to the machine than Python, but easier to write than assembly. It states plainly that these languages **became obsolete and are not used anymore**. Treat this as a definition you may be asked in a short question, not as something to go and install.

## High-Level Languages (p. 24)

Languages such as C, C++, Java and Python. They read close to English, so they are **easily readable by humans** — and for that reason they cannot be run directly by the machine. A translator converts them first.

Advantages the book gives for high-level languages:

- Easy to write, read and understand.
- Portable — the same source can be used on different machines.
- Fewer errors, and quicker to develop and debug.
- No detailed knowledge of the hardware required.

## The comparison the exam asks for

| | Low-level | High-level |
|---|---|---|
| Readable by | the machine directly | humans; needs a translator |
| Speed of execution | fast, no translation step | slower, must be translated |
| Effort to write | high, error-prone | low, close to English |
| Portability | machine-specific | portable across machines |
| Example | machine code, assembly | C++, Java, Python |
''',
            'exercises': [
                {
                    'slug': 'high-level-readable-by-humans',
                    'title': 'Why Is a High-Level Language Called High-Level?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'What makes a language a high-level programming language?'
                    ),
                    'explain': (
                        'High-level languages are built around English-like '
                        'syntax, which makes them easily readable by humans; '
                        'they must be translated before the machine can run '
                        'them. Sindh Board Class X, Unit 2, EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Its syntax is easily readable by humans', 'is_correct': True},
                        {'id': 'b', 'text': 'It is executed directly by the processor', 'is_correct': False},
                        {'id': 'c', 'text': 'It uses only binary digits', 'is_correct': False},
                        {'id': 'd', 'text': 'It works on one specific machine only', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'low-level-readable-by-machines',
                    'title': 'Which Kind Is Easily Readable by Machines?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which type of programming language is easily readable by machines?'
                    ),
                    'explain': (
                        'Machine-level (low-level) language is made of binary '
                        'codes, which is exactly what the processor '
                        'understands. Sindh Board Class X, Unit 2, '
                        'EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Low-level language', 'is_correct': True},
                        {'id': 'b', 'text': 'High-level language', 'is_correct': False},
                        {'id': 'c', 'text': 'Any language written in English words', 'is_correct': False},
                        {'id': 'd', 'text': 'A language used only inside an IDE', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'name-five-high-level-languages',
                    'title': 'Five Common High-Level Languages',
                    'exercise_type': 'multiple_select',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Select every option that is a high-level programming language.'
                    ),
                    'context': (
                        'Short question 2 of Unit 2 EXERCISE B (p. 47) asks for '
                        'five common high-level languages. This checks that you '
                        'can separate them from the low-level ones.'
                    ),
                    'explain': (
                        'C, C++, Java and Python are high-level languages. '
                        'Machine code and assembly are the low-level ones, and '
                        'an interpreter is a translator rather than a language. '
                        'Sindh Board Class X, Unit 2, 2.1.2 and EXERCISE B, p. 47.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'C', 'is_correct': True},
                        {'id': 'b', 'text': 'C++', 'is_correct': True},
                        {'id': 'c', 'text': 'Python', 'is_correct': True},
                        {'id': 'd', 'text': 'Java', 'is_correct': True},
                        {'id': 'e', 'text': 'Machine code', 'is_correct': False},
                        {'id': 'f', 'text': 'Assembly language', 'is_correct': False},
                    ],
                    'xp_reward': 60,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE B — Q2', '47', CLASS),
                },
            ],
        },

        # ── 2.1.3 ──────────────────────────────────────────────────────────
        {
            'slug': 'translators-compiler-interpreter-assembler',
            'title': 'Translators: Compiler, Interpreter, Assembler',
            'content_type': 'text',
            'learning_objective': (
                'Name the three types of translator and explain the difference '
                'between a compiler and an interpreter.'
            ),
            'order': 3,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '2.1.3 Translators', '25-26', CLASS),
            'content_body': '''# Translators

Your source code is not executable. The program that converts it into machine instructions is called a **translator**, and the book gives its role on p. 25: it takes the **source code** you write and produces the machine-level code the processor can run. The result of that translation is **object code**.

Three types are listed (p. 26).

## 1. Compiler

Translates the **whole program in one go**. It reads the complete source file, reports every error it finds, and only then produces an object program that can be executed. Because the translation is finished before the program runs, a compiled program executes quickly — but every change means compiling again.

C++ is compiled. That is exactly why the Run button in this course shows you compiler errors before anything executes.

## 2. Interpreter

Translates and executes **one line at a time**. It stops at the first line that has an error, so a program with a mistake on line 40 runs its first 39 lines before failing. Convenient for testing and for learning, but slower overall because translation happens while the program runs.

## 3. Assembler

Translates **assembly language** (mnemonics such as `ADD`, `MOV`) into machine code. It belongs to the low-level world, not to C++.

## The distinction the exercise tests

| | Compiler | Interpreter |
|---|---|---|
| How much at a time | the entire program | one statement |
| Error reporting | all errors after scanning | stops at the first bad line |
| Output | a saved object/executable | runs immediately, usually no saved program |
| Speed of running | faster | slower |

- A **compiler** translates all at once.
- An **interpreter** translates line by line.
''',
            'exercises': [
                {
                    'slug': 'compiler-translates-all-at-once',
                    'title': 'Which Translator Works on the Whole Program?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which type of translator translates the entire source program at once?'
                    ),
                    'explain': (
                        'A compiler scans the complete program before producing '
                        'object code. Sindh Board Class X, Unit 2, EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Compiler', 'is_correct': True},
                        {'id': 'b', 'text': 'Interpreter', 'is_correct': False},
                        {'id': 'c', 'text': 'Assembler', 'is_correct': False},
                        {'id': 'd', 'text': 'Editor', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'interpreter-line-by-line',
                    'title': 'Line-by-Line Translation',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which translator reads and executes a program one line at a time?'
                    ),
                    'explain': (
                        'An interpreter translates each statement and executes '
                        'it before moving to the next, stopping at the first '
                        'line containing an error. Sindh Board Class X, Unit 2, '
                        'EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Interpreter', 'is_correct': True},
                        {'id': 'b', 'text': 'Compiler', 'is_correct': False},
                        {'id': 'c', 'text': 'Assembler', 'is_correct': False},
                        {'id': 'd', 'text': 'Linker', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'source-code-vs-object-code',
                    'title': 'Source Code and Object Code',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'What is the program that a translator produces from your source code called?'
                    ),
                    'context': (
                        'Short question 7 of EXERCISE B (p. 47) asks for the '
                        'difference between source code and object code.'
                    ),
                    'explain': (
                        'What you write is source code; the machine-level '
                        'output of translation is object code. Sindh Board '
                        'Class X, Unit 2, 2.1.3 and EXERCISE B, p. 47.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Object code', 'is_correct': True},
                        {'id': 'b', 'text': 'Source code', 'is_correct': False},
                        {'id': 'c', 'text': 'Comment code', 'is_correct': False},
                        {'id': 'd', 'text': 'Reserved code', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE B — Q7', '47', CLASS),
                },
            ],
        },

        # ── 2.1.4 ──────────────────────────────────────────────────────────
        {
            'slug': 'types-of-errors',
            'title': 'Syntax, Run-Time and Logic Errors',
            'content_type': 'interactive',
            'learning_objective': (
                'Tell a syntax error, a run-time error and a logic error apart, '
                'and recognise the most frequent syntax mistakes.'
            ),
            'order': 4,
            'duration_minutes': 15,
            'xp_reward': 60,
            'reference': ref(UNIT, '2.1.4 Types of Errors', '27-28', CLASS),
            'content_body': '''# Types of Errors

The book groups errors into three types (pp. 27-28). Knowing which type you are facing is most of the fixing.

## 1. Syntax Error

A **violation of the grammar rules** of the language. The compiler refuses the program and tells you the line. The text names the most frequent causes:

- A missing parenthesis `()`.
- Printing a variable that was never declared.
- A missing semicolon.

Syntax errors are caught **before** anything runs — that is why the Run button in this course shows a compiler message instead of an output panel. Every C++ statement must end with `;`.

## 2. Run-Time Error

The program compiles cleanly, then crashes **while executing**. The book's example is **division by zero**: perfectly legal syntax, and the machine cannot perform the calculation, so the program terminates abnormally.

## 3. Logic Error

The hardest kind, because **nothing stops**. The program compiles, runs, ends without any message and produces the **wrong answer**. The example in the text: a program that should average three numbers but divides the total by 5 instead of 3. The output looks reasonable, so only a person who knows what the answer should be will notice.

The consequence for you as a developer: always test your program with values whose correct result you already know.

## What a compiler really tells you

Compile and run this program, then read the message under the code carefully:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Missing semicolon"
    return 0;
}
```

**Expected output:** a compiler **error** naming the line, because the statement is not terminated with `;`. Nothing is printed — a syntax error stops the program before it can run at all.

## The one that no compiler can catch

```cpp
#include <iostream>
using namespace std;

int main() {
    int a, b, c;
    float average;

    a = 10;
    b = 20;
    c = 30;

    average = (a + b + c) / 5;   // should divide by 3

    cout << average;
    return 0;
}
```

**Expected output:** `12` — the correct average of 10, 20 and 30 is `20`. The program is syntactically perfect and reports no error at all. This is a **logic error**, exactly the kind the textbook describes: it must be detected by the user who knows what the answer should be.
''',
            'exercises': [
                {
                    'slug': 'find-the-syntax-error',
                    'title': 'Find the Syntax Error',
                    'exercise_type': 'debugging',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'This program does not compile. Run it, read the '
                        'compiler message, and correct the single mistake the '
                        'textbook lists as the most common one.'
                    ),
                    'context': (
                        'Section 2.1.4 names a missing semicolon as one of the '
                        'most frequent syntax errors (p. 27).'
                    ),
                    'constraints': 'Change only the error. Do not rewrite the program.',
                    'expected_behavior': 'The program compiles and prints: My first program',
                    'explain': (
                        'Every C++ statement must be terminated with a '
                        'semicolon. `cout << "My first program"` without `;` '
                        'is a syntax error, caught by the compiler before '
                        'anything runs. Sindh Board Class X, Unit 2, 2.1.4, p. 27.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    cout << "My first program"\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    cout << "My first program";\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': 'My first program'},
                    ],
                    'xp_reward': 100,
                    'order': 1,
                    'reference': ref(UNIT, '2.1.4 Types of Errors — Syntax error', '27', CLASS),
                    'hints': [
                        'Run the program first and read which line the compiler complains about.',
                        'A statement in C++ is not finished until you put a ; at the end of it.',
                        'Solution: cout << "My first program";',
                    ],
                },
                {
                    'slug': 'logic-error-average',
                    'title': 'Why Does This Average Look Wrong?',
                    'exercise_type': 'multiple_choice',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'A program adds three numbers and then divides the sum '
                        'by 5 to get the average. It compiles, runs and prints '
                        'a result without any error message. What kind of '
                        'error is this?'
                    ),
                    'explain': (
                        'Nothing fails, yet the answer is wrong: the divisor is '
                        'incorrect. That is a logic error, and the textbook '
                        'notes logic errors are the ones users must detect '
                        'themselves. Sindh Board Class X, Unit 2, 2.1.4, p. 28 '
                        'and EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Logic error', 'is_correct': True},
                        {'id': 'b', 'text': 'Syntax error', 'is_correct': False},
                        {'id': 'c', 'text': 'Run-time error', 'is_correct': False},
                        {'id': 'd', 'text': 'Compiler error', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'divide-by-zero-type',
                    'title': 'Division by Zero',
                    'exercise_type': 'multiple_choice',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'A program compiles successfully and then crashes while '
                        'it is executing because it tries to divide a number by '
                        'zero. Which type of error is this?'
                    ),
                    'explain': (
                        'The mistake cannot be found before execution: the '
                        'program is valid syntax, and the failure only happens '
                        'when the dividing instruction is actually performed — '
                        'the textbook\'s own example of a run-time error. Sindh '
                        'Board Class X, Unit 2, 2.1.4, p. 27.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Run-time error', 'is_correct': True},
                        {'id': 'b', 'text': 'Syntax error', 'is_correct': False},
                        {'id': 'c', 'text': 'Logic error', 'is_correct': False},
                        {'id': 'd', 'text': 'Translator error', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 3,
                    'reference': ref(UNIT, '2.1.4 Types of Errors — Run-Time error', '27', CLASS),
                },
            ],
        },

        # ── 2.2 ────────────────────────────────────────────────────────────
        {
            'slug': 'the-programming-environment-ide',
            'title': 'The C++ Programming Environment and IDE',
            'content_type': 'text',
            'learning_objective': (
                'Describe an IDE and its components, and explain what the '
                'compiler, linker, loader and debugger each do.'
            ),
            'order': 5,
            'duration_minutes': 13,
            'xp_reward': 50,
            'reference': ref(UNIT, '2.2 Programming Environment of C++', '28-38', CLASS),
            'content_body': '''# The Programming Environment of C++

Writing source code is only half of the job; the code has to be edited, translated, connected and started. Section 2.2 (p. 28) describes the tools that do that.

## Integrated Development Environment (p. 29)

An **IDE** puts the programs a developer needs into one application, so you do not have to run each tool separately in the right order. The textbook names **Dev-C++**, **Eclipse** and **VS Code** as environments used for C++.

Its list of benefits:

- One window for editing, translating and running.
- The tools are already configured to work together.
- Errors are shown next to the code that caused them.
- Faster development, because steps that used to be manual are automated.

## Components of an IDE (pp. 29-31)

Each of these is a separate program that the IDE drives for you:

- **Editor (Editing Source Code)** — where you type and save the `.cpp` file, with colour-coded text.
- **Syntax Highlighting** — colours keywords, strings and numbers so a missing quote or semicolon stands out while you type.
- **Code completion** — the IDE proposes the rest of a word or statement once you have begun it.
- **Compiler** — translates the whole source program into object code, and reports syntax errors.
- **Linker** — joins your object code with the machine code of the library functions you used (for example the code behind `cout`) into one executable.
- **Loader** — places the executable into memory and starts it running.
- **Debugger** — runs the program under your control, one step at a time, so you can watch values and find logic errors.

So the chain to a running program is: **edit → compile → link → load → run**.

## Dev-C++ (2.2.3, pp. 31-38)

The textbook then walks through Dev-C++ itself with screenshots: downloading and installing it, creating a new source file, saving it with a `.cpp` extension, writing a `Hello world!` program (Fig 2.5, p. 35), then compiling and running it with the F11 key, and reading the output screen. Lab Activity 1 of this unit (p. 47) is: *in groups, students download, install and configure Dev-C++.*

That installation is deliberately not simulated here — a browser tab is not a compiler desktop. This course executes your C++ with a real `g++` compiler on the server instead, which follows the same edit → compile → link → run chain.
''',
            'exercises': [
                {
                    'slug': 'what-an-ide-facilitates',
                    'title': 'What Does an IDE Facilitate?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'An Integrated Development Environment facilitates which of these?'
                    ),
                    'explain': (
                        'The IDE bundles the editor, the translator and the '
                        'tools that run and debug the program, so the '
                        'developer works in one place. Sindh Board Class X, '
                        'Unit 2, EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Writing the source code only', 'is_correct': False},
                        {'id': 'b', 'text': 'Compiling the program only', 'is_correct': False},
                        {'id': 'c', 'text': 'All of the above — editing, compiling, running and debugging in one application', 'is_correct': True},
                        {'id': 'd', 'text': 'Designing the computer hardware', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'match-the-ide-components',
                    'title': 'Which Component Does What?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Which IDE component joins your object code with the '
                        'library code it needs in order to produce a single '
                        'executable program?'
                    ),
                    'context': 'Section 2.2.2 lists the components of an IDE (pp. 29-31).',
                    'explain': (
                        'The compiler makes object code; the **linker** connects '
                        'that object code with library routines; the loader then '
                        'puts the executable into memory. Sindh Board Class X, '
                        'Unit 2, 2.2.2, pp. 29-31.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Linker', 'is_correct': True},
                        {'id': 'b', 'text': 'Editor', 'is_correct': False},
                        {'id': 'c', 'text': 'Loader', 'is_correct': False},
                        {'id': 'd', 'text': 'Debugger', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, '2.2.2 Components of IDE', '30', CLASS),
                },
                {
                    'slug': 'four-advantages-of-ide',
                    'title': 'Four Advantages of an IDE',
                    'exercise_type': 'multiple_select',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Select the advantages of using an IDE that this unit lists.'
                    ),
                    'context': 'Short question 8 of EXERCISE B (p. 47) asks for four advantages of an IDE.',
                    'explain': (
                        'Editing, compiling and running in one place, automatic '
                        'error reporting and faster development are all IDE '
                        'benefits in 2.2.1. An IDE does **not** remove the need '
                        'to think about logic, and it does not make the '
                        'computer faster. Sindh Board Class X, Unit 2, 2.2.1 and '
                        'EXERCISE B, p. 47.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Editing, compiling and running from a single application', 'is_correct': True},
                        {'id': 'b', 'text': 'Syntax highlighting and code completion that reduce mistakes', 'is_correct': True},
                        {'id': 'c', 'text': 'Errors reported next to the code that caused them', 'is_correct': True},
                        {'id': 'd', 'text': 'Faster program development', 'is_correct': True},
                        {'id': 'e', 'text': 'It removes the need to find logic errors', 'is_correct': False},
                        {'id': 'f', 'text': 'It makes the processor execute programs faster', 'is_correct': False},
                    ],
                    'xp_reward': 60,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE B — Q8', '47', CLASS),
                },
            ],
        },

        # ── 2.3 ────────────────────────────────────────────────────────────
        {
            'slug': 'c-plus-plus-reserved-words-and-data-types',
            'title': 'C++ Reserved Words and Data Types',
            'content_type': 'text',
            'learning_objective': (
                'Explain what a reserved word is and choose the correct C++ '
                'data type for a value.'
            ),
            'order': 6,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, '2.3 C++ Programming Language', '39-41', CLASS),
            'content_body': '''# C++ Programming Language

Section 2.3 (p. 39) describes C++ as a **general-purpose** language that is an **enhancement of C** and supports **object-oriented programming**. The textbook attributes it to **Bjarne Stroustrup**.

## Reserved words (2.3.1, pp. 39-40)

**Reserved words** (also called *keywords*) are the words that belong to the language itself. Their meaning is fixed, and you may **not** use them as names for your own variables or functions.

The numbers the book gives — and expects in a short question:

- **95** reserved words in C++.
- **32** of them were carried over from C.
- **30** are new to C++.

Words you already met are in that set: `int`, `float`, `char`, `return`, `using`, `namespace`, `const`, `if`, `else`, `while`, `for`, `switch`, `case`, `break`, `continue`, `void`, `class`.

Trying to name a variable `int` is a syntax error, because the compiler reads that word as a type and not as a name:

```cpp
#include <iostream>
using namespace std;

int main() {
    int int = 5;      // ERROR: int is a reserved word
    return 0;
}
```

**Expected output:** a compiler error. `int` cannot be a variable name.

## Data types (2.3.2, pp. 40-41)

A **data type** says what kind of value a variable holds and how much memory it occupies. The book's table on p. 41:

| Data type | Keyword | Size | Range / what it holds |
|---|---|---|---|
| Boolean | `bool` | 1 byte | `0` (false) or `1` (true) |
| Character | `char` | 1 byte | -127 to 127, or 0 to 255 |
| Integer | `int` | 4 bytes | -2147483648 to 2147483647 |
| Floating point | `float` | 4 bytes | 1.5e-45 to 3.4e38, 7 decimal digits |
| Double floating point | `double` | 8 bytes | 5.0e-345 to 1.7e308, 15 decimal digits |

Choosing the type is not decoration. Store `3.14159` in an `int` and you lose everything after the point. Store a student's roll number in a `float` and you get `45` displayed as `45.000000`.

Run this program to see all five types declared together:

```cpp
#include <iostream>
using namespace std;

int main() {
    int marks = 85;
    float percentage = 85.5;
    char grade = 'A';
    double distance = 12345678.9012;
    bool passed = true;

    cout << "marks=" << marks;
    cout << " percentage=" << percentage;
    cout << " grade=" << grade;
    cout << " distance=" << distance;
    cout << " passed=" << passed;
    return 0;
}
```

**Expected output:**

```output
marks=85 percentage=85.5 grade=A distance=1.23457e+07 passed=1
```

`passed` prints as `1` because a `bool` is stored as 0 or 1.
''',
            'exercises': [
                {
                    'slug': 'how-many-reserved-words',
                    'title': 'How Many Reserved Words in C++?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'How many reserved words does the textbook state C++ has, '
                        'and how many were carried over from C?'
                    ),
                    'explain': (
                        'Section 2.3.1: C++ has 95 reserved words, of which 32 '
                        'were taken from C and 30 are new to C++. Sindh Board '
                        'Class X, Unit 2, pp. 39-40.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '95 in total, 32 from C', 'is_correct': True},
                        {'id': 'b', 'text': '32 in total, all new to C++', 'is_correct': False},
                        {'id': 'c', 'text': '30 in total, 95 from C', 'is_correct': False},
                        {'id': 'd', 'text': '128 in total, 64 from C', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '2.3.1 Reserved Words', '39-40', CLASS),
                },
                {
                    'slug': 'bool-stores',
                    'title': 'What Does a bool Store?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': 'What can a `bool` variable store?'
                    ,
                    'explain': (
                        'A `bool` occupies 1 byte and stores 0 (false) or 1 '
                        '(true). Sindh Board Class X, Unit 2, EXERCISE A, p. 46 '
                        'and the data type table on p. 41.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'true or false', 'is_correct': True},
                        {'id': 'b', 'text': 'any whole number', 'is_correct': False},
                        {'id': 'c', 'text': 'a single character', 'is_correct': False},
                        {'id': 'd', 'text': 'a very large decimal number', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'largest-data-type',
                    'title': 'Which Type Reserves the Most Memory?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which of these C++ data types needs the most memory?'
                    ),
                    'explain': (
                        '`double` occupies 8 bytes, against 4 for `int` and '
                        '`float` and 1 for `char` and `bool`. Sindh Board '
                        'Class X, Unit 2, EXERCISE A, p. 46 (table on p. 41).'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'double floating point', 'is_correct': True},
                        {'id': 'b', 'text': 'integer', 'is_correct': False},
                        {'id': 'c', 'text': 'floating point', 'is_correct': False},
                        {'id': 'd', 'text': 'character', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'declare-one-of-each-type',
                    'title': 'Declare One Variable of Each Type',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Declare one `int`, one `float`, one `char` and one '
                        '`bool`, give each a value, and print all four on one '
                        'line separated by single spaces, in that order.'
                    ),
                    'context': (
                        'Practice for the data type table in section 2.3.2 (p. 41).'
                    ),
                    'constraints': (
                        'Print the four values separated by spaces and nothing else.'
                    ),
                    'expected_behavior': 'For example: 25 3.5 A 1',
                    'explain': (
                        'Each variable must be declared with the type that '
                        'matches its value. A `bool` prints as 1 for true. '
                        'Sindh Board Class X, Unit 2, 2.3.2, pp. 40-41.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    // Declare age (int), weight (float), grade (char) and passed (bool)\n'
                        '    // then print them separated by spaces\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int age = 25;\n'
                        '    float weight = 3.5;\n'
                        "    char grade = 'A';\n"
                        '    bool passed = true;\n\n'
                        '    cout << age << " " << weight << " " << grade << " " << passed;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '25 3.5 A 1'},
                    ],
                    'xp_reward': 120,
                    'order': 4,
                    'reference': ref(
                        UNIT, '2.3.2 C++ Data Types — practice', '40-41', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Declare each variable with its own type: int age = 25;',
                        "A character literal uses single quotes: char grade = 'A';",
                        'Join the values with cout << a << " " << b; and so on.',
                    ],
                },
            ],
        },

        # ── 2.4 ────────────────────────────────────────────────────────────
        {
            'slug': 'constants-and-variables',
            'title': 'Constants, Variables and How to Name Them',
            'content_type': 'interactive',
            'learning_objective': (
                'Declare and initialise variables, define constants with const '
                'and #define, and apply the six naming rules.'
            ),
            'order': 7,
            'duration_minutes': 18,
            'xp_reward': 60,
            'reference': ref(UNIT, '2.4 Constants and Variables', '41-44', CLASS),
            'content_body': '''# Constants and Variables

Section 2.4 (p. 41) splits stored values into two kinds.

## Constants (2.4.1, pp. 41-42)

A **constant** is a value that cannot change while the program runs. The book names two forms:

- **Literal constant** — the value is written directly in the code: `21`, `12.34`, `'A'`, `"Hello world!"`, `false`, `null`.
- **Defined constant** — you give the value a name and the program uses the name.

Two ways to define a constant in C++:

```cpp
#include <iostream>
using namespace std;

#define MAX_MARKS 100

int main() {
    const float PI = 3.14159;
    float marks = 78.5;

    cout << "PI=" << PI;
    cout << " MAX=" << MAX_MARKS;
    cout << " percent=" << (marks / MAX_MARKS) * 100;
    return 0;
}
```

**Expected output:**

```output
PI=3.14159 MAX=100 percent=78.5
```

- `const float PI = 3.14159;` declares a typed constant; the compiler protects it from being changed.
- `#define MAX_MARKS 100` is a **preprocessor** instruction: the text `MAX_MARKS` is replaced by `100` before compiling even starts.

Convention: constant names are written in **ALL CAPS**, which is why both examples above are uppercase.

## Variables (2.4.1-2.4.3, pp. 42-43)

A **variable** is a named location in memory whose value may change. The text shows it with the same name holding two different values at different times:

```cpp
x = 5;
x = 37;      // perfectly legal — the old value is replaced
```

**Declaring** creates the variable; **initialising** gives it its first value at the same time (p. 43):

```cpp
data_type variable_name;              // declaring
data_type variable_name = value;      // declaring and initialising
```

```cpp
#include <iostream>
using namespace std;

int main() {
    int a;                 // declared, no value yet
    int b = 20;            // declared and initialised
    a = 10;                // assigned afterwards

    cout << a + b;
    return 0;
}
```

**Expected output:** `30`

That is the difference short question 6 of the exercise asks for: declaring reserves the storage, initialising also supplies the first value.

## Rules for naming variables (2.4.2, p. 43)

All six, as printed:

1. Names may contain **letters, digits and the underscore** `_` only.
2. A name **must begin with a letter or an underscore**, never a digit.
3. Names are **case sensitive** — `myVar` and `myvar` are two different variables.
4. No whitespace or special symbols such as `!`, `#`, `%`.
5. **Reserved words cannot be used as names.**
6. By default a name may be up to **32 characters** long.

So `rollNo`, `_total`, `marks_2024` and `myVar` are legal; `2ndPlace`, `my marks`, `total%`, `first-name` and `int` are not.

## Strings in C++ (p. 44)

A `string` holds text of variable length. The book notes that `string` is **not a fundamental data type** — it comes from the C++ string class — and that a string variable can be declared without giving it an initial value. It is normally written with `<string>` included and used like `string name;` (input and output of strings are taught properly in Unit 3).
''',
            'exercises': [
                {
                    'slug': 'allowed-variable-names',
                    'title': 'Which Names Are Allowed?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'According to the rules for naming variables, which characters may a C++ variable name contain?'
                    ),
                    'explain': (
                        'Letters, digits and underscores — and the name must '
                        'start with a letter or an underscore. Sindh Board '
                        'Class X, Unit 2, 2.4.2 (p. 43) and EXERCISE A, p. 46.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Letters, digits and underscores', 'is_correct': True},
                        {'id': 'b', 'text': 'Letters, digits and any symbols', 'is_correct': False},
                        {'id': 'c', 'text': 'Letters and spaces only', 'is_correct': False},
                        {'id': 'd', 'text': 'Digits only, up to 32 of them', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A', '46', CLASS),
                },
                {
                    'slug': 'which-names-are-legal',
                    'title': 'Sort Legal from Illegal Names',
                    'exercise_type': 'multiple_select',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Select every identifier that follows all six naming rules.'
                    ),
                    'context': 'Section 2.4.2, rules on p. 43.',
                    'explain': (
                        'Legal: `_total`, `marks_2024`, `myVar`. Illegal: '
                        '`2ndPlace` starts with a digit, `my marks` contains a '
                        'space, and `float` is a reserved word. Sindh Board '
                        'Class X, Unit 2, 2.4.2, p. 43.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '_total', 'is_correct': True},
                        {'id': 'b', 'text': 'marks_2024', 'is_correct': True},
                        {'id': 'c', 'text': 'myVar', 'is_correct': True},
                        {'id': 'd', 'text': '2ndPlace', 'is_correct': False},
                        {'id': 'e', 'text': 'my marks', 'is_correct': False},
                        {'id': 'f', 'text': 'float', 'is_correct': False},
                    ],
                    'xp_reward': 60,
                    'order': 2,
                    'reference': ref(UNIT, '2.4.2 Rules for Naming Variables', '43', CLASS),
                },
                {
                    'slug': 'declare-vs-initialise',
                    'title': 'Declaring and Initialising Together',
                    'exercise_type': 'fill_blank',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Complete the line that both declares the variable '
                        '`age` and gives it its first value of 17. Write only '
                        'the missing statement, without the semicolon.'
                    ),
                    'context': 'Section 2.4.3 gives the two syntax forms on p. 43.',
                    'expected_behavior': 'int age = 17',
                    'explain': (
                        '`data_type variable_name = value;` declares and '
                        'initialises in one statement. `int age;` alone would '
                        'only declare it. Sindh Board Class X, Unit 2, 2.4.3, p. 43.'
                    ),
                    'starter_code': '// _________;\n',
                    'solution_code': 'int age = 17',
                    'xp_reward': 60,
                    'order': 3,
                    'reference': ref(UNIT, '2.4.3 Declaring and Initializing Variables', '43', CLASS),
                    'hints': [
                        'You need the type first, then the name, then = and the value.',
                        'The type for a whole number of years is int.',
                        'Solution: int age = 17',
                    ],
                },
                {
                    'slug': 'speed-program',
                    'title': 'Compute Speed from Distance and Time',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Write a program that stores distance `d = 150` and '
                        'time `t = 30` in variables and prints the speed '
                        '`s = d / t`.'
                    ),
                    'context': (
                        'Formula programs of this kind are the Unit 3 Lab '
                        'Activity 1 set, and they need the variables and '
                        'operators taught in Units 2 and 3.'
                    ),
                    'constraints': 'Print only the number that results from the calculation.',
                    'expected_behavior': 'The program prints 5.',
                    'explain': (
                        'Declare `float d = 150, t = 30;` and print `d / t`. '
                        'Using `int` for both operands would still give 5 here, '
                        'but a float division is what keeps the answer correct '
                        'for distances that do not divide evenly.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    // d = 150, t = 30, print d / t\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    float d = 150, t = 30;\n'
                        '    float s = d / t;\n\n'
                        '    cout << s;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '5'},
                    ],
                    'xp_reward': 120,
                    'order': 4,
                    'reference': ref(
                        UNIT, '2.4 Constants and Variables — practice', '41-44', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Store the two values in float variables before dividing.',
                        's = d / t; then cout << s;',
                        'Solution: float d = 150, t = 30; cout << d / t;',
                    ],
                },
            ],
        },
    ],
}
