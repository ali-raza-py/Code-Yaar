"""Course 1 — Python Programming Foundations.

Completes the existing `python-foundations` course in place, preserving its
slug and identity. Lessons carry real instructional material, correct code,
expected output, common mistakes and knowledge checks. Runnable code exercises
are graded by the server-side sandbox; the final assessment is graded MCQ.
"""

COURSE = {
    'slug': 'python-foundations',
    'title': 'Python Programming Foundations',
    'subtitle': 'Write, understand, debug and organise real Python programs.',
    'description': (
        'Learn Python from scratch. You will write and run programs, master '
        'variables, conditions, loops, strings, lists and functions, interpret '
        'errors, and finish by building a small working project and passing a '
        'final assessment.'
    ),
    'difficulty': 'beginner',
    'language': 'python',
    'prerequisites': 'None — this is a first programming course.',
    'track': {
        'slug': 'core-programming',
        'title': 'Programming Fundamentals',
        'category': 'programming',
        'description': (
            'Start with Python, continue with C++, then sharpen the problem-'
            'solving and data-structure skills every language builds on. '
            'Languages are lessons inside this track, not separate destinations.'
        ),
    },
    'objectives': [
        'Understand Python syntax and execute basic programs.',
        'Use variables, data types, input, output and operators.',
        'Write conditional statements and loops.',
        'Work with strings and lists.',
        'Create and call functions.',
        'Interpret common errors and debug simple programs.',
        'Build a small working Python project.',
    ],
    'modules': [
        {
            'title': 'Getting Started',
            'slug': 'getting-started',
            'description': 'What Python is and how to run your first program.',
            'lessons': [
                {
                    'title': 'What Python Is and Where It Is Used',
                    'slug': 'what-is-python',
                    'objective': 'Explain what Python is and name places it is used.',
                    'duration': 8,
                    'body': (
                        '# What Python Is\n\n'
                        'Python is a general-purpose programming language known for a '
                        'clean, readable syntax. You write instructions in plain-ish '
                        'English and a Python interpreter runs them line by line.\n\n'
                        '## Where it is used\n'
                        '- Web backends (Django, Flask)\n'
                        '- Data analysis and machine learning\n'
                        '- Automation and scripting\n'
                        '- Teaching programming fundamentals\n\n'
                        '## Why beginners choose it\n'
                        'Python hides much of the bookkeeping other languages require '
                        '(no semicolons, no braces to open a block), so you can focus on '
                        'thinking about the problem.\n\n'
                        'A program is just a sequence of **statements**. A **statement** '
                        'does one thing: show text, store a value, repeat an action.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'python-uses',
                            'title': 'Where is Python used?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which of these is a common real-world use of Python?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Only building operating-system kernels', 'is_correct': False},
                                {'id': 'b', 'text': 'Web backends, data analysis and automation', 'is_correct': True},
                                {'id': 'c', 'text': 'Designing computer CPUs', 'is_correct': False},
                                {'id': 'd', 'text': 'Nothing beyond toys', 'is_correct': False},
                            ],
                        }
                    ],
                },
                {
                    'title': 'Your First Program',
                    'slug': 'first-program',
                    'objective': 'Run a program that prints text and use comments.',
                    'duration': 10,
                    'body': (
                        '# Your First Program\n\n'
                        'The `print()` function displays a value on the screen:\n\n'
                        '```python\nprint("Hello, World!")\n```\n\n'
                        'Expected output:\n\n'
                        '```\nHello, World!\n```\n\n'
                        'Text in quotes is a **string**. Everything after a `#` on a line '
                        'is a **comment** — Python ignores it, and it exists to help the '
                        'human reader.\n\n'
                        '```python\n# This comment explains the next line\nprint(2 + 3)  # shows 5\n```\n\n'
                        '## Common mistakes\n'
                        '- Forgetting the closing parenthesis: `print("hi"` is a syntax error.\n'
                        '- Using curly quotes from a word processor instead of `"`. '
                        'Only plain straight quotes work.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'print-hello',
                            'title': 'Print Hello, World!',
                            'exercise_type': 'code',
                            'instructions': 'Write a program that prints exactly: Hello, World!',
                            'context': 'The traditional first program in any language.',
                            'constraints': 'Use the print() function.',
                            'expected_output': 'Hello, World!',
                            'starter_code': '# Print Hello, World!\n',
                            'solution_code': 'print("Hello, World!")',
                            'test_cases': [{'input': '', 'expected_output': 'Hello, World!'}],
                            'explain': 'print() writes its argument to standard output, followed by a newline.',
                            'xp_reward': 80,
                        },
                        {
                            'slug': 'predict-print-2',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': 'What does this print?\n\n```python\nprint(10 + 5)\n```',
                            'expected_output': '15',
                            'xp_reward': 50,
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Variables and Data',
            'slug': 'variables-and-data',
            'description': 'Store and transform values with variables and types.',
            'lessons': [
                {
                    'title': 'Variables and Naming Rules',
                    'slug': 'variables',
                    'objective': 'Create variables and follow naming rules.',
                    'duration': 12,
                    'body': (
                        '# Variables\n\n'
                        'A **variable** is a name that refers to a value. You create one '
                        'with the assignment operator `=`:\n\n'
                        '```python\nname = "Ali"\nage = 18\n```\n\n'
                        '## Naming rules\n'
                        '- Start with a letter or underscore, then letters, digits or `_`.\n'
                        '- Cannot start with a digit (`2age` is invalid).\n'
                        '- Are case-sensitive (`Age` and `age` differ).\n'
                        '- Cannot be a reserved keyword like `if`, `for`, `class`.\n\n'
                        '## Reassignment\n'
                        '```python\nscore = 0\nscore = score + 10   # score is now 10\n```\n\n'
                        '## Common mistakes\n'
                        'Assigning backwards: `18 = age` is invalid — the name goes on the '
                        'left of `=`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'assign-score',
                            'title': 'Create a variable',
                            'exercise_type': 'code',
                            'instructions': 'Create a variable named `score` with the integer value 100 and print it.',
                            'expected_output': '100',
                            'starter_code': '# create score and print it\n',
                            'solution_code': 'score = 100\nprint(score)',
                            'test_cases': [{'input': '', 'expected_output': '100'}],
                            'xp_reward': 80,
                        },
                        {
                            'slug': 'valid-name',
                            'title': 'Which name is valid?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which of these is a valid Python variable name?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '2nd_place', 'is_correct': False},
                                {'id': 'b', 'text': 'total-score', 'is_correct': False},
                                {'id': 'c', 'text': '_total', 'is_correct': True},
                                {'id': 'd', 'text': 'class', 'is_correct': False},
                            ],
                        },
                    ],
                },
                {
                    'title': 'Data Types and Conversion',
                    'slug': 'data-types',
                    'objective': 'Identify int, float, str, bool and convert between them.',
                    'duration': 12,
                    'body': (
                        '# Core data types\n\n'
                        '| Type | Example | Meaning |\n'
                        '|------|---------|---------|\n'
                        '| `int` | `42` | whole number |\n'
                        '| `float` | `3.14` | decimal number |\n'
                        '| `str` | `"hi"` | text |\n'
                        '| `bool` | `True` | truth value |\n\n'
                        'Check a type with `type()`:\n\n'
                        '```python\nprint(type(42))     # <class \'int\'>\n'
                        'print(type("42"))   # <class \'str\'>\n```\n\n'
                        '## Conversion\n'
                        '`int("5")` → 5, `str(5)` → "5", `float("1.5")` → 1.5.\n\n'
                        '## Common mistakes\n'
                        '`int("1.5")` raises **ValueError** — convert a decimal string with '
                        '`float()` first.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'convert-str-int',
                            'title': 'Add a number to a numeric string',
                            'exercise_type': 'code',
                            'instructions': 'Given `text = "40"`, print the value of text converted to an integer plus 2.',
                            'expected_output': '42',
                            'starter_code': 'text = "40"\n# print int(text) + 2\n',
                            'solution_code': 'text = "40"\nprint(int(text) + 2)',
                            'test_cases': [{'input': '', 'expected_output': '42'}],
                            'explain': 'int("40") turns the string into the integer 40, then +2 gives 42.',
                            'xp_reward': 80,
                        }
                    ],
                },
                {
                    'title': 'Input and Operators',
                    'slug': 'operators',
                    'objective': 'Use arithmetic operators and read user input.',
                    'duration': 12,
                    'body': (
                        '# Operators\n\n'
                        'Arithmetic: `+  -  *  /  //  %  **`.\n\n'
                        '```python\nprint(7 / 2)    # 3.5   true division\n'
                        'print(7 // 2)   # 3     floor division\n'
                        'print(7 % 2)    # 1     remainder\n'
                        'print(2 ** 3)   # 8     power\n```\n\n'
                        '## Reading input\n'
                        '`input()` always returns a **string**, so convert it before doing '
                        'math:\n\n'
                        '```python\nage = int(input("Your age: "))\n```\n\n'
                        'In the exercises and sandbox, assume input is provided through the '
                        'test harness. When a value is given directly, use it as written.\n\n'
                        '## Common mistakes\n'
                        'Forgetting `int(...)` around `input()` then trying to add it to a '
                        'number — that raises a `TypeError`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'calculator-add',
                            'title': 'Practical: sum two numbers',
                            'exercise_type': 'code',
                            'instructions': 'Print the sum of 12 and 30.',
                            'expected_output': '42',
                            'starter_code': '# print 12 + 30\n',
                            'solution_code': 'print(12 + 30)',
                            'test_cases': [{'input': '', 'expected_output': '42'}],
                            'xp_reward': 70,
                        }
                    ],
                },
            ],
        },
        {
            'title': 'Decision Making',
            'slug': 'decision-making',
            'description': 'Make your program branch with if / elif / else.',
            'lessons': [
                {
                    'title': 'if and else',
                    'slug': 'if-else',
                    'objective': 'Run different code depending on a condition.',
                    'duration': 12,
                    'body': (
                        '# Making decisions\n\n'
                        'A **condition** is an expression that is `True` or `False`.\n\n'
                        '```python\nage = 20\nif age >= 18:\n    print("Adult")\nelse:\n    print("Minor")\n```\n\n'
                        'Output: `Adult`.\n\n'
                        'Indentation (four spaces) defines the block — it is not optional in '
                        'Python.\n\n'
                        '## Comparison operators\n'
                        '`==  !=  >  <  >=  <=`. Note `==` compares, a single `=` assigns.\n\n'
                        '## Common mistakes\n'
                        'Using `=` inside an `if`: `if age = 18` is a **SyntaxError**.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'even-odd',
                            'title': 'Practical: even or odd',
                            'exercise_type': 'code',
                            'instructions': 'Given `n = 7`, print "even" if it is divisible by 2, otherwise "odd".',
                            'expected_output': 'odd',
                            'starter_code': 'n = 7\n# print even or odd\n',
                            'solution_code': 'n = 7\nif n % 2 == 0:\n    print("even")\nelse:\n    print("odd")',
                            'test_cases': [
                                {'input': 'n = 7\n', 'expected_output': 'odd'},
                            ],
                            'explain': 'n % 2 is the remainder of dividing by 2; 0 means even.',
                            'xp_reward': 90,
                        },
                        {
                            'slug': 'grade-check',
                            'title': 'Grade calculator',
                            'exercise_type': 'code',
                            'instructions': (
                                'Given `marks = 75`, print "Pass" when marks are at least 50, '
                                'otherwise "Fail".'
                            ),
                            'expected_output': 'Pass',
                            'starter_code': 'marks = 75\n# print Pass or Fail\n',
                            'solution_code': 'marks = 75\nif marks >= 50:\n    print("Pass")\nelse:\n    print("Fail")',
                            'test_cases': [{'input': 'marks = 75\n', 'expected_output': 'Pass'}],
                            'xp_reward': 90,
                        },
                    ],
                },
                {
                    'title': 'elif and Multiple Conditions',
                    'slug': 'elif',
                    'objective': 'Chain several branches and combine conditions.',
                    'duration': 10,
                    'body': (
                        '# Multiple branches\n\n'
                        '```python\nscore = 82\nif score >= 90:\n    grade = "A"\n'
                        'elif score >= 80:\n    grade = "B"\nelse:\n    grade = "C"\n'
                        'print(grade)   # B\n```\n\n'
                        'Python checks branches top to bottom and stops at the first True one.\n\n'
                        '## Logical operators\n'
                        '`and`, `or`, `not` combine conditions:\n\n'
                        '```python\nage = 20\nhas_id = True\nif age >= 18 and has_id:\n    print("allowed")\n```\n\n'
                        '## Common mistakes\n'
                        'Testing `if 60 <= score <= 80` is valid in Python (chained comparison), '
                        'but `if score == 60 or 70` is wrong — it must be `score == 60 or score == 70`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'elif-chain',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'What is printed?\n\n```python\nx = 5\n'
                                'if x > 10:\n    print("big")\nelif x > 3:\n    print("medium")\n'
                                'else:\n    print("small")\n```'
                            ),
                            'expected_output': 'medium',
                            'xp_reward': 60,
                        }
                    ],
                },
            ],
        },
        {
            'title': 'Repetition',
            'slug': 'repetition',
            'description': 'Repeat work safely with loops.',
            'lessons': [
                {
                    'title': 'for Loops and range',
                    'slug': 'for-loops',
                    'objective': 'Loop over a sequence and use range().',
                    'duration': 12,
                    'body': (
                        '# for loops\n\n'
                        '```python\nfor i in range(3):\n    print(i)   # 0 1 2\n```\n\n'
                        '`range(n)` yields 0..n-1. `range(a, b)` yields a..b-1. '
                        '`range(a, b, step)` adds a stride.\n\n'
                        '```python\nfor n in range(1, 4):\n    print(n * 2)   # 2 4 6\n```\n\n'
                        '## Accumulator pattern\n'
                        '```python\ntotal = 0\nfor n in range(1, 6):   # 1..5\n    total = total + n\nprint(total)   # 15\n```\n\n'
                        '## Common mistakes\n'
                        '`range(1, 5)` stops at 4, not 5 — the end is exclusive.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'multiplication-table',
                            'title': 'Practical: times table',
                            'exercise_type': 'code',
                            'instructions': 'Print 3 multiplied by 1..4, each result on its own line.',
                            'expected_output': '3\n6\n9\n12',
                            'starter_code': '# print 3 * 1..4\n',
                            'solution_code': 'for i in range(1, 5):\n    print(3 * i)',
                            'test_cases': [{'input': '', 'expected_output': '3\n6\n9\n12'}],
                            'explain': 'range(1,5) is 1,2,3,4; multiplying each by 3 gives the table.',
                            'xp_reward': 100,
                        },
                        {
                            'slug': 'sum-loop',
                            'title': 'Sum 1..5',
                            'exercise_type': 'code',
                            'instructions': 'Print the sum of the numbers 1 through 5.',
                            'expected_output': '15',
                            'starter_code': 'total = 0\n# add 1..5 into total, then print\n',
                            'solution_code': 'total = 0\nfor n in range(1, 6):\n    total = total + n\nprint(total)',
                            'test_cases': [{'input': '', 'expected_output': '15'}],
                            'xp_reward': 100,
                        },
                    ],
                },
                {
                    'title': 'while Loops and Control',
                    'slug': 'while-loops',
                    'objective': 'Use while, break and continue without infinite loops.',
                    'duration': 10,
                    'body': (
                        '# while loops\n\n'
                        '```python\ncount = 0\nwhile count < 3:\n    print(count)\n    count = count + 1   # 0 1 2\n```\n\n'
                        '`while` repeats **as long as** its condition is true. You must change '
                        'something inside the loop or it never ends.\n\n'
                        '## break and continue\n'
                        '- `break` stops the loop immediately.\n'
                        '- `continue` skips to the next iteration.\n\n'
                        '## Common mistakes\n'
                        'Forgetting to advance the counter → an infinite loop that never '
                        'terminates (the sandbox will time it out).\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'countdown',
                            'title': 'Countdown',
                            'exercise_type': 'code',
                            'instructions': 'Starting from 3, print 3, 2, 1, then stop.',
                            'expected_output': '3\n2\n1',
                            'starter_code': 'n = 3\nwhile n > 0:\n    print(n)\n    # decrement n\n',
                            'solution_code': 'n = 3\nwhile n > 0:\n    print(n)\n    n = n - 1',
                            'test_cases': [{'input': '', 'expected_output': '3\n2\n1'}],
                            'xp_reward': 90,
                        }
                    ],
                },
            ],
        },
        {
            'title': 'Strings and Lists',
            'slug': 'strings-and-lists',
            'description': 'Work with text and ordered collections.',
            'lessons': [
                {
                    'title': 'String Indexing, Slicing and Methods',
                    'slug': 'strings',
                    'objective': 'Access and transform parts of a string.',
                    'duration': 12,
                    'body': (
                        '# Strings\n\n'
                        'A string is an ordered sequence of characters. Indexes start at 0, '
                        'and -1 means the last character.\n\n'
                        '```python\nword = "Python"\nprint(word[0])     # P\nprint(word[-1])    # n\nprint(word[0:3])   # Pyt  (stop is exclusive)\n```\n\n'
                        '## Useful methods\n'
                        '```python\nprint(" hi ".strip())     # "hi"\nprint("ab".upper())       # "AB"\nprint("a,b,c".split(","))  # [\'a\', \'b\', \'c\']\n```\n\n'
                        '## Common mistakes\n'
                        'Strings are immutable: `word[0] = "p"` raises `TypeError`. Build a new '
                        'string instead.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'reverse-string',
                            'title': 'Reverse a string',
                            'exercise_type': 'code',
                            'instructions': 'Print the word "Python" reversed.',
                            'expected_output': 'nohtyP',
                            'starter_code': 'word = "Python"\n# print it reversed\n',
                            'solution_code': 'word = "Python"\nprint(word[::-1])',
                            'test_cases': [{'input': '', 'expected_output': 'nohtyP'}],
                            'explain': 'The slice [::-1] steps backwards through the whole string.',
                            'xp_reward': 90,
                        }
                    ],
                },
                {
                    'title': 'Lists',
                    'slug': 'lists',
                    'objective': 'Create, index and modify lists and iterate over them.',
                    'duration': 12,
                    'body': (
                        '# Lists\n\n'
                        'A list is an ordered, changeable collection.\n\n'
                        '```python\nnums = [10, 20, 30]\nprint(nums[0])     # 10\nprint(len(nums))   # 3\nnums.append(40)  # [10, 20, 30, 40]\n```\n\n'
                        '## Iterating\n'
                        '```python\nfor n in nums:\n    print(n * 2)\n```\n\n'
                        '## Common mistakes\n'
                        '`nums[3]` on a 3-item list raises `IndexError` — the valid indexes are '
                        '0..len-1.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'fix-index-error',
                            'title': 'Debug the list access',
                            'exercise_type': 'debugging',
                            'instructions': (
                                'Fix the bug so it prints the LAST element.\n\n'
                                '```python\nnumbers = [10, 20, 30, 40, 50]\nprint(numbers[5])\n```'
                            ),
                            'expected_output': '50',
                            'starter_code': 'numbers = [10, 20, 30, 40, 50]\nprint(numbers[5])  # fix this\n',
                            'solution_code': 'numbers = [10, 20, 30, 40, 50]\nprint(numbers[4])',
                            'explain': 'Index 5 is out of range; the last element is at index 4 (or -1).',
                            'xp_reward': 90,
                        },
                        {
                            'slug': 'list-sum',
                            'title': 'Sum a list',
                            'exercise_type': 'code',
                            'instructions': 'Print the total of [1, 2, 3, 4].',
                            'expected_output': '10',
                            'starter_code': 'values = [1, 2, 3, 4]\ntotal = 0\n# add each value, print total\n',
                            'solution_code': 'values = [1, 2, 3, 4]\ntotal = 0\nfor v in values:\n    total = total + v\nprint(total)',
                            'test_cases': [{'input': '', 'expected_output': '10'}],
                            'xp_reward': 90,
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Functions and Debugging',
            'slug': 'functions-debugging',
            'description': 'Package logic into reusable functions and fix errors.',
            'lessons': [
                {
                    'title': 'Defining Functions',
                    'slug': 'functions',
                    'objective': 'Define, call and return from functions.',
                    'duration': 12,
                    'body': (
                        '# Functions\n\n'
                        'A function packages reusable steps behind a name.\n\n'
                        '```python\ndef greet(name):\n    return f"Hello, {name}!"\n\n'
                        'message = greet("Sara")\nprint(message)   # Hello, Sara!\n```\n\n'
                        '- **Parameters** (`name`) receive the **arguments** you pass in.\n'
                        '- `return` sends a value back; without it a function returns `None`.\n\n'
                        '## Common mistakes\n'
                        'Printing inside the function instead of returning — that makes the '
                        'value hard to reuse. Return data, print at the edges.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'double-function',
                            'title': 'Write a function',
                            'exercise_type': 'code',
                            'instructions': 'Define `double(n)` returning n * 2, then print double(5).',
                            'expected_output': '10',
                            'starter_code': '# define double(n) and print double(5)\n',
                            'solution_code': 'def double(n):\n    return n * 2\n\nprint(double(5))',
                            'test_cases': [
                                {'input': '', 'expected_output': '10'},
                            ],
                            'explain': 'The function returns n*2; double(5) is 10.',
                            'xp_reward': 100,
                        },
                        {
                            'slug': 'return-none',
                            'title': 'What is returned?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A function with no `return` statement produces which value?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': '0', 'is_correct': False},
                                {'id': 'b', 'text': 'None', 'is_correct': True},
                                {'id': 'c', 'text': 'an empty string', 'is_correct': False},
                                {'id': 'd', 'text': 'nothing at all (crash)', 'is_correct': False},
                            ],
                        },
                    ],
                },
                {
                    'title': 'Reading Errors',
                    'slug': 'reading-errors',
                    'objective': 'Interpret a common error message and fix its cause.',
                    'duration': 10,
                    'body': (
                        '# Reading tracebacks\n\n'
                        'A traceback names the **error type**, the **line**, and the reason:\n\n'
                        '```python\nprint(total)\n# NameError: name \'total\' is not defined\n```\n\n'
                        'Read the **last line first** — that is the actual error. The lines '
                        'above show how you got there.\n\n'
                        'Quick reference:\n'
                        '- `SyntaxError` — the code cannot even be parsed (missing `:` or `)`).\n'
                        '- `NameError` — using a variable that does not exist.\n'
                        '- `TypeError` — mixing incompatible types (e.g. `len(5)`).\n'
                        '- `IndexError` / `KeyError` — accessing something that isn\'t there.\n\n'
                        'Fix the cause, not the symptom.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'fix-name-error',
                            'title': 'Fix the undefined name',
                            'exercise_type': 'debugging',
                            'instructions': (
                                'This raises a NameError. Fix it so it prints 5.\n\n'
                                '```python\nnumber = 5\nprint(numbr)\n```'
                            ),
                            'expected_output': '5',
                            'starter_code': 'number = 5\nprint(numbr)  # fix the typo\n',
                            'solution_code': 'number = 5\nprint(number)',
                            'xp_reward': 80,
                        }
                    ],
                },
            ],
        },
        {
            'title': 'Project',
            'slug': 'project',
            'description': 'Apply everything in a small working program.',
            'lessons': [
                {
                    'title': 'Build a Number-Guessing Game',
                    'slug': 'project-number-game',
                    'objective': 'Combine loops, conditions and functions into one program.',
                    'duration': 20,
                    'body': (
                        '# Project: a small guessing loop\n\n'
                        'The computer holds a secret number. The player keeps guessing until '
                        'they get it right, receiving "too high"/"too low" hints.\n\n'
                        '```python\nsecret = 7\ndef feedback(guess):\n    if guess < secret:\n        return "too low"\n    elif guess > secret:\n        return "too high"\n    return "correct"\n\n'
                        'for guess in [5, 9, 7]:\n    print(feedback(guess))\n```\n\n'
                        'Output:\n\n```\ntoo low\ntoo high\ncorrect\n```\n\n'
                        'This uses comparison operators, `if/elif`, a function and a loop '
                        'together — exactly the skills from this course.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'guess-feedback',
                            'title': 'Write feedback(guess)',
                            'exercise_type': 'code',
                            'instructions': (
                                'With `secret = 7`, define `feedback(guess)` returning "too low", '
                                '"too high" or "correct", then print feedback(5), feedback(9), '
                                'feedback(7) on separate lines.'
                            ),
                            'expected_output': 'too low\ntoo high\ncorrect',
                            'starter_code': 'secret = 7\n# define feedback(guess), then print for 5, 9, 7\n',
                            'solution_code': (
                                'secret = 7\ndef feedback(guess):\n    if guess < secret:\n        return "too low"\n'
                                '    elif guess > secret:\n        return "too high"\n    return "correct"\n\n'
                                'print(feedback(5))\nprint(feedback(9))\nprint(feedback(7))'
                            ),
                            'test_cases': [{'input': '', 'expected_output': 'too low\ntoo high\ncorrect'}],
                            'explain': 'Compare the guess to the secret and return the matching hint.',
                            'xp_reward': 150,
                        }
                    ],
                },
            ],
        },
    ],
    # Final assessment — server-graded MCQ; must reach the passing score.
    'assessment': [
        {
            'slug': 'final-syntax',
            'title': 'Valid statement',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which line is valid Python?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'print "hi"', 'is_correct': False},
                {'id': 'b', 'text': 'print("hi")', 'is_correct': True},
                {'id': 'c', 'text': 'Print(hi)', 'is_correct': False},
                {'id': 'd', 'text': 'println hi', 'is_correct': False},
            ],
        },
        {
            'slug': 'final-division',
            'title': 'Floor division',
            'exercise_type': 'output_prediction',
            'instructions': 'What does `print(9 // 2)` output?',
            'expected_output': '4',
            'xp_reward': 20,
        },
        {
            'slug': 'final-loop-range',
            'title': 'Loop length',
            'exercise_type': 'multiple_choice',
            'instructions': 'How many times does `for i in range(2, 6)` repeat?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': '3', 'is_correct': False},
                {'id': 'b', 'text': '4', 'is_correct': True},
                {'id': 'c', 'text': '5', 'is_correct': False},
                {'id': 'd', 'text': '6', 'is_correct': False},
            ],
        },
        {
            'slug': 'final-string-index',
            'title': 'Last character',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which expression gives the last character of string `s`?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 's[-1]', 'is_correct': True},
                {'id': 'b', 'text': 's[last]', 'is_correct': False},
                {'id': 'c', 'text': 's()', 'is_correct': False},
                {'id': 'd', 'text': 's.length', 'is_correct': False},
            ],
        },
        {
            'slug': 'final-type',
            'title': 'Type of 3.0',
            'exercise_type': 'multiple_choice',
            'instructions': 'What is `type(3.0)`?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'int', 'is_correct': False},
                {'id': 'b', 'text': 'float', 'is_correct': True},
                {'id': 'c', 'text': 'str', 'is_correct': False},
                {'id': 'd', 'text': 'bool', 'is_correct': False},
            ],
        },
    ],
}
