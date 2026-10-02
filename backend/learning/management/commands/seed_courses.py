"""
Seed command for development data.

Usage:
    python manage.py seed_courses

Creates:
    - 1 Python course with 4 chapters
    - Multiple lessons per chapter
    - Exercises with hints per lesson
    - Resources
    - Achievements
"""

from django.core.management.base import BaseCommand
from learning.models import (
    CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Achievement,
)


class Command(BaseCommand):
    help = 'Seed the database with development course data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding course data...')

        # Create or get career track
        track, _ = CareerTrack.objects.get_or_create(
            slug='python',
            defaults={
                'title': 'Python',
                'description': 'Master Python from fundamentals to advanced concepts.',
                'difficulty': 'beginner',
                'estimated_hours': 40,
                'order': 1,
            }
        )

        # Create course
        course, course_created = Course.objects.get_or_create(
            slug='python-foundations',
            defaults={
                'title': 'Python Foundations',
                'subtitle': 'Build your first real programming foundation.',
                'description': 'Learn Python from scratch. Master variables, control flow, functions, and data structures through hands-on exercises.',
                'track': track,
                'difficulty': 'beginner',
                'language': 'python',
                'estimated_hours': 4,
                'total_xp': 3900,
                'instructor': 'Code Yaar',
                'prerequisites': 'None',
                'learning_objectives': [
                    'Variables and data types',
                    'Conditional logic',
                    'Loops and iteration',
                    'Functions and parameters',
                    'Lists and dictionaries',
                    'String manipulation',
                ],
                'is_free': True,
                'is_published': True,
                'order': 1,
            }
        )

        if not course_created:
            self.stdout.write(self.style.WARNING('Course already exists. Skipping.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))

        # ── Chapter 1: Python Basics ──────────────────────────────────────
        ch1 = Chapter.objects.create(
            course=course,
            title='Python Basics',
            slug='python-basics',
            description='Learn the fundamentals of Python programming.',
            order=1,
            xp_reward=500,
        )

        # Lesson 1.1: Hello Python
        l1_1 = Lesson.objects.create(
            chapter=ch1,
            title='Hello Python',
            slug='hello-python',
            content_type='text',
            learning_objective='Write and run your first Python program.',
            content_body='''# Welcome to Python!

Python is one of the most popular programming languages in the world. It's known for being readable, versatile, and powerful.

## Your First Program

In Python, you can display text using the `print()` function:

```python
print("Hello, World!")
```

The `print()` function takes a value and displays it on the screen.

## Strings

Text in Python is called a **string**. You can create strings using single or double quotes:

```python
print("Hello!")
print('Hello!')
```

Both work the same way.
''',
            order=1,
            duration_minutes=10,
            xp_reward=50,
        )

        Exercise.objects.create(
            lesson=l1_1,
            title='Print Hello World',
            slug='print-hello-world',
            exercise_type='code',
            instructions='Write a program that prints "Hello, World!" to the screen.',
            context='Every programmer starts here. The "Hello, World!" program is a tradition.',
            constraints='Use the print() function.',
            expected_behavior='The output should be: Hello, World!',
            difficulty='easy',
            language='python',
            starter_code='# Write your code below\n',
            solution_code='print("Hello, World!")',
            expected_output='Hello, World!',
            test_cases=[
                {'input': '', 'expected_output': 'Hello, World!'},
            ],
            xp_reward=100,
            order=1,
        )

        Hint.objects.create(
            exercise=Exercise.objects.get(slug='print-hello-world'),
            content='Use the print() function with a string argument.',
            order=1,
            xp_penalty=10,
        )
        Hint.objects.create(
            exercise=Exercise.objects.get(slug='print-hello-world'),
            content='The syntax is: print("your text here")',
            order=2,
            xp_penalty=20,
        )
        Hint.objects.create(
            exercise=Exercise.objects.get(slug='print-hello-world'),
            content='Solution: print("Hello, World!")',
            order=3,
            reveals_solution=True,
            xp_penalty=50,
        )

        # Lesson 1.2: Variables
        l1_2 = Lesson.objects.create(
            chapter=ch1,
            title='Variables',
            slug='variables',
            content_type='text',
            learning_objective='Create variables and assign values to them.',
            content_body='''# Variables

A variable is a name that refers to a value. You create a variable using the assignment operator `=`:

```python
name = "Alice"
age = 25
```

## Naming Rules

- Must start with a letter or underscore
- Can contain letters, numbers, and underscores
- Case-sensitive (`Name` and `name` are different)

## Reassigning Variables

You can change the value of a variable:

```python
score = 0
score = 100  # score is now 100
```
''',
            order=2,
            duration_minutes=15,
            xp_reward=50,
        )

        Exercise.objects.create(
            lesson=l1_2,
            title='Create a Variable',
            slug='create-variable',
            exercise_type='code',
            instructions='Create a variable named `score` and assign it the integer value 100.',
            context='Variables let you store and reuse values in your programs.',
            constraints='The variable must be named exactly `score`.',
            expected_behavior='The variable `score` should contain the value 100.',
            difficulty='easy',
            language='python',
            starter_code='# Create a variable named score with value 100\n',
            solution_code='score = 100',
            test_cases=[
                {'variable': 'score', 'expected_value': 100},
            ],
            xp_reward=100,
            order=1,
        )

        Exercise.objects.create(
            lesson=l1_2,
            title='Variable Types',
            slug='variable-types',
            exercise_type='multiple_choice',
            instructions='What type of value does the following expression produce?\n\n```python\ntype(42)\n```',
            difficulty='easy',
            language='python',
            choices=[
                {'id': 'a', 'text': 'str', 'is_correct': False},
                {'id': 'b', 'text': 'int', 'is_correct': True},
                {'id': 'c', 'text': 'float', 'is_correct': False},
                {'id': 'd', 'text': 'bool', 'is_correct': False},
            ],
            xp_reward=50,
            order=2,
        )

        # ── Chapter 2: Control Flow ───────────────────────────────────────
        ch2 = Chapter.objects.create(
            course=course,
            title='Control Flow',
            slug='control-flow',
            description='Learn how to make decisions and repeat actions in Python.',
            order=2,
            xp_reward=500,
        )

        l2_1 = Lesson.objects.create(
            chapter=ch2,
            title='Conditions',
            slug='conditions',
            content_type='text',
            learning_objective='Write if/elif/else statements to make decisions.',
            content_body='''# Conditional Statements

Use `if`, `elif`, and `else` to execute different code based on conditions:

```python
temperature = 30

if temperature > 25:
    print("It's hot!")
elif temperature > 15:
    print("Nice weather.")
else:
    print("It's cold!")
```

## Comparison Operators

- `==` equal to
- `!=` not equal
- `>` greater than
- `<` less than
- `>=` greater or equal
- `<=` less or equal
''',
            order=1,
            duration_minutes=15,
            xp_reward=50,
        )

        Exercise.objects.create(
            lesson=l2_1,
            title='Check Age',
            slug='check-age',
            exercise_type='code',
            instructions='Write a program that checks if the variable `age` is 18 or greater. If so, print "Adult". Otherwise, print "Minor".',
            context='Age verification is a common real-world use of conditionals.',
            difficulty='easy',
            language='python',
            starter_code='age = 20\n\n# Write your if/else statement below\n',
            solution_code='age = 20\n\nif age >= 18:\n    print("Adult")\nelse:\n    print("Minor")',
            expected_output='Adult',
            test_cases=[
                {'input': 'age = 20', 'expected_output': 'Adult'},
                {'input': 'age = 15', 'expected_output': 'Minor'},
            ],
            xp_reward=100,
            order=1,
        )

        l2_2 = Lesson.objects.create(
            chapter=ch2,
            title='Loops',
            slug='loops',
            content_type='text',
            learning_objective='Use for loops to iterate over sequences.',
            content_body='''# For Loops

A `for` loop lets you repeat code for each item in a sequence:

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)
```

## The range() Function

Use `range()` to loop a specific number of times:

```python
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4
```
''',
            order=2,
            duration_minutes=15,
            xp_reward=50,
        )

        Exercise.objects.create(
            lesson=l2_2,
            title='Predict the Output',
            slug='predict-loop-output',
            exercise_type='output_prediction',
            instructions='What will the following code print?\n\n```python\nfor i in range(3):\n    print(i * 2)\n```',
            difficulty='easy',
            language='python',
            expected_output='0\n2\n4',
            xp_reward=75,
            order=1,
        )

        # ── Chapter 3: Functions ──────────────────────────────────────────
        ch3 = Chapter.objects.create(
            course=course,
            title='Functions',
            slug='functions',
            description='Learn to organize your code into reusable blocks.',
            order=3,
            xp_reward=500,
        )

        l3_1 = Lesson.objects.create(
            chapter=ch3,
            title='Defining Functions',
            slug='defining-functions',
            content_type='text',
            learning_objective='Create and call your own functions.',
            content_body='''# Functions

Functions let you group code into reusable blocks:

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Alice")
print(message)  # Hello, Alice!
```

## Parameters and Return Values

- **Parameters** are inputs to a function
- **Return** sends a value back to the caller
''',
            order=1,
            duration_minutes=15,
            xp_reward=50,
        )

        Exercise.objects.create(
            lesson=l3_1,
            title='Write a Function',
            slug='write-function',
            exercise_type='code',
            instructions='Write a function called `double` that takes a number and returns that number multiplied by 2.',
            context='Functions are the building blocks of organized code.',
            difficulty='medium',
            language='python',
            starter_code='# Write your double function below\n',
            solution_code='def double(n):\n    return n * 2',
            test_cases=[
                {'input': 'double(5)', 'expected_output': '10'},
                {'input': 'double(0)', 'expected_output': '0'},
                {'input': 'double(-3)', 'expected_output': '-6'},
            ],
            xp_reward=150,
            order=1,
        )

        # ── Chapter 4: Data Structures ────────────────────────────────────
        ch4 = Chapter.objects.create(
            course=course,
            title='Data Structures',
            slug='data-structures',
            description='Master Python lists and dictionaries.',
            order=4,
            xp_reward=500,
        )

        l4_1 = Lesson.objects.create(
            chapter=ch4,
            title='Lists',
            slug='lists',
            content_type='text',
            learning_objective='Create, access, and modify lists.',
            content_body='''# Lists

A list is an ordered collection of values:

```python
colors = ["red", "green", "blue"]
```

## Accessing Elements

```python
first = colors[0]   # "red"
last = colors[-1]   # "blue"
```

## Modifying Lists

```python
colors.append("yellow")  # Add to end
colors.remove("green")   # Remove by value
```
''',
            order=1,
            duration_minutes=15,
            xp_reward=50,
        )

        Exercise.objects.create(
            lesson=l4_1,
            title='Debug This List',
            slug='debug-list',
            exercise_type='debugging',
            instructions='The code below has a bug. Fix it so that it prints the last element of the list.\n\n```python\nnumbers = [10, 20, 30, 40, 50]\nprint(numbers[5])\n```',
            context='Debugging is a critical skill. Learn to read error messages carefully.',
            difficulty='easy',
            language='python',
            starter_code='numbers = [10, 20, 30, 40, 50]\nprint(numbers[5])  # Fix this line\n',
            solution_code='numbers = [10, 20, 30, 40, 50]\nprint(numbers[4])',
            expected_output='50',
            xp_reward=100,
            order=1,
        )

        l4_2 = Lesson.objects.create(
            chapter=ch4,
            title='Dictionaries',
            slug='dictionaries',
            content_type='text',
            learning_objective='Use dictionaries to store key-value pairs.',
            content_body='''# Dictionaries

A dictionary stores key-value pairs:

```python
student = {
    "name": "Alice",
    "age": 25,
    "grade": "A"
}
```

## Accessing Values

```python
print(student["name"])  # Alice
```

## Adding/Updating

```python
student["email"] = "alice@example.com"
student["age"] = 26
```
''',
            order=2,
            duration_minutes=15,
            xp_reward=50,
        )

        Exercise.objects.create(
            lesson=l4_2,
            title='Fill in the Blank',
            slug='fill-dict',
            exercise_type='fill_blank',
            instructions='Complete the code to create a dictionary with keys "name" and "age".',
            context='Dictionaries are essential for structured data.',
            difficulty='easy',
            language='python',
            starter_code='person = ___("name": "Alice", ___: 25)',
            solution_code='person = {"name": "Alice", "age": 25}',
            xp_reward=100,
            order=1,
        )

        # ── Resources ─────────────────────────────────────────────────────
        Resource.objects.create(
            course=course,
            title='Python Cheat Sheet',
            description='Quick reference for Python syntax and common operations.',
            resource_type='cheat_sheet',
            file_url='/resources/python-cheat-sheet.pdf',
            order=1,
        )
        Resource.objects.create(
            course=course,
            title='Course Slides',
            description='All lecture slides for Python Foundations.',
            resource_type='slides',
            file_url='/resources/python-foundations-slides.pdf',
            order=2,
        )

        # ── Achievements ──────────────────────────────────────────────────
        Achievement.objects.get_or_create(
            slug='first-lesson',
            defaults={
                'title': 'First Steps',
                'description': 'Complete your first lesson.',
                'icon': 'trophy',
                'category': 'course',
                'xp_bonus': 50,
                'condition_type': 'lesson_complete',
                'condition_value': '1',
            }
        )
        Achievement.objects.get_or_create(
            slug='chapter-master',
            defaults={
                'title': 'Chapter Master',
                'description': 'Complete all lessons in a chapter.',
                'icon': 'star',
                'category': 'chapter',
                'xp_bonus': 200,
                'condition_type': 'chapter_complete',
            }
        )
        Achievement.objects.get_or_create(
            slug='streak-7',
            defaults={
                'title': 'Week Warrior',
                'description': 'Maintain a 7-day learning streak.',
                'icon': 'fire',
                'category': 'streak',
                'xp_bonus': 300,
                'condition_type': 'streak_7',
            }
        )
        Achievement.objects.get_or_create(
            slug='python-foundations-complete',
            defaults={
                'title': 'Python Graduate',
                'description': 'Complete the Python Foundations course.',
                'icon': 'graduation',
                'category': 'course',
                'xp_bonus': 500,
                'condition_type': 'course_complete',
                'condition_value': 'python-foundations',
            }
        )

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully seeded:\n'
            f'  - 1 Course: {course.title}\n'
            f'  - {course.chapters.count()} Chapters\n'
            f'  - {Lesson.objects.filter(chapter__course=course).count()} Lessons\n'
            f'  - {Exercise.objects.filter(lesson__chapter__course=course).count()} Exercises\n'
            f'  - {Resource.objects.filter(course=course).count()} Resources\n'
            f'  - {Achievement.objects.count()} Achievements\n'
        ))
