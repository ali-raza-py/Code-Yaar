"""
Class XI, Unit 3 — chapter 3: Input/Output Handling and Operators

    3.4.2 Input Output Handling      (printed pp. 101-105)
    3.4.3 Operators and Operands     (printed pp. 105-115)

Every example value shown in the lessons (10/3 = 3.333..., the assignment
chain, the relational True/False sequence, the bitwise results 2/14/12/-11,
the shift results) is the book's own printed output — see
textbooks/CLASS-XI-SOURCE-VERIFICATION.md.
"""

from .common import ref

UNIT = 'Unit 3'
CLASS = 'Class XI'


CHAPTER_IO_OPS = {
    'slug': 'xi-io-and-operators',
    'title': 'Input/Output and Operators',
    'description': (
        'print in its different forms, f-strings and input(); then the six '
        'operator families the book devotes ten pages to: arithmetic, '
        'assignment, relational, logical, membership and bitwise.'
    ),
    'order': 3,
    'xp_reward': 700,
    'reference': ref(UNIT, '3.4.2-3.4.3 Input Output Handling, Operators and Operands', '101-115', CLASS),
    'lessons': [
        # ── 3.4.2 (print) ──────────────────────────────────────────────────
        {
            'slug': 'printing-output',
            'title': 'Printing Output — print and f-strings',
            'content_type': 'interactive',
            'learning_objective': (
                'Use print() with multiple values and with f-strings, and '
                'explain how each form builds its output.'
            ),
            'order': 1,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.4.2 Input Output Handling — print()', '101-102', CLASS),
            'content_body': '''# Printing Output

`print()` is how every program in this book talks to the learner. Figure
3.15 (p. 101) collects its syntax forms; Example 1 (p. 102) shows the
different faces:

```python
a = 10
b = 20
print(a, b)
print("Sum =", a + b)
print(f"The sum of {a} and {b} is {a + b}")
```

**Expected output:**

```output
10 20
Sum = 30
The sum of 10 and 20 is 30
```

- Comma-separated values print side by side with a space between them.
- Text and values can be joined into one message.
- An **f-string** starts with `f` before the quotes and drops expressions
  straight into `{curly braces}` — the form the book returns to again and
  again (the Shopping Bill program on p. 126 uses f-strings with `:.2f` for
  money).
''',
            'exercises': [
                {
                    'slug': 'predict-print-forms',
                    'title': 'Predict the Three print Forms',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Type exactly what this program prints, one line per '
                        'print statement.'
                    ),
                    'context': (
                        'x = 5\n'
                        'y = 4\n'
                        'print(x, y)\n'
                        'print("Product =", x * y)\n'
                        'print(f"{x} times {y} equals {x * y}")'
                    ),
                    'expected_output': '5 4\nProduct = 20\n5 times 4 equals 20',
                    'explain': (
                        'Comma-separated values join with a space; the string '
                        'and product combine as "Product = 20"; the f-string '
                        'substitutes 5, 4 and 20 into the sentence. Sindh '
                        'Board Class XI, Unit 3, 3.4.2 (Figure 3.15, Example '
                        '1), pp. 101-102.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.4.2 print() syntax forms', '101-102', CLASS),
                    'hints': [
                        'print(x, y) puts a single space between the values.',
                        'Every {expression} in the f-string is replaced by its value.',
                        'Solution: 5 4 / Product = 20 / 5 times 4 equals 20 (three lines).',
                    ],
                },
                {
                    'slug': 'greet-the-user',
                    'title': 'Input and a Welcome Message',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Read one line of input — a name — and print the '
                        'greeting `Hello, Ali!` for the name Ali. Use an '
                        'f-string or concatenation.'
                    ),
                    'context': (
                        'This is the book\'s own Example 1 for input() (pp. '
                        '102-103: a name greeting), and activity 1 on p. 105 '
                        '("input + display program").'
                    ),
                    'constraints': (
                        'Read exactly one value with input() and print '
                        'exactly one line, ending with `!`.'
                    ),
                    'expected_behavior': 'For input "Ali" the program prints: Hello, Ali!',
                    'explain': (
                        'input() delivers what the user typed; the greeting '
                        'places it inside the message. Sindh Board Class XI, '
                        'Unit 3, 3.4.2 Example 1, pp. 102-103; Activity, '
                        'p. 105.'
                    ),
                    'starter_code': (
                        'name = input()\n'
                        '# print Hello, <name>! below\n\n'
                    ),
                    'solution_code': (
                        'name = input()\n'
                        'print(f"Hello, {name}!")\n'
                    ),
                    'test_cases': [
                        {'input': 'Ali\n', 'expected_output': 'Hello, Ali!'},
                        {'input': 'Ayesha\n', 'expected_output': 'Hello, Ayesha!'},
                    ],
                    'xp_reward': 80,
                    'order': 2,
                    'reference': ref(UNIT, '3.4.2 Example 1 — name greeting', '102-103', CLASS),
                    'hints': [
                        'input() already gave you the name; you only need print().',
                        'print(f"Hello, {name}!") builds the greeting with an f-string.',
                    ],
                },
                {
                    'slug': 'input-returns-a-string',
                    'title': 'What Does input() Return?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'What type of value does input() always return?'
                    ),
                    'explain': (
                        'input() always returns a string, even when the user '
                        'types digits — which is why int() and float() exist. '
                        'Sindh Board Class XI, Unit 3, 3.4.2, p. 102; '
                        'EXERCISE A (viii), p. 136.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'String', 'is_correct': True},
                        {'id': 'b', 'text': 'Integer', 'is_correct': False},
                        {'id': 'c', 'text': 'Float', 'is_correct': False},
                        {'id': 'd', 'text': 'It depends on what the user types', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE A (viii)', '136', CLASS),
                },
            ],
        },

        # ── 3.4.2 (input + conversion) ─────────────────────────────────────
        {
            'slug': 'reading-input-and-converting-types',
            'title': 'Reading Input and Converting Types',
            'content_type': 'interactive',
            'learning_objective': (
                'Read numbers with int(input()) / float(input()) and explain '
                'why the conversion is needed.'
            ),
            'order': 2,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.4.2 Input Output Handling — input()', '102-105', CLASS),
            'content_body': '''# Reading Input

`input()` asks the user to type something and hands it to your program —
but **always as a string** (p. 102):

```python
variable = input("Prompt message: ")
```

That single fact causes the classic beginner bug. Two inputs holding `5` and
`7` added without conversion produce `57`, not `12` — Python joined two
strings. The book\'s Example 2 (pp. 102-103) shows the fix, wrapping input
in a conversion:

```python
age = int(input("Enter age: "))
weight = float(input("Enter weight: "))
print(age + 1)
```

**Expected output** when the user types `16` and then `52.5`:

```output
Enter age: Enter weight: 17
```

`int()` turns a string like `"16"` into a whole number, `float()` turns
`"52.5"` into a decimal. "Instructions for Teachers" (p. 103) exists
precisely to make the class demonstrate this string-to-type conversion.

> Verified run: the checker feeds `16` then `52.5` to the sample above.
''',
            'exercises': [
                {
                    'slug': 'string-vs-number-addition',
                    'title': 'The 57 Trap',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'The user types 5 on the first line and 7 on the '
                        'second. What does the program print?'
                    ),
                    'context': (
                        'a = input()\n'
                        'b = input()\n'
                        'print(a + b)'
                    ),
                    'expected_output': '57',
                    'explain': (
                        'input() returns strings (p. 102), and + between two '
                        'strings joins them: "5" + "7" is "57". Convert with '
                        'int() first to add numbers. Sindh Board Class XI, '
                        'Unit 3, 3.4.2, pp. 102-103.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.4.2 input() returns a string', '102-103', CLASS),
                    'hints': [
                        'Nothing here calls int() — what type are a and b?',
                        'Solution: 57 (the two strings joined, not added).',
                    ],
                },
                {
                    'slug': 'area-of-a-rectangle',
                    'title': 'Area of a Rectangle',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read two integers — length, then width — each on '
                        'its own line, and print their product: the area.'
                    ),
                    'context': (
                        'Supplementary practice around 3.4.2\'s Example 2: '
                        'numbers only add after int() converts them (pp. '
                        '102-103).'
                    ),
                    'constraints': (
                        'Use int(input()) for both values and print one '
                        'number.'
                    ),
                    'expected_behavior': 'For inputs 5 and 4 the program prints: 20',
                    'explain': (
                        'Each input() line is a string; int() converts before '
                        'the multiplication, so 5 * 4 gives 20. Sindh Board '
                        'Class XI, Unit 3, 3.4.2 Example 2, pp. 102-103.'
                    ),
                    'starter_code': (
                        'length = int(input())\n'
                        'width = int(input())\n'
                        '# print the area below\n'
                    ),
                    'solution_code': (
                        'length = int(input())\n'
                        'width = int(input())\n'
                        'print(length * width)\n'
                    ),
                    'test_cases': [
                        {'input': '5\n4\n', 'expected_output': '20'},
                        {'input': '10\n3\n', 'expected_output': '30'},
                    ],
                    'xp_reward': 90,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.4.2 input() with int() conversion', '102-103', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'The starter already converted the inputs — now multiply.',
                        'print(length * width)',
                    ],
                },
            ],
        },

        # ── 3.4.3 arithmetic ───────────────────────────────────────────────
        {
            'slug': 'arithmetic-operators',
            'title': 'Arithmetic Operators',
            'content_type': 'interactive',
            'learning_objective': (
                'Use +, -, *, /, //, % and ** and predict their results, '
                'including the difference between / and //.'
            ),
            'order': 3,
            'duration_minutes': 14,
            'xp_reward': 55,
            'reference': ref(UNIT, '3.4.3 Operators — Arithmetic', '105-106', CLASS),
            'content_body': '''# Arithmetic Operators

`ArithmeticOperatorProgram.py` (pp. 105-106) puts all eight operators
through `a = 10` and `b = 3`:

```python
a = 10
b = 3
print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a // b)
print(a % b)
print(a ** b)
```

**Expected output** (the book's own run):

```output
13
7
30
3.3333333333333335
3
1
1000
```

The three that examiners love:

- `/` is **true division** — it always returns a float, even when the
  numbers divide exactly.
- `//` is **floor division** — it divides and chops off the decimal part,
  keeping the whole-number result (`10 // 3` is `3`).
- `%` is the **remainder** (`10 % 3` is `1` — how much is left over).
- `**` is **exponent** — `10 ** 3` means 10 to the power 3, i.e. 1000.
''',
            'exercises': [
                {
                    'slug': 'predict-floor-division',
                    'title': 'Predict 10 // 3 and 10 % 3',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'What does this program print? One line per statement.'
                    ),
                    'context': (
                        'a = 10\n'
                        'b = 3\n'
                        'print(a // b)\n'
                        'print(a % b)'
                    ),
                    'expected_output': '3\n1',
                    'explain': (
                        '10 // 3 floor-divides to 3 and 10 % 3 leaves '
                        'remainder 1 — exactly the book program\'s lines. '
                        'Sindh Board Class XI, Unit 3, 3.4.3 '
                        '(ArithmeticOperatorProgram.py), pp. 105-106.'
                    ),
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.4.3 Arithmetic — // and %', '105-106', CLASS),
                    'hints': [
                        '// keeps the whole part of the division; % keeps the remainder.',
                        'Solution: 3 then 1.',
                    ],
                },
                {
                    'slug': 'quotient-and-remainder',
                    'title': 'Quotient and Remainder',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Read two integers (dividend first, then divisor) '
                        'and print the quotient on one line and the '
                        'remainder on the next.'
                    ),
                    'context': (
                        'The same // and % pair from '
                        'ArithmeticOperatorProgram.py, applied to new '
                        'numbers.'
                    ),
                    'constraints': 'Print exactly two lines: quotient first, remainder second.',
                    'expected_behavior': 'For inputs 17 and 5 the program prints 3 then 2.',
                    'explain': (
                        '17 // 5 is 3 (whole times 5 fits into 17) and 17 % 5 '
                        'is 2 (what remains). Sindh Board Class XI, Unit 3, '
                        '3.4.3, pp. 105-106.'
                    ),
                    'starter_code': (
                        'dividend = int(input())\n'
                        'divisor = int(input())\n'
                        '# print quotient, then remainder\n\n\n'
                    ),
                    'solution_code': (
                        'dividend = int(input())\n'
                        'divisor = int(input())\n'
                        'print(dividend // divisor)\n'
                        'print(dividend % divisor)\n'
                    ),
                    'test_cases': [
                        {'input': '17\n5\n', 'expected_output': '3\n2'},
                        {'input': '20\n4\n', 'expected_output': '5\n0'},
                    ],
                    'xp_reward': 80,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.4.3 Arithmetic operators', '105-106', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        '// gives the quotient, % gives the remainder.',
                        'print(dividend // divisor) then print(dividend % divisor).',
                    ],
                },
                {
                    'slug': 'the-exponent-operator',
                    'title': 'Which Operator Raises to a Power?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which operator computes 10 to the power 3 (giving '
                        '1000)?'
                    ),
                    'explain': (
                        '** is the exponent operator: 10 ** 3 = 1000 in the '
                        'book program. // only floor-divides, % only returns '
                        'the remainder. Sindh Board Class XI, Unit 3, 3.4.3, '
                        'p. 106.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '**', 'is_correct': True},
                        {'id': 'b', 'text': '//', 'is_correct': False},
                        {'id': 'c', 'text': '%', 'is_correct': False},
                        {'id': 'd', 'text': '*', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, '3.4.3 Arithmetic — **', '106', CLASS),
                },
            ],
        },

        # ── 3.4.3 assignment ───────────────────────────────────────────────
        {
            'slug': 'assignment-operators',
            'title': 'Assignment Operators',
            'content_type': 'interactive',
            'learning_objective': (
                'Follow a chain of augmented assignments (=, +=, -=, *=, /=, '
                '//=, **=, %=) and predict each value of the variable.'
            ),
            'order': 4,
            'duration_minutes': 10,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.4.3 Operators — Assignment', '107', CLASS),
            'content_body': '''# Assignment Operators

The assignment table (p. 107) lists `=`, `+=`, `-=`, `*=`, `/=` and the
rest. Each augmented assignment does the arithmetic and stores the result
back into the same variable in one step.

The book's program starts from `a = 10` and runs one line after another —
trace it before pressing Run:

```python
a = 10
print(a)
a += 5
print(a)
a -= 3
print(a)
a *= 2
print(a)
a /= 4
print(a)
a //= 2
print(a)
a **= 3
print(a)
a %= 25
print(a)
```

**Expected output** — the chain exactly as the textbook prints it (p. 107):

```output
10
15
12
24
6.0
3.0
27.0
2.0
```

Watch what `/=` does: `12 /= 2` gives `6.0`, not `6` — true division
returns a float and keeps the decimal. The next line `//= 2` floor-divides
back to `3.0`, `**= 3` raises it to `27.0`, and `%= 25` leaves `2.0`.
''',
            'exercises': [
                {
                    'slug': 'continue-the-chain',
                    'title': 'Continue the Chain',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Starting where the book\'s chain ends (a = 2.0), '
                        'what does the next line print?'
                    ),
                    'context': (
                        'a = 10\n'
                        'a += 5\n'
                        'a -= 3\n'
                        'a *= 4\n'
                        'a /= 4\n'
                        'a //= 2\n'
                        'a **= 3\n'
                        'a %= 25\n'
                        'a += 0.5\n'
                        'print(a)'
                    ),
                    'expected_output': '2.5',
                    'explain': (
                        'The book chain ends at 2.0 (p. 107); adding 0.5 '
                        'gives 2.5. Keep the .0 — a stays a float after '
                        '/=. Sindh Board Class XI, Unit 3, 3.4.3 '
                        '(Assignment), p. 107.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.4.3 Assignment — augmented chain', '107', CLASS),
                    'hints': [
                        'The first eight lines are the book chain you already traced — what value does it end on?',
                        'Solution: 2.5',
                    ],
                },
                {
                    'slug': 'double-with-augmented-assignment',
                    'title': 'Double It',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Read one integer into `n`, then use a single '
                        'augmented assignment (`*=`) to double it and print '
                        'the result.'
                    ),
                    'context': 'Practice for the assignment table (p. 107).',
                    'constraints': 'Use n *= 2 (not n = n * 2) and print one line.',
                    'expected_behavior': 'For input 6 the program prints: 12',
                    'explain': (
                        '`n *= 2` multiplies n by 2 and stores the result '
                        'back in n in one step — 6 becomes 12. Sindh Board '
                        'Class XI, Unit 3, 3.4.3, p. 107.'
                    ),
                    'starter_code': (
                        'n = int(input())\n'
                        '# double n with *= and print it\n\n'
                    ),
                    'solution_code': (
                        'n = int(input())\n'
                        'n *= 2\n'
                        'print(n)\n'
                    ),
                    'test_cases': [
                        {'input': '6\n', 'expected_output': '12'},
                        {'input': '15\n', 'expected_output': '30'},
                    ],
                    'xp_reward': 70,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.4.3 Assignment operators', '107', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        '*= multiplies and re-assigns in one line.',
                        'n *= 2',
                    ],
                },
            ],
        },

        # ── 3.4.3 relational ───────────────────────────────────────────────
        {
            'slug': 'relational-operators',
            'title': 'Relational Operators',
            'content_type': 'interactive',
            'learning_objective': (
                'Compare values with ==, !=, >, <, >= and <= and read the '
                'True/False result of each comparison.'
            ),
            'order': 5,
            'duration_minutes': 10,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.4.3 Operators — Relational', '108', CLASS),
            'content_body': '''# Relational Operators

A **relational operator compares two values and answers True or False**.
The table on p. 108 lists six: `==` equal, `!=` not equal, `>` greater,
`<` less, `>=` greater-or-equal, `<=` less-or-equal.

`ComparisonOperatorProgram.py` (p. 108) runs all six on `a = 10`, `b = 20`:

```python
a = 10
b = 20
print(a == b)
print(a != b)
print(a > b)
print(a < b)
print(a >= b)
print(a <= b)
```

**Expected output:**

```output
False
True
False
True
False
True
```

Careful with the classic trap: `=` assigns, `==` compares. Writing `a = b`
inside a test does not ask whether they are equal — it overwrites `a`.

The book's **Test Yourself** (p. 115) asks which comparisons come out true;
work them on paper first: `4 == 5 - 1`, `55 >= 11 * 5`, `22 != 23 - 1`.
''',
            'exercises': [
                {
                    'slug': 'test-yourself-true-comparisons',
                    'title': 'Test Yourself — Which Are True?',
                    'exercise_type': 'multiple_select',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'From the book\'s Test Yourself (p. 115): which of '
                        'these comparisons evaluate to True? Select all that '
                        'apply.'
                    ),
                    'explain': (
                        '4 == 5 - 1 is True (4 equals 4); 55 >= 11 * 5 is '
                        'True (55 is equal to 55, and >= accepts equality); '
                        '22 != 23 - 1 is False because 23 - 1 is exactly 22. '
                        'Sindh Board Class XI, Unit 3, Test Yourself, p. 115.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '4 == 5 - 1', 'is_correct': True},
                        {'id': 'b', 'text': '55 >= 11 * 5', 'is_correct': True},
                        {'id': 'c', 'text': '22 != 23 - 1', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.4.3 Test Yourself', '115', CLASS),
                    'hints': [
                        'Do the arithmetic on the right side first, then compare.',
                        'Two of the three are True; watch how careful the != case is.',
                    ],
                },
                {
                    'slug': 'comparison-program-output',
                    'title': 'The Six Comparisons',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'With a = 10 and b = 20 (already written), print the '
                        'results of the six comparisons in the book order: '
                        '==, !=, >, <, >=, <= — one per line.'
                    ),
                    'context': 'Recreate ComparisonOperatorProgram.py (p. 108) yourself.',
                    'constraints': 'Six lines of output, each just True or False.',
                    'expected_behavior': (
                        'The program prints False True False True False '
                        'True, one per line.'
                    ),
                    'explain': (
                        '10 is not equal to 20 (False), so != is True; 10 > '
                        '20 is False and 10 < 20 is True; 10 >= 20 is False '
                        'but 10 <= 20 is True — the order the book program '
                        'prints them in. Sindh Board Class XI, Unit 3, 3.4.3 '
                        '(ComparisonOperatorProgram.py), p. 108.'
                    ),
                    'starter_code': (
                        'a = 10\n'
                        'b = 20\n'
                        '# print a == b, a != b, a > b, a < b, a >= b, a <= b\n\n\n\n\n\n\n'
                    ),
                    'solution_code': (
                        'a = 10\n'
                        'b = 20\n'
                        'print(a == b)\n'
                        'print(a != b)\n'
                        'print(a > b)\n'
                        'print(a < b)\n'
                        'print(a >= b)\n'
                        'print(a <= b)\n'
                    ),
                    'test_cases': [
                        {
                            'input': '',
                            'expected_output': (
                                'False\nTrue\nFalse\nTrue\nFalse\nTrue'
                            ),
                        },
                    ],
                    'xp_reward': 70,
                    'order': 2,
                    'reference': ref(UNIT, '3.4.3 ComparisonOperatorProgram.py', '108', CLASS),
                    'hints': [
                        'Each line is print(a <operator> b) in the order of the table.',
                        'print(a == b); print(a != b); print(a > b); print(a < b); print(a >= b); print(a <= b)',
                    ],
                },
            ],
        },

        # ── 3.4.3 logical + membership ─────────────────────────────────────
        {
            'slug': 'logical-and-membership-operators',
            'title': 'Logical and Membership Operators',
            'content_type': 'interactive',
            'learning_objective': (
                'Combine True/False values with and, or, not, and test '
                'membership with in / not in.'
            ),
            'order': 6,
            'duration_minutes': 10,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.4.3 Operators — Logical and Membership', '109', CLASS),
            'content_body': '''# Logical Operators

Logical operators join comparisons and hand back a single True or False
(p. 109). The book's example is `a = True`, `b = False`:

```python
a = True
b = False
print(a and b)
print(a or b)
print(not a)
print(not b)
```

**Expected output:**

```output
False
True
False
True
```

- `and` is True only when **both** sides are True.
- `or` is True when **at least one** side is True.
- `not` flips the value.

# Membership Operators

`in` and `not in` ask whether something exists inside a sequence. On
`name = "Python"` (p. 109) the book prints two True values:

```python
name = "Python"
print("P" in name)
print("y" in name)
```

**Expected output:**

```output
True
True
```

Both letters really are inside `"Python"` — and the test is
case-sensitive, so `"p" in name` would be False.
''',
            'exercises': [
                {
                    'slug': 'predict-and-or-not',
                    'title': 'Predict the Logical Results',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'What does this program print? One line per statement.'
                    ),
                    'context': (
                        'a = True\n'
                        'b = False\n'
                        'print(a and b)\n'
                        'print(a or b)\n'
                        'print(not a and b or not b)'
                    ),
                    'expected_output': 'False\nTrue\nTrue',
                    'explain': (
                        'True and False is False; True or False is True; in '
                        'the third line not a is False so "False and b" is '
                        'False, and not b is True, so False or True is True '
                        '(or binds last, after and). Sindh Board Class XI, '
                        'Unit 3, 3.4.3 (Logical), p. 109.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.4.3 Logical operators', '109', CLASS),
                    'hints': [
                        'Work the third line as (not a and b) or (not b).',
                        'False, True ... and the last one ends in True because not b is True.',
                    ],
                },
                {
                    'slug': 'letters-in-a-word',
                    'title': 'Membership with in',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'With word = "Python" (already written), print '
                        'whether the letter `P` is in the word, then whether '
                        'the letter `p` (lower-case) is in it — one result '
                        'per line.'
                    ),
                    'context': (
                        'Builds on the membership example (p. 109) to show '
                        'that in is case-sensitive.'
                    ),
                    'constraints': 'Two lines: True or False each.',
                    'expected_behavior': 'The program prints True then False.',
                    'explain': (
                        '"P" is in "Python" (True), but membership tests are '
                        'case-sensitive so "p" is not (False). Sindh Board '
                        'Class XI, Unit 3, 3.4.3 (Membership), p. 109.'
                    ),
                    'starter_code': (
                        'word = "Python"\n'
                        '# print "P" in word, then "p" in word\n\n\n'
                    ),
                    'solution_code': (
                        'word = "Python"\n'
                        'print("P" in word)\n'
                        'print("p" in word)\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': 'True\nFalse'},
                    ],
                    'xp_reward': 70,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.4.3 Membership operators', '109', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'The in operator reads like English: "P" in word.',
                        'print("P" in word) then print("p" in word).',
                    ],
                },
            ],
        },

        # ── 3.4.3 bitwise ──────────────────────────────────────────────────
        {
            'slug': 'bitwise-operators',
            'title': 'Bitwise Operators',
            'content_type': 'interactive',
            'learning_objective': (
                'Apply &, |, ^, ~, << and >> to small integers and verify '
                'the book\'s printed results.'
            ),
            'order': 7,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, '3.4.3 Operators — Bitwise', '110-114', CLASS),
            'content_body': '''# Bitwise Operators

Bitwise operators work on the **binary digits** of a number. `bin()` shows
the binary form (p. 110): `bin(10)` is `'0b1010'`, `bin(6)` is `'0b110'`.
The table (p. 110) gives six operators:

| Operator | Name | Meaning |
|---|---|---|
| `&` | AND | 1 bit only where **both** are 1 |
| `|` | OR | 1 bit where **either** is 1 |
| `^` | XOR | 1 bit where the two **differ** |
| `~` | NOT | flips every bit |
| `<<` | Left shift | moves bits left (doubles per shift) |
| `>>` | Right shift | moves bits right (halves per shift) |

The book works each one on `a = 10`, `b = 6` (pp. 110-113):

```python
a = 10
b = 6
print(a & b)
print(a | b)
print(a ^ b)
print(~a)
print(~b)
```

**Expected output** — every value is the book's own printed result:

```output
2
14
12
-11
-7
```

Why `10 & 6` is 2: `1010 & 0110` lines up as only one shared 1-bit, worth
2. `~` is stranger — it turns `n` into `-(n + 1)`, so `~10` is `-11`, `~5`
is `-6`, even `~0` is `-1` (the p. 113 table — and `~6` is `-7` for the
same reason).

The shifts (p. 114): `a = 5` printed `a << 1`, `a << 2`, `a << 3` gives
`10 20 40` (each shift doubles); `a = 20` with `>> 1, >> 2, >> 3` gives
`10 5 2` (each shift halves, floored).
''',
            'exercises': [
                {
                    'slug': 'predict-bitwise-and',
                    'title': 'Predict 10 & 6',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Without running it, what does this print?'
                    ),
                    'context': (
                        'print(10 & 6)\n'
                        'print(bin(10))\n'
                        'print(bin(6))'
                    ),
                    'expected_output': "2\n0b1010\n0b110",
                    'explain': (
                        '10 is 1010 and 6 is 0110 in binary; AND keeps a 1 '
                        'only where both bits are 1, leaving 0010 = 2. bin() '
                        'prefixes 0b. Sindh Board Class XI, Unit 3, 3.4.3 '
                        '(Bitwise AND, bin()), p. 110.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.4.3 Bitwise AND', '110', CLASS),
                    'hints': [
                        'Write both numbers in binary and compare bit by bit.',
                        '1010 & 0110 leaves a single 1-bit: the 2 column.',
                    ],
                },
                {
                    'slug': 'shift-machine',
                    'title': 'The Shift Machine',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read one integer into `a`, then print `a << 1`, '
                        '`a << 2` and `a << 3` on three lines — the book\'s '
                        'left-shift pattern applied to any number.'
                    ),
                    'context': (
                        'For a = 5 the book prints 10, 20, 40 (p. 114). '
                        'Each left shift doubles the value.'
                    ),
                    'constraints': 'Three lines of output, one per shift.',
                    'expected_behavior': 'For input 5 the program prints 10, 20, 40 on three lines.',
                    'explain': (
                        'Shifting left by n multiplies by 2**n: 5 << 1 is 10, '
                        '5 << 2 is 20, 5 << 3 is 40 — exactly the book run. '
                        'Sindh Board Class XI, Unit 3, 3.4.3 (Left Shift), '
                        'p. 114.'
                    ),
                    'starter_code': (
                        'a = int(input())\n\n\n\n'
                    ),
                    'solution_code': (
                        'a = int(input())\n'
                        'print(a << 1)\n'
                        'print(a << 2)\n'
                        'print(a << 3)\n'
                    ),
                    'test_cases': [
                        {'input': '5\n', 'expected_output': '10\n20\n40'},
                        {'input': '3\n', 'expected_output': '6\n12\n24'},
                    ],
                    'xp_reward': 90,
                    'order': 2,
                    'reference': ref(UNIT, '3.4.3 Left Shift', '114', CLASS),
                    'hints': [
                        'The three lines differ only in the shift count: 1, 2, 3.',
                        'print(a << 1); print(a << 2); print(a << 3)',
                    ],
                },
                {
                    'slug': 'which-operator-compares-bits-differ',
                    'title': 'Which Operator Finds Differing Bits?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Which bitwise operator gives 1-bits only where the '
                        'two operands\' bits differ? (The book: a = 10, b = 6 '
                        'gives 12.)'
                    ),
                    'explain': (
                        '^ is XOR: 1010 ^ 0110 = 1100, which is 12 — the '
                        'book\'s printed XOR result. & requires both bits 1, '
                        '| accepts either. Sindh Board Class XI, Unit 3, '
                        '3.4.3 (Bitwise XOR), p. 112.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '^ (XOR)', 'is_correct': True},
                        {'id': 'b', 'text': '& (AND)', 'is_correct': False},
                        {'id': 'c', 'text': '| (OR)', 'is_correct': False},
                        {'id': 'd', 'text': '~ (NOT)', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, '3.4.3 Bitwise XOR', '112', CLASS),
                },
            ],
        },

        # ── challenge: the book activity ───────────────────────────────────
        {
            'slug': 'arithmetic-calculator-challenge',
            'title': 'Challenge — Arithmetic Calculator',
            'content_type': 'interactive',
            'learning_objective': (
                'Combine input, type conversion and branching knowledge into '
                'the calculator the unit exercise asks for.'
            ),
            'order': 8,
            'duration_minutes': 15,
            'xp_reward': 60,
            'reference': ref(UNIT, 'EXERCISE 5 (i) — Arithmetic Calculator activity', '138', CLASS),
            'content_body': '''# Challenge: Arithmetic Calculator

Activity 1 of the unit exercise (p. 138) asks for an **arithmetic
calculator**. You now hold every part it needs: `input()` with `int()`
conversion (pp. 102-103) and the arithmetic operator set (pp. 105-106).

Design: read a number, read an operator as a one-character string, read a
second number, then choose the calculation. The operator test itself uses
the relational `==` from p. 108 — and the next chapter shows `if/elif`
making the choice, so attempt this now and refine it after control
structures.

Sample session (input on the left, output on the right):

```text
7
+
3
10
```

Division with `/` follows the book: `10 / 3` prints `3.3333333333333335` —
no rounding is asked for here.
''',
            'exercises': [
                {
                    'slug': 'calculator-four-operations',
                    'title': 'Build the Calculator',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'hard',
                    'instructions': (
                        'Read an integer, then a line holding one operator '
                        '(`+`, `-`, `*` or `/`), then another integer. Print '
                        'the result of that operation. Division uses normal '
                        '`/` (true division).'
                    ),
                    'context': (
                        'The unit exercise activity: an arithmetic '
                        'calculator (p. 138), built only from operators pp. '
                        '105-108 and input pp. 102-103.'
                    ),
                    'constraints': (
                        'Four inputs lines maximum, exactly one line of '
                        'output. You may use if / elif / else — they are '
                        'taught in the next chapter — or a dict lookup.'
                    ),
                    'expected_behavior': (
                        'Inputs 7, +, 3 print 10; inputs 10, /, 4 print 2.5.'
                    ),
                    'explain': (
                        'Read the operator with input() (a string), compare '
                        'it with == and apply the matching arithmetic '
                        'operator; 7 + 3 = 10 and 10 / 3-style true division '
                        'returns a float (p. 106). Sindh Board Class XI, '
                        'Unit 3, EXERCISE 5 (i), p. 138 (operators pp. '
                        '105-108).'
                    ),
                    'starter_code': (
                        'left = int(input())\n'
                        'operator = input()\n'
                        'right = int(input())\n\n\n\n\n\n\n\n'
                    ),
                    'solution_code': (
                        'left = int(input())\n'
                        'operator = input()\n'
                        'right = int(input())\n'
                        'if operator == "+":\n'
                        '    print(left + right)\n'
                        'elif operator == "-":\n'
                        '    print(left - right)\n'
                        'elif operator == "*":\n'
                        '    print(left * right)\n'
                        'else:\n'
                        '    print(left / right)\n'
                    ),
                    'test_cases': [
                        {'input': '7\n+\n3\n', 'expected_output': '10'},
                        {'input': '7\n-\n3\n', 'expected_output': '4'},
                        {'input': '7\n*\n3\n', 'expected_output': '21'},
                        {'input': '10\n/\n4\n', 'expected_output': '2.5'},
                    ],
                    'xp_reward': 120,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE 5 (i) — Arithmetic Calculator', '138', CLASS),
                    'hints': [
                        'operator is a string like "+" — compare it with ==.',
                        'Chain if / elif / else, one branch per operator.',
                        'Solution: if operator == "+": print(left + right) ... else: print(left / right)',
                    ],
                },
            ],
        },
    ],
}
