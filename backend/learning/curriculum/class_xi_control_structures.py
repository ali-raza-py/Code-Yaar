"""
Class XI, Unit 3 — chapter 4: Control Structures

    3.5 Control Structures   (printed pp. 115-126)

Citation note: this module cites verified section ranges (3.5, 3.5.2
pp. 115-120, 3.5.3 pp. 120-126) and the book's own program names —
"Program Shopping Bill Calculator" (p. 126) — never sub-numbers that were
not individually confirmed in textbooks/CLASS-XI-SOURCE-VERIFICATION.md.
Program bodies and every trace output below are transcribed from the
verified pages.
"""

from .common import ref

UNIT = 'Unit 3'
CLASS = 'Class XI'


CHAPTER_CONTROL = {
    'slug': 'xi-control-structures',
    'title': 'Control Structures',
    'description': (
        'Sequence, selection and repetition: if, if-else, the if-elif-else '
        'ladder and nested if; for with range(), while, break, continue, '
        'nested loops — and the book\'s own programs, up to the Shopping '
        'Bill Calculator.'
    ),
    'order': 4,
    'xp_reward': 800,
    'reference': ref(UNIT, '3.5 Control Structures', '115-126', CLASS),
    'lessons': [
        # ── 3.5 intro + sequence ───────────────────────────────────────────
        {
            'slug': 'control-structures-and-sequence',
            'title': 'Control Structures and Sequence',
            'content_type': 'interactive',
            'learning_objective': (
                'Name the three basic control structures and run the book\'s '
                'sequence program that adds two numbers.'
            ),
            'order': 1,
            'duration_minutes': 10,
            'xp_reward': 45,
            'reference': ref(UNIT, '3.5 Control Structures — definition and sequence', '115', CLASS),
            'content_body': '''# Control Structures

Section 3.5 (p. 115) defines a **control structure** as a way of directing
the order in which a program's statements run, and names the three basics:

| Structure | What it does |
|---|---|
| **Sequence** | statements run one after another, top to bottom |
| **Selection** | choose which statement to run based on a condition |
| **Repetition** | repeat statements while or for a number of times |

## Sequence in action

The book's first program (p. 115) is pure sequence — nothing is skipped,
nothing repeats:

```python
num1 = 5
num2 = 10
sum = num1 + num2
print("Sum =", sum)
```

**Expected output:**

```output
Sum = 15
```

Read it line by line: two values are stored, a third variable collects
their addition, and `print` reports it. Every line depends only on the ones
above it — that is the sequence structure, the default way a program runs.
''',
            'exercises': [
                {
                    'slug': 'sum-two-inputs',
                    'title': 'Sum of Two Numbers',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Adapt the sequence program: read two integers (one '
                        'per line) instead of fixed values and print their '
                        'sum as `Sum = <answer>`.'
                    ),
                    'context': 'The sequence program of section 3.5 (p. 115), now with input().',
                    'constraints': 'One line of output in the form Sum = 12.',
                    'expected_behavior': 'For inputs 5 and 7 the program prints: Sum = 12',
                    'explain': (
                        'int(input()) converts each line to a number, + adds '
                        'them, and the print keeps the book\'s "Sum =" label. '
                        'Sindh Board Class XI, Unit 3, 3.5 (sequence), p. '
                        '115; conversion 3.4.2, pp. 102-103.'
                    ),
                    'starter_code': (
                        'num1 = int(input())\n'
                        'num2 = int(input())\n'
                        'total = num1 + num2\n'
                        '# print in the form: Sum = 15\n'
                    ),
                    'solution_code': (
                        'num1 = int(input())\n'
                        'num2 = int(input())\n'
                        'total = num1 + num2\n'
                        'print("Sum =", total)\n'
                    ),
                    'test_cases': [
                        {'input': '5\n7\n', 'expected_output': 'Sum = 12'},
                        {'input': '10\n15\n', 'expected_output': 'Sum = 25'},
                    ],
                    'xp_reward': 70,
                    'order': 1,
                    'reference': ref(UNIT, '3.5 Sequence program', '115', CLASS),
                    'hints': [
                        'print("Sum =", total) reproduces the book label with any value.',
                    ],
                },
                {
                    'slug': 'three-basic-control-structures',
                    'title': 'The Three Basics',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which set names the three basic control structures '
                        'of section 3.5?'
                    ),
                    'explain': (
                        'Sequence, selection and repetition (p. 115). Note '
                        'the book\'s fill-in-the-blank pair: choosing one '
                        'path out of options is the selection structure '
                        '(EXERCISE B, p. 137). Sindh Board Class XI, Unit 3, '
                        '3.5, p. 115.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Sequence, selection, repetition', 'is_correct': True},
                        {'id': 'b', 'text': 'Input, output, storage', 'is_correct': False},
                        {'id': 'c', 'text': 'Loops, functions, arrays', 'is_correct': False},
                        {'id': 'd', 'text': 'Comments, variables, constants', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '3.5 Control Structures', '115', CLASS),
                },
            ],
        },

        # ── selection: if and if-else ──────────────────────────────────────
        {
            'slug': 'the-if-and-if-else-statements',
            'title': 'The if and if-else Statements',
            'content_type': 'interactive',
            'learning_objective': (
                'Write an if test with a colon and indented block, and add '
                'an else path — the voter and CNIC/CRC programs.'
            ),
            'order': 2,
            'duration_minutes': 15,
            'xp_reward': 55,
            'reference': ref(UNIT, '3.5.2 Selection — if and if-else', '116-117', CLASS),
            'content_body': '''# The if Statement

Python's `if` needs two things the book stresses (p. 116): a **colon** at
the end of the test line, and an **indented block** underneath — the
indentation you practised in Chapter 2 is what says which statements belong
to the `if`.

The voter program (p. 116), run twice:

```python
age = int(input("Enter age: "))
if age >= 18:
    print("You are eligible to vote.")
```

**Expected output** with `20` typed at the prompt:

```output
Enter age: You are eligible to vote.
```

With 16 nothing prints — a plain `if` only has one path. When the condition
fails, the indented block is simply skipped.

# The if-else Statement

To answer *both* ways, the book adds `else` (p. 117). The CNIC/CRC program
is 11 lines and checks national-ID eligibility:

```python
age = int(input("Enter age: "))
if age >= 18:
    print("Adult - eligible for CNIC")
else:
    print("Minor - eligible for CRC")
```

**Expected output** with `17`:

```output
Enter age: Minor - eligible for CRC
```

Exactly one of the two blocks always runs — never both, never neither. The
comparison table on p. 120 puts it plainly: `if` runs its block when the
test is true and does nothing otherwise; `if-else` guarantees an alternative
path.

> **Note:** the book prints "Adult — eligible for CNIC" with an em-dash;
> the runnable sample above uses a plain hyphen so the message stays
> ASCII-simple and the grader compares it exactly.

> Verified run: the checker feeds `20` to the first sample and the second
> sample gets `17`; the CNIC/CRC output shown is that `17` transcript.
''',
            'exercises': [
                {
                    'slug': 'eligible-to-vote',
                    'title': 'Eligible to Vote',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Read an age. If it is 18 or more print '
                        '`Eligible`; otherwise print `Not eligible`.'
                    ),
                    'context': (
                        'The voter program (p. 116) extended with the else '
                        'path of p. 117 so both answers are visible.'
                    ),
                    'constraints': 'Print exactly one word: Eligible or Not eligible.',
                    'expected_behavior': 'For input 18 the program prints: Eligible',
                    'explain': (
                        'age >= 18 is the same test the book uses for voting '
                        'eligibility; the else block covers every younger '
                        'age. Sindh Board Class XI, Unit 3, 3.5.2 (if, '
                        'if-else), pp. 116-117.'
                    ),
                    'starter_code': (
                        'age = int(input())\n'
                        '# if age >= 18 print Eligible, else print Not eligible\n\n\n\n'
                    ),
                    'solution_code': (
                        'age = int(input())\n'
                        'if age >= 18:\n'
                        '    print("Eligible")\n'
                        'else:\n'
                        '    print("Not eligible")\n'
                    ),
                    'test_cases': [
                        {'input': '20\n', 'expected_output': 'Eligible'},
                        {'input': '18\n', 'expected_output': 'Eligible'},
                        {'input': '17\n', 'expected_output': 'Not eligible'},
                    ],
                    'xp_reward': 80,
                    'order': 1,
                    'reference': ref(UNIT, '3.5.2 if voter program', '116-117', CLASS),
                    'hints': [
                        'The colon goes after the test; the print goes indented under it.',
                        'if age >= 18: / print("Eligible") / else: / print("Not eligible")',
                    ],
                },
                {
                    'slug': 'cnic-or-crc',
                    'title': 'CNIC or CRC',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Recreate the book\'s ID program: read an age and '
                        'print `Adult` when it is 18 or more, otherwise '
                        'print `Minor`.'
                    ),
                    'context': 'The if-else example of p. 117 (CNIC at 18, CRC below).',
                    'constraints': 'One line: either Adult or Minor.',
                    'expected_behavior': 'For input 11 the program prints: Minor',
                    'explain': (
                        'The threshold in the book is 18 — at and above it a '
                        'citizen is an Adult (CNIC), below it a Minor (CRC). '
                        'Sindh Board Class XI, Unit 3, 3.5.2 (if-else), '
                        'p. 117.'
                    ),
                    'starter_code': (
                        'age = int(input())\n\n\n\n'
                    ),
                    'solution_code': (
                        'age = int(input())\n'
                        'if age >= 18:\n'
                        '    print("Adult")\n'
                        'else:\n'
                        '    print("Minor")\n'
                    ),
                    'test_cases': [
                        {'input': '11\n', 'expected_output': 'Minor'},
                        {'input': '18\n', 'expected_output': 'Adult'},
                        {'input': '40\n', 'expected_output': 'Adult'},
                    ],
                    'xp_reward': 70,
                    'order': 2,
                    'reference': ref(UNIT, '3.5.2 if-else CNIC/CRC program', '117', CLASS),
                    'hints': [
                        'Same shape as the voter program — only the words change.',
                    ],
                },
                {
                    'slug': 'if-versus-if-else',
                    'title': 'if versus if-else',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'According to the comparison table (p. 120), what '
                        'happens when the test in a plain `if` is false?'
                    ),
                    'explain': (
                        'The indented block is skipped and execution '
                        'continues after it — nothing else runs. The if-else '
                        'form exists precisely to add a second path. Sindh '
                        'Board Class XI, Unit 3, 3.5.2 (comparison table), '
                        'p. 120.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'The indented block is skipped and the program continues', 'is_correct': True},
                        {'id': 'b', 'text': 'Python runs the block anyway', 'is_correct': False},
                        {'id': 'c', 'text': 'The program stops with a runtime error', 'is_correct': False},
                        {'id': 'd', 'text': 'The block runs twice', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, '3.5.2 if vs if-else table', '120', CLASS),
                },
            ],
        },

        # ── if-elif-else + nested if ───────────────────────────────────────
        {
            'slug': 'the-if-elif-else-ladder',
            'title': 'The if-elif-else Ladder and Nested if',
            'content_type': 'interactive',
            'learning_objective': (
                'Choose one path out of many with elif, and test a second '
                'condition inside a first with nested if.'
            ),
            'order': 3,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, '3.5.2 Selection — if-elif-else and nested if', '118-119', CLASS),
            'content_body': '''# The if-elif-else Ladder

Two paths were enough for `if-else`; a category scale needs more doors. The
age-classification program (p. 118) chains `elif` tests and prints the
first category that matches:

```python
age = int(input("Enter age: "))
if age < 0:
    print("Invalid age")
elif age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
elif age < 40:
    print("Young Adult")
elif age < 60:
    print("Middle-Aged")
else:
    print("Senior")
```

**Expected output** with `17`:

```output
Enter age: Teenager
```

Python tests the rungs top to bottom and stops at the first True — with 17,
`age < 0` and `age < 13` fail, `age < 20` wins, and the ladder ends there.
That is why the order of the rungs matters.

# Nested if

A **nested if** puts a second test inside the block of the first, so the
inner condition is only ever checked when the outer one already passed
(p. 119). The book's loan program asks both questions:

```python
age = int(input("Enter age: "))
salary = int(input("Enter monthly salary: "))
if age >= 18:
    if salary >= 30000:
        print("Loan approved")
    else:
        print("Salary requirement not met")
else:
    print("Must be 18 or older")
```

Run with `20, 35000` the loan is approved; with `17, 99999` the salary is
never even looked at — the outer test already failed.
''',
            'exercises': [
                {
                    'slug': 'age-category',
                    'title': 'Age Category',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Recreate the ladder: read an age and print the '
                        'book\'s category — `Child` under 13, `Teenager` '
                        'under 20, `Young Adult` under 40, `Middle-Aged` '
                        'under 60, otherwise `Senior`.'
                    ),
                    'context': 'The age-classification program of p. 118.',
                    'constraints': 'Print exactly one category word, spelt as in the book.',
                    'expected_behavior': 'For input 17 the program prints: Teenager',
                    'explain': (
                        'The ladder tests smallest first: 17 fails `age < 13` '
                        'and passes `age < 20`, giving Teenager. Sindh Board '
                        'Class XI, Unit 3, 3.5.2 (if-elif-else), p. 118.'
                    ),
                    'starter_code': (
                        'age = int(input())\n\n\n\n\n\n\n\n\n\n'
                    ),
                    'solution_code': (
                        'age = int(input())\n'
                        'if age < 13:\n'
                        '    print("Child")\n'
                        'elif age < 20:\n'
                        '    print("Teenager")\n'
                        'elif age < 40:\n'
                        '    print("Young Adult")\n'
                        'elif age < 60:\n'
                        '    print("Middle-Aged")\n'
                        'else:\n'
                        '    print("Senior")\n'
                    ),
                    'test_cases': [
                        {'input': '17\n', 'expected_output': 'Teenager'},
                        {'input': '7\n', 'expected_output': 'Child'},
                        {'input': '35\n', 'expected_output': 'Young Adult'},
                        {'input': '61\n', 'expected_output': 'Senior'},
                    ],
                    'xp_reward': 100,
                    'order': 1,
                    'reference': ref(UNIT, '3.5.2 if-elif-else age categories', '118', CLASS),
                    'hints': [
                        'Order the rungs from the smallest bound upward.',
                        'if age < 13: ... elif age < 20: ... elif age < 40: ... elif age < 60: ... else: ...',
                    ],
                },
                {
                    'slug': 'loan-approval',
                    'title': 'Loan Approval (Nested if)',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read age then salary. Print `Loan Approved` only '
                        'when age is at least 18 **and** salary is at least '
                        '30000; in every other case print `Loan Denied`.'
                    ),
                    'context': 'The nested-if loan program of p. 119.',
                    'constraints': 'Use a nested if (an if inside an if); one line of output.',
                    'expected_behavior': 'For inputs 20 and 35000 the program prints: Loan Approved',
                    'explain': (
                        'The inner salary test only runs once the outer '
                        'age test has passed; both gates must open for the '
                        'approval. Sindh Board Class XI, Unit 3, 3.5.2 '
                        '(Nested if), p. 119.'
                    ),
                    'starter_code': (
                        'age = int(input())\n'
                        'salary = int(input())\n\n\n\n\n\n'
                    ),
                    'solution_code': (
                        'age = int(input())\n'
                        'salary = int(input())\n'
                        'if age >= 18:\n'
                        '    if salary >= 30000:\n'
                        '        print("Loan Approved")\n'
                        '    else:\n'
                        '        print("Loan Denied")\n'
                        'else:\n'
                        '    print("Loan Denied")\n'
                    ),
                    'test_cases': [
                        {'input': '20\n35000\n', 'expected_output': 'Loan Approved'},
                        {'input': '20\n25000\n', 'expected_output': 'Loan Denied'},
                        {'input': '17\n99999\n', 'expected_output': 'Loan Denied'},
                    ],
                    'xp_reward': 100,
                    'order': 2,
                    'reference': ref(UNIT, '3.5.2 Nested if loan program', '119', CLASS),
                    'hints': [
                        'Two spaces of indentation reveal the inner if — it lives inside the outer block.',
                        'The inner else and the outer else both print Loan Denied.',
                    ],
                },
            ],
        },

        # ── repetition: for ────────────────────────────────────────────────
        {
            'slug': 'the-for-loop-and-range',
            'title': 'The for Loop and range()',
            'content_type': 'interactive',
            'learning_objective': (
                'Repeat with for, and control range() in its three forms: '
                'stop, start-and-stop, and step.'
            ),
            'order': 4,
            'duration_minutes': 16,
            'xp_reward': 60,
            'reference': ref(UNIT, '3.5.3 Repetition — for loop and range()', '120-122', CLASS),
            'content_body': '''# The for Loop

A **for loop** repeats a block a set number of times (p. 120). The
book's first loop (pp. 120-121):

```python
for i in range(5):
    print(i)
```

**Expected output:**

```output
0
1
2
3
4
```

`range(5)` hands out the numbers 0 to 4 — it **stops before** 5. The
variable `i` takes each value in turn.

## The three forms of range() (pp. 121-122)

| Form | Meaning | Book example and output |
|---|---|---|
| `range(stop)` | 0 up to stop-1 | `range(5)` → 0 1 2 3 4 |
| `range(start, stop)` | start up to stop-1 | `range(2, 8)` → 2 3 4 5 6 7 |
| `range(start, stop, step)` | jump by step | `range(0, 10, 2)` → 0 2 4 6 8 |

The step can be negative to count down: `range(10, 0, -2)` gives
`10 8 6 4 2`.

## The book's even & odd program (p. 122)

Two loops with a step of 2 walk the even and odd numbers separately:

```python
print("Even numbers:")
for i in range(0, 11, 2):
    print(i)
print("Odd numbers:")
for i in range(1, 11, 2):
    print(i)
```

**Expected output:**

```output
Even numbers:
0
2
4
6
8
10
Odd numbers:
1
3
5
7
9
```

**Which loop to choose?** The comparison table (p. 125) and the book's own
MCQ (p. 136) agree: use `for` when the number of iterations is **known**
beforehand, `while` when it depends on a condition that may change.
''',
            'exercises': [
                {
                    'slug': 'predict-range-two-eight',
                    'title': 'Predict range(2, 8)',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'What does this print? Put every number on its own '
                        'line.'
                    ),
                    'context': (
                        'for i in range(2, 8):\n'
                        '    print(i)'
                    ),
                    'expected_output': '2\n3\n4\n5\n6\n7',
                    'explain': (
                        'range(start, stop) includes the start and excludes '
                        'the stop — 2 through 7, exactly the book\'s second '
                        'form. Sindh Board Class XI, Unit 3, 3.5.3 (range '
                        'forms), pp. 121-122.'
                    ),
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.5.3 range(start, stop)', '121-122', CLASS),
                    'hints': [
                        'The stop number itself never appears.',
                        'Solution: 2 3 4 5 6 7, one per line.',
                    ],
                },
                {
                    'slug': 'countdown-loop',
                    'title': 'Countdown with a Negative Step',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Using one for loop with a negative step, print the '
                        'numbers 10 8 6 4 2 — one per line, exactly the '
                        'book\'s countdown example.'
                    ),
                    'context': 'The third range form with a negative step (p. 122).',
                    'constraints': 'One loop, one range() call.',
                    'expected_behavior': 'The program prints 10, 8, 6, 4, 2 on five lines.',
                    'explain': (
                        'range(10, 0, -2) starts at 10 and steps down by 2, '
                        'stopping before it reaches 0 — giving 10 8 6 4 2. '
                        'Sindh Board Class XI, Unit 3, 3.5.3 (negative '
                        'step), p. 122.'
                    ),
                    'starter_code': (
                        'for i in range(        ):\n'
                        '    print(i)\n'
                    ),
                    'solution_code': (
                        'for i in range(10, 0, -2):\n'
                        '    print(i)\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '10\n8\n6\n4\n2'},
                    ],
                    'xp_reward': 80,
                    'order': 2,
                    'reference': ref(UNIT, '3.5.3 range negative step', '122', CLASS),
                    'hints': [
                        'Three arguments: start, stop, step — the step is what goes down.',
                        'range(10, 0, -2)',
                    ],
                },
                {
                    'slug': 'even-or-odd-branch',
                    'title': 'Even or Odd, Number by Number',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Loop over the numbers 1 to 6 with range(1, 7). For '
                        'each number print `2 Even` or `3 Odd` style: the '
                        'number, a space, then Even or Odd.'
                    ),
                    'context': (
                        'Combines the book\'s even/odd idea (p. 122) with '
                        'the if-else of p. 117 — the pairing the p. 125 '
                        'activity asks for (Repetition + Sequence + '
                        'Selection).'
                    ),
                    'constraints': (
                        'Six lines, e.g. `1 Odd`. Use % 2 to test parity '
                        'inside the loop.'
                    ),
                    'expected_behavior': (
                        'Output: 1 Odd, 2 Even, 3 Odd, 4 Even, 5 Odd, '
                        '6 Even — one per line.'
                    ),
                    'explain': (
                        'i % 2 == 0 selects Even, else Odd — selection '
                        'sitting inside repetition. Sindh Board Class XI, '
                        'Unit 3, 3.5.3 (even/odd loop), p. 122; activity '
                        'p. 125.'
                    ),
                    'starter_code': (
                        'for i in range(1, 7):\n'
                        '    # print "<i> Even" or "<i> Odd"\n\n\n\n'
                    ),
                    'solution_code': (
                        'for i in range(1, 7):\n'
                        '    if i % 2 == 0:\n'
                        '        print(i, "Even")\n'
                        '    else:\n'
                        '        print(i, "Odd")\n'
                    ),
                    'test_cases': [
                        {
                            'input': '',
                            'expected_output': (
                                '1 Odd\n2 Even\n3 Odd\n4 Even\n5 Odd\n6 Even'
                            ),
                        },
                    ],
                    'xp_reward': 100,
                    'order': 3,
                    'reference': ref(UNIT, '3.5.3 even/odd loop activity', '122-125', CLASS),
                    'hints': [
                        'print(i, "Even") puts the number and the word on one line with a space.',
                        'if i % 2 == 0: inside the loop, with an else for Odd.',
                    ],
                },
                {
                    'slug': 'multiplication-table',
                    'title': 'Activity — Multiplication Table',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Read an integer n and print its table from 1 to 5, '
                        'one line per row, in the form `7 x 1 = 7`.'
                    ),
                    'context': (
                        'Book activity (p. 122): "multiplication table from '
                        'user input" — a for loop over range(1, 6).'
                    ),
                    'constraints': (
                        'Rows use the exact form `<n> x <i> = <answer>` with '
                        'spaces around x and =.'
                    ),
                    'expected_behavior': (
                        'For input 3 the first line is 3 x 1 = 3 and the '
                        'fifth is 3 x 5 = 15.'
                    ),
                    'explain': (
                        'One loop, five products: n * i grows with i, so the '
                        'table of 3 runs 3 x 1 = 3 ... 3 x 5 = 15. Sindh '
                        'Board Class XI, Unit 3, 3.5.3 Activity, p. 122.'
                    ),
                    'starter_code': (
                        'n = int(input())\n'
                        'for i in range(1, 6):\n\n'
                    ),
                    'solution_code': (
                        'n = int(input())\n'
                        'for i in range(1, 6):\n'
                        '    print(n, "x", i, "=", n * i)\n'
                    ),
                    'test_cases': [
                        {
                            'input': '3\n',
                            'expected_output': (
                                '3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n'
                                '3 x 4 = 12\n3 x 5 = 15'
                            ),
                        },
                    ],
                    'xp_reward': 90,
                    'order': 4,
                    'reference': ref(UNIT, '3.5.3 Activity — multiplication table', '122', CLASS),
                    'hints': [
                        'print joins arguments with single spaces — exactly what the form needs.',
                        'print(n, "x", i, "=", n * i)',
                    ],
                },
                {
                    'slug': 'which-loop-for-known-iterations',
                    'title': 'Which Loop When Iterations Are Known?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which loop does the book recommend when the number '
                        'of iterations is known before the loop starts?'
                    ),
                    'explain': (
                        'The for loop — the for-vs-while table (p. 125) and '
                        'the book\'s MCQ (p. 136) both pick for when the '
                        'count is known, while for condition-driven '
                        'repetition. Sindh Board Class XI, Unit 3, 3.5.3 '
                        '(for vs while), p. 125; EXERCISE A (v), p. 136.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'for loop', 'is_correct': True},
                        {'id': 'b', 'text': 'while loop', 'is_correct': False},
                        {'id': 'c', 'text': 'Either one — the book says it makes no difference', 'is_correct': False},
                        {'id': 'd', 'text': 'A sequence structure', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 5,
                    'reference': ref(UNIT, 'EXERCISE A (v)', '136', CLASS),
                },
            ],
        },

        # ── repetition: while, break, continue ─────────────────────────────
        {
            'slug': 'the-while-loop-break-continue',
            'title': 'The while Loop, break and continue',
            'content_type': 'interactive',
            'learning_objective': (
                'Repeat on a condition with while, and steer a running loop '
                'with break and continue.'
            ),
            'order': 5,
            'duration_minutes': 14,
            'xp_reward': 55,
            'reference': ref(UNIT, '3.5.3 Repetition — while, break, continue', '123', CLASS),
            'content_body': '''# The while Loop

A `while` loop keeps going **as long as its condition stays true** (p. 123).
The book's counting program:

```python
count = 1
while count <= 5:
    print(count)
    count = count + 1
```

**Expected output:**

```output
1
2
3
4
5
```

Trace it: `count` starts at 1, each round prints it and adds 1, and the
test `count <= 5` is checked before every round — when count reaches 6 the
condition fails and the loop ends. Forget `count = count + 1` and you get
the infinite-loop logical error the debugging section warns about (p. 132).

**for vs while** (table, p. 125): `for` when you know the count, `while`
when you repeat until a condition changes.

# break and continue (p. 123)

Two statements steer a loop from the inside.

```python
for i in range(6):
    if i == 3:
        break
    print(i)
```

**Expected output:**

```output
0
1
2
```

`break` exits the loop on the spot — 3 is never reached. Swap it for
`continue`:

```python
for i in range(6):
    if i % 2 == 0:
        continue
    print(i)
```

**Expected output:**

```output
1
3
5
```

`continue` skips **the rest of that round only** — every even number jumps
over the print and the loop carries on, so the odd survivors appear.
''',
            'exercises': [
                {
                    'slug': 'predict-break-output',
                    'title': 'Predict the break Run',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': 'What does the book\'s break program print?',
                    'context': (
                        'for i in range(6):\n'
                        '    if i == 3:\n'
                        '        break\n'
                        '    print(i)'
                    ),
                    'expected_output': '0\n1\n2',
                    'explain': (
                        'Rounds 0, 1 and 2 print; in round 3 the break exits '
                        'the loop before the print, so 3, 4 and 5 never '
                        'appear. Sindh Board Class XI, Unit 3, 3.5.3 '
                        '(break), p. 123.'
                    ),
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.5.3 break example', '123', CLASS),
                    'hints': [
                        'break fires the moment i is 3 — what comes before the break line?',
                        'Solution: 0 1 2, one per line.',
                    ],
                },
                {
                    'slug': 'predict-continue-output',
                    'title': 'Predict the continue Run',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': 'What does the book\'s continue program print?',
                    'context': (
                        'for i in range(6):\n'
                        '    if i % 2 == 0:\n'
                        '        continue\n'
                        '    print(i)'
                    ),
                    'expected_output': '1\n3\n5',
                    'explain': (
                        'continue skips the print for every even i (0, 2, 4) '
                        'and lets odd rounds through — the book prints 1 3 '
                        '5. Sindh Board Class XI, Unit 3, 3.5.3 '
                        '(continue), p. 123.'
                    ),
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '3.5.3 continue example', '123', CLASS),
                    'hints': [
                        'Which numbers make i % 2 == 0 true — and what does continue do to them?',
                        'Solution: 1 3 5, one per line.',
                    ],
                },
                {
                    'slug': 'while-count-program',
                    'title': 'Count with while',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Recreate the book\'s counting program: with a while '
                        'loop starting count at 1, print the numbers 1 to 5 '
                        'and let the loop end by itself.'
                    ),
                    'context': 'The while program of p. 123.',
                    'constraints': 'Use while (not for); five lines of output.',
                    'expected_behavior': 'The program prints 1 2 3 4 5, one per line.',
                    'explain': (
                        'count = 1 outside, the test count <= 5 before each '
                        'round, print then count = count + 1 inside — the '
                        'exact shape of the book program. Sindh Board Class '
                        'XI, Unit 3, 3.5.3 (while), p. 123.'
                    ),
                    'starter_code': (
                        'count = 1\n'
                        'while count <= 5:\n\n\n'
                    ),
                    'solution_code': (
                        'count = 1\n'
                        'while count <= 5:\n'
                        '    print(count)\n'
                        '    count = count + 1\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '1\n2\n3\n4\n5'},
                    ],
                    'xp_reward': 70,
                    'order': 3,
                    'reference': ref(UNIT, '3.5.3 while counting program', '123', CLASS),
                    'hints': [
                        'The body needs two statements: show the count, then grow it.',
                        'print(count) then count = count + 1, both indented.',
                    ],
                },
                {
                    'slug': 'sum-with-while',
                    'title': 'Sum 1 to 10 with while',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Using a while loop, add every number from 1 to 10 '
                        'into a total and print the total when the loop '
                        'ends.'
                    ),
                    'context': (
                        'Supplementary practice for while — the same running '
                        'total as the sequence program, now repeated '
                        '(section 3.5, pp. 115 and 123).'
                    ),
                    'constraints': 'One number of output: the total.',
                    'expected_behavior': 'The program prints: 55',
                    'explain': (
                        'total grows by i each round while i runs 1..10; '
                        '1+2+...+10 is 55. Sindh Board Class XI, Unit 3, '
                        '3.5.3 (while), p. 123.'
                    ),
                    'starter_code': (
                        'total = 0\n'
                        'i = 1\n'
                        'while i <= 10:\n\n\n'
                        'print(total)\n'
                    ),
                    'solution_code': (
                        'total = 0\n'
                        'i = 1\n'
                        'while i <= 10:\n'
                        '    total = total + i\n'
                        '    i = i + 1\n'
                        'print(total)\n'
                    ),
                    'test_cases': [
                        {'input': '', 'expected_output': '55'},
                    ],
                    'xp_reward': 80,
                    'order': 4,
                    'reference': ref(
                        UNIT, '3.5.3 while loops', '123', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'The loop body adds i to total and then increases i.',
                        'total = total + i / i = i + 1 — both indented.',
                    ],
                },
            ],
        },

        # ── nested loops ───────────────────────────────────────────────────
        {
            'slug': 'nested-loops',
            'title': 'Nested Loops',
            'content_type': 'interactive',
            'learning_objective': (
                'Put one loop inside another and trace which inner values '
                'run for each outer round.'
            ),
            'order': 6,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.5.3 Nested loop', '124', CLASS),
            'content_body': '''# Nested Loops

A loop inside a loop is a **nested loop** (p. 124). The outer loop runs one
round; during that round the **inner loop runs completely**. The book's
program pairs `i` and `j`, both over 1..3:

```python
for i in range(1, 4):
    for j in range(1, 4):
        print(i, j)
```

**Expected output** — the p. 124 run, printed as i-j pairs:

```output
1 1
1 2
1 3
2 1
2 2
2 3
3 1
3 2
3 3
```

Count the lines: 3 outer rounds × 3 inner rounds = 9 pairs. "Instructions
for Teachers" (p. 124) suggests the class vary this by mixing a `for` outer
loop with a `while` inner loop — the tracing rule stays the same.
''',
            'exercises': [
                {
                    'slug': 'trace-the-pairs',
                    'title': 'Trace the Pairs',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'What does this print? Type every line exactly, in '
                        'order.'
                    ),
                    'context': (
                        'for i in range(1, 3):\n'
                        '    for j in range(1, 4):\n'
                        '        print(i, j)'
                    ),
                    'expected_output': (
                        '1 1\n1 2\n1 3\n2 1\n2 2\n2 3'
                    ),
                    'explain': (
                        'i takes 1 and 2; the inner j completes 1, 2, 3 '
                        'inside every outer round, so 2 × 3 = 6 pairs. Sindh '
                        'Board Class XI, Unit 3, 3.5.3 (nested loop), p. 124.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.5.3 Nested loop tracing', '124', CLASS),
                    'hints': [
                        'The inner loop finishes all of its values before i changes.',
                        'Six lines: all the j\'s for i = 1, then all the j\'s for i = 2.',
                    ],
                },
                {
                    'slug': 'star-triangle',
                    'title': 'Challenge — Star Triangle',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'hard',
                    'instructions': (
                        'Read a number of rows n. Print a right triangle of '
                        'stars: row 1 has one `*`, row 2 has `**`, up to row '
                        'n — using a nested loop.'
                    ),
                    'context': (
                        'Supplementary challenge built on nested loops '
                        '(p. 124): the classic picture a nested loop draws.'
                    ),
                    'constraints': 'One row per line; no spaces between the stars.',
                    'expected_behavior': (
                        'For input 3 the program prints *, then **, then ***.'
                    ),
                    'explain': (
                        'The outer loop walks the rows 1..n; the inner loop '
                        'prints i stars on row i — the end="" argument keeps '
                        'them on one line, and the outer print() moves to '
                        'the next row. Sindh Board Class XI, Unit 3, 3.5.3 '
                        '(nested loop), p. 124.'
                    ),
                    'starter_code': (
                        'n = int(input())\n'
                        'for i in range(1, n + 1):\n'
                        '    # print i stars on one line\n\n'
                    ),
                    'solution_code': (
                        'n = int(input())\n'
                        'for i in range(1, n + 1):\n'
                        '    for j in range(i):\n'
                        '        print("*", end="")\n'
                        '    print()\n'
                    ),
                    'test_cases': [
                        {'input': '3\n', 'expected_output': '*\n**\n***'},
                        {'input': '1\n', 'expected_output': '*'},
                    ],
                    'xp_reward': 120,
                    'order': 2,
                    'reference': ref(
                        UNIT, '3.5.3 Nested loops', '124', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'The inner loop should run exactly i times on row i.',
                        'print("*", end="") keeps the stars on one line; a bare print() ends the row.',
                    ],
                },
            ],
        },

        # ── the big program ────────────────────────────────────────────────
        {
            'slug': 'shopping-bill-calculator',
            'title': 'Program — Shopping Bill Calculator',
            'content_type': 'interactive',
            'learning_objective': (
                'Read a full-size textbook program that combines while, '
                'if-elif-else and f-strings, and reuse its total-building '
                'pattern.'
            ),
            'order': 7,
            'duration_minutes': 15,
            'xp_reward': 60,
            'reference': ref(UNIT, '3.5 Program Shopping Bill Calculator', '126', CLASS),
            'content_body': '''# Program — Shopping Bill Calculator (p. 126)

This is the unit's capstone: a 46-line program that ties every control
structure together. Its heart is a **while loop** that keeps asking for
items, prices collected with `float(input())`, category choices, and
f-strings with `:.2f` to print money with exactly two decimals.

A trimmed working copy — same machinery, one item per round:

```python
total = 0.0
more = "y"
while more == "y":
    price = float(input("Price: "))
    qty = int(input("Quantity: "))
    total = total + price * qty
    more = input("More items? (y/n): ")
print(f"Total: {total:.2f}")
```

Run it below and feed it a small basket.

```python
total = 0.0
more = "y"
while more == "y":
    price = float(input())
    qty = int(input())
    total = total + price * qty
    more = input()
print(f"Total: {total:.2f}")
```

```text
12.5
2
n
Total: 25.00
```

`:.2f` is doing real work: `25.0` becomes `25.00`, the way bills are
written. Every concept of the unit — sequence, selection, repetition,
input, formatting — appears in these eight lines.
''',
            'exercises': [
                {
                    'slug': 'running-total',
                    'title': 'Running Total',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'hard',
                    'instructions': (
                        'Read three prices, one per line, add them into a '
                        'running total while-loop-free for once, and print '
                        'the total with two decimals in the form '
                        '`Total: 45.50`.'
                    ),
                    'context': (
                        'Recreates the bill calculator\'s money handling '
                        '(p. 126): float input, an accumulator, and `:.2f` '
                        'formatting.'
                    ),
                    'constraints': (
                        'Use an f-string with `:.2f`; one line of output '
                        'starting with Total: .'
                    ),
                    'expected_behavior': (
                        'For inputs 10.25, 20.25 and 15.00 the program '
                        'prints: Total: 45.50'
                    ),
                    'explain': (
                        'float() converts each price line; adding each to '
                        'total builds the accumulator of the bill program, '
                        'and f"{total:.2f}" writes it like money. Sindh '
                        'Board Class XI, Unit 3, Program Shopping Bill '
                        'Calculator, p. 126.'
                    ),
                    'starter_code': (
                        'total = 0.0\n\n\n\n\n'
                        '# print f"Total: " with two decimals\n'
                    ),
                    'solution_code': (
                        'total = 0.0\n'
                        'total = total + float(input())\n'
                        'total = total + float(input())\n'
                        'total = total + float(input())\n'
                        'print(f"Total: {total:.2f}")\n'
                    ),
                    'test_cases': [
                        {'input': '10.25\n20.25\n15.00\n', 'expected_output': 'Total: 45.50'},
                        {'input': '0.5\n0.5\n0.5\n', 'expected_output': 'Total: 1.50'},
                    ],
                    'xp_reward': 110,
                    'order': 1,
                    'reference': ref(UNIT, 'Program Shopping Bill Calculator — f-strings', '126', CLASS),
                    'hints': [
                        'Accumulator pattern: total = total + float(input()), repeated.',
                        'f"Total: {total:.2f}" formats money the book way.',
                    ],
                },
            ],
        },
    ],
}
