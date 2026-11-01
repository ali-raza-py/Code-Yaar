"""Course 2 — C++ Programming Fundamentals.

Introduces compiled programming: logic, syntax and console I/O. The live
sandbox currently executes Python only, so C++ knowledge checks are graded
honestly as answer comparison (multiple choice / output prediction / fill in
the blank) — the platform does NOT claim that student C++ is compiled or run.
"""

COURSE = {
    'slug': 'cpp-fundamentals',
    'title': 'C++ Programming Fundamentals',
    'subtitle': 'Learn compiled programming through clear, structured C++.',
    'description': (
        'Understand how compiled programs work and write well-structured C++: '
        'the main function, variables and types, console I/O, conditions, loops, '
        'functions and arrays. Note: this course teaches C++ syntax and '
        'reasoning; assessment answers are checked by the server, and C++ code '
        'is not executed by the current sandbox.'
    ),
    'difficulty': 'beginner',
    'language': 'cpp',
    'prerequisites': 'Basic programming logic (Python course recommended first).',
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
        'Describe the structure of a basic C++ program.',
        'Use variables, data types, operators and console I/O.',
        'Implement conditional logic and loops.',
        'Work with functions and arrays.',
        'Compile-and-run concepts and common error types.',
    ],
    'modules': [
        {
            'title': 'Program Structure',
            'slug': 'program-structure',
            'description': 'How C++ programs are built and run.',
            'lessons': [
                {
                    'title': 'Compiled Programs and main()',
                    'slug': 'hello-structure',
                    'objective': 'Identify the parts of a minimal C++ program.',
                    'duration': 12,
                    'body': (
                        '# From source to executable\n\n'
                        'C++ is **compiled**: a compiler translates your `.cpp` source into a '
                        'machine executable before it runs. This differs from Python, which is '
                        'interpreted line by line.\n\n'
                        'A minimal program:\n\n'
                        '```cpp\n#include <iostream>\nusing namespace std;\n\n'
                        'int main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}\n```\n\n'
                        'Expected output:\n\n```\nHello, World!\n```\n\n'
                        '- `#include <iostream>` brings in the input/output library.\n'
                        '- `main()` is where execution starts; `return 0` signals success.\n'
                        '- `cout` writes to the console; `endl` ends the line.\n\n'
                        '## Common mistakes\n'
                        'Forgetting the semicolon after a statement, or omitting `return 0;`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'cpp-entry-point',
                            'title': 'Where does execution start?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which function is the entry point of a C++ program?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'start()', 'is_correct': False},
                                {'id': 'b', 'text': 'main()', 'is_correct': True},
                                {'id': 'c', 'text': 'run()', 'is_correct': False},
                                {'id': 'd', 'text': 'include()', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'cpp-header',
                            'title': 'Console I/O header',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the line that lets a program use cout and cin:\n\n'
                                '```cpp\n#include ______\n```'
                            ),
                            'starter_code': '#include ',
                            'solution_code': '#include <iostream>',
                            'explain': '<iostream> declares the standard input/output streams.',
                            'xp_reward': 50,
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Variables and Input',
            'slug': 'variables-input',
            'description': 'Declare typed variables and read console input.',
            'lessons': [
                {
                    'title': 'Types, Constants and cin',
                    'slug': 'types-input',
                    'objective': 'Declare int, double, char and read a value with cin.',
                    'duration': 14,
                    'body': (
                        '# Typed variables\n\n'
                        'C++ requires you to state a variable\'s type.\n\n'
                        '```cpp\nint age = 20;          // whole number\ndouble price = 3.99;   // decimal\n'
                        'char grade = \'A\';      // single character\nconst double PI = 3.14159; // constant\n```\n\n'
                        '## Reading input\n\n'
                        '```cpp\nint n;\ncin >> n;      // wait for the user to type a number\ncout << n * 2 << endl;\n```\n\n'
                        '## Common mistakes\n'
                        '- Changing a `const` value later is a compile error.\n'
                        '- `3.99` stored in an `int` truncates to `3`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'which-type',
                            'title': 'Choose the type',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which type best stores the value 3.14?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'int', 'is_correct': False},
                                {'id': 'b', 'text': 'char', 'is_correct': False},
                                {'id': 'c', 'text': 'double', 'is_correct': True},
                                {'id': 'd', 'text': 'bool', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'cpp-input-op',
                            'title': 'Reading input operator',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which operator reads a value from the console into a variable?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'cin >> x', 'is_correct': True},
                                {'id': 'b', 'text': 'cout << x', 'is_correct': False},
                                {'id': 'c', 'text': 'scanf(x)', 'is_correct': False},
                                {'id': 'd', 'text': 'read(x)', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Conditions',
            'slug': 'conditions',
            'description': 'Branch with if/else and switch.',
            'lessons': [
                {
                    'title': 'if / else if / switch',
                    'slug': 'branching',
                    'objective': 'Write multi-branch decisions in C++.',
                    'duration': 12,
                    'body': (
                        '# Branching\n\n'
                        '```cpp\nint score = 82;\nif (score >= 90) {\n    cout << "A";\n}\n'
                        'else if (score >= 80) {\n    cout << "B";\n}\nelse {\n    cout << "C";\n}\n```\n\n'
                        'Output: `B`.\n\n'
                        '## switch\n\n'
                        '```cpp\nint day = 3;\nswitch (day) {\n    case 1: cout << "Mon"; break;\n    case 3: cout << "Wed"; break;\n}\n```\n\n'
                        '`break` stops fall-through to the next case.\n\n'
                        '## Common mistakes\n'
                        'Omitting `break` in a switch causes the following cases to also run.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'greatest',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'What is printed?\n\n```cpp\nint a = 5, b = 9;\n'
                                'cout << (a > b ? a : b);\n```'
                            ),
                            'expected_output': '9',
                            'explain': 'The ternary picks the larger value; 9 is greater than 5.',
                            'xp_reward': 60,
                        },
                        {
                            'slug': 'switch-break',
                            'title': 'Role of break',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In a switch statement, what does `break` do?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Ends the whole program', 'is_correct': False},
                                {'id': 'b', 'text': 'Prevents fall-through into the next case', 'is_correct': True},
                                {'id': 'c', 'text': 'Restarts the switch', 'is_correct': False},
                                {'id': 'd', 'text': 'Nothing', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Loops',
            'slug': 'loops',
            'description': 'Repeat work with for and while.',
            'lessons': [
                {
                    'title': 'for and while',
                    'slug': 'iteration',
                    'objective': 'Accumulate values and count with loops.',
                    'duration': 12,
                    'body': (
                        '# Loops\n\n'
                        '```cpp\nint sum = 0;\nfor (int i = 1; i <= 5; i++) {\n    sum += i;\n}\ncout << sum;   // 15\n```\n\n'
                        'A `for` loop header has three parts: **init; condition; update**.\n\n'
                        '```cpp\nint n = 3;\nwhile (n > 0) {\n    cout << n;\n    n--;\n}   // 321\n```\n\n'
                        '## Common mistakes\n'
                        'An update step that never changes the condition produces an infinite loop.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'cpp-loop-sum',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'What is printed?\n\n```cpp\nint s = 0;\nfor (int i = 0; i < 4; i++) {\n'
                                '    s += i;\n}\ncout << s;\n```'
                            ),
                            'expected_output': '6',
                            'explain': 'i runs 0,1,2,3; the sum is 6.',
                            'xp_reward': 60,
                        }
                    ],
                },
            ],
        },
        {
            'title': 'Functions and Arrays',
            'slug': 'functions-arrays',
            'description': 'Reusable functions and simple arrays.',
            'lessons': [
                {
                    'title': 'Functions and Arrays',
                    'slug': 'fn-arrays',
                    'objective': 'Declare a function and traverse an array.',
                    'duration': 14,
                    'body': (
                        '# Functions\n\n'
                        '```cpp\nint add(int a, int b) {\n    return a + b;\n}\nint main() {\n    cout << add(2, 3);   // 5\n}\n```\n\n'
                        'The **return type** (`int`) and **parameters** must be declared.\n\n'
                        '# Arrays\n\n'
                        '```cpp\nint nums[3] = {10, 20, 30};\ncout << nums[0];   // 10\n```\n\n'
                        'Array indexes start at 0 and are fixed in size.\n\n'
                        '## Common mistakes\n'
                        'Reading past the last index (`nums[3]` here) is undefined behaviour.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'array-first',
                            'title': 'First element index',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which index refers to the first element of a C++ array?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '0', 'is_correct': True},
                                {'id': 'b', 'text': '1', 'is_correct': False},
                                {'id': 'c', 'text': '-1', 'is_correct': False},
                                {'id': 'd', 'text': 'size', 'is_correct': False},
                            ],
                        }
                    ],
                },
            ],
        },
        {
            'title': 'Debugging and Practice',
            'slug': 'debugging',
            'description': 'Recognise the three kinds of C++ errors.',
            'lessons': [
                {
                    'title': 'Syntax, Runtime and Logic Errors',
                    'slug': 'error-kinds',
                    'objective': 'Classify common C++ problems.',
                    'duration': 10,
                    'body': (
                        '# Three error families\n\n'
                        '- **Syntax error** — the compiler refuses to build (missing `;`, `}`).\n'
                        '- **Runtime error** — it builds but crashes while running (bad memory).\n'
                        '- **Logic error** — it runs but gives the wrong answer (off-by-one).\n\n'
                        'Logic errors are the hardest because nothing announces them; you find '
                        'them by tracing values and testing edge cases.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'missing-semicolon',
                            'title': 'Classify the error',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A missing semicolon stops the build. What kind of error is it?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Logic error', 'is_correct': False},
                                {'id': 'b', 'text': 'Runtime error', 'is_correct': False},
                                {'id': 'c', 'text': 'Syntax (compile) error', 'is_correct': True},
                                {'id': 'd', 'text': 'Warning only', 'is_correct': False},
                            ],
                        }
                    ],
                },
            ],
        },
    ],
    'assessment': [
        {
            'slug': 'cpp-final-include',
            'title': 'I/O header',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which header is used for console output in C++?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': '<stdio>', 'is_correct': False},
                {'id': 'b', 'text': '<iostream>', 'is_correct': True},
                {'id': 'c', 'text': '<console>', 'is_correct': False},
                {'id': 'd', 'text': 'iostream.h', 'is_correct': False},
            ],
        },
        {
            'slug': 'cpp-final-output',
            'title': 'Output operator',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which statement prints 5 to the console?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'cout << 5;', 'is_correct': True},
                {'id': 'b', 'text': 'cin >> 5;', 'is_correct': False},
                {'id': 'c', 'text': 'print(5);', 'is_correct': False},
                {'id': 'd', 'text': 'echo 5;', 'is_correct': False},
            ],
        },
        {
            'slug': 'cpp-final-loop',
            'title': 'Predict the output',
            'exercise_type': 'output_prediction',
            'instructions': 'What is printed?\n\n```cpp\nfor (int i = 1; i <= 3; i++) cout << i;\n```',
            'expected_output': '123',
            'xp_reward': 20,
        },
        {
            'slug': 'cpp-final-ternary',
            'title': 'Ternary result',
            'exercise_type': 'output_prediction',
            'instructions': 'What is printed?\n\n```cpp\ncout << (10 % 3);\n```',
            'expected_output': '1',
            'xp_reward': 20,
        },
        {
            'slug': 'cpp-final-const',
            'title': 'Constant keyword',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which keyword makes a variable read-only?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'final', 'is_correct': False},
                {'id': 'b', 'text': 'const', 'is_correct': True},
                {'id': 'c', 'text': 'static', 'is_correct': False},
                {'id': 'd', 'text': 'readonly', 'is_correct': False},
            ],
        },
    ],
}
