"""
Seed command for course content — idempotent upsert.

Usage:
    python manage.py seed_courses

Creates or UPDATES (safe to re-run after editing content below):
    - Demo user: demo@codeyaar.dev / demo123
    - Python Foundations course: 6 chapters, 14 lessons, real exercises
    - Git & GitHub Foundations short course: 2 chapters, 5 lessons
    - Resources and achievements

Nothing is ever deleted: chapters/lessons/exercises that are no longer in
the spec are deactivated so existing learner progress records stay intact.
Every exercise that advertises execution is graded by the real sandbox —
no fabricated results, and quiz answers/explanations are revealed only
after an attempt.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from learning.models import (
    CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Achievement, UserProfile,
)

DEMO_EMAIL = 'demo@codeyaar.dev'
DEMO_PASSWORD = 'demo123'

LESSON_FIELDS = (
    'title', 'content_type', 'learning_objective', 'content_body',
    'order', 'duration_minutes', 'xp_reward',
)
EXERCISE_FIELDS = (
    'title', 'exercise_type', 'instructions', 'context', 'constraints',
    'expected_behavior', 'explain', 'difficulty', 'language',
    'starter_code', 'solution_code', 'choices', 'expected_output',
    'test_cases', 'xp_reward', 'is_final_assessment', 'order',
)
RESOURCE_FIELDS = ('description', 'resource_type', 'file_url', 'order')

# ══════════════════════════════════════════════════════════════════════════
#  PYTHON FOUNDATIONS
# ══════════════════════════════════════════════════════════════════════════

PY_CH1 = {
    'slug': 'python-basics',
    'title': 'Python Basics',
    'description': 'Run your first programs and master the building blocks: output, comments, variables, input, and operators.',
    'order': 1,
    'lessons': [
        {
            'slug': 'hello-python',
            'title': 'Hello, Python!',
            'learning_objective': 'Run your first Python program and explain what print() does.',
            'order': 1, 'duration_minutes': 10, 'xp_reward': 50,
            'content_body': '''# Hello, Python!

Python is one of the most popular programming languages in the world. It powers websites, data analysis, artificial intelligence, and automation — and it is famous for reading close to plain English.

By the end of this lesson you will have run a real Python program.

## Your first program

To show something on the screen, Python uses the `print()` function:

```python
print("Hello, World!")
```

**Expected output:** `Hello, World!`

Let us take that apart, piece by piece:

- `print` is the **name** of the function — it tells Python to display something.
- The **parentheses** hold the value the function works on.
- `"Hello, World!"` is a **string** — text wrapped in quotes. The quotes mark where the text starts and ends; they are not printed themselves.

You can print your own message too:

```python
print("Main, yaar!")
```

**Expected output:** `Main, yaar!`

## Why "Hello, World!"?

Since the 1970s, the first program in every new language prints "Hello, World!". It proves your setup works. Every programmer on earth has typed this line — now it is your turn.

## Common mistakes

- Forgetting the parentheses: `print "Hi"` worked in old Python 2 but gives a **SyntaxError** in Python 3. Always write `print(...)`.
- Forgetting the closing quote: `print("Hi` gives a SyntaxError. Every quote must be closed.
- Capitalising the name: `Print("Hi")` gives a **NameError**. Function names are case-sensitive.

## Practice

Press the Run button on the example above and watch the real output appear under the code. Then do the exercise: print a greeting of your own.
''',
            'exercises': [
                {
                    'slug': 'print-hello-world',
                    'title': 'Print Hello, World!',
                    'exercise_type': 'code',
                    'instructions': 'Write a program that prints exactly: Hello, World!',
                    'context': 'Every programmer starts here. The "Hello, World!" program is a tradition.',
                    'constraints': 'Use the print() function. The output must match exactly — no extra text.',
                    'expected_behavior': 'The program prints one line: Hello, World!',
                    'explain': 'print() displays the string you pass it. The quotes tell Python where the text starts and ends — they are not part of the output.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': '# Write your code below\n',
                    'solution_code': 'print("Hello, World!")',
                    'expected_output': 'Hello, World!',
                    'test_cases': [{'input': '', 'expected_output': 'Hello, World!'}],
                    'xp_reward': 100, 'order': 1,
                    'hints': [
                        'The syntax is: print("your text here")',
                        'Make sure the capitalisation and punctuation match exactly: Hello, World!',
                        'Solution: print("Hello, World!")',
                    ],
                },
                {
                    'slug': 'hello-quiz',
                    'title': 'Which line is valid Python 3?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Which line is a correct Python 3 statement to display the text Hi?',
                    'explain': 'Python 3 requires parentheses around the value. print is lowercase — Python names are case-sensitive, and echo() does not exist in Python.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'print("Hi")', 'is_correct': True},
                        {'id': 'b', 'text': 'print "Hi"', 'is_correct': False},
                        {'id': 'c', 'text': 'Print("Hi")', 'is_correct': False},
                        {'id': 'd', 'text': 'echo("Hi")', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
            ],
        },
        {
            'slug': 'print-and-comments',
            'title': 'print(), Comments, and Syntax',
            'learning_objective': 'Print multiple lines and write comments that explain code.',
            'order': 2, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# print(), Comments, and Syntax

Programs are read far more often than they are written. This lesson covers two things you will use in every program from now on: printing output, and writing comments.

## Printing more than one thing

Each `print()` call writes its own line:

```python
print("First line")
print("Second line")
```

**Expected output:** two lines — `First line` then `Second line`.

Separate values with commas and Python joins them with a space:

```python
print("Marks:", 92)
```

**Expected output:** `Marks: 92`

Text can use single OR double quotes — they mean the same thing:

```python
print('Both styles work')
print("Both styles work")
```

## Comments

Anything after a `#` on a line is a **comment**. Python ignores it completely:

```python
# Greet the user before doing any work
print("Salam!")  # this part is a comment too
```

**Expected output:** `Salam!` — the comments never appear.

Comments exist for the human reading the code — including you, three months from now. Explain *why*, not *what*.

## Syntax: the rules of the language

Python is strict about form. A few rules that trip up every beginner:

- Statements normally take one line each.
- Blocks (like `if` blocks) are marked by **indentation** — usually 4 spaces. The colon `:` before an indented block is required.
- Python cares about spaces and capitalisation: `print` is not `Print`.

## Common mistakes

- Writing code after a `#` and wondering why nothing runs — everything after `#` is ignored.
- `print("text` with an unclosed quote — Python reports a SyntaxError on a different line than you expect; check your quotes.
- Random indentation in plain statements — keep top-level lines flush to the left margin.

## Practice

Run the examples above, then complete the exercise: print exactly two lines.
''',
            'exercises': [
                {
                    'slug': 'two-line-print',
                    'title': 'Print Two Lines',
                    'exercise_type': 'code',
                    'instructions': 'Write a program that prints exactly two lines:\nFirst line\nSecond line',
                    'context': 'Multiple print() calls produce multiple lines, in order.',
                    'expected_behavior': 'Line 1: First line — Line 2: Second line',
                    'explain': 'Each print() call outputs one line. Order of calls = order of lines.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': '# Print exactly two lines: First line, then Second line\n',
                    'solution_code': 'print("First line")\nprint("Second line")',
                    'expected_output': 'First line\nSecond line',
                    'test_cases': [{'input': '', 'expected_output': 'First line\nSecond line'}],
                    'xp_reward': 75, 'order': 1,
                    'hints': [
                        'One print() call produces one line.',
                        'You need two print() calls, in order.',
                        'Solution: print("First line") then print("Second line")',
                    ],
                },
                {
                    'slug': 'comments-quiz',
                    'title': 'What does Python do with comments?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What does Python do with text after a # on a line?',
                    'explain': 'A # starts a comment — Python ignores the rest of the line. Comments are for humans only.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'It ignores it', 'is_correct': True},
                        {'id': 'b', 'text': 'It prints it after the code runs', 'is_correct': False},
                        {'id': 'c', 'text': 'It treats it as a syntax error', 'is_correct': False},
                        {'id': 'd', 'text': 'It runs it as code', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
            ],
        },
        {
            'slug': 'variables',
            'title': 'Variables and Data Types',
            'learning_objective': 'Store values in variables and name the four core data types.',
            'order': 3, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# Variables and Data Types

A variable is a **name that refers to a value**. You create one with the assignment operator `=`:

```python
name = "Ayesha"
age = 19
```

Think of it as a labelled box: the label is the name, the box holds the value. From now on, writing `name` anywhere gives you `"Ayesha"`.

## Data types

Python values have **types**. The four you will use constantly:

- `int` — whole numbers: `42`, `-7`, `0`
- `float` — decimal numbers: `3.14`, `0.5`
- `str` — text (strings): `"Karachi"`, `'hi'`
- `bool` — truth values: `True`, `False`

Check a value's type with `type()`:

```python
print(type(42))
print(type("42"))
```

**Expected output:** `<class 'int'>` on the first line and `<class 'str'>` on the second. Notice the difference between the number 42 and the text "42"!

## Naming rules

A variable name:

- must start with a letter or underscore (`score`, `_temp`, `city_name`)
- may contain letters, digits, and underscores (`marks2` is fine)
- cannot start with a digit (`2ndplace` is not)
- cannot contain spaces (`my name` is not)
- is case-sensitive (`Name` and `name` are two different variables)

## Reassigning

A variable can change later — it always holds the most recent value:

```python
score = 0
score = 100
print(score)
```

**Expected output:** `100`

## Common mistakes

- `2marks = 5` → SyntaxError: names cannot start with a digit.
- `marks = "100"` then trying to do maths — that is a string, not a number. Quotes matter.
- Typing the wrong case: assigning `total = 50` then printing `Total` → NameError.
- Forgetting that `=` assigns while comparison comes later with `==`.

## Practice

Run the examples, then create and print your own variable in the exercise.
''',
            'exercises': [
                {
                    'slug': 'create-variable',
                    'title': 'Create and Print a Variable',
                    'exercise_type': 'code',
                    'instructions': 'Create a variable named `score` with the integer value 100, then print it.',
                    'context': 'Variables let you store and reuse values in your programs.',
                    'constraints': 'The variable must be named exactly `score`.',
                    'expected_behavior': 'The program prints: 100',
                    'explain': 'score = 100 stores the integer 100 in a variable; print(score) displays it. No quotes — quotes would make it text.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': '# Create a variable named score with value 100, then print it\n',
                    'solution_code': 'score = 100\nprint(score)',
                    'expected_output': '100',
                    'test_cases': [{'input': '', 'expected_output': '100'}],
                    'xp_reward': 100, 'order': 1,
                    'hints': [
                        'Assignment looks like: name = value',
                        'Use print(score) on the second line.',
                        'Solution: score = 100 then print(score)',
                    ],
                },
                {
                    'slug': 'variable-types',
                    'title': 'What type is 42?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What type does type(42) report?',
                    'explain': '42 without quotes is a whole number, so its type is int. "42" with quotes would be str, and 42.0 would be float.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'str', 'is_correct': False},
                        {'id': 'b', 'text': 'int', 'is_correct': True},
                        {'id': 'c', 'text': 'float', 'is_correct': False},
                        {'id': 'd', 'text': 'bool', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
                {
                    'slug': 'naming-rules',
                    'title': 'Valid variable names',
                    'exercise_type': 'multiple_select',
                    'instructions': 'Select ALL names that are valid Python variable names.',
                    'explain': 'Names may start with letters or underscores and may contain digits, but cannot start with a digit, contain spaces or hyphens, or be a reserved keyword like class.',
                    'difficulty': 'medium', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'user_name', 'is_correct': True},
                        {'id': 'b', 'text': '2ndplace', 'is_correct': False},
                        {'id': 'c', 'text': 'my-score', 'is_correct': False},
                        {'id': 'd', 'text': 'TotalWidth', 'is_correct': True},
                        {'id': 'e', 'text': 'class', 'is_correct': False},
                    ],
                    'xp_reward': 75, 'order': 3,
                },
            ],
        },
        {
            'slug': 'user-input',
            'title': 'User Input and Type Conversion',
            'learning_objective': 'Read text from the user with input() and convert it into int or float.',
            'order': 4, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# User Input and Type Conversion

So far your programs only used values written inside the code. Real programs talk back: they ask the user something and react to the answer.

## input()

The `input()` function pauses the program, waits for the user to type something and press Enter, and hands it back to you:

```python
name = input("Your name: ")
print("Hello, " + name)
```

If the user types `Sara`, the output is: `Hello, Sara`

You cannot type live input into lesson snippets here, so the exercise for this lesson is graded by the code runner which supplies the input for you — read the instructions carefully.

## The golden rule: input() always returns a string

Whatever the user types — `18`, `3.5`, `Karachi` — Python stores it as **text**. That is why this breaks:

```python
age_text = "18"
print(age_text + 1)
```

**Expected result:** a **TypeError** — Python refuses to add text and a number together.

## Converting between types

Wrap the value in the type you want:

```python
age = int("18")
print(age + 1)
```

**Expected output:** `19`

- `int("18")` → the integer 18 (only for whole-number text)
- `float("3.5")` → the number 3.5
- `str(18)` → the text "18"

A typical program that reads a number:

```python
price_text = "250"
quantity_text = "4"
total = int(price_text) * int(quantity_text)
print(total)
```

**Expected output:** `1000`

## Common mistakes

- Forgetting the conversion: `input()` returns str, so maths on it crashes. Convert first with `int()` or `float()`.
- `int("abc")` → **ValueError**: you cannot convert text that is not a number.
- `int("3.5")` → also a ValueError. Use `float("3.5")` for decimals.

## Practice

Answer the quick checks below — they are what beginners actually get wrong in interviews and exams.
''',
            'exercises': [
                {
                    'slug': 'input-returns-str',
                    'title': 'What does input() return?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'A user types 25 in response to input(). What does Python store?',
                    'explain': 'input() always returns a string — the digits are text "25" until you convert them with int().',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'The number 25 (int)', 'is_correct': False},
                        {'id': 'b', 'text': 'The text "25" (str)', 'is_correct': True},
                        {'id': 'c', 'text': 'Nothing until you convert it manually', 'is_correct': False},
                        {'id': 'd', 'text': 'A decimal 25.0 (float)', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 1,
                },
                {
                    'slug': 'convert-age',
                    'title': 'Convert input to a number',
                    'exercise_type': 'fill_blank',
                    'instructions': 'Type the complete statement that reads one line of input and stores it as an integer in the variable age. Write exactly one line of Python.',
                    'context': 'This single line appears in almost every beginner program.',
                    'expected_behavior': 'One assignment using int() around input().',
                    'explain': 'input() grabs the typed text; int(...) converts it; age = ... stores the result. The calls nest: conversion happens on what input returns.',
                    'difficulty': 'easy', 'language': 'python',
                    'solution_code': 'age = int(input())',
                    'xp_reward': 75, 'order': 2,
                    'hints': [
                        'You need input() and int() together.',
                        'int() goes around input(): int(input())',
                        'Solution: age = int(input())',
                    ],
                },
            ],
        },
        {
            'slug': 'operators',
            'title': 'Operators and Expressions',
            'learning_objective': 'Use Python arithmetic operators — including //, % and ** — and predict their results.',
            'order': 5, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# Operators and Expressions

Operators combine values into **expressions**. You already know `+`. Here is the full beginner set.

## Arithmetic

```python
print(7 + 2)
print(7 - 2)
print(7 * 2)
```

**Expected output:** `9`, `5`, `14` — one per line.

Two operators that are NOT what they look like:

```python
print(7 / 2)
```

**Expected output:** `3.5` — single slash division always gives a decimal (float), even when it divides evenly: `6 / 2` gives `3.0`.

```python
print(7 // 2)
```

**Expected output:** `3` — double slash is **floor division**: divide, then throw away the decimal part.

```python
print(7 % 2)
```

**Expected output:** `1` — `%` is the **remainder** (modulo). Ask: "what is left over after whole division?"

```python
print(2 ** 3)
```

**Expected output:** `8` — `**` is exponentiation: 2 to the power 3.

## Why % matters

`n % 2` is `0` for even numbers and `1` for odd numbers — the classic way to check. And `100 % 7` is `2` because 7 goes into 100 fourteen times (98) with 2 left over.

## Shortcut assignment

```python
total = 0
total += 5
print(total)
```

**Expected output:** `5`. `total += 5` means `total = total + 5`. The same works with `-=`, `*=`, `/=`.

## Precedence

Multiplication binds tighter than addition, just like in maths:

```python
print(2 + 3 * 4)
```

**Expected output:** `14` (not 20). Brackets win: `(2 + 3) * 4` is `20`.

## Common mistakes

- Expecting `7 / 2` to print `3` — that is `//`.
- Writing `2 * 3` as `2x3` — Python always needs the operator symbol.
- Forgetting that `**` beats `*`: `2 * 3 ** 2` is `18`, not `36`.

## Practice

Predict, then run, then verify — the exercise below checks the three operators beginners mix up most.
''',
            'exercises': [
                {
                    'slug': 'predict-division',
                    'title': 'Predict: /, // and %',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this program print?\n\nprint(7 / 2)\nprint(7 // 2)\nprint(7 % 2)',
                    'expected_behavior': 'Three lines.',
                    'explain': '7 / 2 = 3.5 (true division always gives a float), 7 // 2 = 3 (floor), 7 % 2 = 1 (remainder of 7 divided by 2).',
                    'difficulty': 'medium', 'language': 'python',
                    'expected_output': '3.5\n3\n1',
                    'xp_reward': 75, 'order': 1,
                    'hints': [
                        'Single / gives a decimal result.',
                        '// keeps only the whole part; % keeps only the leftovers.',
                        'Answer: 3.5 then 3 then 1 (each on its own line)',
                    ],
                },
                {
                    'slug': 'shop-total',
                    'title': 'Shop total',
                    'exercise_type': 'code',
                    'instructions': 'An item costs 250 rupees. Compute and print the cost of 4 items using the variables provided.',
                    'context': 'Real programs compute totals from prices and quantities.',
                    'expected_behavior': 'The program prints: 1000',
                    'explain': 'price * quantity multiplies the two integers; print displays the product 1000.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': 'price = 250\nquantity = 4\n\n# Compute and print the total cost below\n',
                    'solution_code': 'price = 250\nquantity = 4\nprint(price * quantity)',
                    'expected_output': '1000',
                    'test_cases': [{'input': '', 'expected_output': '1000'}],
                    'xp_reward': 75, 'order': 2,
                    'hints': [
                        'Use the * operator.',
                        'print(price * quantity)',
                    ],
                },
                {
                    'slug': 'precedence-quiz',
                    'title': 'What is 2 + 3 * 4?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What does print(2 + 3 * 4) output?',
                    'explain': '* binds tighter than +, so Python computes 3 * 4 = 12 first, then 2 + 12 = 14. Brackets are needed to force the addition first.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': '14', 'is_correct': True},
                        {'id': 'b', 'text': '20', 'is_correct': False},
                        {'id': 'c', 'text': '24', 'is_correct': False},
                        {'id': 'd', 'text': '9', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 3,
                },
            ],
        },
    ],
}

PY_CH2 = {
    'slug': 'control-flow',
    'title': 'Making Decisions and Repeating',
    'description': 'Teach your program to choose with if/elif/else and repeat with for and while loops.',
    'order': 2,
    'lessons': [
        {
            'slug': 'conditions',
            'title': 'Conditional Statements',
            'learning_objective': 'Write if/elif/else programs that react differently to different values.',
            'order': 1, 'duration_minutes': 20, 'xp_reward': 50,
            'content_body': '''# Conditional Statements

Programs become interesting when they can **choose**. An `if` statement runs code only when a condition is true:

```python
temperature = 30

if temperature > 25:
    print("It's hot!")
```

**Expected output:** `It's hot!` — because 30 is greater than 25.

The parts that matter: the condition ends with a **colon** `:`, and the line below is **indented** (4 spaces). The indented line only runs when the condition is true.

## if / elif / else

Check several possibilities in order — the first true branch wins, the rest are skipped:

```python
score = 72

if score >= 80:
    print("Grade A")
elif score >= 60:
    print("Grade B")
else:
    print("Grade C")
```

**Expected output:** `Grade B`

`elif` is short for "else if". `else` catches everything left.

## Comparison operators

- `==` equal to, `!=` not equal
- `>` less/greater, `>=` / `<=` with-equal
- `and`, `or`, `not` combine conditions: `age >= 18 and has_id`

Warning: `=` **assigns**, `==` **compares**. Writing one where you meant the other is a classic bug.

```python
city = "Karachi"
print(city == "Karachi")
```

**Expected output:** `True`

## Common mistakes

- Missing the colon: `if temperature > 25` alone is a SyntaxError.
- Forgetting the indentation — Python needs it to know which lines belong to the branch.
- `if score = 80:` → SyntaxError; comparisons use `==`.
- Branch order: put the strictest condition first. If you test `score >= 50` before `score >= 80`, a score of 95 never reaches the top grade.

## Practice

The exercise reads a real number with input() — the code runner supplies the test values, so Submit grades your program on several ages at once.
''',
            'exercises': [
                {
                    'slug': 'check-age',
                    'title': 'Adult or Minor',
                    'exercise_type': 'code',
                    'instructions': 'The first line reads an age from input. Write an if/else below that prints "Adult" when age is 18 or more, and "Minor" otherwise.',
                    'context': 'Age verification is the most common real-world use of conditionals.',
                    'constraints': 'Print exactly Adult or Minor — nothing else.',
                    'expected_behavior': '20 -> Adult, 15 -> Minor, 18 -> Adult',
                    'explain': 'age >= 18 is the boundary: 18 counts as an adult, so the operator must be >= (not >). The else branch catches every smaller age.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': 'age = int(input())\n\n# Write your if/else statement below\n',
                    'solution_code': 'age = int(input())\n\nif age >= 18:\n    print("Adult")\nelse:\n    print("Minor")',
                    'test_cases': [
                        {'input': '20\n', 'expected_output': 'Adult'},
                        {'input': '15\n', 'expected_output': 'Minor'},
                        {'input': '18\n', 'expected_output': 'Adult'},
                    ],
                    'xp_reward': 100, 'order': 1,
                    'hints': [
                        'The comparison for "18 or more" is: age >= 18',
                        'if needs a colon, and the print lines must be indented.',
                        'Solution: if age >= 18: print("Adult") / else: print("Minor")',
                    ],
                },
                {
                    'slug': 'equals-vs-assign',
                    'title': 'Which compares?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Which operator checks whether two values are equal?',
                    'explain': 'A single = stores a value (assignment). A double == compares two values and produces True or False.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': '==', 'is_correct': True},
                        {'id': 'b', 'text': '=', 'is_correct': False},
                        {'id': 'c', 'text': '!=', 'is_correct': False},
                        {'id': 'd', 'text': ':=', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
                {
                    'slug': 'predict-branch',
                    'title': 'Which branch runs?',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\nx = 5\nif x > 10:\n    print("A")\nelif x > 3:\n    print("B")\nelse:\n    print("C")',
                    'expected_behavior': 'One letter.',
                    'explain': 'x = 5 is not greater than 10, so branch A is skipped. 5 IS greater than 3, so branch B runs and the rest is ignored.',
                    'difficulty': 'medium', 'language': 'python',
                    'expected_output': 'B',
                    'xp_reward': 75, 'order': 3,
                    'hints': [
                        'Test the conditions in order, top to bottom.',
                        '5 > 10 is False; check the next one.',
                    ],
                },
            ],
        },
        {
            'slug': 'loops',
            'title': 'Loops',
            'learning_objective': 'Repeat work with for and while loops, and use range() correctly.',
            'order': 2, 'duration_minutes': 20, 'xp_reward': 50,
            'content_body': '''# Loops

Loops repeat a block of code. Instead of pasting the same print ten times, tell Python once: "do this for each of these".

## for with range()

```python
for i in range(4):
    print(i)
```

**Expected output:** `0`, `1`, `2`, `3` — one per line.

`range(4)` produces numbers from 0 **up to but not including** 4. That off-by-one rule bites everyone once. range has three forms:

- `range(5)` → 0 1 2 3 4
- `range(1, 6)` → 1 2 3 4 5 (start included, end still excluded)
- `range(0, 10, 2)` → 0 2 4 6 8 (step of 2)

## for over a list

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)
```

**Expected output:** the three fruit names, one per line.

## The accumulator pattern

To add things up, keep a running total outside the loop:

```python
total = 0

for n in range(1, 6):
    total += n

print(total)
```

**Expected output:** `15` (1+2+3+4+5)

## while loops

Repeat **as long as** a condition stays true:

```python
count = 3

while count > 0:
    print(count)
    count -= 1

print("Lifoff!")
```

**Expected output:** `3`, `2`, `1`, then `Lifoff!`

A `while` loop must contain something that eventually makes the condition false — otherwise it never stops (the code runner will cut it off with a timeout).

## Common mistakes

- `range(1, 5)` when you meant 1 through 5 — remember the end is EXCLUDED, use `range(1, 6)`.
- Forgetting the colon or indentation after `for` / `while`.
- A while loop that never changes its condition variable → infinite loop.
- Reinitialising the accumulator INSIDE the loop (it gets reset every pass). Keep it above the loop.

## Practice

Predict what a loop prints, then write two loops of your own. The exercises are graded by running your real code.
''',
            'exercises': [
                {
                    'slug': 'predict-loop-output',
                    'title': 'Predict the loop output',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\nfor i in range(3):\n    print(i * 2)',
                    'expected_behavior': 'Three lines.',
                    'explain': 'range(3) gives i = 0, 1, 2. Multiplying each by 2 produces 0, 2, 4 — each printed on its own line.',
                    'difficulty': 'easy', 'language': 'python',
                    'expected_output': '0\n2\n4',
                    'xp_reward': 75, 'order': 1,
                    'hints': [
                        'range(3) starts at 0, not 1.',
                        'Multiply each value by 2 as you go.',
                    ],
                },
                {
                    'slug': 'print-evens',
                    'title': 'Print the even numbers',
                    'exercise_type': 'code',
                    'instructions': 'Use a for loop to print every even number from 2 to 10 (inclusive), one per line.',
                    'context': 'range(start, stop, step) is how you walk numbers in fixed jumps.',
                    'expected_behavior': 'Five lines: 2, 4, 6, 8, 10.',
                    'explain': 'range(2, 11, 2) starts at 2, steps by 2, and stops before 11 — so it yields exactly 2, 4, 6, 8, 10.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': '# Print 2, 4, 6, 8, 10 — one per line\n',
                    'solution_code': 'for i in range(2, 11, 2):\n    print(i)',
                    'expected_output': '2\n4\n6\n8\n10',
                    'test_cases': [{'input': '', 'expected_output': '2\n4\n6\n8\n10'}],
                    'xp_reward': 100, 'order': 2,
                    'hints': [
                        'range can take a step: range(start, stop, step)',
                        'Start at 2, step by 2, and remember the stop value is excluded.',
                        'Solution: for i in range(2, 11, 2): print(i)',
                    ],
                },
                {
                    'slug': 'sum-loop',
                    'title': 'Sum with an accumulator',
                    'exercise_type': 'code',
                    'instructions': 'Using the variable total provided, add every number from 1 to 100 (inclusive) and print the result.',
                    'context': 'This pattern — reset once, loop, accumulate — is the seed of every counting problem.',
                    'expected_behavior': 'The program prints: 5050',
                    'explain': 'range(1, 101) covers 1 through 100 because the end is excluded. total += n inside the loop keeps a running sum; Gauss famously found the answer 5050.',
                    'difficulty': 'medium', 'language': 'python',
                    'starter_code': 'total = 0\n\n# Add every number from 1 to 100 into total, then print it\n',
                    'solution_code': 'total = 0\n\nfor n in range(1, 101):\n    total += n\n\nprint(total)',
                    'expected_output': '5050',
                    'test_cases': [{'input': '', 'expected_output': '5050'}],
                    'xp_reward': 125, 'order': 3,
                    'hints': [
                        'Loop over range(1, 101) — the end is excluded.',
                        'Inside the loop write: total += n',
                        'print(total) goes AFTER the loop, not inside it.',
                    ],
                },
                {
                    'slug': 'infinite-while-quiz',
                    'title': 'Why does this never stop?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What is wrong with this program?\n\ncount = 5\nwhile count > 0:\n    print(count)',
                    'explain': 'The condition depends on count, but nothing inside the loop changes count — it stays 5 forever. A while loop must move its condition closer to false.',
                    'difficulty': 'medium', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'The loop never changes count, so the condition stays True forever', 'is_correct': True},
                        {'id': 'b', 'text': 'while cannot use >', 'is_correct': False},
                        {'id': 'c', 'text': 'print is missing an argument', 'is_correct': False},
                        {'id': 'd', 'text': 'count starts too small', 'is_correct': False},
                    ],
                    'xp_reward': 75, 'order': 4,
                },
            ],
        },
    ],
}

PY_CH3 = {
    'slug': 'data-structures',
    'title': 'Working with Data',
    'description': 'Store and transform text with strings, and collections of values with lists and dictionaries.',
    'order': 3,
    'lessons': [
        {
            'slug': 'strings',
            'title': 'Strings',
            'learning_objective': 'Index, slice, and transform strings with the most common methods.',
            'order': 1, 'duration_minutes': 20, 'xp_reward': 50,
            'content_body': '''# Strings

A string is a **sequence of characters**, and Python gives you tools to pick it apart and reshape it.

## Indexing

Every character has a position number, starting at **0**:

```python
word = "Python"
print(word[0])
print(word[1])
```

**Expected output:** `P`, then `y`. Yes, zero-based — the first character is at position 0.

Negative indices count from the end: `word[-1]` is `"n"`, `word[-2]` is `"o"`.

## Slicing

Take a range of characters with `word[start:stop]` — start included, stop excluded (same rule as range):

```python
word = "Python"
print(word[0:3])
```

**Expected output:** `Pyt`

Leave one side out and Python uses the edge: `word[:3]` is also `"Pyt"`, `word[3:]` is `"hon"`.

## Useful operations

```python
print(len("Karachi"))
```

**Expected output:** `7` — `len()` counts characters.

Methods (note the parentheses — they are functions attached to the string):

```python
print("  hi  ".strip())
print("hello".upper())
print("banana".replace("a", "o"))
```

**Expected output:** `hi` (spaces gone), `HELLO`, `bonono`.

Join values with `+`, or build text inside f-strings:

```python
name = "Sana"
marks = 88
print(f"{name} scored {marks}")
```

**Expected output:** `Sana scored 88`

## Strings do not change in place

```python
greeting = "hello"
greeting.upper()
print(greeting)
```

**Expected output:** still `hello`. String methods return a NEW string; the original is untouched. You must write `greeting = greeting.upper()` to keep the result.

## Common mistakes

- `word[6]` on a 6-letter word → IndexError (valid positions are 0 through 5).
- Expecting `word[0:3]` to include position 3 — the stop is excluded.
- Calling a method but ignoring its return value (the `.upper()` example above).

## Practice

Slice and transform in the exercises below — all graded by running real code.
''',
            'exercises': [
                {
                    'slug': 'slice-predict',
                    'title': 'Predict the slice',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\nword = "Python"\nprint(word[0:3])\nprint(word[-1])',
                    'expected_behavior': 'Two lines.',
                    'explain': 'word[0:3] takes positions 0, 1, 2 — the stop index is excluded — giving Pyt. word[-1] is the last character, n.',
                    'difficulty': 'easy', 'language': 'python',
                    'expected_output': 'Pyt\nn',
                    'xp_reward': 75, 'order': 1,
                    'hints': [
                        'The slice stops BEFORE the second number.',
                        '-1 means the last character.',
                    ],
                },
                {
                    'slug': 'capitalise-city',
                    'title': 'Capitalise a city name',
                    'exercise_type': 'code',
                    'instructions': 'The variable city holds "karachi". Print it with only its first letter capitalised, using a string method.',
                    'context': 'User-entered text almost always needs tidying before display.',
                    'expected_behavior': 'The program prints: Karachi',
                    'explain': '.capitalize() lowercases everything except the first letter — exactly right for names. The result must be printed (or stored); strings never change in place.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': 'city = "karachi"\n\n# Print city with its first letter capitalised\n',
                    'solution_code': 'city = "karachi"\nprint(city.capitalize())',
                    'expected_output': 'Karachi',
                    'test_cases': [{'input': '', 'expected_output': 'Karachi'}],
                    'xp_reward': 75, 'order': 2,
                    'hints': [
                        'There is a method named exactly for this: .capitalize()',
                        'print(city.capitalize())',
                    ],
                },
                {
                    'slug': 'string-immutable-quiz',
                    'title': 'Change a character?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What happens when you run this?\n\nword = "code"\nword[0] = "C"',
                    'explain': 'Strings are immutable — you cannot assign into a position. Build a new string instead, e.g. "C" + word[1:].',
                    'difficulty': 'medium', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'TypeError — strings cannot be changed in place', 'is_correct': True},
                        {'id': 'b', 'text': 'word becomes "Code"', 'is_correct': False},
                        {'id': 'c', 'text': 'SyntaxError — the syntax is invalid', 'is_correct': False},
                        {'id': 'd', 'text': 'Nothing happens silently', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 3,
                },
            ],
        },
        {
            'slug': 'lists',
            'title': 'Lists',
            'learning_objective': 'Create, index, modify, and loop over lists.',
            'order': 2, 'duration_minutes': 20, 'xp_reward': 50,
            'content_body': '''# Lists

A list is an **ordered, changeable collection** of values in square brackets:

```python
colors = ["red", "green", "blue"]
```

Like strings, lists are indexed from 0: `colors[0]` is `"red"` and `colors[-1]` is `"blue"`. Slicing works the same way too: `colors[0:2]` gives the first two items.

## Changing a list

```python
nums = [1, 2, 3]
nums.append(4)
print(nums)
```

**Expected output:** `[1, 2, 3, 4]` — `append()` adds to the end **and changes the list itself** (unlike string methods!).

More tools:

- `nums.insert(0, 99)` — add at a position
- `nums.remove(2)` — delete the value 2 (not position 2!)
- `nums.pop()` — remove and return the last item
- `nums[0] = 7` — replace in place

## Measuring and summarising

```python
marks = [45, 88, 72]
print(len(marks))
print(sum(marks))
print(max(marks))
```

**Expected output:** `3`, then `205`, then `88`.

## Looping over a list

This is the pairing you will use constantly:

```python
for color in ["red", "green", "blue"]:
    print(color)
```

**Expected output:** the three colors on separate lines.

Check membership with `in`:

```python
print("green" in ["red", "green", "blue"])
```

**Expected output:** `True`

## Common mistakes

- `colors[3]` on a 3-item list → IndexError. Positions are 0..2.
- Expecting `append` to return the new list — it modifies in place and returns None. Write `nums.append(4)`, not `nums = nums.append(4)`.
- `remove(x)` when x is not in the list → ValueError.

## Practice

Fix a broken index, then combine everything you know about lists into a short program.
''',
            'exercises': [
                {
                    'slug': 'debug-list',
                    'title': 'Debug the index',
                    'exercise_type': 'debugging',
                    'instructions': 'The code below crashes instead of printing the last number. Fix it.\n\nnumbers = [10, 20, 30, 40, 50]\nprint(numbers[5])',
                    'context': 'IndexError is the most common crash for beginners. Reading the error message carefully IS the fix.',
                    'expected_behavior': 'The fixed program prints: 50',
                    'explain': 'A 5-item list has positions 0 through 4 — numbers[5] is one past the end. Either numbers[4] or numbers[-1] prints the last item.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': 'numbers = [10, 20, 30, 40, 50]\nprint(numbers[5])  # Fix this line\n',
                    'solution_code': 'numbers = [10, 20, 30, 40, 50]\nprint(numbers[-1])',
                    'test_cases': [{'input': '', 'expected_output': '50'}],
                    'xp_reward': 100, 'order': 1,
                    'hints': [
                        'Where does indexing start, and what is the last valid position of a 5-item list?',
                        'Valid positions are 0 to 4 — or count backwards from -1.',
                    ],
                },
                {
                    'slug': 'list-sum-max',
                    'title': 'Sum and maximum',
                    'exercise_type': 'code',
                    'instructions': 'Given the list nums, print its sum on the first line and its largest value on the second line.',
                    'context': 'sum/max/min are how dashboards and reports are built.',
                    'expected_behavior': 'Prints 108 then 42.',
                    'explain': 'sum(nums) adds every element; max(nums) returns the largest. Two print calls produce two lines in order.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': 'nums = [4, 8, 15, 16, 23, 42]\n\n# Print the sum, then the maximum\n',
                    'solution_code': 'nums = [4, 8, 15, 16, 23, 42]\nprint(sum(nums))\nprint(max(nums))',
                    'expected_output': '108\n42',
                    'test_cases': [{'input': '', 'expected_output': '108\n42'}],
                    'xp_reward': 100, 'order': 2,
                    'hints': [
                        'There are built-in functions: sum(...) and max(...)',
                        'Order matters: sum first, then max.',
                    ],
                },
                {
                    'slug': 'append-predict',
                    'title': 'Predict the list',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\nfruits = ["apple", "banana"]\nfruits.append("cherry")\nprint(fruits)',
                    'expected_behavior': 'One line in Python list notation.',
                    'explain': 'append adds to the end in place, so the list holds three strings. print(list) shows Python list notation with single quotes.',
                    'difficulty': 'easy', 'language': 'python',
                    'expected_output': "['apple', 'banana', 'cherry']",
                    'xp_reward': 75, 'order': 3,
                    'hints': [
                        'append places the new item at the END.',
                        'Watch the exact list brackets and quote style.',
                    ],
                },
            ],
        },
        {
            'slug': 'dictionaries',
            'title': 'Dictionaries',
            'learning_objective': 'Store and look up key-value pairs safely.',
            'order': 3, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# Dictionaries

A list answers "what is at position 3?". A **dictionary** answers "what is the value for key name?". It stores key-value pairs in curly braces:

```python
student = {
    "name": "Ali",
    "age": 20,
    "city": "Karachi",
}
```

## Looking values up

```python
print(student["name"])
```

**Expected output:** `Ali`

Square brackets with a **key** — not a position. Keys are strings (or other simple values), and order of storage is not what you look up by.

## The safe lookup: .get()

```python
print(student["phone"])
```

**Expected result:** a **KeyError** — the key does not exist.

```python
print(student.get("phone"))
print(student.get("phone", "not given"))
```

**Expected output:** `None`, then `not given`. `.get()` returns None (or your fallback) instead of crashing. Use it whenever a key might be missing.

## Adding and updating

```python
student["age"] = 21
student["course"] = "Python"
print(student["age"], student["course"])
```

**Expected output:** `21 Python` — assigning to an existing key updates it; assigning to a new key adds it.

## Loops over dictionaries

```python
marks = {"math": 85, "urdu": 90}
for subject in marks:
    print(subject, marks[subject])
```

**Expected output:** `math 85` then `urdu 90`. Looping a dict gives its keys; index the dict to get each value.

## When to use which

- List `[...]` — an ordered collection of similar things, accessed by position.
- Dictionary `{k: v}` — labelled facts about one thing, accessed by name.

## Common mistakes

- `student[name]` without quotes → NameError (Python looks for a variable named name). Keys are strings: `student["name"]`.
- Expecting a missing key to return None from `student[...]` — only `.get()` does that.

## Practice

The three exercises below cover a lookup, a safe .get, and building your first dict.
''',
            'exercises': [
                {
                    'slug': 'dict-output',
                    'title': 'Predict the lookup',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\nmarks = {"math": 85, "urdu": 90}\nprint(marks["urdu"])',
                    'expected_behavior': 'One line.',
                    'explain': 'marks["urdu"] fetches the value stored under the "urdu" key, which is 90.',
                    'difficulty': 'easy', 'language': 'python',
                    'expected_output': '90',
                    'xp_reward': 50, 'order': 1,
                },
                {
                    'slug': 'get-vs-crash',
                    'title': 'Missing key',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'student has no "phone" key. What does student.get("phone", "N/A") return?',
                    'explain': '.get(key, fallback) returns the fallback when the key is missing — no crash. Only the bracket form student["phone"] raises KeyError.',
                    'difficulty': 'medium', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'The fallback string "N/A"', 'is_correct': True},
                        {'id': 'b', 'text': 'KeyError — it crashes', 'is_correct': False},
                        {'id': 'c', 'text': 'The whole dictionary', 'is_correct': False},
                        {'id': 'd', 'text': 'The number 0', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
                {
                    'slug': 'fill-dict',
                    'title': 'Build a dictionary',
                    'exercise_type': 'fill_blank',
                    'instructions': 'Type the complete statement that creates a dictionary called student holding name -> "Ali" and age -> 20. One line of Python.',
                    'context': 'Creating dictionaries with clear labels is step one of every data program.',
                    'expected_behavior': 'A dict literal with two key-value pairs assigned to student.',
                    'explain': 'Curly braces hold key: value pairs separated by commas. Keys are quoted strings; 20 stays an integer.',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': 'student = ???\n',
                    'solution_code': 'student = {"name": "Ali", "age": 20}',
                    'xp_reward': 100, 'order': 3,
                    'hints': [
                        'A dictionary uses curly braces { }.',
                        'Each fact is written "key": value, separated by commas.',
                        'Solution: student = {"name": "Ali", "age": 20}',
                    ],
                },
            ],
        },
    ],
}

PY_CH4 = {
    'slug': 'functions',
    'title': 'Functions',
    'description': 'Write reusable blocks of code with def and return.',
    'order': 4,
    'lessons': [
        {
            'slug': 'defining-functions',
            'title': 'Defining Functions',
            'learning_objective': 'Define functions with parameters and return values, and call them.',
            'order': 1, 'duration_minutes': 20, 'xp_reward': 50,
            'content_body': '''# Functions

A function is a **named block of code** you can reuse. Instead of pasting the same calculation five times, write it once and call it by name.

## def and call

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Ayesha")
print(message)
```

**Expected output:** `Hello, Ayesha!`

Reading it piece by piece:

- `def greet(name):` — defines a function named greet that expects one input. The colon and the indented body are required.
- `name` is a **parameter** — a placeholder for whatever gets passed in.
- `return` hands a value back to the caller.
- `greet("Ayesha")` **calls** the function; `"Ayesha"` is the **argument**.

## return vs print — know the difference

```python
def shout(text):
    return text.upper()

result = shout("hi")
print(result)
```

**Expected output:** `HI`

`return` gives the value back so your program can keep using it. `print` only shows it on screen. A function with NO return statement gives back `None`:

```python
def hi():
    print("Hi")

result = hi()
print(result)
```

**Expected output:** `Hi` then `None`.

## Default parameters

```python
def greet(name, greeting="Salam"):
    return f"{greeting}, {name}!"

print(greet("Bilal"))
print(greet("Bilal", "Hello"))
```

**Expected output:** `Salam, Bilal!` then `Hello, Bilal!` — the second call overrides the default.

## Why functions matter

- **Don't repeat yourself**: write logic once, use it everywhere.
- **Names explain intent**: `calculate_tax(income)` reads better than a wall of arithmetic.
- **Testable in isolation**: small functions are easy to check and fix.

## Common mistakes

- Calling a function before defining it -> NameError. Define first, call after.
- Forgetting `return` and getting None where you expected a value.
- Passing the wrong number of arguments: `greet()` when it needs a name -> TypeError.

## Practice

Define your first real function — the runner will call it with three different inputs.
''',
            'exercises': [
                {
                    'slug': 'write-function',
                    'title': 'Write double()',
                    'exercise_type': 'code',
                    'instructions': 'Write a function named `double` that takes one number and RETURNS it multiplied by 2. The test calls at the bottom are already written for you.',
                    'context': 'Functions are the building blocks of organized code.',
                    'constraints': 'Use return, not print, inside the function.',
                    'expected_behavior': 'The three provided calls print 10, 0, -6.',
                    'explain': 'def double(n): creates the function; return n * 2 hands the product back to the caller so print can display it.',
                    'difficulty': 'medium', 'language': 'python',
                    'starter_code': '# Write your double(n) function here\n\n\nprint(double(5))\nprint(double(0))\nprint(double(-3))\n',
                    'solution_code': 'def double(n):\n    return n * 2\n\n\nprint(double(5))\nprint(double(0))\nprint(double(-3))',
                    'expected_output': '10\n0\n-6',
                    'test_cases': [{'input': '', 'expected_output': '10\n0\n-6'}],
                    'xp_reward': 150, 'order': 1,
                    'hints': [
                        'A function definition starts: def double(n):',
                        'The body can be one line: return n * 2',
                        'Do not print inside the function — the calls below already print.',
                    ],
                },
                {
                    'slug': 'no-return-none',
                    'title': 'What does a bare function return?',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\ndef greet():\n    print("Hi")\n\nresult = greet()\nprint(result)',
                    'expected_behavior': 'Two lines.',
                    'explain': 'greet prints Hi, but has no return statement, so the call evaluates to None — which the second print displays.',
                    'difficulty': 'medium', 'language': 'python',
                    'expected_output': 'Hi\nNone',
                    'xp_reward': 75, 'order': 2,
                    'hints': [
                        'The function prints something itself first.',
                        'What does a function without return give back?',
                    ],
                },
                {
                    'slug': 'default-arg-quiz',
                    'title': 'Default parameters',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Given def order(item, qty=1), what happens when you call order("chai")?',
                    'explain': 'qty=1 is a default: it is used automatically when the caller leaves that argument out.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'qty becomes 1', 'is_correct': True},
                        {'id': 'b', 'text': 'TypeError — qty is missing', 'is_correct': False},
                        {'id': 'c', 'text': 'qty becomes 0', 'is_correct': False},
                        {'id': 'd', 'text': 'qty becomes None', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 3,
                },
            ],
        },
    ],
}

PY_CH5 = {
    'slug': 'errors-and-debugging',
    'title': 'Errors and Debugging',
    'description': 'Read error messages like a professional and guard risky code with try/except.',
    'order': 5,
    'lessons': [
        {
            'slug': 'error-handling',
            'title': 'Error Handling and Debugging',
            'learning_objective': 'Identify the most common Python errors and handle them with try/except.',
            'order': 1, 'duration_minutes': 20, 'xp_reward': 50,
            'content_body': '''# Error Handling and Debugging

Errors are not failures — they are **information**. Every professional programmer spends more time reading errors than writing code.

## Reading a traceback

When a program crashes, Python prints a traceback. Read the **last line** first — it names the error type and a plain-English message. Above it, Python shows which line the problem is on.

## The errors you will actually meet

- **SyntaxError** — the code itself is not valid Python: `print("hi` (missing quote). Caught before the program even starts.
- **NameError** — using a name that was never defined: `Print("hi")` (capital P).
- **TypeError** — wrong kind of value for the operation: `"5" + 5` (text plus number).
- **ValueError** — right type, impossible value: `int("abc")`.
- **IndexError** — position does not exist: `[1, 2][5]`.
- **ZeroDivisionError** — dividing by zero: `10 / 0`.

## try / except: plan for the crash

Wrap risky code in `try`. If it raises the named error, Python runs `except` INSTEAD of crashing:

```python
text = "abc"

try:
    number = int(text)
    print(number)
except ValueError:
    print("Not a number")
```

**Expected output:** `Not a number` — the program survived and said something useful.

Without try/except the program would have died on the conversion line. With it, the ValueError was caught and handled.

## Debugging habits that work

1. Read the last line of the error — it names the problem.
2. Find the line NUMBER it mentions in your code.
3. Change ONE thing at a time, then run again.
4. Add a well-placed `print(...)` to see what a variable actually holds at that moment.

## Common mistakes

- Wrapping everything in a bare `except:` — you also swallow real bugs. Name the error you expect.
- Ignoring the line number in the traceback and guessing.
- Panicking at errors instead of reading them. Errors are pointers.

## Practice

Match errors to causes, then write your own try/except. Both exercises are graded with the real runner.
''',
            'exercises': [
                {
                    'slug': 'match-error',
                    'title': 'Which error?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What error does int("abc") raise?',
                    'explain': 'The argument has the right TYPE (a string) but an impossible VALUE — text that is not a number. That combination is a ValueError.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'ValueError', 'is_correct': True},
                        {'id': 'b', 'text': 'TypeError', 'is_correct': False},
                        {'id': 'c', 'text': 'SyntaxError', 'is_correct': False},
                        {'id': 'd', 'text': 'NameError', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 1,
                },
                {
                    'slug': 'try-divide',
                    'title': 'Guard the division',
                    'exercise_type': 'code',
                    'instructions': 'a is 10 and b is 0. Wrap the division in try/except so the program prints "Cannot divide by zero" instead of crashing.',
                    'context': 'Division by zero is the classic crash — and the classic try/except example.',
                    'constraints': 'Catch ZeroDivisionError specifically. Print exactly: Cannot divide by zero',
                    'expected_behavior': 'The program prints: Cannot divide by zero',
                    'explain': 'try runs the risky division; it raises ZeroDivisionError, so control jumps to the except block, which prints the friendly message and the program ends cleanly.',
                    'difficulty': 'medium', 'language': 'python',
                    'starter_code': 'a = 10\nb = 0\n\n# Replace the direct division below with try/except\nprint(a / b)\n',
                    'solution_code': 'a = 10\nb = 0\n\ntry:\n    print(a / b)\nexcept ZeroDivisionError:\n    print("Cannot divide by zero")',
                    'expected_output': 'Cannot divide by zero',
                    'test_cases': [{'input': '', 'expected_output': 'Cannot divide by zero'}],
                    'xp_reward': 125, 'order': 2,
                    'hints': [
                        'Structure: try: <risky code> / except ZeroDivisionError: <fallback>',
                        'Move print(a / b) inside the try block.',
                        'The except block should print("Cannot divide by zero").',
                    ],
                },
            ],
        },
    ],
}

PY_CH6 = {
    'slug': 'building-a-project',
    'title': 'Build a Project',
    'description': 'Put everything together in a real mini-project, then prove it with the final assessment.',
    'order': 6,
    'lessons': [
        {
            'slug': 'mini-project',
            'title': 'Mini-Project: Student Report Card',
            'learning_objective': 'Combine lists, loops, conditionals, and f-strings in one small program.',
            'order': 1, 'duration_minutes': 30, 'xp_reward': 100,
            'content_body': '''# Mini-Project: Student Report Card

Time to combine everything: variables, lists, loops, conditionals, and formatted output in one working program.

## The brief

You are given a list of students and their marks:

```python
students = [("Ayesha", 88), ("Bilal", 45), ("Sana", 72)]
```

Each item is a **tuple**: (name, marks). The passing mark is **50**.

For every student print `Name: PASS` or `Name: FAIL`, then print one summary line: `Passing: <count>`.

## Expected output — exactly this

For the sample data above the program must print four lines:

`Ayesha: PASS` — then `Bilal: FAIL` — then `Sana: PASS` — then `Passing: 2`

## The pieces you need

Tuple unpacking inside a for loop pulls both values out at once:

```python
for name, marks in [("Ayesha", 88), ("Bilal", 45)]:
    print(name, marks)
```

**Expected output:** `Ayesha 88` then `Bilal 45`.

A counter you update as you go (you saw this in the loops lesson):

```python
passing = 0
```

And an if/else choosing PASS or FAIL per student. f-strings make the output readable: `f"{name}: PASS"`.

## Approach

1. Set up the counter before the loop.
2. Loop over the list, unpacking each row.
3. Decide PASS/FAIL with a conditional; update the counter when a student passes.
4. After the loop, print the summary.

Do it in the editor. The runner grades your program against the real data — no guessing, honest feedback.
''',
            'exercises': [
                {
                    'slug': 'report-card',
                    'title': 'Report card program',
                    'exercise_type': 'code',
                    'instructions': 'Complete the report card: for each (name, marks) print "Name: PASS" (marks >= 50) or "Name: FAIL", then print "Passing: <count>" for the number who passed.',
                    'context': 'One exercise, eight course concepts. This is your graduation test before the final assessment.',
                    'constraints': 'Output must match exactly, in the order given. Passing mark is 50.',
                    'expected_behavior': 'Ayesha: PASS, Bilal: FAIL, Sana: PASS, Passing: 2 — one per line.',
                    'explain': 'The loop unpacks each tuple; the conditional both prints the verdict and increments the counter only on a pass; the summary prints after the loop so it counts every student.',
                    'difficulty': 'medium', 'language': 'python',
                    'starter_code': 'students = [("Ayesha", 88), ("Bilal", 45), ("Sana", 72)]\n\npassing = 0\n\n# Loop, print PASS/FAIL per student, count passes,\n# then print the summary line "Passing: <count>"\n',
                    'solution_code': 'students = [("Ayesha", 88), ("Bilal", 45), ("Sana", 72)]\n\npassing = 0\n\nfor name, marks in students:\n    if marks >= 50:\n        print(f"{name}: PASS")\n        passing += 1\n    else:\n        print(f"{name}: FAIL")\n\nprint(f"Passing: {passing}")',
                    'expected_output': 'Ayesha: PASS\nBilal: FAIL\nSana: PASS\nPassing: 2',
                    'test_cases': [
                        {'input': '', 'expected_output': 'Ayesha: PASS\nBilal: FAIL\nSana: PASS\nPassing: 2'},
                    ],
                    'xp_reward': 200, 'order': 1,
                    'hints': [
                        'for name, marks in students: unpacks both values at once.',
                        'Use if marks >= 50 to choose PASS vs FAIL, and passing += 1 only in the pass branch.',
                        'Summary line after the loop: print(f"Passing: {passing}")',
                    ],
                },
            ],
        },
        {
            'slug': 'final-assessment',
            'title': 'Final Assessment',
            'learning_objective': 'Answer questions covering every topic actually taught in this course.',
            'order': 2, 'duration_minutes': 30, 'xp_reward': 100,
            'content_body': '''# Final Assessment

This is the last lesson. Complete every question below to finish the course.

## What to expect

Eight questions covering ONLY what this course taught: printing, variables and types, input and conversion, operators (including `//` and `%`), conditionals, loops, strings, lists, dictionaries, functions, and errors.

Every question is graded when you submit it, and the explanation appears AFTER your attempt — so mistakes teach you instead of spoiling the answer.

## Honest rules

- Your score is computed from your real submissions. Nothing here is automatic.
- You may retry questions; take what a wrong answer taught you and go again.
- When every question is correct, this lesson marks itself complete and your progress is saved to your account.

Good luck — and remember the motto: **Think. Build. Evolve.**
''',
            'exercises': [
                {
                    'slug': 'fa-types',
                    'title': 'Types: what is "42"?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What is the type of the value "42" (with quotes)?',
                    'explain': 'Quotes make it text, no matter what the characters look like. The number forty-two without quotes is an int.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'str', 'is_correct': True},
                        {'id': 'b', 'text': 'int', 'is_correct': False},
                        {'id': 'c', 'text': 'float', 'is_correct': False},
                        {'id': 'd', 'text': 'bool', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 1, 'is_final_assessment': True,
                },
                {
                    'slug': 'fa-operators',
                    'title': 'Operators: floor and remainder',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\nprint(10 // 3 * 3 + 10 % 3)',
                    'explain': '10 // 3 = 3, times 3 = 9. 10 % 3 = 1 (the leftover). 9 + 1 = 10.',
                    'difficulty': 'medium', 'language': 'python',
                    'expected_output': '10',
                    'xp_reward': 50, 'order': 2, 'is_final_assessment': True,
                },
                {
                    'slug': 'fa-conditions',
                    'title': 'Find the syntax error',
                    'exercise_type': 'debugging',
                    'instructions': 'This program has exactly one bug. Fix it so it prints Adult:\n\nage = 20\nif age >= 18\n    print("Adult")',
                    'context': 'Missing colons are the most common SyntaxError in conditional code.',
                    'expected_behavior': 'The fixed program prints: Adult',
                    'explain': 'An if statement must end with a colon before the indented block: if age >= 18:',
                    'difficulty': 'easy', 'language': 'python',
                    'starter_code': 'age = 20\nif age >= 18\n    print("Adult")\n',
                    'solution_code': 'age = 20\nif age >= 18:\n    print("Adult")',
                    'test_cases': [{'input': '', 'expected_output': 'Adult'}],
                    'xp_reward': 50, 'order': 3, 'is_final_assessment': True,
                    'hints': [
                        'Read the SyntaxError message: which character is missing?',
                        'Every if line ends with : before the indented body.',
                    ],
                },
                {
                    'slug': 'fa-loops',
                    'title': 'Loops: accumulate',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\ntotal = 0\nfor i in range(1, 4):\n    total += i\nprint(total)',
                    'explain': 'range(1, 4) gives 1, 2, 3 (4 excluded). Adding them: 0+1+2+3 = 6.',
                    'difficulty': 'medium', 'language': 'python',
                    'expected_output': '6',
                    'xp_reward': 50, 'order': 4, 'is_final_assessment': True,
                },
                {
                    'slug': 'fa-strings',
                    'title': 'Strings: index',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What does "abc"[1] return?',
                    'explain': 'Indexing starts at 0, so position 1 is the SECOND character: b.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'b', 'is_correct': True},
                        {'id': 'b', 'text': 'a', 'is_correct': False},
                        {'id': 'c', 'text': 'c', 'is_correct': False},
                        {'id': 'd', 'text': 'ab', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 5, 'is_final_assessment': True,
                },
                {
                    'slug': 'fa-lists',
                    'title': 'Lists: sorting',
                    'exercise_type': 'output_prediction',
                    'instructions': 'What does this print?\n\nnums = [3, 1, 2]\nprint(sorted(nums))',
                    'explain': 'sorted() returns a NEW list in ascending order: [1, 2, 3]. The original list is unchanged.',
                    'difficulty': 'easy', 'language': 'python',
                    'expected_output': '[1, 2, 3]',
                    'xp_reward': 50, 'order': 6, 'is_final_assessment': True,
                },
                {
                    'slug': 'fa-functions',
                    'title': 'Functions: return value',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Given def add(a, b): return a + b — what does result = add(2, 3) store in result?',
                    'explain': 'return hands the computed value 5 back to the caller, and = stores it in result. Nothing has been printed.',
                    'difficulty': 'easy', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'The number 5', 'is_correct': True},
                        {'id': 'b', 'text': 'The text "23"', 'is_correct': False},
                        {'id': 'c', 'text': 'None', 'is_correct': False},
                        {'id': 'd', 'text': 'It prints 5 and stores nothing', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 7, 'is_final_assessment': True,
                },
                {
                    'slug': 'fa-input',
                    'title': 'Input: converting',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'You need to add 1 to a number the user types. Which line reads and prepares it correctly?',
                    'explain': 'input() returns a string; wrapping it in int() converts the text to a whole number so arithmetic works.',
                    'difficulty': 'medium', 'language': 'python',
                    'choices': [
                        {'id': 'a', 'text': 'n = int(input())', 'is_correct': True},
                        {'id': 'b', 'text': 'n = input()', 'is_correct': False},
                        {'id': 'c', 'text': 'n = str(input())', 'is_correct': False},
                        {'id': 'd', 'text': 'n = input() + 1', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 8, 'is_final_assessment': True,
                },
            ],
        },
    ],
}

PYTHON_COURSE = {
    'slug': 'python-foundations',
    'title': 'Python Foundations',
    'subtitle': 'Learn Python from zero — one honest, hands-on step at a time.',
    'description': (
        'A beginner-friendly introduction to Python: printing, comments, variables, '
        'data types, user input, operators, conditionals, loops, strings, lists, '
        'dictionaries, functions, and error handling — ending with a small project '
        'and a final assessment. Coding exercises are executed and graded by a real '
        'sandbox, so your progress reflects what you actually solved.'
    ),
    'track_slug': 'python',
    'difficulty': 'beginner',
    'language': 'python',
    'instructor': 'Code Yaar',
    'prerequisites': 'None — this course starts from zero.',
    'learning_objectives': [
        'Write and run Python programs using print()',
        'Store and transform data with variables and the core types',
        'Read user input and convert it with int() and float()',
        'Make decisions with if/elif/else and repeat with loops',
        'Work with strings, lists, and dictionaries',
        'Define reusable functions with parameters and return values',
        'Read common errors and handle them with try/except',
        'Build a small end-to-end program (student report card)',
    ],
    'is_free': True,
    'is_published': True,
    'order': 1,
    'chapters': [PY_CH1, PY_CH2, PY_CH3, PY_CH4, PY_CH5, PY_CH6],
}

# ══════════════════════════════════════════════════════════════════════════
#  GIT & GITHUB FOUNDATIONS (short course)
# ══════════════════════════════════════════════════════════════════════════

GIT_CH1 = {
    'slug': 'git-basics',
    'title': 'Git Basics',
    'description': 'Understand what version control is and how Git records your work.',
    'order': 1,
    'lessons': [
        {
            'slug': 'what-is-git-github',
            'title': 'What Git and GitHub Are (and Why Developers Use Them)',
            'learning_objective': 'Explain what Git and GitHub each are, and the problem version control solves.',
            'order': 1, 'duration_minutes': 12, 'xp_reward': 50,
            'content_body': '''# What Git and GitHub Are

## The problem Git solves

Everyone who has worked on code long enough has lived this: `project_final.zip`, `project_final_REAL.zip`, `project_final_v2_final.zip` — and nobody knows which one works, or what changed since Tuesday.

A **version control system** keeps a complete history of your files: every change, who made it, when, and why. You can open any earlier moment like a time machine, compare versions, and undo mistakes without fear.

## Git

**Git** is the version control program that runs on YOUR computer. It takes snapshots of your project folder and stores them in a hidden history database. It works with no internet at all — the history lives on your machine.

## GitHub

**GitHub** is a website that hosts Git repositories: a place to push your history so it is backed up, shareable, and collaboratable. Other services do the same job (GitLab, Bitbucket), but GitHub is the most common.

The distinction matters and interviews ask it: **Git is the tool, GitHub is the hosting service.** You can use Git without GitHub; GitHub without Git does not exist.

## Why teams care

- Multiple people edit the same project without overwriting each other.
- Every change has an author, a date, and a message — accountability and a paper trail.
- Experiment safely: try something risky, go back if it fails.
- Open-source contribution: download any project's whole history with one command.

## Common confusions

- Thinking GitHub IS Git — it is a service built around it.
- Thinking Git needs the internet — it does not; only sharing needs a connection.
- Thinking version control is only for code — text files of any kind work.

## Practice

Two quick checks below. Answer them, and the explanations will show you why each answer is right. The hands-on commands come in the next lessons.
''',
            'exercises': [
                {
                    'slug': 'git-vs-github',
                    'title': 'Git vs GitHub',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Which statement is correct?',
                    'explain': 'Git is the local version control program; GitHub is a hosting service for Git repositories. Git works offline; GitHub does not run inside your code editor by itself.',
                    'difficulty': 'easy', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'Git is a program that tracks versions; GitHub hosts Git repositories', 'is_correct': True},
                        {'id': 'b', 'text': 'GitHub is the program and Git is the website', 'is_correct': False},
                        {'id': 'c', 'text': 'They are two names for the same product', 'is_correct': False},
                        {'id': 'd', 'text': 'Git only works with an internet connection', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 1,
                },
                {
                    'slug': 'why-version-control',
                    'title': 'The core benefit',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What is the MAIN problem version control solves?',
                    'explain': 'Version control records a full history of changes with authors and messages, so nothing is lost and collaborators do not overwrite each other. It is not primarily a formatting or backup-by-zipping tool.',
                    'difficulty': 'easy', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'A reliable history of every change, shareable safely between people', 'is_correct': True},
                        {'id': 'b', 'text': 'Automatic code formatting', 'is_correct': False},
                        {'id': 'c', 'text': 'Making programs run faster', 'is_correct': False},
                        {'id': 'd', 'text': 'Replacing the need to test code', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
            ],
        },
        {
            'slug': 'repos-commits-history',
            'title': 'Repositories, Commits, and History',
            'learning_objective': 'Describe the repository, what a commit contains, and how commits form history.',
            'order': 2, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# Repositories, Commits, and History

## The repository

A **repository** ("repo") is a project folder plus Git's hidden history database (a `.git` folder inside it). You turn a normal folder into a repo with `git init`, or download one with `git clone`. From then on Git tracks what happens to the files inside.

## The commit — a snapshot with a story

A **commit** is a saved snapshot of your whole project at one moment. Each commit also stores:

- a **message** describing why the change was made
- the **author** and **timestamp**
- a unique fingerprint called a **hash** (like `a3f9c21`) that identifies it forever

Commits link together into a timeline — that timeline IS your project's history. `git log` shows it:

```text
commit a3f9c21  Add login form
commit 7be14d0  Set up project structure
```

## The three areas

Git moves your work through three zones:

1. **Working directory** — the files you are actually editing.
2. **Staging area** — what you have marked for the next snapshot (`git add`).
3. **Repository** — the permanent history of commits (`git commit`).

You choose what goes into a snapshot: edit freely, stage the parts that belong together, then commit. That choice is why the staging area exists.

## Good commit messages

Compare:

- Bad: `fix`, `stuff`, `update2`
- Good: `Fix crash when username is empty`

A good message completes the sentence "If applied, this commit will..." and saves future-you an archaeology project.

## Common confusions

- Thinking a commit stores only the changed FILES — it snapshots the whole project state.
- Forgetting to stage (`git add`) then wondering why `git commit` says nothing to commit.
- Writing one giant commit at the end of the week — small, frequent commits are the point.

## Practice

The two questions below check the staging-area idea and what a commit actually is — the two things every interview and every teammate will assume you know.
''',
            'exercises': [
                {
                    'slug': 'commit-parts',
                    'title': 'What is inside a commit?',
                    'exercise_type': 'multiple_select',
                    'instructions': 'Select everything a Git commit stores.',
                    'explain': 'A commit holds a project snapshot plus its message, author, timestamp, and unique hash. The original filenames and folder are part of the snapshot — but the developer\'s editor settings are not.',
                    'difficulty': 'medium', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'A snapshot of the project files', 'is_correct': True},
                        {'id': 'b', 'text': 'A message describing the change', 'is_correct': True},
                        {'id': 'c', 'text': 'The author and timestamp', 'is_correct': True},
                        {'id': 'd', 'text': 'Your editor\'s colour theme', 'is_correct': False},
                    ],
                    'xp_reward': 60, 'order': 1,
                },
                {
                    'slug': 'staging-area',
                    'title': 'Where does git add put things?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'In the three-area model, what does git add do?',
                    'explain': 'git add moves your current edits into the STAGING area — the shortlist of changes to include in the next commit. The snapshot is only taken when you run git commit.',
                    'difficulty': 'medium', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'Marks changes to be included in the next commit (staging)', 'is_correct': True},
                        {'id': 'b', 'text': 'Saves a permanent snapshot immediately', 'is_correct': False},
                        {'id': 'c', 'text': 'Uploads files to GitHub', 'is_correct': False},
                        {'id': 'd', 'text': 'Deletes the working directory', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
            ],
        },
    ],
}

GIT_CH2 = {
    'slug': 'git-workflow',
    'title': 'Your Git Workflow',
    'description': 'The daily commands, publishing to GitHub, and a README mini-project.',
    'order': 2,
    'lessons': [
        {
            'slug': 'essential-commands',
            'title': 'Essential Git Commands',
            'learning_objective': 'Run the core daily cycle: status, add, commit — and inspect with log and diff.',
            'order': 1, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# Essential Git Commands

You will use these five commands every single day. Practice them on any folder on your own computer — they are safe to try.

## Starting out

```text
git init
```

Turns the current folder into a repository (adds the hidden `.git` history folder).

## The daily cycle

```text
git status
git add index.html
git commit -m "Add home page layout"
```

- `git status` — the flashlight. Shows changed files and what is staged. When lost, run status.
- `git add <file>` — stage a file. `git add .` stages everything changed in the current folder.
- `git commit -m "message"` — take the snapshot, with your message attached.

## Inspecting history

```text
git log --oneline
git diff
```

- `git log` — the timeline of commits (`--oneline` packs each commit to one line).
- `git diff` — shows exactly which LINES changed in your working files, before you stage.

## Undoing (the gentle ones)

- `git restore <file>` — throw away uncommitted changes to one file (checkout of the saved version).
- Staged by mistake? `git restore --staged <file>` unstages it. History is never touched by either.

## A first real transcript

```text
$ git status
        modified:   hello.py
$ git add hello.py
$ git commit -m "Print greeting in Urdu"
[master 9c1e4f2] Print greeting in Urdu
```

## Common confusions

- Running `git commit` right after editing — with nothing staged Git refuses; that is the add step missing.
- `git add .` when you only wanted one file — check `git status` first, make it a habit.
- Forgetting `-m` and landing in a strange editor screen — Ctrl+C (or `:q`) gets you out.

## Practice

Two checks below: which command to reach for, and typing the commit command exactly right.
''',
            'exercises': [
                {
                    'slug': 'status-command',
                    'title': 'Which command tells you the state?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'You just opened an unfamiliar Git project. Which command shows which files changed and what is staged?',
                    'explain': 'git status reports the working state: modified files, staged files, untracked files. log shows history, diff shows line changes, add stages.',
                    'difficulty': 'easy', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'git status', 'is_correct': True},
                        {'id': 'b', 'text': 'git log', 'is_correct': False},
                        {'id': 'c', 'text': 'git add .', 'is_correct': False},
                        {'id': 'd', 'text': 'git init', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 1,
                },
                {
                    'slug': 'commit-command',
                    'title': 'Type the commit command',
                    'exercise_type': 'fill_blank',
                    'instructions': 'Type the exact command that saves all staged changes as a commit with the message Add readme. One line.',
                    'context': 'This is the command you will type thousands of times.',
                    'expected_behavior': 'git commit with -m and the quoted message.',
                    'explain': 'git commit takes the snapshot; -m attaches the message, which must be in quotes so spaces do not break it into separate arguments.',
                    'difficulty': 'medium', 'language': 'none',
                    'solution_code': 'git commit -m "Add readme"',
                    'xp_reward': 60, 'order': 2,
                    'hints': [
                        'The base command is: git commit',
                        'The message flag is -m followed by the text in double quotes.',
                        'Solution: git commit -m "Add readme"',
                    ],
                },
            ],
        },
        {
            'slug': 'github-first-push',
            'title': 'Creating a GitHub Repository and Pushing',
            'learning_objective': 'Connect a local repo to GitHub and describe the push/clone workflow.',
            'order': 2, 'duration_minutes': 15, 'xp_reward': 50,
            'content_body': '''# Creating a GitHub Repository and Pushing

## Honest note first

Your Code Yaar progress comes from the quizzes on this page. **The platform cannot see the repository on your machine, so nothing here is verified as "pushed".** Follow the steps yourself in a real terminal — it takes ten minutes and it is the skill that matters.

## Create the online home

1. On github.com, press **New repository**.
2. Give it a name, leave "Add a README" unchecked for now, press **Create repository**.

GitHub now shows you the exact commands for your empty repo. The one-time setup:

```text
git remote add origin https://github.com/your-name/your-repo.git
```

`origin` is just the conventional nickname for "the main remote URL". `git remote add` links your local history to the online repo.

## Pushing

```text
git push -u origin main
```

**Push** uploads your commits to GitHub. `-u origin main` records that your local branch should track `main` on `origin`, so from now on a plain `git push` is enough.

After that, the daily rhythm is: edit, `git add`, `git commit`, `git push`.

## Cloning

From someone else's repo page, copy its URL and:

```text
git clone https://github.com/openai/openai-python.git
```

Clone downloads the ENTIRE history — every commit — not just the latest files. That is what makes Git great for studying real projects: you can travel through a codebase's past.

## Pulling

```text
git pull
```

Bring other people's committed work into your local copy. Push = upload, pull = download. If both you and a teammate changed the same line, Git asks you to resolve the conflict — you will meet that later, in team projects.

## Common confusions

- Pushing without committing — push uploads COMMITTED history; uncommitted work stays local.
- Wrong URL: `git remote -v` shows what `origin` currently points at.
- "main" vs "master" — the default branch name; GitHub now uses `main`.

## Practice

Two understanding checks. Your real push happens on your own machine — this lesson\'s mini-project in the next lesson brings it together.
''',
            'exercises': [
                {
                    'slug': 'push-what',
                    'title': 'What does push do?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What does git push upload to GitHub?',
                    'explain': 'push sends your local COMMITS (the history with all its snapshots) to the remote repository. Files you have not committed are left behind.',
                    'difficulty': 'medium', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'Your local commits', 'is_correct': True},
                        {'id': 'b', 'text': 'Every file in the folder, staged or not', 'is_correct': False},
                        {'id': 'c', 'text': 'Only the most recent file you edited', 'is_correct': False},
                        {'id': 'd', 'text': 'Your GitHub issues', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 1,
                },
                {
                    'slug': 'clone-what',
                    'title': 'What does clone download?',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Running git clone on a repository URL gives you:',
                    'explain': 'clone downloads the repository including its full commit history and sets it up as a local Git repo with origin configured.',
                    'difficulty': 'easy', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'The files plus the entire commit history, as a ready Git repo', 'is_correct': True},
                        {'id': 'b', 'text': 'Just a zip of the latest files', 'is_correct': False},
                        {'id': 'c', 'text': 'Only the README', 'is_correct': False},
                        {'id': 'd', 'text': 'A copy of your GitHub profile', 'is_correct': False},
                    ],
                    'xp_reward': 50, 'order': 2,
                },
            ],
        },
        {
            'slug': 'readme-mini-project',
            'title': 'The README and Your Mini-Project',
            'learning_objective': 'Write a useful README and complete a self-reported first publish workflow.',
            'order': 3, 'duration_minutes': 20, 'xp_reward': 100,
            'content_body': '''# The README and Your Mini-Project

## What a README is for

The `README.md` file is the front door of your project. A stranger lands on your repo and the README answers, in thirty seconds: **what is this, why does it exist, and how do I run it?**

A beginner-strong structure:

1. **Title** — one line, what it is.
2. **Description** — 2-3 sentences: the problem it solves.
3. **Setup** — what to install, what command starts it.
4. **Usage** — a concrete example of running it.
5. **Contact** — who made it.

## Markdown — the README's language

`.md` files use Markdown, which is plain text with light marks:

- `# Heading` — a big title (`##` smaller)
- `**bold**` and `*italic*`
- `- item` — bullet list
- backticks around `code` and fenced blocks for longer snippets

That is genuinely all you need for a great first README.

## Example — a real first README

```text
# My Python Practice

Solved exercises from the Code Yaar Python Foundations course.

## Running a program

python report_card.py

## Contact

ali@example.com
```

## Mini-project (self-reported)

On your OWN computer — the platform cannot and does not verify it; you will know you did it:

1. Create a small folder, put one Python file in it (reuse your report card!).
2. `git init`, `git add .`, commit with a real message.
3. Write `README.md`, commit again — two commits means you practised the cycle twice.
4. Create a GitHub repo and `git push` (or explore offline with a local repo if you have no account).
5. Open the repo in the browser and admire your own history.

This is the exact workflow of professional developers, from day one.

## Final knowledge check

Three questions below cover the whole course. When all three are correct, the short course is complete and saved to your account.
''',
            'exercises': [
                {
                    'slug': 'readme-purpose',
                    'title': 'Purpose of the README',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'What is the README file for?',
                    'explain': 'The README explains the project to readers: what it is, why it exists, and how to use it. It is not compiled or executed.',
                    'difficulty': 'easy', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'To explain what the project is and how to run it', 'is_correct': True},
                        {'id': 'b', 'text': 'To store the project history', 'is_correct': False},
                        {'id': 'c', 'text': 'To list your GitHub followers', 'is_correct': False},
                        {'id': 'd', 'text': 'To configure your Git username', 'is_correct': False},
                    ],
                    'xp_reward': 40, 'order': 1, 'is_final_assessment': True,
                },
                {
                    'slug': 'workflow-order',
                    'title': 'The correct daily order',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Which is the correct order of the daily Git workflow?',
                    'explain': 'You edit, stage changes with git add, save a snapshot with git commit, then upload history with git push. Skipping staging leaves the commit with nothing to save.',
                    'difficulty': 'medium', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': 'edit -> git add -> git commit -> git push', 'is_correct': True},
                        {'id': 'b', 'text': 'edit -> git push -> git commit -> git add', 'is_correct': False},
                        {'id': 'c', 'text': 'git commit -> edit -> git push -> git add', 'is_correct': False},
                        {'id': 'd', 'text': 'git push -> edit -> git add -> git commit', 'is_correct': False},
                    ],
                    'xp_reward': 40, 'order': 2, 'is_final_assessment': True,
                },
                {
                    'slug': 'markdown-heading',
                    'title': 'Markdown heading',
                    'exercise_type': 'multiple_choice',
                    'instructions': 'Which Markdown line creates a TOP-LEVEL heading?',
                    'explain': 'One # is the largest heading; ## and ### are subsections. Bold is **text**, not headings.',
                    'difficulty': 'easy', 'language': 'none',
                    'choices': [
                        {'id': 'a', 'text': '# Title', 'is_correct': True},
                        {'id': 'b', 'text': '## Title', 'is_correct': False},
                        {'id': 'c', 'text': '**Title**', 'is_correct': False},
                        {'id': 'd', 'text': '-- Title', 'is_correct': False},
                    ],
                    'xp_reward': 40, 'order': 3, 'is_final_assessment': True,
                },
            ],
        },
    ],
}

GIT_COURSE = {
    'slug': 'git-github-foundations',
    'title': 'Git & GitHub Foundations',
    'subtitle': 'The version control workflow every real project runs on.',
    'description': (
        'A short, practical introduction to Git and GitHub: what version control is '
        'and why it exists, how commits build history, the essential status/add/commit '
        'workflow, publishing to GitHub, and writing a useful README — closing with a '
        'mini-project and a final knowledge check. Practical steps are self-reported; '
        'quizzes are graded from your actual answers.'
    ),
    'track_slug': 'developer-tools',
    'difficulty': 'beginner',
    'language': 'other',
    'instructor': 'Code Yaar',
    'prerequisites': 'None. A computer with a terminal helps for the optional hands-on practice.',
    'learning_objectives': [
        'Explain what Git and GitHub each are and the problem they solve',
        'Describe repositories, commits, and the staging area',
        'Use status, add, commit, log, and diff in the daily workflow',
        'Connect a local repository to GitHub and describe push/clone',
        'Write a README that explains and sells your project',
    ],
    'is_free': True,
    'is_published': True,
    'order': 2,
    'chapters': [GIT_CH1, GIT_CH2],
}

COURSE_SPECS = [PYTHON_COURSE, GIT_COURSE]

# Course resources: only real, working external links (no dead PDF paths).
COURSE_RESOURCES = {
    'python-foundations': [
        {
            'title': 'The Python Tutorial (official docs)',
            'description': 'The canonical written tutorial — pairs perfectly with every lesson in this course.',
            'resource_type': 'reference',
            'file_url': 'https://docs.python.org/3/tutorial/',
            'order': 1,
        },
        {
            'title': 'Built-in Functions reference',
            'description': 'Quick lookup for print(), input(), int(), len(), type() and everything else used here.',
            'resource_type': 'cheat_sheet',
            'file_url': 'https://docs.python.org/3/library/functions.html',
            'order': 2,
        },
    ],
    'git-github-foundations': [
        {
            'title': 'Pro Git (free book)',
            'description': 'The complete, free book on Git — read chapter 1 after this course.',
            'resource_type': 'reference',
            'file_url': 'https://git-scm.com/book/en/v2',
            'order': 1,
        },
        {
            'title': 'GitHub Docs: Getting started',
            'description': 'Official step-by-step guide for creating repositories and pushing.',
            'resource_type': 'reference',
            'file_url': 'https://docs.github.com/en/get-started',
            'order': 2,
        },
    ],
}


def _assign(obj, field_names, spec):
    """Copy the given fields from spec onto obj when they differ."""
    changed = False
    for name in field_names:
        if name in spec and getattr(obj, name) != spec[name]:
            setattr(obj, name, spec[name])
            changed = True
    return changed


def _upsert_exercise(lesson, spec):
    exercise, _ = Exercise.objects.get_or_create(
        lesson=lesson, slug=spec['slug'],
        defaults={f: spec[f] for f in EXERCISE_FIELDS if f in spec},
    )
    _assign(exercise, EXERCISE_FIELDS, spec)
    exercise.is_active = True
    exercise.save()

    # Hints carry no learner data — safe to rebuild from the spec.
    exercise.hints.all().delete()
    for i, content in enumerate(spec.get('hints', []), start=1):
        Hint.objects.create(
            exercise=exercise, content=content, order=i,
            reveals_solution=content.startswith('Solution:'),
            xp_penalty=0 if i < 3 else 10,
        )
    return exercise


def _upsert_lesson(chapter, spec):
    lesson, _ = Lesson.objects.get_or_create(
        chapter=chapter, slug=spec['slug'],
        defaults={'content_type': 'text', 'title': spec['title']},
    )
    _assign(lesson, LESSON_FIELDS, spec)
    lesson.is_active = True
    lesson.save()

    spec_slugs = {e['slug'] for e in spec.get('exercises', [])}
    for espec in spec.get('exercises', []):
        _upsert_exercise(lesson, espec)
    # Never delete: retire exercises removed from the spec so old attempt
    # and progress rows keep pointing at real content.
    lesson.exercises.exclude(slug__in=spec_slugs).update(is_active=False)
    return lesson


def _upsert_chapter(course, spec):
    chapter, _ = Chapter.objects.get_or_create(
        course=course, slug=spec['slug'],
        defaults={'title': spec['title']},
    )
    _assign(chapter, ('title', 'description', 'order'), spec)
    chapter.is_active = True
    chapter.save()

    spec_slugs = {l['slug'] for l in spec['lessons']}
    for lspec in spec['lessons']:
        _upsert_lesson(chapter, lspec)
    chapter.lessons.exclude(slug__in=spec_slugs).update(is_active=False)
    return chapter


def _upsert_course(track, spec):
    course, _ = Course.objects.get_or_create(
        slug=spec['slug'],
        defaults={'title': spec['title'], 'description': '', 'track': track},
    )
    _assign(course, (
        'title', 'subtitle', 'description', 'difficulty', 'language',
        'instructor', 'prerequisites', 'learning_objectives', 'is_free',
        'is_published', 'order',
    ), spec)
    course.track = track
    course.is_active = True
    course.save()

    spec_slugs = {c['slug'] for c in spec['chapters']}
    for cspec in spec['chapters']:
        _upsert_chapter(course, cspec)
    course.chapters.exclude(slug__in=spec_slugs).update(is_active=False)

    # Resources: upsert by title; retire anything no longer in the spec
    # (this is what removes the old broken local PDF links).
    rs = COURSE_RESOURCES.get(spec['slug'], [])
    titles = set()
    for rspec in rs:
        titles.add(rspec['title'])
        resource, _ = Resource.objects.get_or_create(
            course=course, title=rspec['title'],
            defaults={f: rspec[f] for f in RESOURCE_FIELDS if f in rspec},
        )
        _assign(resource, RESOURCE_FIELDS, rspec)
        resource.is_active = True
        resource.save()
    course.resources.exclude(title__in=titles).update(is_active=False)
    return course


class Command(BaseCommand):
    help = 'Seed/refresh course content (idempotent upsert — safe to re-run)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding course data...')

        # Demo user so the app can be explored without signing up
        User = get_user_model()
        demo_user, demo_created = User.objects.get_or_create(
            username='demo',
            defaults={'email': DEMO_EMAIL, 'first_name': 'Demo', 'last_name': 'Learner'},
        )
        if demo_created:
            demo_user.set_password(DEMO_PASSWORD)
            demo_user.save()
        UserProfile.objects.get_or_create(user=demo_user)
        Token.objects.get_or_create(user=demo_user)

        tracks = {}
        for track_spec in (
            {
                'slug': 'python',
                'title': 'Python',
                'description': 'Master Python from fundamentals to advanced concepts.',
                'difficulty': 'beginner', 'estimated_hours': 40, 'order': 1,
            },
            {
                'slug': 'developer-tools',
                'title': 'Developer Tools',
                'description': 'The everyday tools of real software work: version control and collaboration.',
                'difficulty': 'beginner', 'estimated_hours': 6, 'order': 2,
            },
        ):
            track, _ = CareerTrack.objects.get_or_create(
                slug=track_spec['slug'],
                defaults={f: track_spec[f] for f in ('title', 'description', 'difficulty', 'estimated_hours', 'order')},
            )
            tracks[track_spec['slug']] = track

        for spec in COURSE_SPECS:
            course = _upsert_course(tracks[spec['track_slug']], spec)
            self.stdout.write(self.style.SUCCESS(
                f'  {course.title}: {course.chapters.filter(is_active=True).count()} chapters, '
                f'{course.lesson_count} lessons, {course.exercise_count} exercises '
                f'({course.total_xp} XP, ~{course.estimated_hours}h)'
            ))

        # ── Achievements ────────────────────────────────────────────────
        for achievement in (
            {
                'slug': 'first-lesson', 'title': 'First Steps',
                'description': 'Complete your first lesson.', 'icon': 'trophy',
                'category': 'course', 'xp_bonus': 50,
                'condition_type': 'lesson_complete', 'condition_value': '1',
            },
            {
                'slug': 'chapter-master', 'title': 'Chapter Master',
                'description': 'Complete all lessons in a chapter.', 'icon': 'star',
                'category': 'chapter', 'xp_bonus': 200,
                'condition_type': 'chapter_complete',
            },
            {
                'slug': 'streak-7', 'title': 'Week Warrior',
                'description': 'Maintain a 7-day learning streak.', 'icon': 'fire',
                'category': 'streak', 'xp_bonus': 300,
                'condition_type': 'streak_7',
            },
            {
                'slug': 'python-foundations-complete', 'title': 'Python Graduate',
                'description': 'Complete the Python Foundations course.', 'icon': 'graduation',
                'category': 'course', 'xp_bonus': 500,
                'condition_type': 'course_complete', 'condition_value': 'python-foundations',
            },
            {
                'slug': 'git-foundations-complete', 'title': 'Version Control Ready',
                'description': 'Complete the Git & GitHub Foundations course.', 'icon': 'graduation',
                'category': 'course', 'xp_bonus': 300,
                'condition_type': 'course_complete', 'condition_value': 'git-github-foundations',
            },
        ):
            Achievement.objects.get_or_create(
                slug=achievement['slug'],
                defaults={k: v for k, v in achievement.items() if k != 'slug'},
            )

        self.stdout.write(self.style.SUCCESS(
            f'Done. Demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}'
        ))
