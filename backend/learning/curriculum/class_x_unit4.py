"""
UNIT 4 — CONTROL STRUCTURE (printed pages 70-92).

Section outline as printed in the textbook:

    4.1 Control Statements ............... p. 71
    4.2 Selection / Decision Making ...... p. 71
        4.2.1 "if" (Program 1) ........... pp. 71-73
        Nested "if" (Program 2) .......... p. 73
        4.2.2 "if-else" (Program 3) ...... p. 74
        4.2.3 else-if (Program 4) ........ pp. 75-76
        4.2.4 "switch" (Program 5) ....... pp. 76-78
        4.2.5 If / If-Else / switch differences  p. 78
    4.3 Iteration / Loop ................. p. 79
        4.3.1 "for" (Program 6) .......... pp. 79-80
        4.3.2 "while" (Program 7) ........ pp. 81-82
        4.3.3 "do while" (Program 8) ..... pp. 82-83
        Nested loops (Program 9) ......... p. 84
        4.3.4 for / while / do-while differences  p. 85
    4.4 Jump Statements .................. p. 86
        (break Program 10, continue Program 11, goto, return, exit())
    SUMMARY pp. 89-90 | EXERCISE pp. 90-91 | LAB ACTIVITIES p. 92

Held back on purpose (see textbooks/CLASS-X-SOURCE-VERIFICATION.md):

* Program 7 (the character counter, p. 81) uses `getche()`, which reads the
  console device and hangs under the sandbox's piped stdin. It is taught as a
  read-only sample with the book's own explanation, and a clearly-labelled
  `cin` adaptation is offered for real execution practice.
* The matching-column exercise (EXERCISE C, p. 91) is left for manual review:
  the scan's column layout is not legible enough to reproduce without
  inventing pairs.
"""

from .common import ref

UNIT = 'Unit 4'
CLASS = 'Class X'

