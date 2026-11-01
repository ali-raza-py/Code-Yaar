"""
Class XI, Unit 3 — chapters 1 and 2:

    CH-1  Programming with Python        (3.1-3.2, printed pp. 92-94)
    CH-2  The IDE and Writing Python     (3.3-3.4.1, printed pp. 94-101)

Every statement below was read off the scanned textbook page by page and is
recorded with its printed page in textbooks/CLASS-XI-SOURCE-VERIFICATION.md.
Where practice goes beyond what the book prints, the exercise is marked
supplementary in its reference.
"""

from .common import ref

UNIT = 'Unit 3'
CLASS = 'Class XI'


CHAPTER_INTRO = {
    'slug': 'xi-programming-with-python',
    'title': 'Programming with Python',
    'description': (
        'What a program and a programming language are, how low-level and '
        'high-level languages compare, and the career areas the book opens '
        'for Python developers.'
    ),
    'order': 1,
    'xp_reward': 250,
    'reference': ref(UNIT, '3.1-3.2 Programming and Career Growth with Python', '92-94', CLASS),
    'lessons': [
        # ── 3.1 ────────────────────────────────────────────────────────────
        {
            'slug': 'what-is-a-program',
            'title': 'What Is a Program?',
            'content_type': 'text',
            'learning_objective': (
                'Define "program" and "programming language" and sort '
                'languages into low-level, mid-level and high-level.'
            ),
            'order': 1,
            'duration_minutes': 9,
            'xp_reward': 40,
            'reference': ref(UNIT, '3.1 Programming (incl. 3.1.1 language types)', '92-93', CLASS),
            'content_body': '''# What Is a Program?

Section 3.1 (p. 92) starts from the definition the board exam expects:

> A **program** is a set of instructions that tells the computer how to perform a task. A **programming language** is the artificial language we use to write those instructions so the computer can understand them.

## The three levels (3.1.1, Figure 3.1, p. 92)

Figure 3.1 divides programming languages into three groups:

| Level | How it reads | Examples in the book |
|---|---|---|
| **Low-level** | closest to the machine | machine / binary language |
| **Mid-level** | symbolic, one step above machine | assembly language |
| **High-level** | close to English, easy to write | C++, JAVA, PYTHON |

## High-level languages side by side (p. 93)

The comparison prose on p. 93 singles out three languages:

- **C++** — used for system software and games.
- **Java** — "write once, run anywhere".
- **Python** — a high-level language with simple syntax, used for data analysis, artificial intelligence and web development.

This course uses Python, exactly the language the Class XI textbook teaches — every program you will write runs with the sandbox built into the page.
''',
            'exercises': [
                {
                    'slug': 'definition-of-program',
                    'title': 'Defining a Program',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'According to section 3.1, what is a program?'
                    ),
                    'explain': (
                        'A program is a set of instructions that tells the '
                        'computer how to perform a task. Sindh Board Class XI, '
                        'Unit 3, 3.1, p. 92.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'A set of instructions that tells the computer how to perform a task', 'is_correct': True},
                        {'id': 'b', 'text': 'A device that stores files', 'is_correct': False},
                        {'id': 'c', 'text': 'A program is another name for the operating system', 'is_correct': False},
                        {'id': 'd', 'text': 'A keyboard used to type code', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, '3.1 Programming', '92', CLASS),
                },
                {
                    'slug': 'highest-level-of-language',
                    'title': 'Levels of Programming Languages',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'In Figure 3.1\'s classification, what kind of '
                        'language is Python?'
                    ),
                    'explain': (
                        'Figure 3.1 (p. 92) places C++, JAVA and PYTHON in the '
                        'high-level group; the lowest level is machine/binary, '
                        'and assembly is the mid-level. Sindh Board Class XI, '
                        'Unit 3, 3.1.1, p. 92.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'High-level language', 'is_correct': True},
                        {'id': 'b', 'text': 'Low-level language', 'is_correct': False},
                        {'id': 'c', 'text': 'Mid-level (assembly) language', 'is_correct': False},
                        {'id': 'd', 'text': 'Machine language', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 2,
                    'reference': ref(UNIT, '3.1.1 Language types (Figure 3.1)', '92', CLASS),
                },
                {
                    'slug': 'closest-to-machine-language',
                    'title': 'Which Language Is Closest to the Machine?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which kind of programming language is closest to the '
                        'machine (binary) level?'
                    ),
                    'explain': (
                        'The low-level group of Figure 3.1 is the machine/'
                        'binary language — the one closest to the machine; '
                        'high-level languages like Python are the furthest. '
                        'Sindh Board Class XI, Unit 3, Exercise A (vi), '
                        'p. 136; section 3.1.1, p. 92.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Low-level (machine/binary) language', 'is_correct': True},
                        {'id': 'b', 'text': 'High-level language like Python', 'is_correct': False},
                        {'id': 'c', 'text': 'A database language like SQL', 'is_correct': False},
                        {'id': 'd', 'text': 'A markup language like HTML', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE A (vi)', '136', CLASS),
                },
            ],
        },

        # ── 3.2 ────────────────────────────────────────────────────────────
        {
            'slug': 'career-growth-with-python',
            'title': 'Career Growth with Python',
            'content_type': 'text',
            'learning_objective': (
                'Name the career areas the textbook connects with Python.'
            ),
            'order': 2,
            'duration_minutes': 6,
            'xp_reward': 30,
            'reference': ref(UNIT, '3.2 Career Growth with Python', '93-94', CLASS),
            'content_body': '''# Career Growth with Python

Section 3.2 (pp. 93-94) lists the fields where Python is used, each with a
line of explanation:

1. **Software Development** — building applications.
2. **Data Science & Analysis** — working with data to find meaning in it.
3. **Artificial Intelligence / Machine Learning** — systems that learn.
4. **Web Development** — with the frameworks **Django** and **Flask**.
5. **Automation & Scripting** — writing small programs that do repetitive work.
6. **Cybersecurity & Networking** — protecting and connecting systems.

The unit\'s closing "Career Opportunities" page (p. 134) turns the same list
into job titles: Python Developer, Software Developer, Web Developer, Data
Analyst, Automation/Scripting Engineer, Mobile App Developer and Game
Developer.

> **Activity from the book (p. 94):** "Demonstrate the different frameworks of Python." In interview terms that means being able to say, for example, that Django is the full-featured web framework while Flask is the lightweight one — both serve the Web Development career area above.
''',
            'exercises': [
                {
                    'slug': 'python-web-frameworks',
                    'title': 'Python Web Frameworks',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which pair of web frameworks does section 3.2 name '
                        'for Python Web Development?'
                    ),
                    'explain': (
                        'Section 3.2 (p. 94) names Django and Flask under Web '
                        'Development. Sindh Board Class XI, Unit 3, 3.2, '
                        'pp. 93-94.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Django and Flask', 'is_correct': True},
                        {'id': 'b', 'text': 'React and Vue', 'is_correct': False},
                        {'id': 'c', 'text': 'Laravel and Symfony', 'is_correct': False},
                        {'id': 'd', 'text': 'Node and Express', 'is_correct': False},
                    ],
                    'xp_reward': 30,
                    'order': 1,
                    'reference': ref(UNIT, '3.2 Career Growth with Python', '94', CLASS),
                },
                {
                    'slug': 'data-science-area',
                    'title': 'Python and Data',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which career area in section 3.2 is about working '
                        'with data to find meaning in it?'
                    ),
                    'explain': (
                        'Data Science & Analysis. The same section also lists '
                        'Software Development, AI/ML, Web Development, '
                        'Automation & Scripting, and Cybersecurity & '
                        'Networking. Sindh Board Class XI, Unit 3, 3.2, '
                        'pp. 93-94.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Data Science & Analysis', 'is_correct': True},
                        {'id': 'b', 'text': 'Cybersecurity & Networking', 'is_correct': False},
                        {'id': 'c', 'text': 'Game Development', 'is_correct': False},
                        {'id': 'd', 'text': 'Mobile App Development', 'is_correct': False},
                    ],
                    'xp_reward': 30,
                    'order': 2,
                    'reference': ref(UNIT, '3.2 Career Growth with Python', '93-94', CLASS),
                },
            ],
        },
    ],
}


