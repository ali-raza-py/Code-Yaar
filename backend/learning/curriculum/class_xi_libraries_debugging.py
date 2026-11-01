"""
Class XI, Unit 3 — chapter 5: Libraries and Debugging

    3.6 Libraries in Python       (printed pp. 127-132)
    3.7 Debugging Code in Python  (printed pp. 132-133)

Non-deterministic book material (random, datetime, the Report Card
Generator activity) is taught as samples and reasoning items only — the
verification file records the sandbox rule that such output is never
auto-graded by comparison.
"""

from .common import ref

UNIT = 'Unit 3'
CLASS = 'Class XI'


CHAPTER_LIBS_DEBUG = {
    'slug': 'xi-libraries-and-debugging',
    'title': 'Libraries and Debugging',
    'description': (
        'The five ways to import, the built-in math/random/datetime '
        'libraries, third-party packages with pip, and the three error '
        'types plus reading tracebacks.'
    ),
    'order': 5,
    'xp_reward': 600,
    'reference': ref(UNIT, '3.6-3.7 Libraries in Python, Debugging Code in Python', '127-133', CLASS),
    'lessons': [
        # ── 3.6 imports + math ─────────────────────────────────────────────
        {
            'slug': 'importing-libraries',
            'title': 'Libraries and the Five Ways to Import',
            'content_type': 'interactive',
            'learning_objective': (
                'Explain what libraries are for and write all five import '
                'styles from section 3.6.'
            ),
            'order': 1,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.6 Libraries in Python — import forms', '127-128', CLASS),
            'content_body': '''# Libraries in Python

Section 3.6 (p. 127) defines **libraries** as pre-written code you borrow
instead of rebuilding: ready-made functions that your program can call. The
math library is the book's running example, and it shows **five ways to
import it** (pp. 127-128), each doing the same job with different reach:

```python
import math
print(math.sqrt(16))
```

**Expected output:**

```output
4.0
```

| # | The import line | How you then call it |
|---|---|---|
| 1 | `import math` | `math.sqrt(16)` |
| 2 | `import math as m` | `m.sqrt(16)` |
| 3 | `from math import sqrt` | `sqrt(16)` — bare name |
| 4 | `from math import sqrt, pi, factorial` | only those three arrive |
| 5 | `from math import *` | everything in math, bare |

Style 1 is the safest habit: `math.sqrt(16)` says where the function came
from. Style 5 pulls in every name and can quietly clash with your own
variables. Every runnable fence below uses one of the five — press Run and
compare.
''',
            'exercises': [
                {
                    'slug': 'count-the-import-ways',
                    'title': 'How Many Import Styles?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'How many ways to import a library does section 3.6 '
                        'demonstrate?'
                    ),
                    'explain': (
                        'Five: plain import, import ... as, from ... import '
                        'one name, from ... import several names, and from '
                        '... import *. Sindh Board Class XI, Unit 3, 3.6, '
                        'pp. 127-128.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Five', 'is_correct': True},
                        {'id': 'b', 'text': 'Two', 'is_correct': False},
                        {'id': 'c', 'text': 'Three', 'is_correct': False},
                        {'id': 'd', 'text': 'Seven', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.6 Ways to import', '127-128', CLASS),
                },
                {
                    'slug': 'alias-import-fill-blank',
                    'title': 'The Alias Import',
                    'exercise_type': 'fill_blank',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Fill the blank in the line so the program works: '
                        'the call below must reach math.sqrt as '
                        'm.sqrt(). Submit only the completed import line.'
                    ),
                    'context': (
                        'import ____________________\n'
                        'print(m.sqrt(16))'
                    ),
                    'expected_output': '',
                    'solution_code': 'import math as m\n',
                    'explain': (
                        '`import math as m` binds the whole library to the '
                        'short name m — style 2 of section 3.6. Sindh Board '
                        'Class XI, Unit 3, 3.6, p. 127.'
                    ),
                    'starter_code': (
                        'import ____________________\n'
                        'print(m.sqrt(16))\n'
                    ),
                    'xp_reward': 60,
                    'order': 2,
                    'reference': ref(UNIT, '3.6 import ... as', '127', CLASS),
                    'hints': [
                        'The call below uses the name m — the import must create it.',
                        'Solution: import math as m',
                    ],
                },
            ],
        },
        {
            'slug': 'the-math-library',
            'title': 'The math Library in Action',
            'content_type': 'interactive',
            'learning_objective': (
                'Call math functions — sqrt, pow, ceil, floor, pi — and '
                'predict their results.'
            ),
            'order': 2,
            'duration_minutes': 12,
            'xp_reward': 55,
            'reference': ref(UNIT, '3.6.1 Built-in Libraries — math', '128-129', CLASS),
            'content_body': '''# The math Library

The built-in math program (pp. 128-129) walks through the functions the
board exam expects you to know:

```python
import math
print(math.pi)
print(math.sqrt(16))
print(math.pow(2, 3))
print(math.ceil(4.2))
print(math.floor(4.9))
```

**Expected output** (each value is the function's result as the book's run
shows it):

```output
3.141592653589793
4.0
8.0
5
4
```

- `sqrt(16)` — square root, always a float (`4.0`).
- `pow(2, 3)` — 2 to the power 3 = 8.0; `pow` returns a float too.
- `ceil(4.2)` — rounds **up** to the next whole number: 5.
- `floor(4.9)` — drops the decimal: 4.
- `math.pi` — the constant 3.141592653589793.

Note ceil and floor answered `5` and `4` — plain ints — while sqrt and pow
kept their `.0`. Running the fence below and editing the numbers is the
fastest way to lock that in.
''',
            'exercises': [
                {
                    'slug': 'predict-math-results',
                    'title': 'Predict the math Results',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'What does this print? One line per statement.'
                    ),
                    'context': (
                        'import math\n'
                        'print(math.sqrt(25))\n'
                        'print(math.ceil(3.1))\n'
                        'print(math.floor(3.9))'
                    ),
                    'expected_output': '5.0\n4\n3',
                    'explain': (
                        'sqrt returns a float (5.0); ceil(3.1) rounds up to '
                        '4; floor(3.9) drops the decimal to 3 — the exact '
                        'int/float behaviour of the book program. Sindh '
                        'Board Class XI, Unit 3, 3.6.1 (math), pp. 128-129.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.6.1 math functions', '128-129', CLASS),
                    'hints': [
                        'sqrt keeps the .0; ceil and floor return plain ints.',
                        'Solution: 5.0 / 4 / 3.',
                    ],
                },
                {
                    'slug': 'hypotenuse-with-math',
                    'title': 'Hypotenuse with math.sqrt',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read two integers — the sides of a right triangle — '
                        'and print the hypotenuse using math.sqrt on the '
                        'sum of their squares.'
                    ),
                    'context': (
                        'Applies math.sqrt (pp. 128-129) to the exponent '
                        'operator ** from p. 106.'
                    ),
                    'constraints': 'import math and print exactly one value.',
                    'expected_behavior': 'For inputs 3 and 4 the program prints: 5.0',
                    'explain': (
                        'sqrt(3² + 4²) = sqrt(25) = 5.0 — sqrt always '
                        'returns a float. Sindh Board Class XI, Unit 3, '
                        '3.6.1 (math), pp. 128-129.'
                    ),
                    'starter_code': (
                        'import math\n'
                        'a = int(input())\n'
                        'b = int(input())\n\n'
                    ),
                    'solution_code': (
                        'import math\n'
                        'a = int(input())\n'
                        'b = int(input())\n'
                        'print(math.sqrt(a ** 2 + b ** 2))\n'
                    ),
                    'test_cases': [
                        {'input': '3\n4\n', 'expected_output': '5.0'},
                        {'input': '6\n8\n', 'expected_output': '10.0'},
                    ],
                    'xp_reward': 90,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.6.1 math.sqrt', '128-129', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'a ** 2 squares a (Unit 3 arithmetic, p. 106).',
                        'math.sqrt(a ** 2 + b ** 2)',
                    ],
                },
            ],
        },

        # ── random + datetime ──────────────────────────────────────────────
        {
            'slug': 'random-and-datetime',
            'title': 'The random and datetime Libraries',
            'content_type': 'interactive',
            'learning_objective': (
                'Explain what random.randint / random / uniform produce and '
                'how datetime.now() with strftime formats dates and times.'
            ),
            'order': 3,
            'duration_minutes': 14,
            'xp_reward': 55,
            'reference': ref(UNIT, '3.6.1 Built-in Libraries — random and datetime', '128-131', CLASS),
            'content_body': '''# The random Library

`random` produces numbers you cannot predict — which is exactly why the
book uses it for the guess-the-number game (activity 2, p. 138). Its three
functions (pp. 128-130):

```python
import random
print(random.randint(1, 10))
print(random.random())
print(random.uniform(1, 5))
```

```text
7
0.8444218515250481
3.6189376645882186
```

- `randint(1, 10)` — a whole number **between 1 and 10, both included**.
- `random()` — a float between 0 and 1.
- `uniform(1, 5)` — a float anywhere between 1 and 5.

Run the fence above a few times: no two runs match. That is the honest
reason this lesson never asks you to "predict" random output — a sample
run only shows *one* possible answer.

# The datetime Library

`datetime` tells you today's date and time (pp. 128-130):

```python
import datetime
now = datetime.datetime.now()
print(now.strftime("%d-%m-%Y"))
print(now.strftime("%I:%M %p"))
```

```text
01-11-2026
10:35 AM
```

`strftime` is the formatting dial: `%d` day, `%m` month, `%Y` four-digit
year, `%I` hour (12-hour clock), `%M` minutes, `%p` AM/PM. The transcript
above was produced on the day this course was built — tomorrow it differs,
so datetime items are reasoning items, never graded by output comparison.

# Activity — Report Card Generator (pp. 130-131)

The book's activity combines all three libraries: **random** generates each
subject's marks, **math** rounds the average (ceil/floor), and **datetime**
stamps the printed card with the current date. A 48-line program with a
full sample run — grades computed, average rounded, date header on top.
Open your VS Code, build a mini version: three `randint(40, 100)` marks,
their average with `round()`, and a `strftime("%d-%m-%Y")` header. The
book deliberately leaves the layout to you.
''',
            'exercises': [
                {
                    'slug': 'which-function-gives-random-integer',
                    'title': 'Random Whole Numbers',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which function returns a random whole number '
                        'between 1 and 10, both included?'
                    ),
                    'explain': (
                        'random.randint(1, 10) — the integer cousin of '
                        'random() and uniform(). Sindh Board Class XI, '
                        'Unit 3, 3.6.1 (random), pp. 128-130.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'random.randint(1, 10)', 'is_correct': True},
                        {'id': 'b', 'text': 'random.random()', 'is_correct': False},
                        {'id': 'c', 'text': 'math.ceil(1, 10)', 'is_correct': False},
                        {'id': 'd', 'text': 'randrange.upTo(10)', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.6.1 random.randint', '129', CLASS),
                },
                {
                    'slug': 'strftime-format-code',
                    'title': 'Reading strftime Codes',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'In the book\'s datetime example, what does the '
                        'format string "%d-%m-%Y" produce?'
                    ),
                    'explain': (
                        'Day-Month-Year with a four-digit year, e.g. '
                        '01-11-2026 — the exact transcript line of the '
                        'lesson. %I:%M %p is the clock-time format. Sindh '
                        'Board Class XI, Unit 3, 3.6.1 (datetime.strftime), '
                        'pp. 129-130.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'A date like 01-11-2026', 'is_correct': True},
                        {'id': 'b', 'text': 'A time like 10:35 AM', 'is_correct': False},
                        {'id': 'c', 'text': 'The number of seconds since midnight', 'is_correct': False},
                        {'id': 'd', 'text': 'A random integer', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '3.6.1 datetime strftime', '129-130', CLASS),
                },
            ],
        },

        # ── third-party ────────────────────────────────────────────────────
        {
            'slug': 'third-party-libraries',
            'title': 'Third-Party Libraries',
            'content_type': 'text',
            'learning_objective': (
                'Install third-party packages with pip and match Numpy, '
                'Pandas and Matplotlib to their jobs.'
            ),
            'order': 4,
            'duration_minutes': 8,
            'xp_reward': 40,
            'reference': ref(UNIT, '3.6.2 Third Party Libraries', '132', CLASS),
            'content_body': '''# Third-Party Libraries

Built-in libraries ship with Python. **Third-party libraries** are written
by the wider community and installed yourself with the **pip** tool, from
the template on p. 132:

```text
pip install library_name
```

The book introduces three, each with a one-line purpose:

| Library | Job (p. 132) |
|---|---|
| **Numpy** | numerical computing |
| **Pandas** | data analysis |
| **Matplotlib** | drawing graphs |

These three are the reason the career section (pp. 93-94, 134) connects
Python to Data Science: a Data Analyst's daily tools are exactly Numpy,
Pandas and Matplotlib. Installation happens in the terminal — the Top
Menus Bar's Terminal entry (Figure 3.x tour, p. 95) opens it inside VS
Code.
''',
            'exercises': [
                {
                    'slug': 'which-library-draws-graphs',
                    'title': 'Which Library Draws Graphs?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which third-party library does the book assign to '
                        'drawing graphs?'
                    ),
                    'explain': (
                        'Matplotlib — the p. 132 table: Numpy for numerical '
                        'computing, Pandas for data analysis, Matplotlib '
                        'for graphs. Sindh Board Class XI, Unit 3, 3.6.2, '
                        'p. 132.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Matplotlib', 'is_correct': True},
                        {'id': 'b', 'text': 'Numpy', 'is_correct': False},
                        {'id': 'c', 'text': 'Pandas', 'is_correct': False},
                        {'id': 'd', 'text': 'math', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.6.2 Third Party Libraries', '132', CLASS),
                },
                {
                    'slug': 'install-tool',
                    'title': 'Installing a Package',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which command installs a third-party library in '
                        'Python?'
                    ),
                    'explain': (
                        'pip — section 3.6.2 gives the exact form '
                        '"pip install library_name". Sindh Board Class XI, '
                        'Unit 3, 3.6.2, p. 132.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'pip install library_name', 'is_correct': True},
                        {'id': 'b', 'text': 'import library_name', 'is_correct': False},
                        {'id': 'c', 'text': 'python run library_name', 'is_correct': False},
                        {'id': 'd', 'text': 'download library_name', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '3.6.2 pip', '132', CLASS),
                },
            ],
        },

        # ── 3.7 debugging ──────────────────────────────────────────────────
        {
            'slug': 'debugging-and-tracebacks',
            'title': 'Debugging and Tracebacks',
            'content_type': 'interactive',
            'learning_objective': (
                'Tell syntax, runtime and logical errors apart, and read a '
                'traceback to find the offending line.'
            ),
            'order': 5,
            'duration_minutes': 14,
            'xp_reward': 55,
            'reference': ref(UNIT, '3.7 Debugging Code in Python', '132-133', CLASS),
            'content_body': '''# Debugging

**Debugging** (p. 132) is the work of finding and fixing errors. The book
sorts every error into three types, each with its own example:

| Type | When it happens | Book example |
|---|---|---|
| **Syntax error** | the code breaks Python's grammar; it never starts | a missing closing parenthesis |
| **Runtime error / exception** | starts fine, crashes mid-run | `x = 10 / 0` |
| **Logical error** | runs to the end, silently gives wrong answers | `i -= 1` where you meant `i += 1` — an endless loop |

A syntax error is the compiler catching a typo; a runtime error is the
program meeting reality (dividing by zero); a logical error is *you* being
wrong while Python does exactly what you said — the dangerous kind.

## Reading tracebacks (p. 133)

When Python crashes it prints a **traceback** naming the error **type** and
the **place** — file and line number. The book's two specimens:

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

from `x = int("abc")` — the text 'abc' is not a whole number.

```text
IndentationError: expected an indented block
```

when the body after `if b > a:` was left flush at column 0 — the same rule
you drilled in Chapter 2.

Fix it yourself: the program below has a syntax error. Run it, read the
message, then correct the line.

```python
total = 0
for i in range(1, 4)
    total = total + i
print(total)
```
''',
            'exercises': [
                {
                    'slug': 'missing-parenthesis-error-type',
                    'title': 'Which Error Type?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Forgetting a closing parenthesis is which of the '
                        'book\'s three error types?'
                    ),
                    'explain': (
                        'A syntax error — the code breaks the grammar rule '
                        'and never starts. 10 / 0 is the runtime example and '
                        'the i -= 1 endless loop the logical one. Sindh '
                        'Board Class XI, Unit 3, 3.7, p. 132.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Syntax error', 'is_correct': True},
                        {'id': 'b', 'text': 'Runtime error / exception', 'is_correct': False},
                        {'id': 'c', 'text': 'Logical error', 'is_correct': False},
                        {'id': 'd', 'text': 'Library error', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.7 Three types of errors', '132', CLASS),
                },
                {
                    'slug': 'int-abc-traceback',
                    'title': 'Read the Traceback',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Which error does `x = int("abc")` raise, according '
                        'to the traceback example on p. 133?'
                    ),
                    'explain': (
                        'ValueError: invalid literal for int() with base 10: '
                        "'abc' — a runtime exception, because 'abc' simply "
                        'is not a number. Sindh Board Class XI, Unit 3, 3.7 '
                        '(Reading Error Messages), p. 133.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'ValueError', 'is_correct': True},
                        {'id': 'b', 'text': 'IndentationError', 'is_correct': False},
                        {'id': 'c', 'text': 'SyntaxError', 'is_correct': False},
                        {'id': 'd', 'text': 'ZeroDivisionError', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '3.7 Traceback example 1', '133', CLASS),
                },
                {
                    'slug': 'fix-the-missing-colon',
                    'title': 'Fix the Missing Colon',
                    'exercise_type': 'debugging',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'This program crashes before it runs: the `for` line '
                        'is missing its colon. Fix it so it prints 6.'
                    ),
                    'context': (
                        'Syntax errors are the p. 132 category — the colon '
                        'after a compound statement header is Python\'s '
                        'grammar rule you met in 3.5.2 (p. 116).'
                    ),
                    'constraints': 'Change punctuation only; the answer must be 6.',
                    'expected_behavior': 'The fixed program prints: 6',
                    'explain': (
                        'Every for header ends with a colon; with it, range'
                        '(1, 4) yields 1+2+3 = 6 — the IndentationError and '
                        'SyntaxError examples both live in 3.7. Sindh Board '
                        'Class XI, Unit 3, 3.7, pp. 132-133 (colon rule '
                        '116).'
                    ),
                    'starter_code': (
                        'total = 0\n'
                        'for i in range(1, 4)\n'
                        '    total = total + i\n'
                        'print(total)\n'
                    ),
                    'solution_code': (
                        'total = 0\n'
                        'for i in range(1, 4):\n'
                        '    total = total + i\n'
                        'print(total)\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '6'},
                    ],
                    'xp_reward': 80,
                    'order': 3,
                    'reference': ref(UNIT, '3.7 Syntax errors', '132', CLASS),
                    'hints': [
                        'Read like a traceback: which line does Python point at?',
                        'Solution: add : at the end of the for line.',
                    ],
                },
                {
                    'slug': 'divide-by-zero-error-type',
                    'title': 'The 10 / 0 Crash',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'The book\'s `x = 10 / 0` example is which error '
                        'type?'
                    ),
                    'explain': (
                        'A runtime error (exception): the program starts '
                        'fine and crashes only when the division actually '
                        'runs. Sindh Board Class XI, Unit 3, 3.7, p. 132.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Runtime error / exception', 'is_correct': True},
                        {'id': 'b', 'text': 'Syntax error', 'is_correct': False},
                        {'id': 'c', 'text': 'Logical error', 'is_correct': False},
                        {'id': 'd', 'text': 'Import error', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 4,
                    'reference': ref(UNIT, '3.7 Runtime errors', '132', CLASS),
                },
            ],
        },

        # ── unit-exercise challenges ───────────────────────────────────────
        {
            'slug': 'guess-the-number-challenge',
            'title': 'Challenge — Guess the Number',
            'content_type': 'interactive',
            'learning_objective': (
                'Combine random, while and if-else into the number-guessing '
                'game the unit exercise asks for.'
            ),
            'order': 6,
            'duration_minutes': 15,
            'xp_reward': 60,
            'reference': ref(UNIT, 'EXERCISE 5 (ii) — Guess the Number game', '138', CLASS),
            'content_body': '''# Challenge: Guess the Number

Activity 2 of the unit exercise (p. 138): a **guess-the-number game using
the random module**. Everything it needs has now been taught — `randint`
to pick the secret, `input()` to collect guesses, a `while` loop to keep
asking, and `if-else` to judge each try.

The loop shape, with the book's tools:

```python
import random
secret = random.randint(1, 10)
guess = 0
while guess != secret:
    guess = int(input("Your guess: "))
    if guess < secret:
        print("Too low")
    elif guess > secret:
        print("Too high")
print("Correct!")
```

Because `randint` is random, this program **cannot be graded by output
comparison** — no two runs are alike (see why in the random lesson). Your
task below fixes the one thing a grader can check: a version whose secret
is a known value, played exactly like the book's game.
''',
            'exercises': [
                {
                    'slug': 'guess-fixed-secret',
                    'title': 'Play the Game with a Known Secret',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'hard',
                    'instructions': (
                        'The secret is 7 (already written). Loop: read a '
                        'guess, print `Too low` or `Too high` while it is '
                        'wrong, and print `Correct!` and stop when it is '
                        'right.'
                    ),
                    'context': (
                        'The guess-the-number game (p. 138) with the random '
                        'seed pinned down so the grader can test the loop '
                        'logic itself.'
                    ),
                    'constraints': (
                        'One line per guess; `Correct!` includes the '
                        'exclamation mark and appears exactly once.'
                    ),
                    'expected_behavior': (
                        'Guesses 5, 9, 7 print Too low, Too high, Correct! '
                        'on three lines.'
                    ),
                    'explain': (
                        'while guess != secret keeps the game alive; the '
                        'if/elif compare against the secret, and reaching '
                        'equality ends the loop and prints Correct! — the '
                        'same skeleton the book activity draws, with a '
                        'fixed secret for grading. Sindh Board Class XI, '
                        'Unit 3, EXERCISE 5 (ii), p. 138 (while p. 123, '
                        'if-elif p. 118).'
                    ),
                    'starter_code': (
                        'secret = 7\n'
                        'guess = 0\n'
                        '# loop until the guess equals the secret\n\n\n\n\n'
                        'print("Correct!")\n'
                    ),
                    'solution_code': (
                        'secret = 7\n'
                        'guess = 0\n'
                        'while guess != secret:\n'
                        '    guess = int(input())\n'
                        '    if guess < secret:\n'
                        '        print("Too low")\n'
                        '    elif guess > secret:\n'
                        '        print("Too high")\n'
                        'print("Correct!")\n'
                    ),
                    'test_cases': [
                        {'input': '5\n9\n7\n', 'expected_output': 'Too low\nToo high\nCorrect!'},
                        {'input': '7\n', 'expected_output': 'Correct!'},
                    ],
                    'xp_reward': 120,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE 5 (ii) — Guess the Number', '138', CLASS),
                    'hints': [
                        'The loop condition compares guess with secret.',
                        'Inside: read a guess, then if / elif for Too low / Too high.',
                    ],
                },
                {
                    'slug': 'random-not-output-gradable',
                    'title': 'Why Random Cannot Be Predicted',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Why can a program using random.randint(1, 10) '
                        'never be graded by comparing its printed output '
                        'to a fixed answer?'
                    ),
                    'explain': (
                        'Every run may draw a different number — output '
                        'comparison needs a deterministic result. That is '
                        'why this platform grades deterministic parts only '
                        '(the reasoning items), never random or datetime '
                        'transcripts. Sindh Board Class XI, Unit 3, 3.6.1 '
                        '(random), pp. 128-130; activity p. 138.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Because each run can produce a different number', 'is_correct': True},
                        {'id': 'b', 'text': 'Because randint returns only even numbers', 'is_correct': False},
                        {'id': 'c', 'text': 'Because random() must be imported twice', 'is_correct': False},
                        {'id': 'd', 'text': 'Because Python cannot print random values', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '3.6.1 random', '128-130', CLASS),
                },
            ],
        },
        {
            'slug': 'atm-simulation-challenge',
            'title': 'Challenge — ATM Simulation',
            'content_type': 'interactive',
            'learning_objective': (
                'Bring the whole unit together in the book\'s final activity: '
                'a menu-driven ATM with PIN check, deposit, withdraw and '
                'balance.'
            ),
            'order': 7,
            'duration_minutes': 20,
            'xp_reward': 70,
            'reference': ref(UNIT, 'EXERCISE 5 (iii) — ATM Simulation', '138', CLASS),
            'content_body': '''# Challenge: ATM Simulation

The unit's last activity (p. 138) is the boss fight: an **ATM simulation**
with a PIN check, a menu that repeats, **deposit**, **withdraw**, and
**balance** — the book prints a full sample transcript of one session.

It is "detailed" precisely because everything from Unit 3 shows up:

- `input()` with conversion (pp. 102-103)
- if-else for the PIN and menu choices (pp. 116-118)
- a `while` loop so the machine stays logged in until the user quits
  (p. 123)
- an accumulator variable as the balance (p. 115)

A skeleton in the book's spirit — read the shape, then build the full
machine yourself. The sample transcript below is one pinned-down session
so a grader can check it: PIN 1234, then 1) deposit 500, 2) deposit 400,
3) withdraw 200, 4) show balance, 5) quit.

```text
1234
1
500
1
400
2
200
3
700.0
4
Bye
```

The `700.0` line is the whole session in one number: 0 + 500 + 400 - 200.
''',
            'exercises': [
                {
                    'slug': 'atm-menu-machine',
                    'title': 'Build the ATM',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'hard',
                    'instructions': (
                        'Read the PIN (correct PIN is 1234). If wrong, print '
                        '`Wrong PIN` and stop. If right, loop reading menu '
                        'choices: `1` then a deposit amount adds it, `2` '
                        'then a withdrawal amount subtracts it, `3` prints '
                        'the current balance, `4` prints `Bye` and ends. '
                        'Amounts are floats.'
                    ),
                    'context': (
                        'The ATM simulation activity (p. 138): PIN attempt, '
                        'menu, deposit, withdraw, balance.'
                    ),
                    'constraints': (
                        'Read choice and amount each with their own input() '
                        'line. Print the balance exactly as Python shows '
                        'the float, and Bye on quit.'
                    ),
                    'expected_behavior': (
                        '1234 / 1 / 500 / 1 / 400 / 2 / 200 / 3 / 4 prints '
                        '700.0 then Bye.'
                    ),
                    'explain': (
                        'The PIN test is the if-else of p. 117; the menu is '
                        'the while + if-elif ladder pattern of pp. 118 and '
                        '123; the balance is an accumulator (p. 115) and '
                        'float conversion (p. 103). Together they form the '
                        'book\'s ATM activity. Sindh Board Class XI, Unit 3, '
                        'EXERCISE 5 (iii), p. 138.'
                    ),
                    'starter_code': (
                        'CORRECT_PIN = "1234"\n'
                        'balance = 0.0\n'
                        'pin = input()\n'
                        'if pin != CORRECT_PIN:\n'
                        '    print("Wrong PIN")\n'
                        'else:\n'
                        '    choice = input()\n'
                        '    while choice != "4":\n'
                        '# 1 deposit, 2 withdraw, 3 print balance — inside the loop\n\n\n\n\n\n\n'
                        '    print("Bye")\n'
                    ),
                    'solution_code': (
                        'CORRECT_PIN = "1234"\n'
                        'balance = 0.0\n'
                        'pin = input()\n'
                        'if pin != CORRECT_PIN:\n'
                        '    print("Wrong PIN")\n'
                        'else:\n'
                        '    choice = input()\n'
                        '    while choice != "4":\n'
                        '        if choice == "1":\n'
                        '            balance = balance + float(input())\n'
                        '        elif choice == "2":\n'
                        '            balance = balance - float(input())\n'
                        '        elif choice == "3":\n'
                        '            print(balance)\n'
                        '        choice = input()\n'
                        '    print("Bye")\n'
                    ),
                    'test_cases': [
                        {
                            'input': '1234\n1\n500\n1\n400\n2\n200\n3\n4\n',
                            'expected_output': '700.0\nBye',
                        },
                        {
                            'input': '9999\n',
                            'expected_output': 'Wrong PIN',
                        },
                        {
                            'input': '1234\n3\n4\n',
                            'expected_output': '0.0\nBye',
                        },
                    ],
                    'xp_reward': 150,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE 5 (iii) — ATM Simulation', '138', CLASS),
                    'hints': [
                        'Menu choices are strings from input() — compare with "1", "2", "3", "4".',
                        'Deposit and withdraw each read one more line: the amount.',
                        'Solution: balance = balance + float(input()) for 1, - for 2, print(balance) for 3, and choice = input() at the loop bottom.',
                    ],
                },
            ],
        },
    ],
}