CHAPTER = {
    'slug': 'unit-4-control-structure',
    'title': 'Unit 4 — Control Structure',
    'description': (
        'Decisions and repetition: if, nested if, if-else, the else-if '
        'ladder and switch; for, while and do-while loops, nested loops, and '
        'the five jump statements — with the textbook\'s own programs and '
        'lab practicals.'
    ),
    'order': 3,
    'xp_reward': 700,
    'reference': ref(UNIT, 'Control Structure', '70-92', CLASS),
    'lessons': [
        # ── 4.1 ────────────────────────────────────────────────────────────
        {
            'slug': 'control-statements-overview',
            'title': 'What Are Control Statements?',
            'content_type': 'text',
            'learning_objective': (
                'Explain the default flow of a program and name the three '
                'types of control statement.'
            ),
            'order': 1,
            'duration_minutes': 8,
            'xp_reward': 40,
            'reference': ref(UNIT, '4.1 Control Statements', '71', CLASS),
            'content_body': '''# What Are Control Statements?

Left alone, a C++ program runs **from top to bottom**, one statement after another, exactly in the order you wrote them. Section 4.1 (p. 71) calls this the default flow and then asks the obvious question: what if we want to *skip* statements, *repeat* them, or *jump* somewhere else?

A **control statement** changes the order in which statements are executed. The book lists **three types**:

| Type | What it does | C++ statements |
|---|---|---|
| **Selection / Decision Making** | choose between paths | `if`, `if-else`, `switch` |
| **Iteration / Loops** | repeat a block | `for`, `while`, `do-while` |
| **Jump** | leave or skip within a block | `break`, `continue`, `goto`, `return`, `exit()` |

Everything else in this unit is detail on those three families. One tracing example before moving on — this program just prints in order, with no control statement at all:

```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "One\\n";
    cout << "Two\\n";
    cout << "Three";
    return 0;
}
```

**Expected output:**

```output
One
Two
Three
```

Add a single `if`, and "Two" can be skipped; add a `for`, and everything can run ten times. That is control.
''',
            'exercises': [
                {
                    'slug': 'three-types-of-control-statements',
                    'title': 'How Many Types of Control Statements?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'According to section 4.1, into how many types are '
                        'control statements divided?'
                    ),
                    'explain': (
                        'Three: Selection/Decision Making, Iteration (loops) '
                        'and Jump. Sindh Board Class X, Unit 4, 4.1, p. 71. '
                        'EXERCISE A (iii), p. 90 asks the same.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Three', 'is_correct': True},
                        {'id': 'b', 'text': 'Two', 'is_correct': False},
                        {'id': 'c', 'text': 'Four', 'is_correct': False},
                        {'id': 'd', 'text': 'Five', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A (iii)', '90', CLASS),
                },
                {
                    'slug': 'default-flow-of-program',
                    'title': 'Default Flow of Execution',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Without any control statements, in what order does a '
                        'C++ program execute its statements?'
                    ),
                    'explain': (
                        'Statements run sequentially, from top to bottom, in '
                        'the written order; control statements are what change '
                        'that. Sindh Board Class X, Unit 4, 4.1, p. 71.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'From top to bottom, one after another', 'is_correct': True},
                        {'id': 'b', 'text': 'From the last statement backwards', 'is_correct': False},
                        {'id': 'c', 'text': 'In random order, decided by the compiler', 'is_correct': False},
                        {'id': 'd', 'text': 'Only the statements inside main that contain cout', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '4.1 Control Statements', '71', CLASS),
                },
            ],
        },

        # ── 4.2.1 + 4.2.2 ──────────────────────────────────────────────────
        {
            'slug': 'the-if-statement',
            'title': 'The if Statement and Nested if',
            'content_type': 'interactive',
            'learning_objective': (
                'Write an `if` test, and explain why an inner `if` is only '
                'tested when the outer one is true.'
            ),
            'order': 2,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, '4.2.1 "if" and Nested "if"', '71-73', CLASS),
            'content_body': '''# The "if" Statement

The simplest decision (p. 71): **if** a test condition is true, run the statements inside the braces; **if** it is false, skip them entirely. The book's syntax:

```cpp
if (test condition)
{
    Statement(s);
}
```

Figure 4.1 (p. 72) draws it as a diamond: the condition is asked once, one path is taken.

## Program 1 — a grade check (pp. 72-73)

Marks at or above 70 earn an A:

```cpp
#include <iostream>
using namespace std;

int main() {
    int marks;
    cout << "Enter marks: ";
    cin >> marks;

    if (marks >= 70) {
        cout << "A Grade";
    }
    return 0;
}
```

Run it with `75` as input — the body executes. Now run it with `60` — nothing is printed after the prompt, because the condition was false and the block was skipped. That skipping is the whole point of `if`.

## The nested "if" (p. 73)

An `if` inside another `if`. The inner condition is **only tested when the outer one is true** — if the outer fails, the inner never even runs. Program 2 from p. 73:

```cpp
#include <iostream>
using namespace std;

int main() {
    int marks, age;
    cout << "Enter marks and age: ";
    cin >> marks >> age;

    if (marks >= 60) {
        if (age >= 18) {
            cout << "you got the job";
        }
    }
    cout << "\\nGood Luck";
    return 0;
}
```

**Expected output** with input `70 19`:

```output
Enter marks and age: you got the job
Good Luck
```

Trace the three cases until you can predict all of them:

| marks | age | what happens |
|---|---|---|
| 70 | 19 | outer true, inner true → "you got the job", then "Good Luck" |
| 70 | 15 | outer true, inner false → only "Good Luck" |
| 40 | 30 | outer false → the inner test never runs → only "Good Luck" |

"Good Luck" is outside both blocks, so it prints no matter what — putting a statement inside or after the braces is a decision with a real difference in behaviour.
''',
            'exercises': [
                {
                    'slug': 'program1-a-grade-output',
                    'title': 'Program 1 Output',
                    'exercise_type': 'output_prediction',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Program 1 (pp. 72-73) tests `if (marks >= 70)` and '
                        'prints `A Grade` inside the block. The learner enters '
                        '`65`. What does the `if` block output?'
                    ),
                    'context': 'Answer with exactly what the block prints, or nothing at all if it does not run.',
                    'expected_output': 'nothing',
                    'explain': (
                        '65 is not >= 70, so the condition is false and the '
                        'block is skipped — an `if` prints nothing when its '
                        'test fails. Sindh Board Class X, Unit 4, 4.2.1, '
                        'pp. 72-73.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int marks = 65;\n'
                        '    if (marks >= 70) {\n'
                        '        cout << "A Grade";\n'
                        '    }\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '4.2.1 "if" — Program 1', '72-73', CLASS),
                    'hints': [
                        'Is 65 greater than or equal to 70?',
                        'When the test fails, the statements in the braces never run.',
                    ],
                },
                {
                    'slug': 'nested-if-both-true',
                    'title': 'A Nested if, Fully Tested',
                    'exercise_type': 'output_prediction',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'With input `70 15`, what does Program 2 (p. 73) '
                        'display? Answer with the text after the prompt, '
                        'including the line break.'
                    ),
                    'context': 'The job offer needs marks >= 60 AND age >= 18; "Good Luck" sits outside both blocks.',
                    'expected_output': 'Good Luck',
                    'explain': (
                        'marks 70 passes the outer test, but age 15 fails the '
                        'inner one, so "you got the job" is skipped; "Good '
                        'Luck" is outside the blocks and always prints. Sindh '
                        'Board Class X, Unit 4, nested "if", p. 73.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int marks, age;\n'
                        '    cin >> marks >> age;\n'
                        '\n'
                        '    if (marks >= 60) {\n'
                        '        if (age >= 18) {\n'
                        '            cout << "you got the job";\n'
                        '        }\n'
                        '    }\n'
                        '    cout << "Good Luck";\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'xp_reward': 60,
                    'order': 2,
                    'reference': ref(UNIT, 'Nested "if" — Program 2', '73', CLASS),
                    'hints': [
                        'The outer test passes — but check the inner one before deciding what prints.',
                        'Only "Good Luck" survives; it is outside both blocks.',
                    ],
                },
                {
                    'slug': 'is-it-even',
                    'title': 'Write an if: Is It Even?',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read one integer from input. If it is even, print '
                        '`Even`. (A number is even when `n % 2 == 0`.)'
                    ),
                    'context': (
                        'Unit 3 taught `%` (modulus); this applies it inside an '
                        '`if`, the way Program 1 applies `>=`. This is '
                        'supplementary practice around section 4.2.1.'
                    ),
                    'constraints': (
                        'Use `cin` to read the number and a single `if`. Print '
                        'exactly `Even` — nothing else — when the number is '
                        'even, and print nothing when it is odd.'
                    ),
                    'expected_behavior': 'For input 8 the program prints: Even',
                    'explain': (
                        '`n % 2` is the remainder after dividing by 2; when it '
                        'is 0 the number is even and the block runs. Sindh '
                        'Board Class X, Unit 4, 4.2.1, pp. 71-73 (with Unit 3, '
                        '3.4.1, pp. 57-58 for `%`).'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n;\n'
                        '    cin >> n;\n'
                        '\n'
                        '    // print "Even" when n is even\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n;\n'
                        '    cin >> n;\n'
                        '\n'
                        '    if (n % 2 == 0) {\n'
                        '        cout << "Even";\n'
                        '    }\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '8\n', 'expected_output': 'Even'},
                        {'input': '7\n', 'expected_output': ''},
                    ],
                    'xp_reward': 100,
                    'order': 3,
                    'reference': ref(
                        UNIT, '4.2.1 "if" — practice', '71-73', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'The remainder operator from Unit 3 tells you divisibility: n % 2.',
                        'Write: if (n % 2 == 0) { cout << "Even"; }',
                    ],
                },
            ],
        },

        # ── 4.2.2 ──────────────────────────────────────────────────────────
        {
            'slug': 'the-if-else-statement',
            'title': 'The if-else Statement',
            'content_type': 'interactive',
            'learning_objective': (
                'Provide an alternative path with `else`, so something runs '
                'when the test is false.'
            ),
            'order': 3,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '4.2.2 "if-else"', '74', CLASS),
            'content_body': '''# The "if-else" Statement

A plain `if` says nothing when the condition fails. **if-else** gives a second path: exactly one of the two blocks always runs — never both, never neither. Figure 4.2 (p. 74) shows the diamond with both exits drawn.

```cpp
if (test condition)
{
    Statement(s);        // runs when true
}
else
{
    Statement(s);        // runs when false
}
```

## Program 3 — pass or fail (p. 74)

The book's example, with 40 as the pass mark:

```cpp
#include <iostream>
using namespace std;

int main() {
    int marks;
    cout << "Enter marks: ";
    cin >> marks;

    if (marks >= 40) {
        cout << "Pass";
    }
    else {
        cout << "Fail";
    }
    return 0;
}
```

**Expected output** with input `35`:

```output
Enter marks: Fail
```

With `52` it prints `Pass`. Whichever number the learner types, exactly one word appears — that is the guarantee `else` adds.

> **Common mistake:** putting a semicolon straight after `if (condition);`. That terminates the `if` with an empty body, so the block below always runs. The `else` never takes a semicolon either — it is a keyword that introduces a block, not a statement.
''',
            'exercises': [
                {
                    'slug': 'pass-or-fail-program',
                    'title': 'Pass or Fail',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Write Program 3 yourself: read marks and print `Pass` '
                        'when marks are 40 or more, otherwise print `Fail`.'
                    ),
                    'context': 'Section 4.2.2, Program 3, p. 74.',
                    'constraints': 'Print exactly `Pass` or exactly `Fail`, with nothing else.',
                    'expected_behavior': 'For input 40 the program prints: Pass',
                    'explain': (
                        '`marks >= 40` selects the first block; the `else` '
                        'block catches every other value. Sindh Board Class X, '
                        'Unit 4, 4.2.2, p. 74.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int marks;\n'
                        '    cin >> marks;\n'
                        '\n'
                        '    // if marks >= 40 print Pass, else print Fail\n\n\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int marks;\n'
                        '    cin >> marks;\n'
                        '\n'
                        '    if (marks >= 40) {\n'
                        '        cout << "Pass";\n'
                        '    }\n'
                        '    else {\n'
                        '        cout << "Fail";\n'
                        '    }\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '52\n', 'expected_output': 'Pass'},
                        {'input': '40\n', 'expected_output': 'Pass'},
                        {'input': '39\n', 'expected_output': 'Fail'},
                    ],
                    'xp_reward': 90,
                    'order': 1,
                    'reference': ref(UNIT, '4.2.2 "if-else" — Program 3', '74', CLASS),
                    'hints': [
                        '>= 40 goes in the if; everything else belongs to the else.',
                        'if (marks >= 40) { cout << "Pass"; } else { cout << "Fail"; }',
                    ],
                },
                {
                    'slug': 'if-else-runs-one-block',
                    'title': 'How Many Blocks Run?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'In an `if-else` statement, how many of the two blocks '
                        'execute for a single test?'
                    ),
                    'explain': (
                        'Exactly one: the `if` block when the condition is '
                        'true, the `else` block when it is false. Sindh Board '
                        'Class X, Unit 4, 4.2.2, p. 74.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Exactly one', 'is_correct': True},
                        {'id': 'b', 'text': 'Both blocks, in order', 'is_correct': False},
                        {'id': 'c', 'text': 'Neither, only the test runs', 'is_correct': False},
                        {'id': 'd', 'text': 'It depends on the compiler', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '4.2.2 "if-else"', '74', CLASS),
                },
            ],
        },

        # ── 4.2.3 ──────────────────────────────────────────────────────────
        {
            'slug': 'the-else-if-ladder',
            'title': 'The else-if Ladder',
            'content_type': 'interactive',
            'learning_objective': (
                'Chain `else if` tests to choose one path out of many, and '
                'read the book\'s grade ladder.'
            ),
            'order': 4,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, '4.2.3 else-if', '75-76', CLASS),
            'content_body': '''# The else-if Ladder

One `if` picks between two paths. Real grading has more than two answers, so the book (pp. 75-76) chains the tests into a **ladder**: try the first condition, then the second, and so on — the first test that passes wins, and all the rest are skipped.

## Program 4 — the marks ladder (pp. 75-76)

The textbook shows this first as **deeply nested ifs**, then rewritten as a flat ladder, and makes the key point itself: *"This format only increases the readability of program while there is no any change for compiler."* The two forms behave identically; the ladder is easier to read.

```cpp
#include <iostream>
using namespace std;

int main() {
    int marks;
    cout << "Enter marks: ";
    cin >> marks;

    if (marks >= 80) {
        cout << "A1 Grade";
    }
    else if (marks >= 70) {
        cout << "A Grade";
    }
    else if (marks >= 60) {
        cout << "B Grade";
    }
    else if (marks >= 50) {
        cout << "C Grade";
    }
    else {
        cout << "Fail";
    }
    return 0;
}
```

**Expected output** with input `65`:

```output
Enter marks: B Grade
```

Trace `65`: not `>= 80`, not `>= 70`, yes `>= 60` → prints `B Grade` and stops checking. Order matters: if you put `>= 50` first, `65` would match it and never reach the B test. **Always ladder from the strictest threshold down.**

## The in-book task (p. 76)

The section ends with a written task: read two integers and an operator (`+ - * /`) and use an else-if ladder to perform the chosen calculation. That is the exercise you write below.
''',
            'exercises': [
                {
                    'slug': 'grade-ladder-output',
                    'title': 'Read the Ladder',
                    'exercise_type': 'output_prediction',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Program 4 (pp. 75-76): input `80`. What grade prints? '
                        'Answer with the grade only.'
                    ),
                    'context': 'Careful: the A1 test (>= 80) comes before the A test (>= 70).',
                    'expected_output': 'A1 Grade',
                    'explain': (
                        '80 is >= 80, so the very first test matches and prints '
                        '`A1 Grade`; the ladder stops there and never reaches '
                        'the >= 70 test. Sindh Board Class X, Unit 4, 4.2.3, '
                        'pp. 75-76.'
                    ),
                    'starter_code': (
                        'if (marks >= 80)      cout << "A1 Grade";\n'
                        'else if (marks >= 70) cout << "A Grade";\n'
                        'else if (marks >= 60) cout << "B Grade";\n'
                        'else if (marks >= 50) cout << "C Grade";\n'
                        'else                  cout << "Fail";\n'
                    ),
                    'xp_reward': 60,
                    'order': 1,
                    'reference': ref(UNIT, '4.2.3 else-if — Program 4', '75-76', CLASS),
                    'hints': [
                        'Which test is checked first?',
                        '80 satisfies the first condition, so the answer is A1 Grade.',
                    ],
                },
                {
                    'slug': 'simple-calculator-ladder',
                    'title': 'A Two-Number Calculator',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'hard',
                    'instructions': (
                        'Read two integers and then a single character for the '
                        'operator (`+`, `-` or `*`), and print the result of '
                        'that operation. Use an else-if ladder.'
                    ),
                    'context': (
                        'The in-book task at the end of section 4.2.3 (p. 76) '
                        'asks for a calculator built with else-if; this version '
                        'is auto-graded for `+`, `-` and `*`.'
                    ),
                    'constraints': (
                        'Read the two integers first, then the operator. Print '
                        'only the numeric result. Chain the tests with `else if`.'
                    ),
                    'expected_behavior': 'For input `12 5 +` the program prints: 17',
                    'explain': (
                        'Each `else if` compares the operator char to one of '
                        '`\'+\'`, `\'-\'`, `\'*\'` and prints the matching '
                        'calculation; the first true test wins. Sindh Board '
                        'Class X, Unit 4, 4.2.3, p. 76.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int a, b;\n'
                        '    char op;\n'
                        '    cin >> a >> b >> op;\n'
                        '\n'
                        '    // else-if ladder over op\n\n\n\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int a, b;\n'
                        '    char op;\n'
                        '    cin >> a >> b >> op;\n'
                        '\n'
                        '    if (op == \'+\') {\n'
                        '        cout << a + b;\n'
                        '    }\n'
                        '    else if (op == \'-\') {\n'
                        '        cout << a - b;\n'
                        '    }\n'
                        '    else if (op == \'*\') {\n'
                        '        cout << a * b;\n'
                        '    }\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '12 5 +\n', 'expected_output': '17'},
                        {'input': '12 5 -\n', 'expected_output': '7'},
                        {'input': '12 5 *\n', 'expected_output': '60'},
                    ],
                    'xp_reward': 130,
                    'order': 2,
                    'reference': ref(
                        UNIT, '4.2.3 else-if — in-book task', '76', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Read the operator into a char and compare it with == inside each else if.',
                        'if (op == \'+\') cout << a + b; else if (op == \'-\') cout << a - b; else if (op == \'*\') cout << a * b;',
                    ],
                },
            ],
        },
        # ── 4.2.4 + 4.2.5 ──────────────────────────────────────────────────
        {
            'slug': 'the-switch-statement',
            'title': 'The switch Statement',
            'content_type': 'interactive',
            'learning_objective': (
                'Branch on the value of a character or integer with `switch`, '
                '`case`, `break` and `default`, and say when switch beats '
                'if-else.'
            ),
            'order': 5,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, '4.2.4 "switch" and 4.2.5', '76-78', CLASS),
            'content_body': '''# The "switch" Statement

When one variable is compared against many fixed values, `switch` reads better than a long else-if ladder. Figure 4.3 (p. 76) draws the multi-way branch. The syntax (pp. 76-78):

```cpp
switch (expression) {
    case constant1:  statements;  break;
    case constant2:  statements;  break;
    default:         statements;
}
```

- `expression` must be an **integer or character** — the book is explicit (4.2.5, p. 78) that switch cannot use `<` or `>`, and cannot match ranges.
- Each `case` needs a **constant** followed by a **colon** (EXERCISE A (vi), p. 90).
- `break` stops execution falling through into the next case; `default` runs when nothing matched. The book marks both **optional** (EXERCISE A (ix)).

## Program 5 — day of the week (pp. 77-78)

```cpp
#include <iostream>
using namespace std;

int main() {
    int day;
    cout << "Enter day number (1-7): ";
    cin >> day;

    switch (day) {
        case 1: cout << "Sunday";    break;
        case 2: cout << "Monday";    break;
        case 3: cout << "Tuesday";   break;
        case 4: cout << "Wednesday"; break;
        case 5: cout << "Thursday";  break;
        case 6: cout << "Friday";    break;
        case 7: cout << "Saturday";  break;
        default: cout << "Invalid day number";
    }
    return 0;
}
```

**Expected output** with input `1`:

```output
Enter day number (1-7): Sunday
```

Type `9` and it falls to `default` and prints `Invalid day number`.

## The break trap

Remove a `break` and execution **continues into the next case** without re-testing it — that is "fall through". It is why Program 5 puts `break` after every day.

## switch vs if-else (4.2.5, p. 78)

| | if / if-else | switch |
|---|---|---|
| Tests | any condition, including ranges (`<`, `>`) | only equality against integer/char constants |
| Many fixed values | ladder gets hard to read | clean multi-way branch |
| Ranges (like the grade ladder) | ideal | cannot express them |

The grade ladder in the previous lesson **cannot** be a switch — `marks >= 80` is a range, not a single value.
''',
            'exercises': [
                {
                    'slug': 'day-name-switch',
                    'title': 'Day Number to Day Name',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Recreate Program 5: read a day number and print the '
                        'matching day name using a `switch`. For any number '
                        'outside 1-7 print `Invalid day number`. (Only 1, 4 and '
                        '7 are graded here, but write all seven cases plus '
                        'default.)'
                    ),
                    'context': 'Section 4.2.4, Program 5, pp. 77-78.',
                    'constraints': 'Every `case` must end with `break`; use `default` for invalid input.',
                    'expected_behavior': 'For input 4 the program prints: Wednesday',
                    'explain': (
                        '`switch` matches the integer against each `case`; the '
                        '`break` ends the switch so it does not fall through, '
                        'and `default` catches everything else. Sindh Board '
                        'Class X, Unit 4, 4.2.4, pp. 76-78.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int day;\n'
                        '    cin >> day;\n'
                        '\n'
                        '    // switch over day -> Sunday .. Saturday, default\n\n\n\n\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int day;\n'
                        '    cin >> day;\n'
                        '\n'
                        '    switch (day) {\n'
                        '        case 1: cout << "Sunday";    break;\n'
                        '        case 2: cout << "Monday";    break;\n'
                        '        case 3: cout << "Tuesday";   break;\n'
                        '        case 4: cout << "Wednesday"; break;\n'
                        '        case 5: cout << "Thursday";  break;\n'
                        '        case 6: cout << "Friday";    break;\n'
                        '        case 7: cout << "Saturday";  break;\n'
                        '        default: cout << "Invalid day number";\n'
                        '    }\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '1\n', 'expected_output': 'Sunday'},
                        {'input': '4\n', 'expected_output': 'Wednesday'},
                        {'input': '7\n', 'expected_output': 'Saturday'},
                        {'input': '9\n', 'expected_output': 'Invalid day number'},
                    ],
                    'xp_reward': 120,
                    'order': 1,
                    'reference': ref(UNIT, '4.2.4 "switch" — Program 5', '77-78', CLASS),
                    'hints': [
                        'One `case N:` line per day, each followed by break.',
                        'case 1: cout << "Sunday"; break; ... default: cout << "Invalid day number";',
                    ],
                },
                {
                    'slug': 'switch-cannot-test-ranges',
                    'title': 'What switch Cannot Do',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'According to section 4.2.5, why can the marks grade '
                        'ladder NOT be written as a single `switch`?' 
                    ),
                    'explain': (
                        'switch only matches an integer or character against '
                        'fixed `case` constants; it cannot test ranges with `<` '
                        'or `>`, and `marks >= 80` is a range. Sindh Board '
                        'Class X, Unit 4, 4.2.5, p. 78.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'switch cannot use < or > to match a range', 'is_correct': True},
                        {'id': 'b', 'text': 'switch can only handle text strings', 'is_correct': False},
                        {'id': 'c', 'text': 'switch always runs every case', 'is_correct': False},
                        {'id': 'd', 'text': 'switch needs a semicolon after every case', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, '4.2.5 Difference between if, if-else and switch', '78', CLASS),
                },
                {
                    'slug': 'missing-break-falls-through',
                    'title': 'The Missing break',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'What happens when a `case` block does not end with a '
                        '`break`? (EXERCISE A (ix), p. 90 notes break is '
                        'optional — so you must know its effect.)'
                    ),
                    'explain': (
                        'Without `break`, execution falls through and runs the '
                        'statements of the following cases too, until a break '
                        'or the end of the switch. Sindh Board Class X, Unit 4, '
                        '4.2.4, pp. 76-78.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'It keeps running into the next cases (fall through)', 'is_correct': True},
                        {'id': 'b', 'text': 'The compiler refuses the program', 'is_correct': False},
                        {'id': 'c', 'text': 'The switch jumps to default', 'is_correct': False},
                        {'id': 'd', 'text': 'Nothing; break changes nothing', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 3,
                    'reference': ref(UNIT, '4.2.4 "switch" — break', '76-78', CLASS),
                },
            ],
        },

        # ── 4.3.1 ──────────────────────────────────────────────────────────
        {
            'slug': 'the-for-loop',
            'title': 'Repeating with the for Loop',
            'content_type': 'interactive',
            'learning_objective': (
                'Write a `for` loop with its three parts and use it to repeat '
                'a known number of times.'
            ),
            'order': 6,
            'duration_minutes': 15,
            'xp_reward': 55,
            'reference': ref(UNIT, '4.3.1 "for"', '79-80', CLASS),
            'content_body': '''# The "for" Loop

Section 4.3 (p. 79) groups the loops into **for, while and do-while**. The `for` loop (4.3.1, pp. 79-80, Figure 4.4) is the one you reach for when you **know how many times** to repeat — the book calls it a *definite repetition* / *counter-controlled* / *pre-test* loop.

Its header has three parts, separated by **semicolons**:

```cpp
for (initialization; condition; increment/decrement)
{
    Statement(s);
}
```

1. **Initialization** — runs once, before anything (`count = 2`).
2. **Condition testing** — checked before every pass; when false the loop ends.
3. **Increment/decrement** — runs after each pass (`count = count + 2`).

## Program 6 — even numbers 2 to 20 (p. 80)

```cpp
#include <iostream>
using namespace std;

int main() {
    int count;
    for (count = 2; count <= 20; count = count + 2) {
        cout << count << " ";
    }
    return 0;
}
```

**Expected output:**

```output
2 4 6 8 10 12 14 16 18 20
```

Trace the counter: 2, 4, 6 … 20, and when `count` becomes 22 the condition `count <= 20` fails and the loop stops. That is **ten** prints.

> The loop body can be a single statement without braces — Program 6 could drop the `{ }` and behave the same, because only the one `cout` line belongs to the loop.
''',
            'exercises': [
                {
                    'slug': 'count-one-to-ten',
                    'title': 'Print 1 to 10',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'easy',
                    'instructions': (
                        'Write a `for` loop that prints the numbers 1 to 10 on '
                        'one line, each followed by a space: '
                        '`1 2 3 4 5 6 7 8 9 10`.'
                    ),
                    'context': 'Section 4.3.1 — apply the Program 6 shape with a step of 1.',
                    'constraints': 'Use `cout << i << " "` inside a single `for` loop.',
                    'expected_behavior': 'Prints: 1 2 3 4 5 6 7 8 9 10',
                    'explain': (
                        '`for (i = 1; i <= 10; i++)` starts at 1, tests before '
                        'each pass and adds 1 after each, printing 1..10. Sindh '
                        'Board Class X, Unit 4, 4.3.1, pp. 79-80.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int i;\n'
                        '    // for loop 1..10 printing i and a space\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int i;\n'
                        '    for (i = 1; i <= 10; i++) {\n'
                        '        cout << i << " ";\n'
                        '    }\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '1 2 3 4 5 6 7 8 9 10'},
                    ],
                    'xp_reward': 90,
                    'order': 1,
                    'reference': ref(
                        UNIT, '4.3.1 "for" — practice', '79-80', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Initialization i = 1, condition i <= 10, increment i++.',
                        'for (i = 1; i <= 10; i++) { cout << i << " "; }',
                    ],
                },
                {
                    'slug': 'squares-one-to-ten',
                    'title': 'LAB: Squares of 1 to 10',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'LAB ACTIVITIES 9 (p. 92): print the square of every '
                        'number from 1 to 10, each followed by a space: '
                        '`1 4 9 16 25 36 49 64 81 100`.'
                    ),
                    'context': 'A for loop where the body prints `i * i`.',
                    'constraints': 'Loop 1..10 and print `i * i` with a trailing space.',
                    'expected_behavior': 'Prints: 1 4 9 16 25 36 49 64 81 100',
                    'explain': (
                        'Same loop as counting to ten, but the printed value is '
                        '`i * i`. Sindh Board Class X, Unit 4, LAB ACTIVITIES '
                        '9, p. 92 (loop form from 4.3.1, pp. 79-80).'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int i;\n'
                        '    // for loop 1..10 printing i*i and a space\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int i;\n'
                        '    for (i = 1; i <= 10; i++) {\n'
                        '        cout << i * i << " ";\n'
                        '    }\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '1 4 9 16 25 36 49 64 81 100'},
                    ],
                    'xp_reward': 100,
                    'order': 2,
                    'reference': ref(UNIT, 'LAB ACTIVITIES 9', '92', CLASS),
                    'hints': [
                        'Reuse the 1..10 loop but print i * i instead of i.',
                        'cout << i * i << " ";',
                    ],
                },
                {
                    'slug': 'for-loop-three-parts',
                    'title': 'The Three Parts of a for Header',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which separates the initialization, the condition and '
                        'the increment in a `for` loop header?'
                    ),
                    'explain': (
                        'The three parts of a `for` header are separated by '
                        'semicolons: `for (init; condition; increment)`. Sindh '
                        'Board Class X, Unit 4, 4.3.1, pp. 79-80.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Semicolons ( ; )', 'is_correct': True},
                        {'id': 'b', 'text': 'Commas ( , )', 'is_correct': False},
                        {'id': 'c', 'text': 'Colons ( : )', 'is_correct': False},
                        {'id': 'd', 'text': 'Spaces only', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, '4.3.1 "for"', '79-80', CLASS),
                },
            ],
        },
        # ── 4.3.2 + 4.3.3 + nested + 4.3.4 ─────────────────────────────────
        {
            'slug': 'while-and-do-while-loops',
            'title': 'The while and do-while Loops',
            'content_type': 'interactive',
            'learning_objective': (
                'Repeat an unknown number of times with `while` and `do-while`, '
                'and explain the post-test guarantee of `do-while`.'
            ),
            'order': 7,
            'duration_minutes': 18,
            'xp_reward': 60,
            'reference': ref(UNIT, '4.3.2-4.3.4 while, do-while, nested', '81-85', CLASS),
            'content_body': '''# The while Loop (4.3.2, pp. 81-82)

Use `while` when you **do not know in advance** how many times the body must run — an *indefinite*, *pre-test* loop (Figure 4.5). The condition is checked **before** every pass; if it is false on the very first check, the body never runs.

```cpp
while (condition)
{
    Statement(s);
}
```

## Program 7 — counting typed characters (p. 81, read-only)

The book\'s own `while` example counts characters typed until the user presses Enter, using `getche()`. It is shown here **without a Run button** on purpose:

```cpp-static
#include <iostream>
#include <conio.h>
using namespace std;

int main() {
    int count = 0;
    char ch;
    cout << "Type characters (Enter to stop):";
    do {
        ch = getche();
        count++;
    } while (ch != '\\r');
    count--;
    cout << "\\nYou typed " << count << " characters";
    return 0;
}
```

> **Why this snippet cannot run in the sandbox:** `getche()` reads straight from the console device, not from standard input. Measured against the sandbox\'s piped stdin it waits forever and is stopped by the timeout. It still runs fine in Dev-C++ on a real keyboard — the environment Unit 2 introduced. So learn its logic here, and use `cin` for the executable practice below.

## The do-while Loop (4.3.3, pp. 82-83)

A `do-while` is a **post-test** loop: the body runs **first**, then the condition is checked. That guarantees the body executes **at least once**. Note the **semicolon** after `while(condition);` — the book stresses it.

```cpp
do
{
    Statement(s);
}
while (condition);
```

Program 8 (p. 83) totals employee salaries while the user keeps pressing `y` — a natural `do-while`, because you want to ask for at least one salary before checking whether to continue.

Countdown is a small, runnable `do-while` you can picture:

```cpp
#include <iostream>
using namespace std;

int main() {
    int n = 5;
    do {
        cout << n << " ";
        n--;
    } while (n >= 1);
    return 0;
}
```

**Expected output:**

```output
5 4 3 2 1
```

## Nested loops (p. 84)

A loop inside a loop. For every single pass of the outer loop, the inner loop runs **all the way through**. Program 9 prints the numbers 1 to 10 across five rows — an outer loop of 5 rows with an inner loop of 2 numbers each. If the outer runs 5 times and the inner runs 3 times each pass, the inner body executes 5 × 3 = **15** times total.

## for vs while vs do-while (4.3.4, p. 85)

| | for | while | do-while |
|---|---|---|---|
| Test | pre-test | pre-test | **post-test** |
| Repetition | definite (counted) | indefinite | indefinite |
| Runs at least once? | only if the start passes | only if true first | **always** |
| Best when | count is known | stop condition unknown | must run once first |
''',
            'exercises': [
                {
                    'slug': 'sum-one-to-twenty-while',
                    'title': 'LAB: Sum 1 to 20 with while',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'LAB ACTIVITIES 2 (p. 92): using a `while` loop, add '
                        'the numbers 1 to 20 and print the total. The answer '
                        'is `210`.'
                    ),
                    'context': 'A running total inside a pre-test while loop.',
                    'constraints': 'Start at 1, loop while n <= 20, print only the final sum.',
                    'expected_behavior': 'Prints: 210',
                    'explain': (
                        '`while (n <= 20) { sum += n; n++; }` accumulates '
                        '1+2+…+20 = 210. Sindh Board Class X, Unit 4, LAB '
                        'ACTIVITIES 2, p. 92 (while form from 4.3.2, pp. 81-82).'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n = 1, sum = 0;\n'
                        '    // while loop adding 1..20\n\n\n\n'
                        '    cout << sum;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n = 1, sum = 0;\n'
                        '    while (n <= 20) {\n'
                        '        sum = sum + n;\n'
                        '        n++;\n'
                        '    }\n'
                        '    cout << sum;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '210'},
                    ],
                    'xp_reward': 110,
                    'order': 1,
                    'reference': ref(UNIT, 'LAB ACTIVITIES 2', '92', CLASS),
                    'hints': [
                        'Keep adding n to sum and increasing n while n <= 20.',
                        'while (n <= 20) { sum = sum + n; n++; }',
                    ],
                },
                {
                    'slug': 'countdown-do-while',
                    'title': 'Countdown with do-while',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'medium',
                    'instructions': (
                        'Using a `do-while` loop, print the numbers 5 down to 1 '
                        'on one line, each followed by a space: `5 4 3 2 1`.'
                    ),
                    'context': 'Section 4.3.3 — the post-test loop.',
                    'constraints': 'Body runs first, then the condition; end the loop with a semicolon.',
                    'expected_behavior': 'Prints: 5 4 3 2 1',
                    'explain': (
                        '`do { cout << n << " "; n--; } while (n >= 1);` prints '
                        '5..1. The body always runs at least once because the '
                        'test is post-. Sindh Board Class X, Unit 4, 4.3.3, '
                        'pp. 82-83.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n = 5;\n'
                        '    // do-while printing n and a space, then n--\n\n\n\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n = 5;\n'
                        '    do {\n'
                        '        cout << n << " ";\n'
                        '        n--;\n'
                        '    } while (n >= 1);\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '5 4 3 2 1'},
                    ],
                    'xp_reward': 100,
                    'order': 2,
                    'reference': ref(
                        UNIT, '4.3.3 "do while" — practice', '82-83', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'Put the cout and n-- inside the do block.',
                        'do { cout << n << " "; n--; } while (n >= 1);',
                    ],
                },
                {
                    'slug': 'do-while-runs-at-least-once',
                    'title': 'Which Loop Always Runs Once?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which loop is guaranteed to execute its body at least '
                        'one time, even if the condition is false to begin with?'
                    ),
                    'explain': (
                        '`do-while` is a post-test loop: the body runs before '
                        'the condition is first checked. Sindh Board Class X, '
                        'Unit 4, 4.3.3 / 4.3.4, pp. 82-85.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'do-while', 'is_correct': True},
                        {'id': 'b', 'text': 'while', 'is_correct': False},
                        {'id': 'c', 'text': 'for', 'is_correct': False},
                        {'id': 'd', 'text': 'All three run at least once', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, '4.3.4 Difference between for, while, do-while', '85', CLASS),
                },
                {
                    'slug': 'nested-loop-total-runs',
                    'title': 'Count a Nested Loop',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'An outer loop runs 5 times; its inner loop runs 3 '
                        'times on every outer pass. How many times does the '
                        'inner body run in total?'
                    ),
                    'context': 'Nested loops, p. 84 (the idea behind Program 9).',
                    'explain': (
                        'The inner loop fully runs for each outer iteration, so '
                        'the total is 5 × 3 = 15. Sindh Board Class X, Unit 4, '
                        'nested loops, p. 84.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '15', 'is_correct': True},
                        {'id': 'b', 'text': '8', 'is_correct': False},
                        {'id': 'c', 'text': '5', 'is_correct': False},
                        {'id': 'd', 'text': '3', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 4,
                    'reference': ref(UNIT, 'Nested loops', '84', CLASS),
                },
            ],
        },

        # ── 4.4 ────────────────────────────────────────────────────────────
        {
            'slug': 'jump-statements',
            'title': 'Jump Statements: break, continue, goto, return, exit',
            'content_type': 'interactive',
            'learning_objective': (
                'Leave or skip inside a loop or function with the five jump '
                'statements.'
            ),
            'order': 8,
            'duration_minutes': 14,
            'xp_reward': 55,
            'reference': ref(UNIT, '4.4 Jump Statements', '86-88', CLASS),
            'content_body': '''# Jump Statements

Section 4.4 (p. 86) lists **five** statements that move control out of the normal top-to-bottom order: `break`, `continue`, `goto`, `return` and `exit()`.

- **`break`** — ends the nearest loop or `switch` immediately; control jumps to just after it. Program 10 adds numbers until the user enters `0`, then breaks.
- **`continue`** — skips the rest of the current pass and goes back to the **top of the loop** for the next test. Program 11 reads five numbers and ignores any that are not positive with `continue`.
- **`goto`** — an unconditional jump to a labelled line (the book\'s example uses a `warning:` label). It works, but the book itself says it **is not advised** because it makes flow hard to follow.
- **`return`** — ends the current function and hands back a value (`return [expression/value];`); in `main()` it ends the program.
- **`exit()`** — terminates the whole program at once. It is defined in `stdlib.h` with the syntax `void exit(int);`.

## Program 10 in a runnable form

A `break` that stops reading as soon as a `0` appears:

```cpp
#include <iostream>
#include <cstdlib>
using namespace std;

int main() {
    int n, sum = 0;
    while (true) {
        cin >> n;
        if (n == 0) {
            break;                 // leave the loop at once
        }
        sum = sum + n;
    }
    cout << sum;
    return 0;
}
```

With input `4 5 6 0`, the `0` triggers `break`, so the loop stops and the sum is `15` — the `0` is never added.

> `goto` is taught by description only here. It is valid C++ but the textbook discourages it, and none of the graded exercises use it.
''',
            'exercises': [
                {
                    'slug': 'sum-until-zero-break',
                    'title': 'Program 10: Add Until Zero',
                    'exercise_type': 'code',
                    'language': 'cpp',
                    'difficulty': 'hard',
                    'instructions': (
                        'Read integers one after another. Add each to a running '
                        'total, but as soon as a `0` is read, `break` out of '
                        'the loop and print the total. (The `0` itself is not '
                        'added.)'
                    ),
                    'context': 'Section 4.4, Program 10 (break).',
                    'constraints': 'Use a loop with `break` when the input value is 0.',
                    'expected_behavior': 'For input `4 5 6 0` the program prints: 15',
                    'explain': (
                        '`while(true)` reads a number; `if (n == 0) break;` '
                        'leaves the loop before adding the zero, so 4+5+6 = 15. '
                        'Sindh Board Class X, Unit 4, 4.4 (break, Program 10), '
                        'p. 86.'
                    ),
                    'starter_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n, sum = 0;\n'
                        '    while (true) {\n'
                        '        cin >> n;\n'
                        '        // break when n == 0, otherwise add it\n\n\n\n'
                        '    }\n'
                        '    cout << sum;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'solution_code': (
                        '#include <iostream>\n'
                        'using namespace std;\n'
                        '\n'
                        'int main() {\n'
                        '    int n, sum = 0;\n'
                        '    while (true) {\n'
                        '        cin >> n;\n'
                        '        if (n == 0) {\n'
                        '            break;\n'
                        '        }\n'
                        '        sum = sum + n;\n'
                        '    }\n'
                        '    cout << sum;\n'
                        '    return 0;\n'
                        '}\n'
                    ),
                    'test_cases': [
                        {'input': '4 5 6 0\n', 'expected_output': '15'},
                        {'input': '10 0\n', 'expected_output': '10'},
                        {'input': '0\n', 'expected_output': '0'},
                    ],
                    'xp_reward': 130,
                    'order': 1,
                    'reference': ref(UNIT, '4.4 Jump — break, Program 10', '86', CLASS),
                    'hints': [
                        'Right after reading n, test for 0 and break before adding.',
                        'if (n == 0) break;  sum = sum + n;',
                    ],
                },
                {
                    'slug': 'break-vs-continue',
                    'title': 'break vs continue',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'What does the `continue` statement do inside a loop?'
                    ),
                    'explain': (
                        '`continue` skips the rest of the current pass and '
                        'returns to the top of the loop for the next test; '
                        '`break` would end the loop entirely. Sindh Board '
                        'Class X, Unit 4, 4.4 (continue, Program 11), p. 86.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Skips the rest of this pass and goes to the top of the loop', 'is_correct': True},
                        {'id': 'b', 'text': 'Ends the whole program', 'is_correct': False},
                        {'id': 'c', 'text': 'Terminates the loop completely', 'is_correct': False},
                        {'id': 'd', 'text': 'Restarts the loop from the first iteration', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, '4.4 Jump — continue, Program 11', '86', CLASS),
                },
                {
                    'slug': 'exit-header',
                    'title': 'Where is exit() Defined?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Which header does the book say `exit()` is defined in?'
                    ),
                    'explain': (
                        '`exit()` is defined in `stdlib.h`, with the syntax '
                        '`void exit(int);`. Sindh Board Class X, Unit 4, 4.4 '
                        '(exit), p. 86.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'stdlib.h', 'is_correct': True},
                        {'id': 'b', 'text': 'iostream', 'is_correct': False},
                        {'id': 'c', 'text': 'conio.h', 'is_correct': False},
                        {'id': 'd', 'text': 'math.h', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, '4.4 Jump — exit()', '86', CLASS),
                },
            ],
        },
    ],
}