CHAPTER_IDE = {
    'slug': 'xi-ide-and-python-basics',
    'title': 'The IDE and Python Basics',
    'description': (
        'What an IDE does, how the book sets up Visual Studio Code, the '
        'fundamentals of Python (comments, statements, 4-space indentation), '
        'the first program and variables with data types.'
    ),
    'order': 2,
    'xp_reward': 400,
    'reference': ref(UNIT, '3.3-3.4 IDE and Fundamentals of Python Programming', '94-101', CLASS),
    'lessons': [
        # ── 3.3 ────────────────────────────────────────────────────────────
        {
            'slug': 'what-is-an-ide',
            'title': 'What Is an IDE?',
            'content_type': 'text',
            'learning_objective': (
                'Define an IDE and name its five key features from section 3.3.'
            ),
            'order': 1,
            'duration_minutes': 7,
            'xp_reward': 35,
            'reference': ref(UNIT, '3.3 Integrated Development Environment (IDE)', '94', CLASS),
            'content_body': '''# What Is an IDE?

An **IDE (Integrated Development Environment)** is a single application that
brings everything a programmer needs into one place. Section 3.3 (p. 94)
lists its key features:

| Feature | What it gives you |
|---|---|
| **Code Editor** | a place to write your program |
| **Syntax Highlighting** | colours keywords so code is easy to read |
| **Auto completion** | suggestions that complete your code as you type |
| **Run/Execute Tool** | starts the program with one click |
| **Debugger** | finds and fixes errors step by step |

The book then chooses one IDE for the whole course: **Visual Studio Code**
(3.3.1, p. 94) — a free code editor that becomes a full IDE once the Python
extensions are installed.
''',
            'exercises': [
                {
                    'slug': 'ide-feature-that-finds-errors',
                    'title': 'Which IDE Feature Finds Errors?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which key IDE feature is described as finding and '
                        'fixing errors in your program?'
                    ),
                    'explain': (
                        'The Debugger. The five key features of section 3.3 '
                        'are Code Editor, Syntax Highlighting, Auto '
                        'completion, Run/Execute Tool and Debugger. Sindh '
                        'Board Class XI, Unit 3, 3.3, p. 94.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Debugger', 'is_correct': True},
                        {'id': 'b', 'text': 'Code Editor', 'is_correct': False},
                        {'id': 'c', 'text': 'Syntax Highlighting', 'is_correct': False},
                        {'id': 'd', 'text': 'Auto completion', 'is_correct': False},
                    ],
                    'xp_reward': 30,
                    'order': 1,
                    'reference': ref(UNIT, '3.3 IDE key features', '94', CLASS),
                },
            ],
        },
        {
            'slug': 'visual-studio-code',
            'title': 'Visual Studio Code and Its Interface',
            'content_type': 'text',
            'learning_objective': (
                'Locate the parts of the VS Code window the book labels and '
                'name the recommended Python extensions.'
            ),
            'order': 2,
            'duration_minutes': 8,
            'xp_reward': 35,
            'reference': ref(UNIT, '3.3.1 Visual Studio Code — user interface', '94-99', CLASS),
            'content_body': '''# Visual Studio Code

Section 3.3.1 (p. 94) introduces **Visual Studio Code**: a free code editor
that becomes an IDE once you add extensions for your language. Figures 3.2
and 3.3 (pp. 95-99) walk through the window, part by part:

1. **Top Menus Bar** — File, Edit, Selection, View, Go, Run, Terminal, Help (p. 95).
2. **Start Section** — open a folder, clone a repository, get started (p. 95).
3. **Side Bar** — six views labelled a-f in the figures (pp. 95-98):
   - a) **Explorer** — your files and folders
   - b) **Search** — find across the project
   - c) **Source Control** — version control (p. 97)
   - d) **Run & Debug** (p. 97)
   - e) **Extensions** — where you install add-ons (p. 98)
   - f) **Manage Setting** — settings and preferences (p. 98)
4. **Search Bar** at the top of the window (p. 99).

In the Extensions view the book recommends three add-ons for this course
(p. 98): **Python**, **Prettier** (code formatting) and **Python Debugger**.

A Python file is saved with the **`.py`** extension — the book confirms this
again in its own fill-in-the-blank exercise (p. 137).
''',
            'exercises': [
                {
                    'slug': 'python-file-extension',
                    'title': 'The .py Extension',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which extension does a Python file use?'
                    ),
                    'explain': (
                        'Python files end in .py — one of the book\'s own '
                        'fill-in-the-blank answers. Sindh Board Class XI, '
                        'Unit 3, EXERCISE B, p. 137 (also 3.3.1, pp. 94-99).'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '.py', 'is_correct': True},
                        {'id': 'b', 'text': '.cpp', 'is_correct': False},
                        {'id': 'c', 'text': '.java', 'is_correct': False},
                        {'id': 'd', 'text': '.txt', 'is_correct': False},
                    ],
                    'xp_reward': 30,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE B (iv)', '137', CLASS),
                },
                {
                    'slug': 'recommended-extensions',
                    'title': 'Recommended VS Code Extensions',
                    'exercise_type': 'multiple_select',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Which extensions does section 3.3.1 recommend '
                        'installing for Python programming? Select all that '
                        'apply.'
                    ),
                    'explain': (
                        'The book recommends Python, Prettier and Python '
                        'Debugger in the Extensions view (p. 98). Pylance is '
                        'not among the extensions this section names. Sindh '
                        'Board Class XI, Unit 3, 3.3.1 (e), p. 98.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'Python', 'is_correct': True},
                        {'id': 'b', 'text': 'Prettier', 'is_correct': True},
                        {'id': 'c', 'text': 'Python Debugger', 'is_correct': True},
                        {'id': 'd', 'text': 'Pylance', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, '3.3.1 Extensions', '98', CLASS),
                },
            ],
        },

        # ── 3.4 ────────────────────────────────────────────────────────────
        {
            'slug': 'fundamentals-comments-indentation',
            'title': 'Python Fundamentals — Comments, Statements, Indentation',
            'content_type': 'interactive',
            'learning_objective': (
                'Read a Python program with comments and run SimpleProgram.py, '
                'and fix a program broken by bad indentation.'
            ),
            'order': 3,
            'duration_minutes': 12,
            'xp_reward': 50,
            'reference': ref(UNIT, '3.4 Fundamentals of Python Programming', '99-100', CLASS),
            'content_body': '''# Fundamentals of Python Programming

Section 3.4 (p. 99) lays down three rules before any program is written:

- **Comments** start with `#`. Python ignores everything on that line — use
  comments to explain what the code does.
- **Statements and expressions** are the instructions themselves; one
  instruction per line, run from top to bottom (p. 100).
- **Indentation is mandatory.** Blocks (loops, ifs) are built by indenting,
  and the book\'s standard is **4 spaces per level** (p. 99).

## SimpleProgram.py (Figure 3.11, p. 99)

This is the first real program in the textbook. Press **Run Code** below,
then hit **Try it yourself** and modify the messages:

```python
# SimpleProgram.py
print("Hello, World!")
print("Welcome to Python")
print(100)
```

**Expected output:**

```output
Hello, World!
Welcome to Python
100
```

Three statements, three lines of output, in the order written — the program
runs from top to bottom (p. 100). The `#` line produces nothing; it is there
for the human reader.

> **Common mistake:** mixing tabs and spaces, or indenting only when it
> "looks nice". Python counts the indentation itself — move a line and you
> move it into or out of a block.
''',
            'exercises': [
                {
                    'slug': 'simple-program-output',
                    'title': 'Predict SimpleProgram.py',
                    'exercise_type': 'output_prediction',
                    'language': 'python',
                    'difficulty': 'easy',
                    'instructions': (
                        'Read the program and type exactly what it prints. '
                        'Put each output line on its own line.'
                    ),
                    'context': (
                        '# SimpleProgram.py\n'
                        'print("Hello, World!")\n'
                        'print("Welcome to Python")\n'
                        'print(100)'
                    ),
                    'expected_output': 'Hello, World!\nWelcome to Python\n100',
                    'explain': (
                        'Statements run top to bottom (p. 100): three prints, '
                        'one line each; the comment is ignored. Sindh Board '
                        'Class XI, Unit 3, 3.4 (Figure 3.11), pp. 99-100.'
                    ),
                    'xp_reward': 50,
                    'order': 1,
                    'reference': ref(UNIT, '3.4 SimpleProgram.py (Figure 3.11)', '99-100', CLASS),
                    'hints': [
                        'Three print statements make three lines of output.',
                        'Solution: Hello, World!\nWelcome to Python\n100',
                    ],
                },
                {
                    'slug': 'fix-the-indentation',
                    'title': 'Fix the Indentation',
                    'exercise_type': 'debugging',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'The body of the `for` loop is not indented, so this '
                        'program is invalid. Indent it correctly so it adds '
                        '1, 2 and 3 and prints `6`.'
                    ),
                    'context': (
                        'Section 3.4 (p. 99) makes indentation mandatory, '
                        'with 4 spaces as the standard per level.'
                    ),
                    'constraints': 'Change the indentation only — do not alter the code itself.',
                    'expected_behavior': 'The fixed program prints: 6',
                    'explain': (
                        'Statements inside the `for` block must be indented '
                        '(4 spaces is the book standard, p. 99); the total '
                        'print stays outside the loop, so 1+2+3 = 6 is '
                        'printed once. Sindh Board Class XI, Unit 3, 3.4, '
                        'p. 99; the IndentationError appears again in 3.7, '
                        'p. 133.'
                    ),
                    'starter_code': (
                        'total = 0\n'
                        'for i in range(1, 4):\n'
                        'total = total + i\n'
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
                    'xp_reward': 90,
                    'order': 2,
                    'reference': ref(UNIT, '3.4 Indentation', '99', CLASS),
                    'hints': [
                        'The line after "for ... :" must be indented by 4 spaces.',
                        '"print(total)" stays at column 0 — it belongs outside the loop.',
                        'Solution: indent "total = total + i" with four spaces.',
                    ],
                },
                {
                    'slug': 'standard-indentation',
                    'title': 'The Standard Indentation',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'How many spaces per level does the textbook give as '
                        'the standard indentation?'
                    ),
                    'explain': (
                        '4 spaces per level (a single tab also counts); the '
                        'book\'s MCQ set asks the same. Sindh Board Class XI, '
                        'Unit 3, 3.4, p. 99; EXERCISE A (vii), p. 136.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '4 spaces', 'is_correct': True},
                        {'id': 'b', 'text': '2 spaces', 'is_correct': False},
                        {'id': 'c', 'text': '8 spaces', 'is_correct': False},
                        {'id': 'd', 'text': 'Indentation does not matter in Python', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 3,
                    'reference': ref(UNIT, 'EXERCISE A (vii)', '136', CLASS),
                },
            ],
        },

        # ── 3.4.1 ──────────────────────────────────────────────────────────
        {
            'slug': 'variables-and-data-types',
            'title': 'Variables and Data Types',
            'content_type': 'interactive',
            'learning_objective': (
                'Name variables that follow the book\'s rules and match the '
                'eight data types of the summary table to their examples.'
            ),
            'order': 4,
            'duration_minutes': 14,
            'xp_reward': 55,
            'reference': ref(UNIT, '3.4.1 Variables and Data Types', '100-101', CLASS),
            'content_body': '''# Variables and Data Types

A **variable is a named space of memory** that holds a value (p. 100). Python
needs no type declaration — the type is decided by the value you assign
(this is why the book calls it dynamic). Figure 3.12 shows four at once:

```python
name = "Ali"
age = 16
height = 5.7
is_student = True
```

## Naming rules (p. 100)

- Names may contain **letters, digits and underscores** `_`.
- A name must **start with a letter or an underscore** — never a digit.
- Names are **case-sensitive**: `Age` and `age` are different variables.
- **Avoid keywords** — words Python already owns, like `if`, `for`, `while`.

## The summary table (p. 101)

The table on p. 101 collects the types with one example each:

| Type | Example |
|---|---|
| `int` | `100` |
| `float` | `3.14` |
| `str` | `"hello"` |
| `bool` | `True` |
| `list` | `[1, 2, 3]` |
| `dict` | `{"name": "Ali", "age": 16}` |
| `tuple` | `(10, 20)` |
| `set` | `{1, 2, 3}` |

Figure 3.13 (p. 100) draws the same family as a tree: Numbers (int, float,
complex), Bool, Set, Dict, and Sequence (String, List, Tuple).

You can ask Python what type anything is with `type()`:

```python
age = 16
print(type(age))
```

**Expected output:**

```output
<class 'int'>
```
''',
            'exercises': [
                {
                    'slug': 'illegal-variable-name',
                    'title': 'Which Name Is Illegal?',
                    'exercise_type': 'multiple_choice',
                    'language': 'none',
                    'difficulty': 'easy',
                    'instructions': (
                        'Which of these is NOT a legal Python variable name?'
                    ),
                    'explain': (
                        'A name must start with a letter or underscore — '
                        '"2ndroll" starts with a digit, so it is illegal. '
                        'This mirrors the book\'s own MCQ on illegal names. '
                        'Sindh Board Class XI, Unit 3, 3.4.1, p. 100; '
                        'EXERCISE A (ii), p. 136.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': '2ndroll', 'is_correct': True},
                        {'id': 'b', 'text': 'my_score', 'is_correct': False},
                        {'id': 'c', 'text': 'total', 'is_correct': False},
                        {'id': 'd', 'text': '_temp', 'is_correct': False},
                    ],
                    'xp_reward': 40,
                    'order': 1,
                    'reference': ref(UNIT, 'EXERCISE A (ii)', '136', CLASS),
                },
                {
                    'slug': 'spot-the-valid-names',
                    'title': 'Spot the Valid Names',
                    'exercise_type': 'multiple_select',
                    'language': 'none',
                    'difficulty': 'medium',
                    'instructions': (
                        'Select every variable name below that follows the '
                        'book\'s naming rules.'
                    ),
                    'explain': (
                        'Letters, digits and underscores are allowed as long '
                        'as the first character is a letter or underscore and '
                        'the word is not a keyword: total, _count and rollNo2 '
                        'are valid. 3marks starts with a digit and if is a '
                        'keyword. Sindh Board Class XI, Unit 3, 3.4.1, p. 100.'
                    ),
                    'choices': [
                        {'id': 'a', 'text': 'total', 'is_correct': True},
                        {'id': 'b', 'text': '_count', 'is_correct': True},
                        {'id': 'c', 'text': 'rollNo2', 'is_correct': True},
                        {'id': 'd', 'text': '3marks', 'is_correct': False},
                        {'id': 'e', 'text': 'if', 'is_correct': False},
                    ],
                    'xp_reward': 50,
                    'order': 2,
                    'reference': ref(UNIT, '3.4.1 Variable naming rules', '100', CLASS),
                },
                {
                    'slug': 'what-type-is-it',
                    'title': 'Check the Types',
                    'exercise_type': 'code',
                    'language': 'python',
                    'difficulty': 'medium',
                    'instructions': (
                        'Create one value of each type — an `int`, a `float`, '
                        'a `str` and a `bool` — and print the type of each '
                        'with `type()`, one per line, in that order.'
                    ),
                    'context': (
                        'Section 3.4.1\'s summary table (p. 101) lists the '
                        'types; `type()` is the tool that confirms them.'
                    ),
                    'constraints': (
                        'Print four lines only. Any values of the right types '
                        'work — the grader checks the four type lines, not '
                        'the values.'
                    ),
                    'expected_behavior': (
                        'For int 5, float 2.5, str "hi" and bool True the '
                        'program prints <class \'int\'>, <class \'float\'>, '
                        '<class \'str\'>, <class \'bool\'> on four lines.'
                    ),
                    'explain': (
                        'type() returns the type of any value: whole numbers '
                        'are int, decimals are float, quoted text is str, and '
                        'True/False is bool — the first four rows of the '
                        'summary table. Sindh Board Class XI, Unit 3, 3.4.1, '
                        'pp. 100-101.'
                    ),
                    'starter_code': (
                        '# Create one value of each type, then print(type(...)) for each\n'
                        '\n'
                    ),
                    'solution_code': (
                        'a = 5\n'
                        'b = 2.5\n'
                        'c = "hi"\n'
                        'd = True\n'
                        'print(type(a))\n'
                        'print(type(b))\n'
                        'print(type(c))\n'
                        'print(type(d))\n'
                    ),
                    'test_cases': [
                        {
                            'input': '',
                            'expected_output': (
                                "<class 'int'>\n"
                                "<class 'float'>\n"
                                "<class 'str'>\n"
                                "<class 'bool'>"
                            ),
                        },
                    ],
                    'xp_reward': 100,
                    'order': 3,
                    'reference': ref(
                        UNIT, '3.4.1 Variables and Data Types', '100-101', CLASS,
                        source_type='supplementary',
                    ),
                    'hints': [
                        'int = whole number, float = decimal, str = quoted text, bool = True/False.',
                        'print(type(a)) shows the type of a.',
                        'Solution: a = 5; b = 2.5; c = "hi"; d = True; then print each type.',
                    ],
                },
            ],
        },
    ],
}
