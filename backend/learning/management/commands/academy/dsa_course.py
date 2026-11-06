"""Course 5 — Data Structures & Algorithms.

Eleven chapters from "what is a data structure" to implementing the core
structures and algorithms every CS course and interview expects, closing
with a Student Records Management project. Implementations are shown in
Python (executed and graded by the real server-side sandbox) with parallel
C++ versions, dry-run tables and complexity analysis for every major
algorithm. Multiple-choice and answer-graded items check the C++ reading
without pretending to compile it.
"""

COURSE = {
    'slug': 'problem-solving-dsa',
    'title': 'Data Structures & Algorithms',
    'subtitle': 'Measure the cost, choose the structure, implement the algorithm.',
    'description': (
        'A structured introduction to the core of computer science: how to '
        'analyse the time and space cost of a solution, and how to build and '
        'use arrays, strings, linked lists, stacks, queues, hash tables, '
        'trees and graphs, plus the searching, sorting and problem-solving '
        'techniques that run on them. Every algorithm is explained in plain '
        'language first, implemented in Python (graded by the real sandbox) '
        'and shown again in C++ with dry-run tables, so you can read and '
        'reason about both.'
    ),
    'difficulty': 'intermediate',
    'language': 'python',
    'prerequisites': (
        'Basic C++ or Python: variables, loops, conditionals and functions. '
        'The Python Foundations or C++ Fundamentals course on Code Yaar '
        'prepares you fully.'
    ),
    'track': {
        'slug': 'cs-fundamentals',
        'title': 'Computer Science Fundamentals',
        'category': 'programming',
        'description': (
            'The theory every programmer leans on: how to organise data, '
            'how to process it efficiently, and how computers talk to each '
            'other and store what they know.'
        ),
    },
    'objectives': [
        'Analytic thinking: state inputs, outputs and edge cases before coding.',
        'Compute time and space complexity with Big-O and compare two solutions.',
        'Implement and traverse arrays, strings and the two-pointer technique.',
        'Build singly and doubly linked lists and explain their trade-offs.',
        'Use stacks and queues to model real problems (undo, balancing, scheduling).',
        'Implement linear and binary search, and the classic sorts, with analysis.',
        'Construct and traverse binary trees and BSTs; insert and search them.',
        'Explain hashing, collisions, and BFS/DFS graph traversal.',
        'Recognise when recursion, divide & conquer, greedy or DP fits a problem.',
        'Design a Student Records system choosing structures by required operations.',
    ],
    'certification': {'passing_score': 70},
    'modules': [
        # ════════════════════ Chapter 1 ════════════════════
        {
            'title': 'Introduction to DSA',
            'slug': 'intro-dsa',
            'description': 'What data structures and algorithms are, why they matter, and the ADT lens.',
            'lessons': [
                {
                    'title': 'Data Structures and Algorithms — the Two Halves',
                    'slug': 'what-are-ds-algos',
                    'objective': 'Define data structures, algorithms, and their relationship.',
                    'duration': 10,
                    'body': """# The pair that makes software work

An **algorithm** is a finite, unambiguous sequence of steps that turns an
input into a desired output. A recipe is the analogy that never fails:
ingredients (input), steps (procedure), dish (output) — and the steps must
be precise enough that any cook can follow them.

A **data structure** is an organised collection of data designed so that
certain operations on it are efficient. A timetable, a dictionary, a
stack of plates — organisation exists to make *finding, adding, removing
or processing* easier.

The relationship, famously: **programs = data structures + algorithms**.
Algorithms act on structures; the structure you choose changes which
algorithms are cheap. Searching a name:

- In an unordered pile of 1,000 pages → check each page: up to 1,000 looks.
- In an alphabetical phone book → halve the search space each look: about 10.

Same algorithm idea ("find the name"), wildly different cost, because the
**organisation of the data** changed the work each step requires.

## What this course builds
For each major structure — arrays, linked lists, stacks, queues, hash
tables, trees, graphs — you will learn:

1. **What it is** and the real problems it models.
2. **What operations it supports** (insert, delete, search, traverse)
   and how you write them.
3. **How much each operation costs** (chapter 2 gives the language).
4. **When to choose it** over the alternatives.

Plus the classic algorithm families: searching, sorting, recursion and the
design strategies built on them.

## Important terminology
- **ADT (Abstract Data Type):** the *contract* — what operations exist and
  what they guarantee, ignoring how they are built. "A list supports
  append, get-by-index and length" is a contract.
- **Data structure (implementation):** the actual code and memory that
  honours a contract. Python's `list` and a C++ `std::vector` both
  implement the dynamic-array ADT.

Thinking in ADTs first is what lets you move between languages: the ideas
do not change, only the syntax does.

## Real-world application
A delivery app keeps "pending orders" both as a queue (first order paid
is first order dispatched) and a hash table keyed by order-ID (customer
support jumps straight to any order). Same data, two structures, because
two different teams ask two different questions of it.

## Common mistakes
- Believing DSA is competitive-programming trivia. It is daily work: every
  API, database index and spreadsheet is a structure with a cost profile.
- Memorising code before understanding the operations it supports. Names
  and languages change; the contracts do not.

## Lesson summary
Algorithms are precise step-recipes; data structures are organised
containers; cost analysis (next chapter) is the language that says which
pairing is the right one for your problem.""",
                    'exercises': [
                        {
                            'slug': 'algorithm-definition',
                            'title': 'What makes a recipe an algorithm',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which property must every algorithm have?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'It must run in under one second', 'is_correct': False},
                                {'id': 'b', 'text': 'Unambiguous steps that terminate on a valid output', 'is_correct': True},
                                {'id': 'c', 'text': 'It must use recursion', 'is_correct': False},
                                {'id': 'd', 'text': 'It must be written in Python or C++', 'is_correct': False},
                            ],
                            'explain': 'Finiteness, definiteness (no ambiguity), input/output and effectiveness define an algorithm — speed and language do not.',
                        },
                        {
                            'slug': 'adt-vs-structure',
                            'title': 'Contract versus implementation',
                            'exercise_type': 'multiple_choice',
                            'instructions': '“A stack supports push, pop and peek; pop returns the most recent item” is a description of…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'One specific implementation in C++', 'is_correct': False},
                                {'id': 'b', 'text': 'An abstract data type — the contract any implementation must honour', 'is_correct': True},
                                {'id': 'c', 'text': 'A time-complexity claim', 'is_correct': False},
                                {'id': 'd', 'text': 'An algorithm', 'is_correct': False},
                            ],
                            'explain': 'The ADT names the operations and guarantees; arrays or linked lists can each implement that contract.',
                        },
                        {
                            'slug': 'structure-change-cost',
                            'title': 'Why organisation matters',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Finding a name is ~1000 comparisons in an unordered pile but ~10 in a sorted phone book. This shows…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Phone books use better programs', 'is_correct': False},
                                {'id': 'b', 'text': 'How data is organised changes the work each algorithm step must do', 'is_correct': True},
                                {'id': 'c', 'text': 'Sorting data is pointless', 'is_correct': False},
                                {'id': 'd', 'text': 'Humans search faster than computers', 'is_correct': False},
                            ],
                            'explain': 'The same goal — find the name — costs different work on differently organised data. That is the core DSA insight.',
                        },
                    ],
                },
                {
                    'title': 'Why DSA Matters and the Problem-Solving Method',
                    'slug': 'why-and-method',
                    'objective': 'Apply a four-step method to an unfamiliar problem before coding.',
                    'duration': 12,
                    'body': """# Why this subject pays for itself

**Correctness is table stakes; efficiency is the grade.** Two programs can
both be right, yet one finishes in a blink and the other in a century.
Scale is the multiplier: a 2-second-per-task inefficiency is annoying on
100 records and catastrophic on 100 million. Every large system you use —
search, maps, social feeds — is large-scale DSA engineering; when
Instagram's feed got slow, the fix was data-structure work, not new
hardware alone.

Interviews test it because it is the common denominator of all software
work: you will be asked to design a feature, then asked "what does it
cost?" — both are DSA questions.

**Job and exam reality in Pakistan and abroad:** every serious software
interview (service companies, product firms, NTS/GCAT CS sections,
university CS courses) is built on exactly the chapter list of this course.

## The four-step problem-solving method
Used in every chapter from now on:

1. **Understand.** Restate the problem in your own words. List inputs,
   outputs, and constraints. Hunt edge cases: empty? one item? all the
   same? negatives? duplicates? huge size?
2. **Plan.** Decide the data structures and the approach *in words or
   pseudocode*. Sketch a dry run on a tiny example by hand.
3. **Implement.** Write it in small pieces; test each piece.
4. **Review.** Re-check edge cases, then measure the cost (next chapter)
   and ask whether a cheaper pairing exists.

## Worked example of step 1 — "find the largest number in a list"
Inputs: a list of numbers. Output: one number (or none if empty).
Edge cases: empty list (what should happen? — *decide and state it*),
single element, all negatives (the accumulator must not start at 0!).

## Worked example of step 2 — "is a word a palindrome?"
Word plan: compare first with last, second with second-last… stop when
pointers meet. Two pointers. That plan becomes code in a chapter 3
exercise — the plan was language-free; the implementation could be Python
*or* C++.

## The habit that separates good solutions
Beginners jump into code; practitioners spend most effort in Understand +
Plan. When the plan is right, implementation is translation.

## Common mistakes
- Coding before listing edge cases, then "fixing" surprises forever.
- Solving without ever asking the cost question.
- Copying a solution without re-running the four steps on a new problem —
  the method, not the answer, is the skill.

## Lesson summary
DSA pays off through scale, interviews and cleaner design. The
four-step method — Understand, Plan, Implement, Review — is the repeatable
process this course drills on every problem.""",
                    'exercises': [
                        {
                            'slug': 'method-order',
                            'title': 'The first two steps',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL activities that belong to the Understand and Plan steps (before real code).',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Listing edge cases: empty input, duplicates, negatives', 'is_correct': True},
                                {'id': 'b', 'text': 'Choosing data structures and writing pseudocode', 'is_correct': True},
                                {'id': 'c', 'text': 'Dry-running the approach by hand on a tiny example', 'is_correct': True},
                                {'id': 'd', 'text': 'Optimising loop unrolling in the final binary', 'is_correct': False},
                            ],
                            'explain': 'Understand and Plan are language-free thinking: cases, structures, approach, hand-trace. Micro-optimisation belongs (if at all) to Review.',
                        },
                        {
                            'slug': 'why-efficiency',
                            'title': 'The scale argument',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why does algorithmic efficiency matter more as data grows?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Because a per-item disadvantage is multiplied by the number of items', 'is_correct': True},
                                {'id': 'b', 'text': 'Because computers slow down with age', 'is_correct': False},
                                {'id': 'c', 'text': 'Because big inputs force bugs', 'is_correct': False},
                                {'id': 'd', 'text': 'Efficiency does not change with size', 'is_correct': False},
                            ],
                            'explain': 'Costs are per-operation × operations. Scale is the second factor, and it is the one that explodes.',
                        },
                        {
                            'slug': 'edge-cases-value',
                            'title': 'Accumulator seeding',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'In Python: max_seen = 0, then loop through [-5, -2, -9] '
                                'updating max_seen only when a value is greater. What '
                                'single number does max_seen hold at the end? (Type it '
                                'exactly.)'
                            ),
                            'xp_reward': 60,
                            'expected_output': '0',
                            'explain': 'No negative beats 0, so the wrong seed wins: the true maximum is -2. This is the classic edge-case trap step 1 exists to catch.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 1 Quiz',
                    'slug': 'intro-dsa-quiz',
                    'objective': 'Check the foundational vocabulary and method.',
                    'duration': 4,
                    'body': """# Chapter 1 quiz

Five questions on structures, algorithms, ADTs and the method.""",
                    'exercises': [
                        {
                            'slug': 'q1-finiteness',
                            'title': 'Termination requirement',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A step-by-step procedure that may never end is NOT an algorithm because it lacks…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Finiteness', 'is_correct': True},
                                {'id': 'b', 'text': 'Recursion', 'is_correct': False},
                                {'id': 'c', 'text': 'A GUI', 'is_correct': False},
                                {'id': 'd', 'text': 'Variables', 'is_correct': False},
                            ],
                            'explain': 'An algorithm must terminate after finitely many steps for every valid input.',
                        },
                        {
                            'slug': 'q1-stack-adt',
                            'title': 'Naming the contract',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The list of operations and guarantees of a “list” — append, get, length — without any code, is called…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'An abstract data type', 'is_correct': True},
                                {'id': 'b', 'text': 'A compiler', 'is_correct': False},
                                {'id': 'c', 'text': 'A dry run', 'is_correct': False},
                                {'id': 'd', 'text': 'A hash map', 'is_correct': False},
                            ],
                            'explain': 'ADT = behaviour contract. Python list, C++ vector and arrays are implementations.',
                        },
                        {
                            'slug': 'q1-program-equals',
                            'title': 'The classic equation',
                            'exercise_type': 'multiple_choice',
                            'instructions': '“Programs = ___ + algorithms.”',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'data structures', 'is_correct': True},
                                {'id': 'b', 'text': 'compilers', 'is_correct': False},
                                {'id': 'c', 'text': 'recursion', 'is_correct': False},
                                {'id': 'd', 'text': 'variables', 'is_correct': False},
                            ],
                            'explain': 'Niklaus Wirth’s famous formulation — the two halves of every program.',
                        },
                        {
                            'slug': 'q1-edge-case-hunting',
                            'title': 'Method order',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In the four-step method, hunting for edge cases happens…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'During Understand, before planning', 'is_correct': True},
                                {'id': 'b', 'text': 'Only after the program ships', 'is_correct': False},
                                {'id': 'c', 'text': 'Inside the compiler', 'is_correct': False},
                                {'id': 'd', 'text': 'Never — inputs are always well-formed', 'is_correct': False},
                            ],
                            'explain': 'Edge cases shape the plan; discovering them in production is how outages happen.',
                        },
                        {
                            'slug': 'q1-skill-transfer',
                            'title': 'Language independence',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why does learning DSA make you productive in a NEW programming language faster?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'DSA syntax is identical across languages', 'is_correct': False},
                                {'id': 'b', 'text': 'The structures, contracts and cost reasoning transfer; only syntax changes', 'is_correct': True},
                                {'id': 'c', 'text': 'All languages compile the same', 'is_correct': False},
                                {'id': 'd', 'text': 'DSA replaces learning syntax', 'is_correct': False},
                            ],
                            'explain': 'A queue is a queue in Python, C++ or Java; you are re-learning names, not ideas.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 2 ════════════════════
        {
            'title': 'Time and Space Complexity',
            'slug': 'complexity',
            'description': 'Big-O as a comparison language: the common classes, best/average/worst, and memory cost.',
            'lessons': [
                {
                    'title': 'Big-O: Comparing Growth, Not Timing Runs',
                    'slug': 'big-o-intro',
                    'objective': 'State the Big-O class of simple loops and explain why we ignore constants.',
                    'duration': 14,
                    'body': """# Measuring an algorithm without a stopwatch

Wall-clock time depends on the machine, the language, even the phase of
the moon. What actually matters is **how the work grows as the input
grows**. Big-O notation names that growth.

## The idea in one sentence
Big-O describes the **dominant term** of the operation count as the input
size n gets large, dropping constants and smaller terms.

## Why constants vanish
An algorithm that does 5n steps and one that does 100n steps are both
**O(n)** — because when n doubles, *both* double; when n becomes a
million, the 20× gap in front never changes which one wins long-term.
We keep only the part that matters at scale. (In practice the constant
matters sometimes — Big-O is a map, not the territory; but it is the
right first question.)

## Counting steps from code — the loop rules
```python
for i in range(n):        # n times
    x = i * 2             # constant work each time
```
→ **O(n)**. One loop over the data: linear.

```python
for i in range(n):        # n times
    for j in range(n):    # n times each
        total += 1
```
→ **O(n²)**. Nested full loops: n × n — quadratic.

```python
while n > 1:              # n → n/2 → n/4 → … → 1
    n //= 2
```
→ **O(log n)**. Halving each step: logarithmic — 30 steps for a billion.

```python
a = arr[0]; print(sum_of_two)   # no dependence on n at all
```
→ **O(1)**. Constant.

## The ladder, from best to worst
| Class | Name | n = 1,000,000 feel |
|---|---|---|
| O(1) | constant | instant |
| O(log n) | logarithmic | ~20 steps |
| O(n) | linear | a second |
| O(n log n) | linearithmic | seconds — the sorting floor |
| O(n²) | quadratic | minutes to hours |
| O(2ⁿ) | exponential | heat death of the universe |

Every doubling of n: O(n) work doubles; O(n²) quadruples; O(2ⁿ) doubles
*the exponent*. That comparison — how fast the curve itself accelerates —
is what "order of growth" means.

## A worked dry-run count
For the sum of a list, count operations on n = 4: `total = 0` (1),
loop body ×4 (assignments/adds ≈ 4–8), `return` (1) → ≈ 6–10 steps.
For n = 4,000,000 → ≈ 8,000,000 steps. Ratio grows 1:1 → linear,
therefore **O(n)**. The table form (each line of code × how many times it
runs × cost per run) is exactly how you analyse any snippet — write it
out on exams.

## Important notes
- Worst case is the default promise in engineering: "this search is
  O(n)" means *no input makes it worse than linear*.
- Big-O is an upper bound; Θ (Theta) says "exactly this growth". Casual
  usage calls both "Big-O" — fine here, just know the difference.

## Common mistakes
- Saying "O(n²) is always slower than O(n)". For n = 3 the quadratic one
  may finish first; the claim is about growth, not small inputs.
- Counting loop iterations but ignoring the *work inside* the loop
  (calling `len()` is O(1) in Python but O(n) in some languages).
- Confusing "fast code" with "good Big-O": a constant-factor-heavy O(n)
  beats a clever O(n log n) only at small scale — know which regime you
  are in.

## Lesson summary
Big-O = dominant-term growth comparison with constants dropped. Count:
iterations × work per iteration. Ladder 1 < log n < n < n log n < n² <
2ⁿ. It answers "what happens when the data gets big?".""",
                    'exercises': [
                        {
                            'slug': 'nested-loop-class',
                            'title': 'Nested full loops',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A loop of n iterations, each running an inner loop of n iterations with O(1) work inside — the class is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(n)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n log n)', 'is_correct': False},
                                {'id': 'c', 'text': 'O(n²)', 'is_correct': True},
                                {'id': 'd', 'text': 'O(2n)', 'is_correct': False},
                            ],
                            'explain': 'n × n = n² iterations dominate. (O(2n) would just be O(n) anyway — constants drop.)',
                        },
                        {
                            'slug': 'halving-loop',
                            'title': 'Halving loop',
                            'exercise_type': 'multiple_choice',
                            'instructions': '`while n > 1: n //= 2` runs how many times, in Big-O of the starting n?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(n)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(log n)', 'is_correct': True},
                                {'id': 'c', 'text': 'O(1)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n/2)', 'is_correct': False},
                            ],
                            'explain': 'Each step halves: you can only halve log₂(n) times before reaching 1. 1,000,000 halves in ~20 steps.',
                        },
                        {
                            'slug': 'constant-drop-reason',
                            'title': 'Why drop the 100×?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Big-O treats 5n and 100n both as O(n) because…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'constants are impossible to count', 'is_correct': False},
                                {'id': 'b', 'text': 'as n grows, what matters is how work scales with n, not the fixed multiplier', 'is_correct': True},
                                {'id': 'c', 'text': '100 is smaller than n', 'is_correct': False},
                                {'id': 'd', 'text': 'the CPU handles big constants better', 'is_correct': False},
                            ],
                            'explain': 'Doubling n doubles BOTH; the ratio 100:5 never changes the scaling *class*. (At small n, constants do matter — know the regime.)',
                        },
                        {
                            'slug': 'which-beows-at-scale',
                            'title': 'Growth winner',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'For very large n, which class eventually does the LEAST work?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'O(n²)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n log n)', 'is_correct': False},
                                {'id': 'c', 'text': 'O(log n)', 'is_correct': True},
                                {'id': 'd', 'text': 'O(n)', 'is_correct': False},
                            ],
                            'explain': 'Order: log n < n < n log n < n². Logarithmic grows slowest of these.',
                        },
                        {
                            'slug': 'count-the-sum-loop',
                            'title': 'Dry-run counting',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'A function does: total=0; then for each of the n items '
                                'runs one += statement; then returns. Ignoring constants, '
                                'the operation count grows like n raised to what power? '
                                'Answer with the exponent only: O(n^__)\n'
                                '(One digit.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': '1',
                            'explain': 'One pass: O(n¹) = O(n) — linear.',
                        },
                    ],
                },
                {
                    'title': 'Best, Average and Worst; Space Complexity',
                    'slug': 'cases-and-space',
                    'objective': 'Distinguish the three cases and analyse memory usage in the same notation.',
                    'duration': 10,
                    'body': """# Which run are you measuring?

Linear search finds a target in a list. If the target is the first
element, it stops immediately: **best case = O(1)**. If it is last or
absent, the scan runs to the end: **worst case = O(n)**. On a random
arrangement, expect half the list: **average case = O(n)** (same class —
constants dropped).

Notation: best Ω(n) here, worst O(n), average Θ(n) — in casual speech all
three are "Big-O", and what you must add is *which case* you mean.

**Engineering default: worst case.** When you promise a service "answers
within its bound", you promise the worst input, not the lucky one.
(Bubble sort: best O(n) if already sorted — but nobody buys a sort by its
best day.)

### Dry-run table — linear search for 7 in [3, 7, 9, 1]
| Step | i | arr[i] | comparison | action |
|---|---|---|---|---|
| 1 | 0 | 3 | 3 ≠ 7 | continue |
| 2 | 1 | 7 | 7 = 7 | **return 1** |

Found at index 1 after 2 comparisons — this specific run is neither best
nor worst; the classes describe the *family of inputs*, not one trace.

## Space complexity — the other bill
Same counting method applied to **extra memory** the algorithm needs
beyond the input itself.

- Searching through a list with one index variable: O(1) space.
- Copying the list into a sorted new list: O(n) space.
- Recursion that nests n calls deep: O(n) space for the call stack —
  people forget this one constantly.
- Merge sort splits into halves recursively: O(n) auxiliary space;
  insertion sort shifts elements in place: O(1) — a real reason to pay
  insertion sort's O(n²) time in memory-tight spots.

**Time–space trade-off:** a count-array (frequency table) turns "count
duplicates" from O(n²) comparisons into O(n) passes plus O(k) memory.
Cache, index tables and hash maps all buy speed with space.

## Space ladder example
Two nested loops that only move integer indices: O(1) space, O(n²) time.
One loop that builds an n×n matrix: O(n²) space, O(n²) time. The matrix
is not "better" because its space class matches its time — always ask
both bills separately.

## Common mistakes
- Quoting best case as *the* complexity of an algorithm ("quick sort is
  O(n log n)" — its worst case is O(n²); say average).
- Forgetting the call stack when recursion is used.
- Calling in-place algorithms O(1) space while ignoring the input itself;
  the convention is *extra* space — state your convention.

## Lesson summary
Algorithms have best/average/worst *cases* over input families — quote
worst by default. Space counts extra memory, including recursion depth.
Every design choice pays one bill to save the other.""",
                    'exercises': [
                        {
                            'slug': 'linear-search-best',
                            'title': 'Best case of linear search',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The best-case time of linear search on a list of n items is…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'O(1) — the target is the first element', 'is_correct': True},
                                {'id': 'b', 'text': 'O(n) always', 'is_correct': False},
                                {'id': 'c', 'text': 'O(log n)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n²)', 'is_correct': False},
                            ],
                            'explain': 'The best case is one comparison; the worst (absent/last) is n.',
                        },
                        {
                            'slug': 'recursion-space',
                            'title': 'Hidden memory of recursion',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A recursive function that calls itself n times before returning uses extra space of at least…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'O(1) — recursion is free', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n) call-stack depth', 'is_correct': True},
                                {'id': 'c', 'text': 'O(log n)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n²)', 'is_correct': False},
                            ],
                            'explain': 'Each pending call holds a stack frame; depth n = O(n) space — a classic reason to prefer iterative versions.',
                        },
                        {
                            'slug': 'trade-off-choice',
                            'title': 'Buying speed',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Building a frequency table to count duplicates in O(n) instead of checking every pair in O(n²) is an example of…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'trading space for time', 'is_correct': True},
                                {'id': 'b', 'text': 'trading time for space', 'is_correct': False},
                                {'id': 'c', 'text': 'a divide-and-conquer split', 'is_correct': False},
                                {'id': 'd', 'text': 'a hash collision', 'is_correct': False},
                            ],
                            'explain': 'The table costs O(k) memory but saves a factor of n in work — the most common trade in this course.',
                        },
                        {
                            'slug': 'merge-vs-insert-space',
                            'title': 'Auxiliary space of the classic sorts',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct space claims (auxiliary).',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Insertion sort: O(1)', 'is_correct': True},
                                {'id': 'b', 'text': 'Merge sort: O(n)', 'is_correct': True},
                                {'id': 'c', 'text': 'Bubble sort: O(n)', 'is_correct': False},
                                {'id': 'd', 'text': 'Recursive quicksort (average): O(log n) stack', 'is_correct': True},
                            ],
                            'explain': 'Bubble sort is in-place too — O(1), making (c) the false one. Quicksort keeps only log n frames on average.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 2 Quiz',
                    'slug': 'complexity-quiz',
                    'objective': 'Check Big-O analysis and space reasoning.',
                    'duration': 4,
                    'body': """# Chapter 2 quiz

Six questions on growth classes, cases and memory.""",
                    'exercises': [
                        {
                            'slug': 'q2-double-loop-half',
                            'title': 'Inner loop that halves',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'An outer loop runs n times; the inner loop starts at the outer index and runs to the end. Class?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(n)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n log n)', 'is_correct': False},
                                {'id': 'c', 'text': 'O(n²) — iterations are n + (n−1) + … + 1', 'is_correct': True},
                                {'id': 'd', 'text': 'O(n³)', 'is_correct': False},
                            ],
                            'explain': 'The triangular sum n(n+1)/2 has dominant term n²/2 → O(n²). This pattern is exactly how bubble/selection/insertion sorts count.',
                        },
                        {
                            'slug': 'q2-default-case',
                            'title': 'The engineering promise',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'When a documentation says "lookup is O(1)", professionals read it as…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'the average run', 'is_correct': False},
                                {'id': 'b', 'text': 'the worst-case guarantee unless stated otherwise', 'is_correct': True},
                                {'id': 'c', 'text': 'the best case', 'is_correct': False},
                                {'id': 'd', 'text': 'the only possible case', 'is_correct': False},
                            ],
                            'explain': 'Bounds are promises; promises quote the worst. (Hash tables actually quote O(1) *average* — so good docs say so.)',
                        },
                        {
                            'slug': 'q2-sorted-scan',
                            'title': 'Binary search class',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Repeatedly halving a *sorted* range to find a target costs…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'O(n)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(log n)', 'is_correct': True},
                                {'id': 'c', 'text': 'O(1)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n²)', 'is_correct': False},
                            ],
                            'explain': 'Halving until one item remains: log₂ n comparisons. You meet the implementation in chapter 6.',
                        },
                        {
                            'slug': 'q2-ordering',
                            'title': 'Rank the ladder',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Ordered from slowest-growing (best) to fastest-growing (worst):',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ)', 'is_correct': True},
                                {'id': 'b', 'text': 'O(log n) < O(1) < O(n) < O(n²) < O(n log n) < O(2ⁿ)', 'is_correct': False},
                                {'id': 'c', 'text': 'O(1) < O(n) < O(log n) < O(n²) < O(n log n) < O(2ⁿ)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n log n) < O(log n) < O(1) < O(n) < O(n²) < O(2ⁿ)', 'is_correct': False},
                            ],
                            'explain': 'Memorise the ladder shape: constant, log, linear, log-linear, quadratic, exponential.',
                        },
                        {
                            'slug': 'q2-space-matrix',
                            'title': 'Building a matrix',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Creating an n×n matrix of zeros inside an otherwise O(n²)-time function uses extra space…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(1)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n)', 'is_correct': False},
                                {'id': 'c', 'text': 'O(n²)', 'is_correct': True},
                                {'id': 'd', 'text': 'O(log n)', 'is_correct': False},
                            ],
                            'explain': 'The matrix itself is n² stored values — the space bill matches the time bill here.',
                        },
                        {
                            'slug': 'q2-small-input-constants',
                            'title': 'The constant-factor caveat',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'An O(n) algorithm and an O(n log n) algorithm run on n = 5. Which finishes first?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Always the O(n log n) one — smaller class always wins', 'is_correct': False},
                                {'id': 'b', 'text': 'Cannot be concluded from classes alone: at small n, constants and overhead can dominate', 'is_correct': True},
                                {'id': 'c', 'text': 'Both take identical time', 'is_correct': False},
                                {'id': 'd', 'text': 'Big-O decides runtime for any specific input', 'is_correct': False},
                            ],
                            'explain': 'Classes describe growth; single runs depend on both class and constant. (This is why std::sort uses insertion sort for tiny ranges.)',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 3 ════════════════════
        {
            'title': 'Arrays and Strings',
            'slug': 'arrays-strings',
            'description': 'Indexing, traversal, insertion/deletion cost, string work and the two-pointer technique.',
            'lessons': [
                {
                    'title': 'Array Fundamentals: Indexes, Traversal, Search',
                    'slug': 'array-basics',
                    'objective': 'Explain contiguous storage and O(1) indexing; traverse and search arrays in Python and C++.',
                    'duration': 14,
                    'body': """# Arrays: the workhorse structure

An **array** stores elements of the same type in **contiguous memory**.
Because they sit side by side, the computer can compute any element's
address directly: `address(i) = base + i × size`. No walking required —
**indexing is O(1)**.

## Python lists vs C++ arrays (know both, they behave differently)
```python
a = [3, 1, 4, 1, 5]      # list: dynamic, mixed types allowed
a[2]                      # 4 — O(1)
a.append(9)               # grow at the end — amortised O(1)
```

```cpp
int a[5] = {3, 1, 4, 1, 5};   // fixed size at compile time
std::vector<int> v = {3,1,4}; // dynamic like Python's list
v.push_back(9);                // amortised O(1)
```

A C-style array cannot grow; `std::vector` and Python lists reserve spare
capacity and occasionally copy everything into a bigger block — which is
why appending is *amortised* O(1): most appends are cheap, rare ones are
expensive, the average stays constant.

## Traversal — the universal pattern
```python
def find_first_even(xs):
    for x in xs:            # visit each element once: O(n)
        if x % 2 == 0:
            return x        # early exit: best case O(1)
    return None
```

```cpp
// same search over a vector, index form
for (size_t i = 0; i < v.size(); ++i) {
    if (v[i] % 2 == 0) return v[i];
}
return -1;
```

### Dry-run — find_first_even([7, 3, 8, 2])
| Step | x | x % 2 == 0? | action |
|---|---|---|---|
| 1 | 7 | no | continue |
| 2 | 3 | no | continue |
| 3 | 8 | **yes** | return 8 |

## Insert and delete — the expensive part
Inserting at position i in an array shifts everything from i onward one
slot right: **O(n)**. Same for deletion (shift left). Inserting at the
END costs no shifts — amortised O(1). This asymmetry (fast at the tip,
slow in the middle) is the entire reason linked lists exist — next
chapter.

## Searching an array
- Unordered: linear scan O(n) — nothing else is possible.
- Sorted: binary search O(log n) — chapter 6 builds it carefully.

## Important terminology
- **Index** (position number) vs **element** (the value at it).
- Python indexes start at 0; negatives count from the end (`a[-1]`).
- C++ arrays have **no bounds checking** — `a[10]` on a 5-element array
  is undefined behaviour, not an exception. Off-by-one bugs live here.

## Common mistakes
- Off-by-one loops: `for i in range(len(a) - 1)` skips the last element
  when you meant to visit all (`range(len(a))`).
- Reusing one variable name as both index and value in dry-runs — trace
  tables (Step/Value/Action columns) prevent the confusion.
- Assuming append is always O(1) *worst case* — it is amortised; in
  real-time code the rare copy burst matters.

## Lesson summary
Contiguity buys O(1) indexing and cache-friendly traversal; it charges
O(n) for middle insert/delete. Scan patterns (accumulate, find, test-any)
plus dry-run tables are the daily toolkit.""",
                    'exercises': [
                        {
                            'slug': 'index-why-o1',
                            'title': 'Why indexing is O(1)',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Array access `a[i]` is constant time because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the CPU caches the whole array', 'is_correct': False},
                                {'id': 'b', 'text': 'the element\u2019s address is computed directly from base + i × size', 'is_correct': True},
                                {'id': 'c', 'text': 'indexes are sorted', 'is_correct': False},
                                {'id': 'd', 'text': 'Python lists are linked internally', 'is_correct': False},
                            ],
                            'explain': 'Contiguous storage turns position into arithmetic — no walk needed.',
                        },
                        {
                            'slug': 'middle-insert-cost',
                            'title': 'Insertion in the middle',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inserting one value at index 0 of a 1,000-element array (Python/C++ style) costs about…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '1 operation', 'is_correct': False},
                                {'id': 'b', 'text': '1,000 shifts to make room: O(n)', 'is_correct': True},
                                {'id': 'c', 'text': 'log 1000 operations', 'is_correct': False},
                                {'id': 'd', 'text': 'depends on the values', 'is_correct': False},
                            ],
                            'explain': 'Everything from index 0 onward moves one slot right — n shifts.',
                        },
                        {
                            'slug': 'first-even-code',
                            'title': 'Code: first multiple of 5',
                            'exercise_type': 'code',
                            'instructions': (
                                'Write a program that prints the first number divisible '
                                'by 5 in the list [11, 17, 20, 25, 33]. Print exactly '
                                'one number.'
                            ),
                            'context': 'Scan with early exit — the find pattern from the lesson.',
                            'constraints': 'Use a loop; do not hard-code the answer.',
                            'expected_output': '20',
                            'starter_code': 'nums = [11, 17, 20, 25, 33]\n# print the first number divisible by 5\n',
                            'solution_code': 'nums = [11, 17, 20, 25, 33]\nfor n in nums:\n    if n % 5 == 0:\n        print(n)\n        break',
                            'test_cases': [{'input': '', 'expected_output': '20'}],
                            'explain': '20 is the first value passing n % 5 == 0; break exits immediately — the rest of the list is never visited.',
                            'xp_reward': 100,
                        },
                    ],
                },
                {
                    'title': 'String Manipulation',
                    'slug': 'strings',
                    'objective': 'Reverse, count, compare and build strings efficiently; know immutability costs.',
                    'duration': 12,
                    'body': """# Strings are arrays of characters — with extra rules

Everything from the array lesson applies: O(1) index, O(n) traversal.
Python strings add one rule: they are **immutable** — `s.upper()` returns
a NEW string; `s += '!'` builds a new copy every time. Looping `s += x`
n times copies an ever-growing string: O(n²) accidentally. The fix is the
**collector pattern**:

```python
parts = []                # O(1) append each
for word in words:
    parts.append(word.upper())
result = ' '.join(parts)  # one final pass
```

C++ `std::string` is mutable — `s += '!'` in a loop is amortised O(1)
per step, like vector push_back. Same thinking, different default.

## The patterns you will use constantly
```python
total_vowels = sum(1 for c in s if c in 'aeiou')   # count with filter
is_pal = s == s[::-1]                              # slice reverse
first_two = s[:2]                                  # slicing: start:stop
```

```cpp
// count vowels, range-for over std::string
int vowels = 0;
for (char c : s) {
    if (c=='a'||c=='e'||c=='i'||c=='o'||c=='u') ++vowels;
}
```

### Dry-run — reverse "CODE" with two pointers
| Step | left | right | swap | result so far |
|---|---|---|---|---|
| 1 | 0 (C) | 3 (E) | C↔E | EODC |
| 2 | 1 (O) | 2 (D) | O↔D | EDOC |
| 3 | 2 | 1 | stop (left ≥ right) | EDOC |

## Important terminology
- **Substring** — a contiguous run inside the string ("CODE" contains
  "OD"). **Subsequence** may skip characters — different problem class.
- Lexicographic order — dictionary comparison, character by character;
  `'Apple' < 'banana'` is True in ASCII because uppercase letters sort
  before lowercase (a classic exam trap).

## Real-world application
Validation, parsing and text processing are string scans: counting words
in a post, checking an email shape, masking a CNIC number
(`cnic[:4] + '*****' + cnic[-4:]`) — all single-pass loops.

## Common mistakes
- `s = s + x` inside loops (Python) — accidental O(n²).
- Forgetting case in comparisons: `s == 'yes'` fails on `'YES'`; normalise
  with `s.lower()` first.
- Off-by-one on the last character: `s[len(s)]` is out of range in both
  languages — it is `s[len(s) - 1]` / `s[s.size()-1]`.

## Lesson summary
Strings behave like character arrays; respect immutability (collector +
join), reuse the scan patterns, and dry-run reversals with tables.""",
                    'exercises': [
                        {
                            'slug': 'immutability-cost',
                            'title': 'The += loop trap',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Building a long Python string with `s += piece` inside a loop over n pieces is worst-case…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'O(n) — appends are free', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n²) — each step copies the whole string built so far', 'is_correct': True},
                                {'id': 'c', 'text': 'O(log n)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(1)', 'is_correct': False},
                            ],
                            'explain': 'Immutable strings: every += allocates and copies. Collect into a list and join once — O(n).',
                        },
                        {
                            'slug': 'count-char-code',
                            'title': 'Code: count the letter a',
                            'exercise_type': 'code',
                            'instructions': (
                                'Write a program that prints how many times the letter '
                                '"a" appears in the string "abracadabra". Print one '
                                'number only.'
                            ),
                            'context': 'Count-with-filter: the string version of the scan accumulator.',
                            'constraints': 'Use a loop; do not hard-code the answer.',
                            'expected_output': '5',
                            'starter_code': 'word = "abracadabra"\ncount = 0\n# count the letter a\n',
                            'solution_code': 'word = "abracadabra"\ncount = 0\nfor c in word:\n    if c == "a":\n        count += 1\nprint(count)',
                            'test_cases': [{'input': '', 'expected_output': '5'}],
                            'explain': 'a-b-r-a-c-a-d-a-b-r-a hides five a\u2019s; the accumulator increments once per match.',
                            'xp_reward': 100,
                        },
                        {
                            'slug': 'slice-reverse',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Python: print("Yaar"[::-1]). What exactly is printed? (One word.)',
                            'xp_reward': 40,
                            'expected_output': 'raaY',
                            'explain': 'Step -1 walks backward: r-a-a-Y. Case is preserved, so the capital Y ends the word.',
                        },
                        {
                            'slug': 'substring-vs-subsequence',
                            'title': 'Vocabulary check',
                            'exercise_type': 'multiple_choice',
                            'instructions': '"OD" inside "CODE" is a substring. A subsequence differs because it…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'must be shorter', 'is_correct': False},
                                {'id': 'b', 'text': 'may skip characters; substrings must be contiguous', 'is_correct': True},
                                {'id': 'c', 'text': 'is always uppercase', 'is_correct': False},
                                {'id': 'd', 'text': 'cannot repeat letters', 'is_correct': False},
                            ],
                            'explain': '"CE" is a subsequence of CODE but not a substring — contiguity is the dividing line.',
                        },
                    ],
                },
                {
                    'title': 'The Two-Pointer Technique',
                    'slug': 'two-pointers',
                    'objective': 'Use paired or racing indexes to scan in one pass without extra memory.',
                    'duration': 12,
                    'body': """# Two pointers: two indexes, one pass, no extra space

A **two-pointer** solution keeps two variables that move through the data
according to a rule, so you avoid nested loops or a copied structure.

## Pattern 1 — ends inward: reverse & palindrome
```python
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

### Dry-run — "level"
| Step | left | s[left] | right | s[right] | equal? |
|---|---|---|---|---|---|
| 1 | 0 | l | 4 | l | yes |
| 2 | 1 | e | 3 | e | yes |
| 3 | 2 | — loop ends (2 < 2 false) | | | **True** |

Work done: n/2 comparisons → **O(n) time, O(1) space** — versus slicing
(`s == s[::-1]`) which is also O(n) but builds a full copy: O(n) space.

## Pattern 2 — same direction, different pace: the search pair
On a **sorted** array, find two numbers summing to a target by anchoring
one pointer at each end and moving based on the sum:

```python
def has_pair(nums, target):        # nums sorted
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target: return True
        if s < target:  lo += 1     # need a bigger sum
        else:           hi -= 1     # need a smaller sum
    return False
```

### Dry-run — [1, 3, 5, 8], target 13
| Step | lo | hi | sum | action |
|---|---|---|---|---|
| 1 | 1 | 8 | 9 < 13 | lo → 1 |
| 2 | 3 | 8 | 11 < 13 | lo → 2 |
| 3 | 5 | 8 | 13 | **True** |

O(n) instead of the O(n²) all-pairs scan — sortedness let each step
eliminate a whole row of pairs.

## Why the technique matters
It converts "compare elements against each other" problems from quadratic
to linear, using only two variables. Interview staples (pair sum,
container width, remove duplicates, window problems) are pattern
variations.

## Common mistakes
- Forgetting the pointers must obey a *rule*; random movement is not the
  technique — the rule (which pointer moves and why) is the algorithm.
- Applying the sorted pair-sum to an **unsorted** array — the elimination
  logic breaks; sort first (O(n log n)) or use a set (O(n) time, O(n) space).
- Off-by-one on the loop condition: `left <= right` in a swap loop touches
  the middle twice.

## Lesson summary
Two pointers = coordinated indexes with a movement rule. Ends-inward for
palindromes/reversal; sorted bookends for pair-sums. Linear time, constant
space.""",
                    'exercises': [
                        {
                            'slug': 'palindrome-space',
                            'title': 'Cost of the palindrome scan',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The two-pointer is_palindrome from the lesson runs in…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(n) time, O(1) extra space', 'is_correct': True},
                                {'id': 'b', 'text': 'O(n) time, O(n) space', 'is_correct': False},
                                {'id': 'c', 'text': 'O(n²) time', 'is_correct': False},
                                {'id': 'd', 'text': 'O(log n) time', 'is_correct': False},
                            ],
                            'explain': 'Half the characters compared once each; only two integer variables extra.',
                        },
                        {
                            'slug': 'pair-sum-move-rule',
                            'title': 'Which pointer moves',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In the sorted pair-sum scan, if current sum < target you move…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'hi leftward — a smaller value lowers the sum', 'is_correct': False},
                                {'id': 'b', 'text': 'lo rightward — the next-larger left value raises the sum', 'is_correct': True},
                                {'id': 'c', 'text': 'both pointers inward together', 'is_correct': False},
                                {'id': 'd', 'text': 'neither; restart from scratch', 'is_correct': False},
                            ],
                            'explain': 'On sorted data, raising the smaller side is the only way to grow the sum without losing candidates — the elimination argument is why O(n) is enough.',
                        },
                        {
                            'slug': 'remove-duplicates-code',
                            'title': 'Code: compact a sorted list',
                            'exercise_type': 'code',
                            'instructions': (
                                'The sorted list [1, 1, 2, 3, 3, 3] is given. Print the '
                                'values without duplicates, one per line, in order.'
                            ),
                            'context': 'Same-direction pointers: compare each element to its predecessor.',
                            'constraints': 'Do not use set(). Print exactly the lines shown by the expected output.',
                            'expected_output': '1\n2\n3',
                            'starter_code': 'nums = [1, 1, 2, 3, 3, 3]\n# print each distinct value once\n',
                            'solution_code': 'nums = [1, 1, 2, 3, 3, 3]\nprev = None\nfor n in nums:\n    if n != prev:\n        print(n)\n    prev = n',
                            'test_cases': [{'input': '', 'expected_output': '1\n2\n3'}],
                            'explain': 'On sorted input duplicates are adjacent; remembering prev is the one-variable pointer trick.',
                            'xp_reward': 120,
                        },
                    ],
                },
                {
                    'title': 'Chapter 3 Quiz',
                    'slug': 'arrays-strings-quiz',
                    'objective': 'Check array and string reasoning.',
                    'duration': 5,
                    'body': """# Chapter 3 quiz

Six questions on arrays, strings and two pointers.""",
                    'exercises': [
                        {
                            'slug': 'q3-fastest-op',
                            'title': 'Cheapest array operation',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which operation on a Python list / C++ vector is O(1) (amortised or worst)?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Insert at the front', 'is_correct': False},
                                {'id': 'b', 'text': 'Read by index', 'is_correct': True},
                                {'id': 'c', 'text': 'Delete from the middle', 'is_correct': False},
                                {'id': 'd', 'text': 'Check whether a value is present', 'is_correct': False},
                            ],
                            'explain': 'Indexing is direct arithmetic; front/middle edits shift runs; membership scans.',
                        },
                        {
                            'slug': 'q3-cpp-bounds',
                            'title': 'Out-of-range in C++',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Reading a[10] from an int a[5] in C++ does what?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Throws an IndexError', 'is_correct': False},
                                {'id': 'b', 'text': 'Undefined behaviour — no automatic bounds check (except .at())', 'is_correct': True},
                                {'id': 'c', 'text': 'Returns 0', 'is_correct': False},
                                {'id': 'd', 'text': 'Resizes the array', 'is_correct': False},
                            ],
                            'explain': 'C++ trusts you; Python raises instead. This difference is why off-by-one bugs are language-flavoured.',
                        },
                        {
                            'slug': 'q3-palindrome-slice',
                            'title': 'Slice versus pointers',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Compared with the two-pointer scan, `s == s[::-1]` to test palindromes…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'is also O(1) space', 'is_correct': False},
                                {'id': 'b', 'text': 'costs O(n) extra space for the reversed copy', 'is_correct': True},
                                {'id': 'c', 'text': 'is O(n²) time', 'is_correct': False},
                                {'id': 'd', 'text': 'cannot handle uppercase', 'is_correct': False},
                            ],
                            'explain': 'Both O(n) time; slicing pays a full extra string. For huge texts the difference is real.',
                        },
                        {
                            'slug': 'q3-amortised',
                            'title': 'Amortised meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': '"append is amortised O(1)" means…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'every single append is O(1)', 'is_correct': False},
                                {'id': 'b', 'text': 'over many appends the average cost per append is constant, despite rare resize copies', 'is_correct': True},
                                {'id': 'c', 'text': 'append is slow but rare', 'is_correct': False},
                                {'id': 'd', 'text': 'the list stores fewer than n items', 'is_correct': False},
                            ],
                            'explain': 'Doubling capacity makes the burst of O(n) copies rarer and rarer; spread over all appends, the average is constant.',
                        },
                        {
                            'slug': 'q3-predecessor-logic',
                            'title': 'Why dedupe needs sortedness',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The prev-variable dedupe works in one pass because sorted input guarantees…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'duplicates are adjacent', 'is_correct': True},
                                {'id': 'b', 'text': 'no duplicates exist', 'is_correct': False},
                                {'id': 'c', 'text': 'values are small', 'is_correct': False},
                                {'id': 'd', 'text': 'the list fits in cache', 'is_correct': False},
                            ],
                            'explain': 'Equal values sit next to each other once sorted, so comparing with the predecessor catches every repeat.',
                        },
                        {
                            'slug': 'q3-lexicographic',
                            'title': 'ASCII ordering trap',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Python: print("Apple" < "banana"). What is printed? (One word, capitalised.)',
                            'xp_reward': 40,
                            'expected_output': 'True',
                            'explain': 'Uppercase letters have smaller codes than lowercase, so Apple sorts before banana — case surprises exams.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 4 ════════════════════
        {
            'title': 'Linked Lists',
            'slug': 'linked-lists',
            'description': 'Nodes and pointers; singly and doubly linked lists; insert, delete and traverse — implemented.',
            'lessons': [
                {
                    'title': 'Nodes and Pointers: The Idea',
                    'slug': 'nodes-pointers',
                    'objective': 'Describe a linked list and contrast its cost profile with arrays.',
                    'duration': 10,
                    'body': """# Arrays were too stubborn — lists that chain

Chapter 3's charge: inserting in the middle of an array shifts every
later element. A **linked list** fixes that by giving up contiguity:
each element (**node**) stores a value **and the address of the next
node**. The nodes can sit anywhere in memory, chained by pointers.

```
head ─→ [3|●] ─→ [7|●] ─→ [1|∅]
```

- The first node is the **head**; `∅` (None/nullptr) marks the end.
- To reach the 5th node you must **walk** 4 links — no arithmetic
  shortcut, so index access is O(n), not O(1).
- To insert after a node you already hold: create the new node, rewire
  two pointers — **O(1)**, no shifting. (Finding that position first
  still costs the O(n) walk.)

## Where linked lists genuinely shine
- Frequent insert/delete **at known positions** (you already have the
  pointer): editor undo chains, scheduler task lists, LRU caches.
- Building stacks/queues without resizing or copying (chapter 5).

## Where they hurt
- No random access, no cache locality — walking chases scattered memory;
  arrays stream through the CPU cache. In practice arrays win most
  real workloads, which is why Python has no linked list and C++'s
  `std::list` is rarely the right answer. Learn linked lists to
  **understand pointers and to build the next chapter's structures**.

## Vocabulary, precisely
- **Pointer/reference:** a variable holding an address, not a value.
- **Dangling pointer:** pointing at freed memory — C++'s classic crash.
- Python hides manual pointers: every object variable IS a reference;
  `node.next` is just a reference stored inside an object.

## Exam-style comparison table (memorise the shape)
| Operation | Array/Vector | Linked list |
|---|---|---|
| Access by index | O(1) | O(n) |
| Insert/delete at front | O(n) | O(1) |
| Insert/delete once positioned | O(n) | O(1) |
| Memory layout | contiguous | scattered + link overhead |
| Search (unordered) | O(n), cache-fast | O(n), pointer-chasing |

## Common mistakes
- Saying "linked lists make insertion O(1)" without the honest caveat:
  *once you hold the position.* Finding it is the real cost.
- Losing the head: `head = head.next` before saving the node you wanted
  gone — the node becomes unreachable (Python garbage-collects it; C++
  leaks it).

## Lesson summary
Linked lists trade contiguity (fast indexing, caching) for pointer chains
(fast splice-in/splice-out at known spots). Cost table above is the
whole comparison.""",
                    'exercises': [
                        {
                            'slug': 'why-index-slow',
                            'title': 'Why index access is O(n)',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In a linked list, reaching the k-th node takes O(k) because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'nodes are stored in sorted order', 'is_correct': False},
                                {'id': 'b', 'text': 'the only way to location is following links from the head one by one', 'is_correct': True},
                                {'id': 'c', 'text': 'the CPU must decompress pointers', 'is_correct': False},
                                {'id': 'd', 'text': 'k must be halved first', 'is_correct': False},
                            ],
                            'explain': 'Without contiguity there is no address arithmetic; links are the only map.',
                        },
                        {
                            'slug': 'insert-cost-caveat',
                            'title': 'The honest insertion claim',
                            'exercise_type': 'multiple_choice',
                            'instructions': '"Linked-list insertion is O(1)" is true only when…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'the list is empty', 'is_correct': False},
                                {'id': 'b', 'text': 'you already hold a pointer to the position', 'is_correct': True},
                                {'id': 'c', 'text': 'values are unique', 'is_correct': False},
                                {'id': 'd', 'text': 'the new value is the largest', 'is_correct': False},
                            ],
                            'explain': 'The rewiring itself is constant work; searching the position is the linear part.',
                        },
                        {
                            'slug': 'cache-locality',
                            'title': 'Real hardware cost',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Arrays often beat linked lists in practice even with equal Big-O because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'arrays use less memory per element and load predictably into CPU cache', 'is_correct': True},
                                {'id': 'b', 'text': 'arrays have a smaller Big-O class', 'is_correct': False},
                                {'id': 'c', 'text': 'linked lists cannot store integers', 'is_correct': False},
                                {'id': 'd', 'text': 'Python optimises arrays only', 'is_correct': False},
                            ],
                            'explain': 'Same class, different constant: contiguity is cache-friendly, scattered nodes are not.',
                        },
                    ],
                },
                {
                    'title': 'Implementing a Singly Linked List',
                    'slug': 'singly-implement',
                    'objective': 'Build Node and LinkedList classes with prepend, append, traverse, delete.',
                    'duration': 16,
                    'body': """# Two tiny classes, one real structure

```python
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def prepend(self, value):          # O(1)
        self.head = Node(value, self.head)
        self.size += 1

    def append(self, value):           # O(n): walk to the tail
        new = Node(value)
        if self.head is None:
            self.head = new
        else:
            cur = self.head
            while cur.next is not None:
                cur = cur.next
            cur.next = new
        self.size += 1

    def delete(self, value):           # O(n) find + O(1) rewire
        cur, prev = self.head, None
        while cur is not None:
            if cur.value == value:
                if prev is None: self.head = cur.next   # deleting head
                else:            prev.next = cur.next
                self.size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def __iter__(self):                # makes `for x in lst:` work
        cur = self.head
        while cur is not None:
            yield cur.value
            cur = cur.next
```

## Trace — prepend(9) onto [1, 5]
`self.head = Node(9, self.head)`:
new node's next = old head (1→5); head now points at 9 → **9 → 1 → 5**.
Two assignments — that is all O(1) front insertion means.

## The pointer-rewiring diagram to draw in exams
Delete node B between A and C: `A.next = C` (in code, `prev.next =
cur.next`). B is now unreachable — Python frees it; in C++ you must
`delete` it yourself or leak memory.

## The same skeleton in C++ (read, don't run)
```cpp
struct Node { int value; Node* next; };
void prepend(Node*& head, int value) {
    head = new Node{value, head};   // reference-to-pointer: head itself moves
}
```
C++ makes the pointer visible (`Node*`, `new`, `delete`) — Python's
`self.head = Node(value, self.head)` is the same rewiring with the
`*` hidden.

### Dry-run table — delete(5) from [1, 5, 9]
| Step | prev | cur | cur.value == 5? | action |
|---|---|---|---|---|
| 1 | None | 1 | no | advance |
| 2 | 1 | 5 | **yes** | `prev.next = cur.next` → 1 → 9 |

## Common mistakes
- Forgetting the head case when deleting (prev is None → move head).
- Walking `while cur.next` when you need `while cur` and vice versa —
  draw two nodes and trace by hand once and it sticks.
- Not updating `size`, then `len` lies.

## Lesson summary
Node(value, next) + a head reference = a singly linked list. Prepend
O(1); append/delete/contains O(n); deletion is one careful rewire with a
prev trailing pointer.""",
                    'exercises': [
                        {
                            'slug': 'prepend-work',
                            'title': 'Count the assignments',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Prepending to a non-empty singly linked list changes how many `next` pointers?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'One — the new node points at the old head; head is then updated', 'is_correct': True},
                                {'id': 'b', 'text': 'All of them', 'is_correct': False},
                                {'id': 'c', 'text': 'None', 'is_correct': False},
                                {'id': 'd', 'text': 'Two per node', 'is_correct': False},
                            ],
                            'explain': 'New node stores old head as its next; then head points to the new node. Existing links untouched.',
                        },
                        {
                            'slug': 'walk-to-third',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'A LinkedList holds 3 → 7 → 11 (head is 3). '
                                'Python: cur = lst.head.next; print(cur.value). '
                                'What is printed? (One number.)'
                            ),
                            'xp_reward': 50,
                            'expected_output': '7',
                            'explain': 'head.next is the second node (7); walking links is manual indexing.',
                        },
                        {
                            'slug': 'build-length-code',
                            'title': 'Code: count the nodes',
                            'exercise_type': 'code',
                            'instructions': (
                                'The linked list 4 → 8 → 15 → 16 → 23 is built for you '
                                'in the starter code. Print how many nodes it contains '
                                'by walking from head to the end.'
                            ),
                            'context': 'Traversal with a counter — the list version of every array scan.',
                            'constraints': 'Walk with a while loop over .next; do not use the size attribute.',
                            'expected_output': '5',
                            'starter_code': (
                                'class Node:\n    def __init__(self, value, next=None):\n'
                                '        self.value = value\n        self.next = next\n\n'
                                'head = Node(4, Node(8, Node(15, Node(16, Node(23)))))\n'
                                '# count the nodes\n'
                            ),
                            'solution_code': (
                                'class Node:\n    def __init__(self, value, next=None):\n'
                                '        self.value = value\n        self.next = next\n\n'
                                'head = Node(4, Node(8, Node(15, Node(16, Node(23)))))\n'
                                'count = 0\ncur = head\nwhile cur is not None:\n'
                                '    count += 1\n    cur = cur.next\nprint(count)'
                            ),
                            'test_cases': [{'input': '', 'expected_output': '5'}],
                            'explain': 'Advance cur one link per step, stop at None, count the stops.',
                            'xp_reward': 120,
                        },
                    ],
                },
                {
                    'title': 'Doubly Linked Lists',
                    'slug': 'doubly',
                    'objective': 'Explain the backward link and the extra constant cost it buys.',
                    'duration': 10,
                    'body': """# Two links per node: walk both ways

A **doubly linked list** stores `prev` and `next` per node:

```
None ← [3] ⇄ [7] ⇄ [1] → None
         head        tail
```

## What the backward link buys
- **Delete a node you hold in O(1) without knowing its predecessor**:
  `node.prev.next = node.next; node.next.prev = node.prev` (guard the
  ends). Singly linked deletion needed that trailing `prev` pointer or a
  re-walk from head.
- **Traverse in reverse**, browser history (back AND forward), text
  editors, LRU caches (C++'s `std::list`, Python's `list` internally is
  not doubly linked — the dict+linked-list combo is how real LRU caches
  are written).

## What it costs
- Two pointers per node (~double the link memory) and **twice the
  rewiring per insert/delete** — still O(1) once positioned, just a
  bigger constant.

### Dry-run — insert 9 between 7 and 1
| Step | action |
|---|---|
| 1 | new.next = 1 ; new.prev = 7 |
| 2 | 7.next = new |
| 3 | 1.prev = new |

Four assignments; order matters only in that the new node must read the
old links (7↔1) before the old nodes stop pointing at each other.

## Python's own version
```python
from collections import deque   # doubly linked list of blocks
q = deque([1, 2, 3])
q.appendleft(0); q.pop()        # both ends O(1)
```

`deque` is the doubly linked list of the standard library — proof the
structure is not just history.

## Common mistakes
- Forgetting the end-guards: when prev or next is None (head/tail
  deletion), assigning through it crashes.
- Updating only one direction and leaving a one-way link — trace tables
  expose this instantly.

## Lesson summary
Doubly linked = pay two pointers per node, gain reverse traversal and
true O(1) deletion-without-predecessor. The 4-step insert is the exam
standard.""",
                    'exercises': [
                        {
                            'slug': 'doubly-advantage',
                            'title': 'The real gain',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The main algorithmic advantage of a doubly linked list over a singly one is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Faster index access', 'is_correct': False},
                                {'id': 'b', 'text': 'O(1) removal of a node given only that node, plus backward traversal', 'is_correct': True},
                                {'id': 'c', 'text': 'Smaller memory', 'is_correct': False},
                                {'id': 'd', 'text': 'Built-in sorting', 'is_correct': False},
                            ],
                            'explain': 'Access and searching stay linear; the win is prev-link moves.',
                        },
                        {
                            'slug': 'insert-count',
                            'title': 'Rewiring count',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inserting a node between two known neighbours in a doubly linked list sets how many pointers (including the new node\u2019s)?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '2', 'is_correct': False},
                                {'id': 'b', 'text': '4 — new.prev, new.next, left neighbour\u2019s next, right neighbour\u2019s prev', 'is_correct': True},
                                {'id': 'c', 'text': '1', 'is_correct': False},
                                {'id': 'd', 'text': '8', 'is_correct': False},
                            ],
                            'explain': 'The dry-run table lists exactly four assignments.',
                        },
                        {
                            'slug': 'deque-identity',
                            'title': 'Standard-library cousin',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which Python standard-library type is implemented as a doubly linked structure with O(1) both-ends operations?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'deque', 'is_correct': True},
                                {'id': 'b', 'text': 'list', 'is_correct': False},
                                {'id': 'c', 'text': 'dict', 'is_correct': False},
                                {'id': 'd', 'text': 'tuple', 'is_correct': False},
                            ],
                            'explain': 'collections.deque = double-ended (linked blocks); list is a dynamic array.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 4 Quiz',
                    'slug': 'linked-lists-quiz',
                    'objective': 'Check linked-list reasoning and pointer logic.',
                    'duration': 5,
                    'body': """# Chapter 4 quiz

Six questions on nodes, chains and rewiring.""",
                    'exercises': [
                        {
                            'slug': 'q4-contains-cost',
                            'title': 'Membership test',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Checking whether a value is in an unsorted linked list of n nodes costs…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'O(1)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n) — walk from head until match or None', 'is_correct': True},
                                {'id': 'c', 'text': 'O(log n)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n²)', 'is_correct': False},
                            ],
                            'explain': 'No structure to exploit: contains is a linear scan.',
                        },
                        {
                            'slug': 'q4-lost-head',
                            'title': 'Reaching the end',
                            'exercise_type': 'output_prediction',
                            'instructions': 'After `head = head.next` once on [2, 4, 8], printing all remaining values yields? (Type them comma-separated like: 4, 8)',
                            'xp_reward': 40,
                            'expected_output': '4, 8',
                            'explain': 'The chain now starts at the second node; 2 is unreachable (and freed in Python).',
                        },
                        {
                            'slug': 'q4-cpp-leak',
                            'title': 'Who frees what',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Deleting a node by rewiring past it: Python vs C++?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Both free it immediately', 'is_correct': False},
                                {'id': 'b', 'text': 'Python garbage-collects it; C++ leaks it unless you delete it', 'is_correct': True},
                                {'id': 'c', 'text': 'Neither can ever free memory', 'is_correct': False},
                                {'id': 'd', 'text': 'C++ frees automatically, Python needs delete', 'is_correct': False},
                            ],
                            'explain': 'Unreachable ≠ freed in C++; that is why list implementations there call delete or use smart pointers.',
                        },
                        {
                            'slug': 'q4-front-insert',
                            'title': 'Front insert shootout',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inserting at the FRONT: array/vector vs linked list?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Array O(n) shift; list O(1) rewire', 'is_correct': True},
                                {'id': 'b', 'text': 'Both O(1)', 'is_correct': False},
                                {'id': 'c', 'text': 'Array O(1); list O(n)', 'is_correct': False},
                                {'id': 'd', 'text': 'Both O(n)', 'is_correct': False},
                            ],
                            'explain': 'The front is the array\u2019s worst insertion spot and the list\u2019s best.',
                        },
                        {
                            'slug': 'q4-iterators',
                            'title': 'Why __iter__ exists',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Giving LinkedList an __iter__ (yielding values while walking) makes…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '`for x in lst:` work without exposing nodes', 'is_correct': True},
                                {'id': 'b', 'text': 'indexing O(1)', 'is_correct': False},
                                {'id': 'c', 'text': 'the list sorted', 'is_correct': False},
                                {'id': 'd', 'text': 'memory freed', 'is_correct': False},
                            ],
                            'explain': 'Iterators hide the walk: callers loop over values, nodes stay private.',
                        },
                        {
                            'slug': 'q4-when-choose-array',
                            'title': 'Default choice',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You need frequent random reads (get i-th) and mostly end-appends. Choose…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Linked list — pointers are flexible', 'is_correct': False},
                                {'id': 'b', 'text': 'Array/vector — O(1) indexing and amortised O(1) push beat lists here', 'is_correct': True},
                                {'id': 'c', 'text': 'Doubly linked list', 'is_correct': False},
                                {'id': 'd', 'text': 'Either is equally fast', 'is_correct': False},
                            ],
                            'explain': 'Match the structure to the operations you actually use — the course\u2019s central design rule.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 5 ════════════════════
        {
            'title': 'Stacks and Queues',
            'slug': 'stacks-queues',
            'description': 'LIFO and FIFO as disciplines; implementations; circular queues; real applications.',
            'lessons': [
                {
                    'title': 'Stacks: Last In, First Out',
                    'slug': 'stacks',
                    'objective': 'Implement a stack, and recognise undo/history problems it models.',
                    'duration': 12,
                    'body': """# The stack discipline

A **stack** allows insertion and removal only at one end — the **top**.
**LIFO**: the last thing pushed is the first thing popped. No peeking
into the middle by contract.

```python
class Stack:
    def __init__(self):
        self.items = []            # list end = top (both ops amortised O(1))
    def push(self, v): self.items.append(v)
    def pop(self):     return self.items.pop()      # IndexError if empty
    def peek(self):    return self.items[-1] if self.items else None
    def is_empty(self): return not self.items
```

C++ mirrors it: `std::stack<int>` (or a `vector` with push_back/pop_back)
— same four operations.

## Why "only one end" is a feature
It exactly matches problems where **the most recent obligation must be
finished first**:
- **Undo** in editors: the last change un-does first.
- **Function calls:** the most recent call must return before the one
  below it resumes — the *call stack* is a real stack, and
  "stack overflow" means too many nested calls.
- **Back button / browser history.**
- **Balanced brackets:** scan left to right; push openers; on a closer,
  pop and require a match; leftovers at the end mean unclosed openers.

### Dry-run — `({)}`
| Char | action | stack |
|---|---|---|
| ( | push | ( |
| { | push | ( { |
| ) | pop expects ( → got { | **mismatch → invalid** |

## Cost table
push O(1) · pop O(1) · peek O(1) · search O(n) and *not allowed by the
contract* — if you need searching, you wanted a different structure.

## Common mistakes
- Popping an empty stack (crash) — guard with is_empty, like every
  textbook pops-without-looking-and-regrets-it.
- Implementing with the list FRONT (insert(0)/pop(0)) — that is O(n);
  use the end.
- Confusing the ADT (stack) with its implementation (list/vector/nodes).

## Lesson summary
Stack = discipline of the most-recent-first. Four operations, all O(1),
modelled on undo, calls and nesting; bracket checking is the classic
exercise.""",
                    'exercises': [
                        {
                            'slug': 'undo-lifo',
                            'title': 'Why undo is a stack',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'An editor undoes the MOST RECENT change first because undo history is…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'a queue — first in, first out', 'is_correct': False},
                                {'id': 'b', 'text': 'a stack — the last action must be the first reversed', 'is_correct': True},
                                {'id': 'c', 'text': 'a hash table — keyed by time', 'is_correct': False},
                                {'id': 'd', 'text': 'a sorted array', 'is_correct': False},
                            ],
                            'explain': 'Reversal must happen newest-first to stay consistent; that is LIFO exactly.',
                        },
                        {
                            'slug': 'brackets-invalid',
                            'title': 'Trace: ([)]',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Running the bracket algorithm on `([)]` reports invalid at which character?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'the first ) — it meets top-of-stack [, not (', 'is_correct': True},
                                {'id': 'b', 'text': 'the ] — wrong order', 'is_correct': False},
                                {'id': 'c', 'text': 'it is actually valid', 'is_correct': False},
                                {'id': 'd', 'text': 'the second ( — duplicate', 'is_correct': False},
                            ],
                            'explain': 'Dry-run: push ( , push [ , then ) needs top ( but sees [ — mismatch.',
                        },
                        {
                            'slug': 'stack-sequence-code',
                            'title': 'Code: pop order',
                            'exercise_type': 'code',
                            'instructions': (
                                'Push 1, 2, 3 onto a stack, then pop everything and '
                                'print each popped value on its own line. '
                                'Expected three lines.'
                            ),
                            'context': 'Direct rehearsal of LIFO behaviour.',
                            'constraints': 'Use the Stack class from the lesson or list append/pop.',
                            'expected_output': '3\n2\n1',
                            'starter_code': 'stack = []\n# push 1, 2, 3 then pop and print all\n',
                            'solution_code': 'stack = []\nfor v in (1, 2, 3):\n    stack.append(v)\nwhile stack:\n    print(stack.pop())',
                            'test_cases': [{'input': '', 'expected_output': '3\n2\n1'}],
                            'explain': 'Last in (3) comes out first; the reverse of the push order is the signature answer of every stack exam.',
                            'xp_reward': 100,
                        },
                    ],
                },
                {
                    'title': 'Queues and Circular Queues',
                    'slug': 'queues',
                    'objective': 'Implement FIFO queues, explain the deque trick and the circular-array variant.',
                    'duration': 12,
                    'body': """# The queue discipline

A **queue** inserts at the **rear**, removes from the **front**. **FIFO**:
first served, first done — ticket lines, print jobs, message brokers,
CPU task scheduling, BFS (chapter 9) — anything where fairness or order
of arrival matters.

```python
from collections import deque
q = deque()
q.append('task1')      # enqueue  O(1)
q.popleft()            # dequeue  O(1)
q[0]                   # peek front
```

Naive `list` version — `append` + `pop(0)` — is a trap: pop(0) shifts
every element, O(n) per dequeue. The deque (doubly linked blocks from
chapter 4!) gives both ends O(1). C++'s `std::queue` likewise wraps a
list/deque.

## Circular queue — the array version done right
With a fixed array of size k and two indices:

```
enqueue: rear = (rear + 1) % k
dequeue: front = (front + 1) % k
empty:   front == rear   |  full: (rear + 1) % k == front
```

The modulo **wraps** the pointers around the end, so the array is reused
without shifting — the trick behind ring buffers in audio, networking
and embedded systems (exam favourite: draw the array as a circle).

### Dry-run — k=4, push a,b,c, pop, push d
| Step | front | rear | contents |
|---|---|---|---|
| push a | 0 | 1 | a |
| push b | 0 | 2 | a b |
| push c | 0 | 3 | a b c |
| pop a | 1 | 3 | b c |
| push d | 1 | **0** (3+1 % 4) | b c d (wrapped!) |

## Costs and contracts
enqueue O(1) · dequeue O(1) · peek O(1) · again, arbitrary access is
**not** part of the contract.

## Deque: the hybrid
A double-ended queue allows append/pop on BOTH ends in O(1) — use it
when the problem says "sliding window" (keep recent items, drop oldest:
the window's left edge leaves from the front while newcomers join the
back).

## Common mistakes
- list.pop(0) in loops (silent O(n²)).
- Forgetting the full condition in circular queues (front == rear means
  EMPTY by convention — that is why one slot is kept spare, or a size
  counter is stored).
- Calling the front "top" — top is stack language; mixing vocabularies
  muddies dry-runs.

## Lesson summary
Queue = fairness discipline, FIFO; implement with deque or a circular
array of modulo-wrapped indices; deque/peek/enqueue all O(1).""",
                    'exercises': [
                        {
                            'slug': 'queue-vs-stack-choice',
                            'title': 'Pick the discipline',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A printer must process jobs in the order they arrived. Use…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'a stack — newest first', 'is_correct': False},
                                {'id': 'b', 'text': 'a queue — first in, first out', 'is_correct': True},
                                {'id': 'c', 'text': 'a binary tree', 'is_correct': False},
                                {'id': 'd', 'text': 'a hash table', 'is_correct': False},
                            ],
                            'explain': 'Arrival order = FIFO = queue. Stacks would print the newest job first — furious users.',
                        },
                        {
                            'slug': 'pop0-cost',
                            'title': 'The list-front trap',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Using `q.pop(0)` on a Python list as a dequeue makes n dequeues cost…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(n) total', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n²) total — every pop shifts the rest', 'is_correct': True},
                                {'id': 'c', 'text': 'O(1) amortised', 'is_correct': False},
                                {'id': 'd', 'text': 'O(log n)', 'is_correct': False},
                            ],
                            'explain': 'pop(0) is an array deletion at index 0: linear each time. deque exists precisely for this.',
                        },
                        {
                            'slug': 'circular-wrap',
                            'title': 'Where does rear go',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'In a circular queue of size k, the rear advances with '
                                'rear = (rear + 1) __ k. Write the single operator '
                                'symbol that wraps the index.'
                            ),
                            'xp_reward': 40,
                            'solution_code': '%',
                            'explain': 'Modulo wraps k back to 0 — the whole trick in one character.',
                        },
                        {
                            'slug': 'queue-output-code',
                            'title': 'Code: serve three tasks',
                            'exercise_type': 'code',
                            'instructions': (
                                'Enqueue A, B, C in order, then dequeue and print all '
                                'three, one per line.'
                            ),
                            'context': 'FIFO rehearsal.',
                            'constraints': 'Use collections.deque append/popleft.',
                            'expected_output': 'A\nB\nC',
                            'starter_code': 'from collections import deque\nq = deque()\n# enqueue A, B, C then dequeue and print all\n',
                            'solution_code': 'from collections import deque\nq = deque()\nfor t in ("A", "B", "C"):\n    q.append(t)\nwhile q:\n    print(q.popleft())',
                            'test_cases': [{'input': '', 'expected_output': 'A\nB\nC'}],
                            'explain': 'Order of arrival is preserved: A first in, first out.',
                            'xp_reward': 100,
                        },
                    ],
                },
                {
                    'title': 'Chapter 5 Quiz',
                    'slug': 'stacks-queues-quiz',
                    'objective': 'Check stack/queue reasoning.',
                    'duration': 4,
                    'body': """# Chapter 5 quiz

Five questions on LIFO, FIFO and their implementations.""",
                    'exercises': [
                        {
                            'slug': 'q5-callstack',
                            'title': 'Function calls',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why does the program call stack have to be a stack, not a queue?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Because the most recent call must finish and return before its caller resumes', 'is_correct': True},
                                {'id': 'b', 'text': 'Because queues are slower', 'is_correct': False},
                                {'id': 'c', 'text': 'Because functions arrive in sorted order', 'is_correct': False},
                                {'id': 'd', 'text': 'It could be either with no consequence', 'is_correct': False},
                            ],
                            'explain': 'Nesting is inherently LIFO: f calls g; g returns first, always.',
                        },
                        {
                            'slug': 'q5-two-stacks-queue',
                            'title': 'Classic design',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Simulating a queue with two stacks: enqueue pushes onto stack A; dequeue…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'pops from A directly', 'is_correct': False},
                                {'id': 'b', 'text': 'if B is empty, dump A into B (reversing order) then pop B', 'is_correct': True},
                                {'id': 'c', 'text': 'sorts A', 'is_correct': False},
                                {'id': 'd', 'text': 'pops the middle of A', 'is_correct': False},
                            ],
                            'explain': 'Two reversals = original order; each element moves at most twice → amortised O(1) per operation.',
                        },
                        {
                            'slug': 'q5-bracket-leftover',
                            'title': 'End-of-scan check',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The bracket algorithm finishes with a non-empty stack. The input…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'is valid', 'is_correct': False},
                                {'id': 'b', 'text': 'has unclosed opening brackets', 'is_correct': True},
                                {'id': 'c', 'text': 'has extra closing brackets', 'is_correct': False},
                                {'id': 'd', 'text': 'was empty', 'is_correct': False},
                            ],
                            'explain': 'Leftover openers never met their closers; extra closers would have popped an empty stack instead.',
                        },
                        {
                            'slug': 'q5-window-structure',
                            'title': 'Sliding window tool',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Keeping the latest k items while dropping the oldest each step is naturally done with…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'a stack', 'is_correct': False},
                                {'id': 'b', 'text': 'a deque (append right, popleft left)', 'is_correct': True},
                                {'id': 'c', 'text': 'insertion at the front of a list', 'is_correct': False},
                                {'id': 'd', 'text': 'a binary tree', 'is_correct': False},
                            ],
                            'explain': 'Window = FIFO expiry at one end, arrivals at the other — deque\u2019s home turf.',
                        },
                        {
                            'slug': 'q5-empty-pop',
                            'title': 'Guard the pop',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Popping an empty stack in Python…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'returns None quietly', 'is_correct': False},
                                {'id': 'b', 'text': 'raises IndexError', 'is_correct': True},
                                {'id': 'c', 'text': 'returns 0', 'is_correct': False},
                                {'id': 'd', 'text': 'reverses the stack', 'is_correct': False},
                            ],
                            'explain': 'Underflow is an exception in Python (undefined behaviour in raw C++) — check emptiness first.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 6 ════════════════════
        {
            'title': 'Searching Algorithms',
            'slug': 'searching',
            'description': 'Linear search, binary search implemented carefully, and when each applies.',
            'lessons': [
                {
                    'title': 'Linear Search',
                    'slug': 'linear-search',
                    'objective': 'Implement linear search and state its cases precisely.',
                    'duration': 8,
                    'body': """# The honest default: look at everything

When data is **unordered**, no algorithm can do better than checking each
element — linear search is optimal, not lazy.

```python
def linear_search(arr, target):
    for i, x in enumerate(arr):     # index and value together
        if x == target:
            return i                # found: return position
    return -1                       # universal "absent" sentinel
```

```cpp
int linearSearch(const std::vector<int>& a, int t) {
    for (size_t i = 0; i < a.size(); ++i)
        if (a[i] == t) return static_cast<int>(i);
    return -1;
}
```

### Dry-run — target 7 in [3, 1, 7, 9]
| i | arr[i] | == 7? | action |
|---|---|---|---|
| 0 | 3 | no | next |
| 1 | 1 | no | next |
| 2 | 7 | **yes** | return 2 |

**Cases:** best O(1) (first slot) · worst O(n) (last or absent) ·
average O(n/2) → O(n). Space O(1).

## The -1 convention
Returning the found **index** (not the value — the caller has it) and
**-1** for absent lets one integer answer both "is it there?" and
"where?". Alternatives: `None`, `not found` exceptions — know your
language's custom.

## Real-world application
Small data, one-off lookup: scanning a config list at startup is exactly
linear search — when n is tiny, the simplest optimal method is also the
fastest in real time (no sorting tax).

## Common mistakes
- Returning `i` after the loop even when not found (forgot the -1).
- Forgetting the scan stops early: `break`/`return` inside the loop is
  what makes best case O(1).

## Lesson summary
Linear search: enumerate, compare, early return; O(n) worst, O(1) space;
the correct choice whenever data is unsorted or tiny.""",
                    'exercises': [
                        {
                            'slug': 'why-linear-optimal-unsorted',
                            'title': 'The lower bound argument',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why can nothing beat O(n) on a truly unordered list?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Computers are limited to one comparison per element', 'is_correct': False},
                                {'id': 'b', 'text': 'Any unchecked element could be the target — skipping risks a wrong "absent"', 'is_correct': True},
                                {'id': 'c', 'text': 'Sorting would be required and forbidden', 'is_correct': False},
                                {'id': 'd', 'text': 'Linear search has hidden cache benefits', 'is_correct': False},
                            ],
                            'explain': 'Without order there is no information to exploit; the worst case forces a full scan. This argument is the seed of all lower-bound thinking.',
                        },
                        {
                            'slug': 'linear-code',
                            'title': 'Code: search it yourself',
                            'exercise_type': 'code',
                            'instructions': (
                                'Print the index of 15 in [4, 8, 15, 16, 23] using a '
                                'linear search; print -1 if absent. One number only.'
                            ),
                            'context': 'Implement the lesson function and call it.',
                            'constraints': 'Use a loop; do not use list.index().',
                            'expected_output': '2',
                            'starter_code': 'nums = [4, 8, 15, 16, 23]\ntarget = 15\n# print the index of target, or -1\n',
                            'solution_code': 'nums = [4, 8, 15, 16, 23]\ntarget = 15\nfor i, x in enumerate(nums):\n    if x == target:\n        print(i)\n        break\nelse:\n    print(-1)',
                            'test_cases': [{'input': '', 'expected_output': '2'}],
                            'explain': '15 sits at index 2; the loop-else runs only if break never fired — Python\u2019s tidy sentinel.',
                            'xp_reward': 100,
                        },
                    ],
                },
                {
                    'title': 'Binary Search: The Sorted Power Move',
                    'slug': 'binary-search',
                    'objective': 'Implement iterative binary search with correct bounds and explain the halving.',
                    'duration': 16,
                    'body': """# Divide the search space in half, every step

**Precondition: the data must be sorted.** Binary search compares the
target with the **middle** element; one comparison eliminates half of
everything.

```python
def binary_search(arr, target):      # arr must be sorted ascending
    lo, hi = 0, len(arr) - 1         # inclusive bounds
    while lo <= hi:                  # while a candidate remains
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1             # target is to the RIGHT
        else:
            hi = mid - 1             # target is to the LEFT
    return -1                        # bounds crossed: absent
```

### Dry-run — target 23 in [4, 8, 15, 16, 23, 42, 55]
| lo | hi | mid | arr[mid] | decision | new range |
|---|---|---|---|---|---|
| 0 | 6 | 3 | 16 | 23 > 16 | lo=4 |
| 4 | 6 | 5 | 42 | 23 < 42 | hi=4 |
| 4 | 4 | 4 | 23 | **found** | return 4 |

7 elements → 3 comparisons. The count is how many halvings reach size 1:
**⌊log₂ n⌋ + 1**. For 1,000,000 items: 20 steps worst case.

## The three details that make or break it (classic bug list)
1. **`hi = len(arr) - 1` and `while lo <= hi`** — inclusive range, so
   `lo == hi` is still one live candidate. `lo < hi` misses the last
   element; mismatching these two is the #1 exam error.
2. **`mid + 1 / mid - 1`** when moving bounds — mid itself was already
   checked; keeping it re-checks forever or loops.
3. **(lo + hi) // 2 overflow** — a famous historical bug (Java/Python
   big ints save you; C++ int overflows). Correct habit: `lo + (hi - lo) // 2`.

## Binary search C++ (same skeleton)
```cpp
int lo = 0, hi = (int)a.size() - 1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == t) return mid;
    if (a[mid] < t) lo = mid + 1; else hi = mid - 1;
}
return -1;
```

## Searching by *condition*, not equality
The general form finds the **first position where a condition becomes
true** (first ≥ x, last ≤ x). std::lower_bound / bisect_left implement
exactly this — same halving, different test.

## Cost and requirement
O(log n) time, O(1) space — but **sorting first costs O(n log n)**.
Binary search pays off when you search the SAME sorted data many times;
for one search on unsorted data, linear is the honest optimum.

## Common mistakes
- Running it on unsorted data and blaming the algorithm.
- Off-by-one loops (`<` vs `<=`) — trace [5] searching 5: with `lo < hi`
  it returns -1.
- Forgetting mid is already compared when tightening bounds.

## Lesson summary
Binary search: inclusive bounds, ≤ loop, mid±1 updates, overflow-safe
mid; log₂ n comparisons by halving; requires sorted data and rewards
repeated searches.""",
                    'exercises': [
                        {
                            'slug': 'comparisons-count',
                            'title': 'Halving count',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Worst-case comparisons of binary search on 128 sorted items:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '7', 'is_correct': True},
                                {'id': 'b', 'text': '64', 'is_correct': False},
                                {'id': 'c', 'text': '128', 'is_correct': False},
                                {'id': 'd', 'text': '1', 'is_correct': False},
                            ],
                            'explain': '128 = 2⁷: seven halvings reach one candidate.',
                        },
                        {
                            'slug': 'loop-condition',
                            'title': 'The ≤ choice',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'With inclusive bounds (hi = n-1), the loop must run while…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'lo < hi — equal means done', 'is_correct': False},
                                {'id': 'b', 'text': 'lo <= hi — lo == hi is still one unexamined element', 'is_correct': True},
                                {'id': 'c', 'text': 'mid != target', 'is_correct': False},
                                {'id': 'd', 'text': 'hi > 0', 'is_correct': False},
                            ],
                            'explain': 'Inclusive range: a single live candidate sits at lo == hi; strict < skips it (the classic bug).',
                        },
                        {
                            'slug': 'implement-bs',
                            'title': 'Code: binary search it',
                            'exercise_type': 'code',
                            'instructions': (
                                'The sorted list [2, 5, 8, 12, 17, 21, 27] is given. '
                                'Implement binary search and print the index of 21 '
                                '(or -1 if absent). One number only.'
                            ),
                            'context': 'Use the exact skeleton; check yourself against the dry-run table method.',
                            'constraints': 'Do not use the `in` operator or list.index().',
                            'expected_output': '5',
                            'starter_code': 'arr = [2, 5, 8, 12, 17, 21, 27]\ntarget = 21\n# binary search: print index or -1\n',
                            'solution_code': 'arr = [2, 5, 8, 12, 17, 21, 27]\ntarget = 21\nlo, hi = 0, len(arr) - 1\nwhile lo <= hi:\n    mid = lo + (hi - lo) // 2\n    if arr[mid] == target:\n        print(mid)\n        break\n    elif arr[mid] < target:\n        lo = mid + 1\n    else:\n        hi = mid - 1\nelse:\n    print(-1)',
                            'test_cases': [{'input': '', 'expected_output': '5'}],
                            'explain': 'Path: mid 3 (12) → right; mid 5 (21) → found. Two comparisons for 7 items — the halving made visible.',
                            'xp_reward': 150,
                        },
                        {
                            'slug': 'when-not-to-binary',
                            'title': 'Sort tax',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'One lookup in an unsorted 10,000-record list: best plan…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Sort (O(n log n)) then binary search', 'is_correct': False},
                                {'id': 'b', 'text': 'Linear scan — sorting for a single lookup costs more than it saves', 'is_correct': True},
                                {'id': 'c', 'text': 'Binary search directly on the unsorted data', 'is_correct': False},
                                {'id': 'd', 'text': 'Hash the whole list twice', 'is_correct': False},
                            ],
                            'explain': 'Binary search\u2019s precondition plus its sort tax decide when it is worth it: repeated searches on the same sorted data.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 6 Quiz',
                    'slug': 'searching-quiz',
                    'objective': 'Check search reasoning.',
                    'duration': 4,
                    'body': """# Chapter 6 quiz

Five questions on the two searches.""",
                    'exercises': [
                        {
                            'slug': 'q6-halving-27',
                            'title': 'Worst-case steps',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Binary search on 27 sorted elements needs at most how many comparisons?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '5', 'is_correct': True},
                                {'id': 'b', 'text': '13', 'is_correct': False},
                                {'id': 'c', 'text': '27', 'is_correct': False},
                                {'id': 'd', 'text': '3', 'is_correct': False},
                            ],
                            'explain': '27→13→6→3→1→0: five halvings. log₂(27) ≈ 4.75 → ⌊⌋+1 = 5.',
                        },
                        {
                            'slug': 'q6-mid-bug',
                            'title': 'The endless loop',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Writing `hi = mid` (instead of mid - 1) when the target is smaller can cause…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'an infinite loop when lo == mid (mid never excluded)', 'is_correct': True},
                                {'id': 'b', 'text': 'wrong answer but always terminates', 'is_correct': False},
                                {'id': 'c', 'text': 'a memory leak', 'is_correct': False},
                                {'id': 'd', 'text': 'nothing — both are fine', 'is_correct': False},
                            ],
                            'explain': 'Already-compared mid must leave the range, or a two-element range can never shrink.',
                        },
                        {
                            'slug': 'q6-precondition',
                            'title': 'Broken precondition',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Running binary search on [5, 2, 9, 1] for 2 returns…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'index 1 — it always finds the truth', 'is_correct': False},
                                {'id': 'b', 'text': 'possibly -1: the halving logic assumes order to eliminate halves', 'is_correct': True},
                                {'id': 'c', 'text': 'a crash', 'is_correct': False},
                                {'id': 'd', 'text': 'the whole list', 'is_correct': False},
                            ],
                            'explain': '"arr[mid] < target means go right" is meaningless without sortedness; elimination logic dies.',
                        },
                        {
                            'slug': 'q6-overflow-mid',
                            'title': 'Overflow-safe mid',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the C++-safe midpoint expression: '
                                'mid = lo + (______ - lo) / 2;  (write the variable name)'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'hi',
                            'explain': 'lo + (hi-lo)/2 never adds two huge indexes; the historical Java bug is the war story.',
                        },
                        {
                            'slug': 'q6-which-search-match',
                            'title': 'Match problem to method',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct pairings.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Dictionary word lookup while scanning alphabetically: binary-style halving fits', 'is_correct': True},
                                {'id': 'b', 'text': 'First item matching a test in unsorted data: linear scan', 'is_correct': True},
                                {'id': 'c', 'text': 'Repeated phonebook searches: sort once, binary search many', 'is_correct': True},
                                {'id': 'd', 'text': 'Binary search on a linked list: best use of the structure', 'is_correct': False},
                            ],
                            'explain': 'Binary search needs O(1) midpoint access — linked lists destroy that advantage (that pairing is a classic interview trick).',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 7 ════════════════════
        {
            'title': 'Sorting Algorithms',
            'slug': 'sorting',
            'description': 'The three classroom sorts, then merge sort and quick sort, plus stability and the practical comparison.',
            'lessons': [
                {
                    'title': 'Bubble, Selection and Insertion Sort',
                    'slug': 'simple-sorts',
                    'objective': 'Implement the three O(n²) sorts and dry-run them step by step.',
                    'duration': 15,
                    'body': """# Three sorts you must be able to write from memory

These three are slow — O(n²) comparisons — but every CS exam and interview
warm-up asks for them, and they teach the two moves every sort shares:
**compare two elements** and **place them in order**.

## Bubble sort — push the big ones down
Repeatedly walk the list, swapping adjacent pairs that are out of order.
Each full pass "bubbles" the largest remaining value to the end, so pass
*i* needs one fewer look.

```python
def bubble_sort(a):
    n = len(a)
    for i in range(n - 1):            # n-1 passes are enough
        for j in range(n - 1 - i):    # tail is already sorted
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a
```

Dry-run on `[5, 2, 9, 1]`:

| Pass | Comparisons / swaps | Array after pass |
|---|---|---|
| 1 | (5,2) swap → (5,9) ok → (9,1) swap | `[2, 5, 1, 9]` |
| 2 | (2,5) ok → (5,1) swap | `[2, 1, 5, 9]` |
| 3 | (2,1) swap | `[1, 2, 5, 9]` |

Largest 9 settled after pass 1, second-largest after pass 2 — that is why
the inner loop shrinks by `i` each pass. An optional `swapped` flag lets
an almost-sorted list exit early: best case O(n).

## Selection sort — find the min, put it front
Scan the unsorted part for its smallest element, swap it to the front of
the unsorted part, repeat. Fewer *swaps* than bubble sort (at most n-1),
but always the same Θ(n²) *comparisons* — no early exit.

```python
def selection_sort(a):
    n = len(a)
    for i in range(n - 1):
        min_at = i
        for j in range(i + 1, n):     # find min in a[i:]
            if a[j] < a[min_at]:
                min_at = j
        a[i], a[min_at] = a[min_at], a[i]
    return a
```

Dry-run `[5, 2, 9, 1]`: pass 1 finds 1 at index 3, swaps → `[1, 2, 9, 5]`;
pass 2's min is 2 already placed; pass 3 finds 5, swaps → `[1, 2, 5, 9]`.

## Insertion sort — like sorting playing cards
Take each element and insert it into the sorted prefix, shifting larger
values right — exactly how most people sort a hand of cards.

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:  # shift bigger elements right
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a
```

Its superpower: **O(n) on nearly-sorted data** and genuinely useful for
small pieces — real libraries (Python's Timsort, C++'s introsort) switch
to insertion sort once a subrange shrinks below ~16–32 items.

## Expected output
All three turn `[5, 2, 9, 1]` into `[1, 2, 5, 9]`. They differ in *how
many comparisons and swaps* it takes and in *side benefits* (early exit,
minimum swaps, near-sorted speed).

## Common mistakes
- Off-by-one loop bounds: bubble's inner loop runs to `n-1-i`, selection's
  inner scan starts at `i+1`, insertion compares `a[j] > key` *before*
  writing — each boundary protects an already-settled region.
- Forgetting the swap in selection sort when `min_at == i` is harmless but
  scanning `range(n)` instead of `range(i + 1, n)` can re-select settled
  elements.
- Claiming selection sort is "faster because fewer swaps" without noting
  it still does every comparison.

## Lesson summary
Bubble: adjacent swaps, shrinks each pass. Selection: pick the min,
swap once per pass. Insertion: shift-and-insert, fast on near-sorted
input. All O(n²) worst case; insertion sort earns its place inside real
library sorts.
""",
                    'exercises': [
                        {
                            'slug': 'implement-bubble',
                            'title': 'Write bubble sort',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'Implement bubble_sort(a) so it returns the list sorted '
                                'ascending by repeatedly swapping adjacent out-of-order '
                                'pairs, then run it on [5, 2, 9, 1] and print the result '
                                'as space-separated values: 1 2 5 9'
                            ),
                            'context': 'Watch the inner loop bound shrink as the tail settles.',
                            'xp_reward': 120,
                            'starter_code': (
                                'def bubble_sort(a):\n'
                                '    # swap adjacent out-of-order pairs until sorted\n'
                                '    return a\n'
                                '\n'
                                'arr = [5, 2, 9, 1]\n'
                                "print(' '.join(map(str, bubble_sort(arr))))\n"
                            ),
                            'solution_code': (
                                'def bubble_sort(a):\n'
                                '    n = len(a)\n'
                                '    for i in range(n - 1):\n'
                                '        for j in range(n - 1 - i):\n'
                                '            if a[j] > a[j + 1]:\n'
                                '                a[j], a[j + 1] = a[j + 1], a[j]\n'
                                '    return a\n'
                                '\n'
                                'arr = [5, 2, 9, 1]\n'
                                "print(' '.join(map(str, bubble_sort(arr))))\n"
                            ),
                            'expected_output': '1 2 5 9',
                            'test_cases': [{'input': '', 'expected_output': '1 2 5 9'}],
                            'explain': 'n-1 passes, inner loop to n-1-i; a[j] > a[j+1] triggers the swap.',
                        },
                        {
                            'slug': 'insertion-nearly-sorted',
                            'title': 'Why insertion sort loves near-sorted data',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why does insertion sort run in close to O(n) on a list that is already almost sorted?',
                            'xp_reward': 60,
                            'choices': [
                                {'id': 'a', 'text': 'The while-shift loop stops almost immediately for each key because the sorted prefix usually ends before one comparison', 'is_correct': True},
                                {'id': 'b', 'text': 'It skips elements at random', 'is_correct': False},
                                {'id': 'c', 'text': 'It uses a hash table internally', 'is_correct': False},
                                {'id': 'd', 'text': 'It never performs comparisons, only moves', 'is_correct': False},
                            ],
                            'explain': 'Each key finds its place after ~1 comparison when the prefix is already ordered — the inner loop is what costs, and it barely runs.',
                        },
                        {
                            'slug': 'counting-selection',
                            'title': 'Selection-sort comparisons',
                            'exercise_type': 'output_prediction',
                            'instructions': 'How many comparisons does selection sort make on 4 elements? (Pass 1: 3, pass 2: 2, pass 3: 1. Answer with the number only.)',
                            'xp_reward': 40,
                            'expected_output': '6',
                            'explain': 'n(n-1)/2 = 4·3/2 = 6 — fixed regardless of input order.',
                        },
                    ],
                },
                {
                    'title': 'Merge Sort — Divide and Conquer',
                    'slug': 'merge-sort',
                    'objective': 'Explain divide & conquer and implement merge sort with its cost analysis.',
                    'duration': 15,
                    'body': """# Split, sort, combine

**Divide and conquer** solves a problem by: ① dividing it into smaller
independent copies, ② solving each copy, ③ combining the answers. Merge
sort is the cleanest introduction:

1. **Divide:** split the list in half.
2. **Conquer:** sort each half recursively (a 1-element list is already sorted).
3. **Combine:** *merge* the two sorted halves into one sorted list.

The magic is step 3. Merging two sorted lists is O(n) and easy — walk two
fingers, always take the smaller head:

```python
def merge(left, right):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:      # <= keeps stability
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])             # one side may have leftovers
    out.extend(right[j:])
    return out

def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    return merge(left, right)
```

## Dry run on [8, 3, 5, 1]

| Step | What happens | Result |
|---|---|---|
| Divide | `[8,3]` / `[5,1]`, then `[8]` `[3]`, `[5]` `[1]` | 4 singletons |
| Merge | `[8]`+`[3]` → `[3,8]`; `[5]`+`[1]` → `[1,5]` | two sorted halves |
| Merge | `[3,8]`+`[1,5]`: 1, 3, 5, 8 | `[1, 3, 5, 8]` |

## Why the cost is O(n log n)
Each **level** of recursion merges every element exactly once → O(n) work
per level. Halving until singletons takes **log₂n levels**. Total:
O(n log n) — best, worst, and average. Space: O(n) for the auxiliary
lists (its main drawback versus in-place sorts).

## C++ parallel
`std::inplace_merge` merges without extra space (slowly); the stable
library sort `std::stable_sort` is merge-sort-family. Python's built-in
`sorted()` is **Timsort** — a tuned, run-detecting merge/insertion hybrid.

## Common mistakes
- Merging without the leftover `extend` calls — the result loses elements.
- Using `<` instead of `<=` on equal elements: still correct output, but
  no longer **stable** (see the stability lesson).
- Forgetting the base case `len(a) <= 1` → infinite recursion.

## Lesson summary
Split in half, sort recursively, merge linearly: O(n log n) guaranteed,
stable, at the price of O(n) extra memory.""",
                    'exercises': [
                        {
                            'slug': 'implement-merge',
                            'title': 'Merge two sorted lists',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'Write merge(left, right) that combines two sorted lists '
                                'into one sorted list using the two-finger walk, then '
                                'print merge([1, 4, 7], [2, 3, 8, 9])'
                            ),
                            'context': 'Compare the two heads, move the smaller one, extend leftovers at the end.',
                            'xp_reward': 120,
                            'starter_code': (
                                'def merge(left, right):\n'
                                '    # two-finger merge\n'
                                '    return out\n'
                                '\n'
                                'print(merge([1, 4, 7], [2, 3, 8, 9]))\n'
                            ),
                            'solution_code': (
                                'def merge(left, right):\n'
                                '    out, i, j = [], 0, 0\n'
                                '    while i < len(left) and j < len(right):\n'
                                '        if left[i] <= right[j]:\n'
                                '            out.append(left[i]); i += 1\n'
                                '        else:\n'
                                '            out.append(right[j]); j += 1\n'
                                '    out.extend(left[i:])\n'
                                '    out.extend(right[j:])\n'
                                '    return out\n'
                                '\n'
                                'print(merge([1, 4, 7], [2, 3, 8, 9]))\n'
                            ),
                            'expected_output': '[1, 2, 3, 4, 7, 8, 9]',
                            'test_cases': [{'input': '', 'expected_output': '[1, 2, 3, 4, 7, 8, 9]'}],
                            'explain': 'The two extend() calls after the loop are what most people forget; without them the tail disappears.',
                        },
                        {
                            'slug': 'merge-levels',
                            'title': 'Recursion levels',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Merge sort splits the list in half until size 1. How many levels for 8 elements? (Answer with the number only.)',
                            'xp_reward': 40,
                            'expected_output': '3',
                            'explain': '8 → 4 → 2 → 1 is 3 halvings: log₂8 = 3.',
                        },
                        {
                            'slug': 'merge-worst-case',
                            'title': 'Merge sort worst case',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What is merge sort\'s worst-case time complexity, and why is it the same as its best case?',
                            'xp_reward': 60,
                            'choices': [
                                {'id': 'a', 'text': 'O(n log n) — it always splits evenly and always merges every element once per level', 'is_correct': True},
                                {'id': 'b', 'text': 'O(n²) — two nested loops', 'is_correct': False},
                                {'id': 'c', 'text': 'O(n) — merging is linear', 'is_correct': False},
                                {'id': 'd', 'text': 'O(log n) — halving dominates', 'is_correct': False},
                            ],
                            'explain': 'Input order never changes the work: the split pattern and the per-level merge are fixed, so best = worst = O(n log n).',
                        },
                    ],
                },
                {
                    'title': 'Quick Sort and Stability',
                    'slug': 'quick-sort-stability',
                    'objective': 'Implement quick sort, explain partitions, and define stable vs unstable sorting.',
                    'duration': 15,
                    'body': """# Quick sort — partition around a pivot

Quick sort also divides and conquers, but it splits **by value, not by
position**: pick a **pivot**, **partition** the array so everything ≤
pivot is left and everything > pivot is right, then recurse on the two
sides. No merge step needed — the partitioning *is* the work.

```python
def quick_sort(a):
    if len(a) <= 1:
        return a
    pivot = a[len(a) // 2]                 # middle element as pivot
    low    = [x for x in a if x <  pivot]  # strictly smaller
    equal  = [x for x in a if x == pivot]  # duplicates grouped
    high   = [x for x in a if x >  pivot]  # strictly larger
    return quick_sort(low) + equal + quick_sort(high)
```

## Dry run on [8, 3, 5, 1] (pivot 5)

| Step | Result |
|---|---|
| Partition | low `[3, 1]` · equal `[5]` · high `[8]` |
| Recurse low (pivot 3) | `[1] + [3] + []` → `[1, 3]` |
| Combine | `[1, 3] + [5] + [8]` → `[1, 3, 5, 8]` |

**Cost:** average O(n log n) with small constants and in-place variants;
**worst case O(n²)** when pivots keep landing at the extreme (sorted
input + first-element pivot is the textbook disaster). Randomised or
median-of-three pivots make that practically impossible, which is why
C++'s `std::sort` is **introsort** — quick sort that falls back to heap
sort if recursion deepens too much.

## Stable vs unstable
A sort is **stable** when equal elements keep their original relative
order. Sort students by grade only: a stable sort preserves registration
order inside each grade band; an unstable one scrambles it.

- Stable: insertion, merge, bubble, Python's `sorted()` (Timsort), C++ `std::stable_sort`.
- Unstable: quick sort (the list-comprehension version above is stable
  by luck of scanning left-to-right, but classic in-place partitioning
  is not), selection, heap, C++ `std::sort`.

## Which do you actually use?
In real code you call the library sort. You learn these because: (1)
interviews ask, (2) the *design strategies* — divide & conquer, pivot
partitioning, incremental insertion — recur everywhere, and (3) knowing
merge vs quick explains why libraries are hybrid.

| Sort | Best | Avg | Worst | Space | Stable |
|---|---|---|---|---|---|
| Bubble | O(n) | O(n²) | O(n²) | O(1) | yes |
| Selection | O(n²) | O(n²) | O(n²) | O(1) | no |
| Insertion | O(n) | O(n²) | O(n²) | O(1) | yes |
| Merge | O(n log n) | O(n log n) | O(n log n) | O(n) | yes |
| Quick | O(n log n) | O(n log n) | O(n²) | O(log n) in-place | no |

## Common mistakes
- Choosing the first element as pivot on possibly-sorted data — the
  O(n²) trap.
- Losing duplicates: a two-list partition (`<` and `>=`) drops nothing
  only if every element lands in exactly one list; three-list partitioning
  makes it obvious.
- Calling quick sort "always faster than merge" — on linked lists or when
  stability matters, merge is often the better pick.

## Lesson summary
Quick sort partitions by value and recurses: fastest average case, O(n²)
in theory, unstable. Stability = equal keys keep input order; it decides
merge-vs-quick as much as raw speed does.""",
                    'exercises': [
                        {
                            'slug': 'implement-quick',
                            'title': 'Write quick sort',
                            'exercise_type': 'code',
                            'difficulty': 'hard',
                            'instructions': (
                                'Implement quick_sort(a) with the three-list partitioning '
                                '(low/equal/high around a pivot) and print '
                                'quick_sort([8, 3, 1, 9, 2])'
                            ),
                            'context': 'Base case: a list of 0 or 1 elements is already sorted.',
                            'xp_reward': 150,
                            'starter_code': (
                                'def quick_sort(a):\n'
                                '    # base case + low/equal/high partition\n'
                                '    return a\n'
                                '\n'
                                'print(quick_sort([8, 3, 1, 9, 2]))\n'
                            ),
                            'solution_code': (
                                'def quick_sort(a):\n'
                                '    if len(a) <= 1:\n'
                                '        return a\n'
                                '    pivot = a[len(a) // 2]\n'
                                '    low = [x for x in a if x < pivot]\n'
                                '    equal = [x for x in a if x == pivot]\n'
                                '    high = [x for x in a if x > pivot]\n'
                                '    return quick_sort(low) + equal + quick_sort(high)\n'
                                '\n'
                                'print(quick_sort([8, 3, 1, 9, 2]))\n'
                            ),
                            'expected_output': '[1, 2, 3, 8, 9]',
                            'test_cases': [{'input': '', 'expected_output': '[1, 2, 3, 8, 9]'}],
                            'explain': 'Grouping equal elements separately is what keeps duplicates intact and all-equal input fast.',
                        },
                        {
                            'slug': 'stability-definition',
                            'title': 'What stability guarantees',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A sort is stable if…',
                            'xp_reward': 60,
                            'choices': [
                                {'id': 'a', 'text': 'elements that compare equal keep their original relative order after sorting', 'is_correct': True},
                                {'id': 'b', 'text': 'it never crashes on large input', 'is_correct': False},
                                {'id': 'c', 'text': 'it sorts in O(n log n) every time', 'is_correct': False},
                                {'id': 'd', 'text': 'it uses no extra memory', 'is_correct': False},
                            ],
                            'explain': 'Stability is about equal keys, not robustness or memory — it is what makes multi-key sorting (grade, then name) work by sorting secondary key first.',
                        },
                        {
                            'slug': 'quick-worst-trigger',
                            'title': 'Quick sort\'s O(n²) trigger',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL situations that push quick sort toward its O(n²) worst case.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Already-sorted input with first-element pivot', 'is_correct': True},
                                {'id': 'b', 'text': 'Pivot repeatedly lands at one extreme of the value range', 'is_correct': True},
                                {'id': 'c', 'text': 'Partitions come out near 50/50 every time', 'is_correct': False},
                                {'id': 'd', 'text': 'Using a middle or randomised pivot', 'is_correct': False},
                            ],
                            'explain': 'Balanced partitions give log n depth — the disaster only strikes when every split is maximally lopsided (n + 0).',
                        },
                        {
                            'slug': 'q7-pivot-output',
                            'title': 'Dry-run the partition',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Array [7, 2, 6, 4, 9], pivot 6. Using three-list partitioning (low: <pivot, equal: =pivot, high: >pivot), write the low list exactly as Python prints it.',
                            'xp_reward': 40,
                            'expected_output': '[2, 4]',
                            'explain': 'Elements below 6 in scan order are 2 then 4 — list comprehensions preserve relative order.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 7 Quiz',
                    'slug': 'sorting-quiz',
                    'objective': 'Check your command of the five sorts, their costs, and stability.',
                    'duration': 10,
                    'body': """# Chapter 7 Quiz

Six questions over the simple sorts, merge and quick sort, and stability.
Recall the dry-run tables and the comparison chart before answering.""",
                    'exercises': [
                        {
                            'slug': 'q7-which-o-n2',
                            'title': 'Which is not O(n²)',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which sort does NOT have O(n²) worst-case time?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Merge sort', 'is_correct': True},
                                {'id': 'b', 'text': 'Bubble sort', 'is_correct': False},
                                {'id': 'c', 'text': 'Selection sort', 'is_correct': False},
                                {'id': 'd', 'text': 'Quick sort (bad pivots)', 'is_correct': False},
                            ],
                            'explain': 'Merge\'s split is positional, never value-dependent: worst case stays O(n log n).',
                        },
                        {
                            'slug': 'q7-after-pass1',
                            'title': 'After one bubble pass',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Bubble-sort start: [6, 4, 8, 2]. What is the array after the FIRST full pass? Format: space-separated, like 4 6 2 8',
                            'xp_reward': 40,
                            'expected_output': '4 6 2 8',
                            'explain': 'Swaps: (6,4)→[4,6,…], (6,8) ok, (8,2)→[4,6,2,8]. The largest lands at the end after pass 1.',
                        },
                        {
                            'slug': 'q7-card-sorter',
                            'title': 'The card-hand sort',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which sort matches how most people sort playing cards in hand — take the next card and insert it into the sorted part?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Insertion sort', 'is_correct': True},
                                {'id': 'b', 'text': 'Merge sort', 'is_correct': False},
                                {'id': 'c', 'text': 'Selection sort', 'is_correct': False},
                                {'id': 'd', 'text': 'Heap sort', 'is_correct': False},
                            ],
                            'explain': 'Insertion sort literally is the card-hand method — and O(n log n)-ish hybrids lean on it for small runs.',
                        },
                        {
                            'slug': 'q7-merge-space',
                            'title': 'Merge sort extra space',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Merge sort\'s auxiliary space complexity is O(__) (one term exactly as written here, lowercase: n, log n, or 1).',
                            'xp_reward': 40,
                            'solution_code': 'n',
                            'explain': 'Every merge copies elements into new lists — O(n) extra memory is merge sort\'s classic trade.',
                        },
                        {
                            'slug': 'q7-stable-pick',
                            'title': 'Choosing a stable sort',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL stable sorts.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Merge sort', 'is_correct': True},
                                {'id': 'b', 'text': 'Insertion sort', 'is_correct': True},
                                {'id': 'c', 'text': 'Python\'s sorted() (Timsort)', 'is_correct': True},
                                {'id': 'd', 'text': 'C++ std::sort', 'is_correct': False},
                            ],
                            'explain': 'std::sort (introsort) is famously unstable; std::stable_sort exists precisely because of that.',
                        },
                        {
                            'slug': 'q7-divide-conquer',
                            'title': 'Divide & conquer steps',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Divide and conquer has three steps: divide, conquer, and ____ (one word, lowercase, the combine step for merge sort).',
                            'xp_reward': 40,
                            'solution_code': 'merge',
                            'explain': 'Divide in half, conquer recursively, merge the sorted halves — quick sort instead partitions.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 8 ════════════════════
        {
            'title': 'Trees and Binary Search Trees',
            'slug': 'trees',
            'description': 'Tree vocabulary, the BST contract, insert/search, and the four classic traversals.',
            'lessons': [
                {
                    'title': 'Tree Vocabulary',
                    'slug': 'tree-terminology',
                    'objective': 'Name every part of a tree and tell binary trees from BSTs.',
                    'duration': 12,
                    'body': """# From lists to hierarchies

Arrays and linked lists model **sequences**. But most real data is
**hierarchical**: a file system (folders inside folders), an organisation
chart, an HTML document (the DOM), a chess endgame (move trees). A
**tree** is the data structure for hierarchy.

## Definitions you must own
- **Node:** one item, holding a value and links to its children.
- **Root:** the top node — the only one with no parent.
- **Parent / child / sibling:** the link relationships, exactly like a family tree.
- **Leaf:** a node with no children.
- **Edge:** the parent→child link itself.
- **Depth** of a node: edges from the root down to it (root: depth 0).
- **Height** of a tree: longest root→leaf path in edges (single node: height 0).

A **binary tree** is a tree where every node has at most two children,
called **left** and **right**. That tiny restriction is what makes the
algorithms clean: every node has at most two places to go.

## Binary tree vs Binary Search Tree
A plain binary tree says nothing about *which* value goes left or right.
A **Binary Search Tree (BST)** adds the ordering contract:

> for every node: everything in its **left** subtree < node < everything
> in its **right** subtree (no duplicates in the strict form).

The contract holds **recursively** — not just at the root. A tree where
the root looks fine but some grandchild violates the rule is NOT a BST.

## Why BSTs are fast — and when they aren't
Search in a BST uses the same halving instinct as binary search: compare
with the node, go left or right, discard the other subtree. Each step
eliminates a whole subtree — so cost is proportional to **height**:

- Balanced BST: height ≈ log₂n → search/insert O(log n). ✅
- Degenerate BST (insert sorted data 1,2,3,…): every node only has a
  right child — the tree is a **linked list in disguise**, height n, O(n)
  per operation. ❌

Keeping trees balanced is the job of advanced variants (AVL, red-black
trees — mentioned in the hashing/graphs chapter's closing notes) that
rotate nodes after inserts so height stays logarithmic.

## Balanced vs complete vs full (exam vocabulary)
- **Full:** every node has 0 or 2 children.
- **Complete:** every level full except possibly the last, which is
  filled left-to-right (this is what heap arrays rely on).
- **Balanced:** left/right subtree heights of every node differ by a
  small bound (AVL: ≤ 1).

## Common mistakes
- Calling any connected diagram a tree — a tree has **no cycles** and
  exactly one path from root to every node.
- Checking only direct children when validating a BST: `root.right.left`
  must still be greater than the root.
- Confusing depth (node→root) with height (node→deepest leaf).

## Lesson summary
Trees model hierarchy; binary trees cap children at two; BSTs add the
recursive left<node<right contract; everything a BST does fast depends on
height staying logarithmic.""",
                    'exercises': [
                        {
                            'slug': 'leaf-definition',
                            'title': 'Naming the nodes',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In tree vocabulary, what is a leaf?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'A node with no children', 'is_correct': True},
                                {'id': 'b', 'text': 'The root of a small tree', 'is_correct': False},
                                {'id': 'c', 'text': 'A node with exactly one child', 'is_correct': False},
                                {'id': 'd', 'text': 'The last value inserted', 'is_correct': False},
                            ],
                            'explain': 'Leaves terminate branches — no children. Insert order has nothing to do with it.',
                        },
                        {
                            'slug': 'bst-contract',
                            'title': 'The BST ordering rule',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which statement is the BST contract?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'For every node, all left-subtree values < node < all right-subtree values', 'is_correct': True},
                                {'id': 'b', 'text': 'Left child < right child for every parent only', 'is_correct': False},
                                {'id': 'c', 'text': 'Values arrive in sorted insertion order', 'is_correct': False},
                                {'id': 'd', 'text': 'Every level is completely filled', 'is_correct': False},
                            ],
                            'explain': 'Option b is the classic trap: the rule must hold for the ENTIRE subtree, recursively — grandparents count.',
                        },
                        {
                            'slug': 'degenerate-shape',
                            'title': 'When a BST becomes slow',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about BSTs.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Inserting already-sorted data creates a chain of height n', 'is_correct': True},
                                {'id': 'b', 'text': 'Search cost is proportional to the tree height', 'is_correct': True},
                                {'id': 'c', 'text': 'A balanced BST has height about log₂n', 'is_correct': True},
                                {'id': 'd', 'text': 'BST search is always O(1)', 'is_correct': False},
                            ],
                            'explain': 'O(1) belongs to hash tables, not BSTs; a degenerate BST degrades to linked-list costs.',
                        },
                    ],
                },
                {
                    'title': 'Building a BST: Insert and Search',
                    'slug': 'bst-insert-search',
                    'objective': 'Implement BST insertion and search on Node objects.',
                    'duration': 15,
                    'body': """# Nodes, then the two operations

A BST node mirrors the linked-list node idea — but with **two** links:

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
            return
        cur = self.root
        while True:
            if value < cur.value:
                if cur.left is None:
                    cur.left = Node(value); return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = Node(value); return
                cur = cur.right

    def search(self, value):
        cur = self.root
        while cur:
            if value == cur.value:
                return True
            cur = cur.left if value < cur.value else cur.right
        return False
```

## Insert walkthrough: build from 5, 3, 8, 1, 4

| Insert | Comparison trail | Placement |
|---|---|---|
| 5 | empty tree | becomes root |
| 3 | 3 < 5 | left child of 5 |
| 8 | 8 > 5 | right child of 5 |
| 1 | 1<5 → 1<3 | left child of 3 |
| 4 | 4<5 → 4>3 | **right** child of 3 |

Result:

```
        5
      /   \
     3     8
    / \
   1   4
```

Notice: 4 could NOT be left of 3 (4 > 3), and inserting never rotates
existing nodes — new values always land as fresh leaves in the strict BST.

## Search = decisions, not scanning
Searching 4: at 5 go left (4<5), at 3 go right (4>3), hit. Every node
discards an entire subtree — the same elimination power as binary search,
but spread across pointers instead of an index range.

## C++ parallel

```cpp
struct Node { int value; Node *left = nullptr, *right = nullptr;
              Node(int v) : value(v) {} };

Node* insert(Node* cur, int v) {          // recursive style
    if (!cur) return new Node(v);
    if (v < cur->value) cur->left  = insert(cur->left,  v);
    else                cur->right = insert(cur->right, v);
    return cur;
}
```

The recursive form is the one to recognise in textbooks: *"insert into
the correct child, and if there is no child, this spot is it."*

## Common mistakes
- Inserting 4 to the left of 5 only, ignoring that the trail must keep
  descending (BSTs are not "root compare then dump on a side").
- Forgetting `self.root = None` for an empty tree and dereferencing None.
- Using `<=` in the left branch — it silently corrupts the no-duplicate
  contract many proofs assume.

## Lesson summary
Insert follows the value down until it finds an empty child slot;
search follows the same trail looking for equality. Both cost O(height).""",
                    'exercises': [
                        {
                            'slug': 'implement-bst',
                            'title': 'Build and read a BST',
                            'exercise_type': 'code',
                            'difficulty': 'hard',
                            'instructions': (
                                'Build a BST class with insert(value) as walked through above, '
                                'insert 5, 3, 8, 1, 4 in that order, then print the tree '
                                'values in ascending order (in-order: left, node, right). '
                                'Expected: [1, 3, 4, 5, 8]'
                            ),
                            'context': 'In-order traversal of a BST visits values sorted — a property worth memorising.',
                            'xp_reward': 150,
                            'starter_code': (
                                'class Node:\n'
                                '    def __init__(self, value):\n'
                                '        self.value = value\n'
                                '        self.left = None\n'
                                '        self.right = None\n'
                                '\n'
                                'class BST:\n'
                                '    def __init__(self):\n'
                                '        self.root = None\n'
                                '\n'
                                '    def insert(self, value):\n'
                                '        # descend and attach a new leaf\n'
                                '        pass\n'
                                '\n'
                                'def inorder(node):\n'
                                '    if node:\n'
                                '        yield from inorder(node.left)\n'
                                '        yield node.value\n'
                                '        yield from inorder(node.right)\n'
                                '\n'
                                't = BST()\n'
                                'for v in [5, 3, 8, 1, 4]:\n'
                                '    t.insert(v)\n'
                                'print(list(inorder(t.root)))\n'
                            ),
                            'solution_code': (
                                'class Node:\n'
                                '    def __init__(self, value):\n'
                                '        self.value = value\n'
                                '        self.left = None\n'
                                '        self.right = None\n'
                                '\n'
                                'class BST:\n'
                                '    def __init__(self):\n'
                                '        self.root = None\n'
                                '\n'
                                '    def insert(self, value):\n'
                                '        if self.root is None:\n'
                                '            self.root = Node(value)\n'
                                '            return\n'
                                '        cur = self.root\n'
                                '        while True:\n'
                                '            if value < cur.value:\n'
                                '                if cur.left is None:\n'
                                '                    cur.left = Node(value); return\n'
                                '                cur = cur.left\n'
                                '            else:\n'
                                '                if cur.right is None:\n'
                                '                    cur.right = Node(value); return\n'
                                '                cur = cur.right\n'
                                '\n'
                                'def inorder(node):\n'
                                '    if node:\n'
                                '        yield from inorder(node.left)\n'
                                '        yield node.value\n'
                                '        yield from inorder(node.right)\n'
                                '\n'
                                't = BST()\n'
                                'for v in [5, 3, 8, 1, 4]:\n'
                                '    t.insert(v)\n'
                                'print(list(inorder(t.root)))\n'
                            ),
                            'expected_output': '[1, 3, 4, 5, 8]',
                            'test_cases': [{'input': '', 'expected_output': '[1, 3, 4, 5, 8]'}],
                            'explain': 'If your output is not sorted, the insert trail stopped too early or compared with the wrong node.',
                        },
                        {
                            'slug': 'search-trail',
                            'title': 'Dry-run a search',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'Tree: root 5; left child 3 (children 1 and 4); right child 8. '
                                'How many nodes does BST search visit when looking for 4? '
                                '(Answer with the number only.)'
                            ),
                            'xp_reward': 40,
                            'expected_output': '3',
                            'explain': '5 → 3 → 4: three comparisons. Search visits one node per level of the trail.',
                        },
                        {
                            'slug': 'insert-position',
                            'title': 'Where does 6 land?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'BST built from 5, 3, 8, 1, 4 (see table). Inserting 6 next attaches it as…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'right child of 5', 'is_correct': False},
                                {'id': 'b', 'text': 'left child of 8', 'is_correct': True},
                                {'id': 'c', 'text': 'right child of 4', 'is_correct': False},
                                {'id': 'd', 'text': 'left child of 4', 'is_correct': False},
                            ],
                            'explain': '6>5 go right to 8; 6<8 go left — empty, so it attaches there. Note 6>4 but 4 is in 5\'s left subtree — the trail never sees it.',
                        },
                    ],
                },
                {
                    'title': 'Tree Traversals',
                    'slug': 'traversals',
                    'objective': 'Run in-order, pre-order, post-order and level-order traversals by hand and in code.',
                    'duration': 12,
                    'body': """# Four orders for visiting every node

**Traversal** = visit each node exactly once in a defined order. The
three depth-first orders differ only in **when the node itself is
printed** relative to its children:

- **In-order:** left → node → right
- **Pre-order:** node → left → right
- **Post-order:** left → right → node
- **Level-order (BFS):** level by level, left to right (uses a queue)

## Dry run on the same tree

```
        5
      /   \
     3     8
    / \
   1   4
```

| Traversal | Visit sequence |
|---|---|
| In-order | 1, 3, 4, 5, 8 ← **sorted!** |
| Pre-order | 5, 3, 1, 4, 8 ← root first: good for copying a tree |
| Post-order | 1, 4, 3, 8, 5 ← children before parent: good for deleting |
| Level-order | 5, 3, 8, 1, 4 ← by depth |

```python
def inorder(node):
    if node:
        inorder(node.left)
        print(node.value)
        inorder(node.right)
```

Three facts worth memorising:
1. **In-order on a BST prints sorted values** — this is what makes the
   BST a "sorted container" without paying for sorting.
2. **Pre-order** rebuilds the exact tree shape (node before children), so
   serialising/cloning uses it.
3. **Post-order** deletes/moves files after their contents — `rm -r`
   style tools work bottom-up for the same reason.

Level-order needs a **queue** — pop a node, push its children — the
chapter-5 structure reappearing inside chapter-8 code, which is no
accident: BFS *is* queue-driven exploration.

## C++ parallel
The recursive shape is identical; `std::queue<Node*> q;` drives BFS, and
iterative DFS with an explicit `std::stack` is the interview follow-up.

## Common mistakes
- Printing the node in in-order *before* recursing left — that silently
  turns it into pre-order.
- Forgetting the `if node:` base case → crash on None.
- Assuming level-order = sorted order (true for that tree's in-order,
  not for BFS).

## Lesson summary
Same tree, four disciplined visit orders; the name encodes when the node
is processed — in-, pre- (before children), post- (after children), and
level-order via a queue.""",
                    'exercises': [
                        {
                            'slug': 'run-inorder',
                            'title': 'In-order output',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'The Node tree is built for you. Complete inorder(node) '
                                'so it prints one value per line in in-order '
                                '(left, node, right) and run it. '
                                'Tree:\n    8\n   / \\\n  3   10\n / \\ \\\n1   6  14'
                            ),
                            'xp_reward': 120,
                            'starter_code': (
                                'class Node:\n'
                                '    def __init__(self, v, l=None, r=None):\n'
                                '        self.v, self.left, self.right = v, l, r\n'
                                '\n'
                                'root = Node(8, Node(3, Node(1), Node(6)),\n'
                                '                  Node(10, None, Node(14)))\n'
                                '\n'
                                'def inorder(node):\n'
                                '    # left, self, right — print with print(node.v)\n'
                                '    pass\n'
                                '\n'
                                'inorder(root)\n'
                            ),
                            'solution_code': (
                                'class Node:\n'
                                '    def __init__(self, v, l=None, r=None):\n'
                                '        self.v, self.left, self.right = v, l, r\n'
                                '\n'
                                'root = Node(8, Node(3, Node(1), Node(6)),\n'
                                '                  Node(10, None, Node(14)))\n'
                                '\n'
                                'def inorder(node):\n'
                                '    if node:\n'
                                '        inorder(node.left)\n'
                                '        print(node.v)\n'
                                '        inorder(node.right)\n'
                                '\n'
                                'inorder(root)\n'
                            ),
                            'expected_output': '1\n3\n6\n8\n10\n14',
                            'test_cases': [{'input': '', 'expected_output': '1\n3\n6\n8\n10\n14'}],
                            'explain': 'The tree happens to satisfy the BST rule, so in-order prints it sorted — a good self-check.',
                        },
                        {
                            'slug': 'which-traversal-name',
                            'title': 'Name that order',
                            'exercise_type': 'output_prediction',
                            'instructions': 'On the dry-run tree (root 5, left 3 with 1,4; right 8), what is the PRE-order sequence? Comma-separated.',
                            'xp_reward': 40,
                            'expected_output': '5, 3, 1, 4, 8',
                            'explain': 'Pre-order: node before children — 5 first, then its left subtree 3,1,4, then 8.',
                        },
                        {
                            'slug': 'traversal-uses',
                            'title': 'Match order to job',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct pairings.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'In-order on a BST: produce values sorted', 'is_correct': True},
                                {'id': 'b', 'text': 'Post-order: delete a tree children-first', 'is_correct': True},
                                {'id': 'c', 'text': 'Pre-order: serialise a tree so its shape can be rebuilt', 'is_correct': True},
                                {'id': 'd', 'text': 'Level-order: find the tree height in one pass without recursion, using a stack', 'is_correct': False},
                            ],
                            'explain': 'Level-order uses a QUEUE, not a stack — structures from chapter 5 showing up exactly where they belong.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 8 Quiz',
                    'slug': 'trees-quiz',
                    'objective': 'Check vocabulary, BST mechanics and traversal recall.',
                    'duration': 10,
                    'body': """# Chapter 8 Quiz

Six questions on tree vocabulary, the BST contract, insert/search costs
and the four traversals.""",
                    'exercises': [
                        {
                            'slug': 'q8-height-single',
                            'title': 'Height of one node',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Height measured in EDGES on the longest root→leaf path. A tree with only the root: what is its height? (number only)',
                            'xp_reward': 40,
                            'expected_output': '0',
                            'explain': 'No edges exist, so height 0 — some textbooks count nodes instead (then 1); know which convention a question uses.',
                        },
                        {
                            'slug': 'q8-max-children',
                            'title': 'Binary tree cap',
                            'exercise_type': 'fill_blank',
                            'instructions': 'A binary tree allows each node at most ____ children. (digit)',
                            'xp_reward': 40,
                            'solution_code': '2',
                            'explain': 'Two: named left and right — the names matter for traversal order.',
                        },
                        {
                            'slug': 'q8-not-a-bst',
                            'title': 'Spot the violation',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Root 10, left child 5, right child 15, and 15 has a LEFT child 8. Is this a valid BST?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'No — 8 sits in 10\'s right subtree but is smaller than 10', 'is_correct': True},
                                {'id': 'b', 'text': 'Yes — 8 > 5 so it is fine somewhere', 'is_correct': False},
                                {'id': 'c', 'text': 'Yes — every parent\'s direct children are ordered', 'is_correct': False},
                                {'id': 'd', 'text': 'No — a BST cannot have 4 nodes', 'is_correct': False},
                            ],
                            'explain': 'The contract is about whole subtrees: everything right of 10 must exceed 10. Checking only direct children misses it.',
                        },
                        {
                            'slug': 'q8-sorted-traversal',
                            'title': 'The sorted one',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which traversal of a BST visits values in ascending order?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'In-order', 'is_correct': True},
                                {'id': 'b', 'text': 'Pre-order', 'is_correct': False},
                                {'id': 'c', 'text': 'Post-order', 'is_correct': False},
                                {'id': 'd', 'text': 'Level-order', 'is_correct': False},
                            ],
                            'explain': 'Left subtree (smaller) → node → right subtree (larger), applied recursively.',
                        },
                        {
                            'slug': 'q8-degenerate-cost',
                            'title': 'Chain tree cost',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A BST built by inserting 1, 2, 3, …, n (right-child chain) has search cost of order…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'O(n)', 'is_correct': True},
                                {'id': 'b', 'text': 'O(log n)', 'is_correct': False},
                                {'id': 'c', 'text': 'O(1)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n log n)', 'is_correct': False},
                            ],
                            'explain': 'Height = n ⇒ no elimination power. Self-balancing trees (AVL, red-black) exist to prevent exactly this.',
                        },
                        {
                            'slug': 'q8-bfs-structure',
                            'title': 'Level-order engine',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Level-order traversal is driven by a ____ (the chapter-5 FIFO structure, one lowercase word).',
                            'xp_reward': 40,
                            'solution_code': 'queue',
                            'explain': 'FIFO keeps the frontier exactly one level deep — stack would give depth-first instead.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 9 ════════════════════
        {
            'title': 'Hashing and Graphs',
            'slug': 'hashing-graphs',
            'description': 'How hash tables turn keys into indexes and survive collisions, then graphs with BFS and DFS.',
            'lessons': [
                {
                    'title': 'Hash Tables',
                    'slug': 'hash-tables',
                    'objective': 'Explain the hash → index jump and the two collision strategies.',
                    'duration': 15,
                    'body': """# The structure that skips the search

Every structure so far asks you to **compare your way to the answer** —
one step at a time (list), or halving each step (BST). A **hash table**
decides the location outright: run the key through a **hash function**,
use the result as an **array index**, drop the value there. Lookup =
recompute the index, grab the slot. Expected **O(1)** — constant time,
regardless of size.

```python
class HashMap:                      # tiny teaching version
    def __init__(self, size=8):
        self.slots = [[] for _ in range(size)]  # each slot: chain of (key, value)
        self.size = size

    def index(self, key):           # hash then squeeze into range
        return hash(key) % self.size

    def put(self, key, value):
        i = self.index(key)
        for pos, (k, v) in enumerate(self.slots[i]):
            if k == key:            # update existing key
                self.slots[i][pos] = (key, value)
                return
        self.slots[i].append((key, value))   # insert new pair

    def get(self, key):
        for k, v in self.slots[self.index(key)]:
            if k == key:
                return v
        raise KeyError(key)

h = HashMap()
h.put('ali', 90)
print(h.get('ali'))
```

(The production answer is simply `d = {'ali': 90}; d['ali']` — Python's
`dict` and C++'s `unordered_map` are exactly this structure, hardened.)

## Collisions: the unavoidable wrinkle
Two different keys may hash to the same index — a **collision**. Two
classic fixes:

- **Chaining** (above): each slot holds a small list of pairs; worst
  case a long chain degrades lookups to O(chain length).
- **Open addressing**: if the slot is taken, probe the next index
  (linear probing) until an empty one is found. Keeps everything in the
  array, but clusters slow it down.

A **good hash function** spreads keys evenly (so chains stay short) and
is **consistent** (same key → same index every time). Python guarantees
`hash()` consistency within a process.

## The load factor and resizing
`load factor = stored items / slots`. When it climbs past ~0.7 (Python
resizes `dict` once load nears 2/3), the table **doubles** its slot
array and rehashes everything — that rare rehash is why a single
dict-insert can spike while the **amortised** cost stays O(1).

## Trade-offs versus a BST
- Hash table: O(1) lookup, **no order**, iteration order is insertion
  order (Python 3.7+, an implementation detail turned language promise).
- BST: O(log n) lookup, but sorted traversal, range queries
  ("everything between A and M"), and neighbour ops come free.
Choose by the questions you need to ask of the data.

## Common mistakes
- Expecting hash tables to be sorted — they are deliberately unordered.
- Writing an inconsistent hash (e.g. including a mutable field) so
  `get` looks in a different bucket than `put` stored in.
- Forgetting `key in d` before `d[key]` and eating the KeyError — or the
  opposite habit, `try/except` everywhere.

## Lesson summary
Hash function turns keys into indexes; collisions happen and are handled
by chaining or probing; keep the load factor down by resizing; pay for O(1)
with lost ordering.""",
                    'exercises': [
                        {
                            'slug': 'implement-hashmap',
                            'title': 'Write put and get',
                            'exercise_type': 'code',
                            'difficulty': 'hard',
                            'instructions': (
                                'Complete HashMap.put/get with chaining (each slot is a '
                                'list of [key, value] pairs; index = hash(key) % size). '
                                'Put ali=90 then sara=85 then update ali=95, and print '
                                'get("ali") followed by get("sara") — one per line. '
                                'Expected: 95 then 85.'
                            ),
                            'context': 'Use the skeleton exactly as given; slots is already initialised to empty lists.',
                            'xp_reward': 150,
                            'starter_code': (
                                'class HashMap:\n'
                                '    def __init__(self, size=8):\n'
                                '        self.size = size\n'
                                '        self.slots = [[] for _ in range(size)]\n'
                                '\n'
                                '    def index(self, key):\n'
                                '        return hash(key) % self.size\n'
                                '\n'
                                '    def put(self, key, value):\n'
                                '        # update existing pair in the chain, else append\n'
                                '        pass\n'
                                '\n'
                                '    def get(self, key):\n'
                                '        # scan the chain; raise KeyError if absent\n'
                                '        raise KeyError(key)\n'
                                '\n'
                                'h = HashMap()\n'
                                'h.put("ali", 90)\n'
                                'h.put("sara", 85)\n'
                                'h.put("ali", 95)\n'
                                'print(h.get("ali"))\n'
                                'print(h.get("sara"))\n'
                            ),
                            'solution_code': (
                                'class HashMap:\n'
                                '    def __init__(self, size=8):\n'
                                '        self.size = size\n'
                                '        self.slots = [[] for _ in range(size)]\n'
                                '\n'
                                '    def index(self, key):\n'
                                '        return hash(key) % self.size\n'
                                '\n'
                                '    def put(self, key, value):\n'
                                '        chain = self.slots[self.index(key)]\n'
                                '        for pos, (k, v) in enumerate(chain):\n'
                                '            if k == key:\n'
                                '                chain[pos] = (key, value)\n'
                                '                return\n'
                                '        chain.append((key, value))\n'
                                '\n'
                                '    def get(self, key):\n'
                                '        for k, v in self.slots[self.index(key)]:\n'
                                '            if k == key:\n'
                                '                return v\n'
                                '        raise KeyError(key)\n'
                                '\n'
                                'h = HashMap()\n'
                                'h.put("ali", 90)\n'
                                'h.put("sara", 85)\n'
                                'h.put("ali", 95)\n'
                                'print(h.get("ali"))\n'
                                'print(h.get("sara"))\n'
                            ),
                            'expected_output': '95\n85',
                            'test_cases': [{'input': '', 'expected_output': '95\n85'}],
                            'explain': 'The update branch in put is the part everyone forgets: without it ali appears twice and get returns the stale 90.',
                        },
                        {
                            'slug': 'collision-definition',
                            'title': 'What a collision is',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A hash-table collision happens when…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'two different keys produce the same index', 'is_correct': True},
                                {'id': 'b', 'text': 'the table becomes completely empty', 'is_correct': False},
                                {'id': 'c', 'text': 'a key is stored twice', 'is_correct': False},
                                {'id': 'd', 'text': 'the hash function returns a negative number', 'is_correct': False},
                            ],
                            'explain': 'Different keys, same slot — inevitable once you have more possible keys than slots; chaining/probing exist to absorb it.',
                        },
                        {
                            'slug': 'hash-vs-bst',
                            'title': 'Pick the right tool',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL statements true of hash tables (expected case) but NOT of BSTs.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Average lookup in O(1)', 'is_correct': True},
                                {'id': 'b', 'text': 'Can answer "all keys between 10 and 20" cheaply', 'is_correct': False},
                                {'id': 'c', 'text': 'Iterates keys in no sorted order', 'is_correct': True},
                                {'id': 'd', 'text': 'Guarantees O(log n) worst-case lookup', 'is_correct': False},
                            ],
                            'explain': 'Range queries and ordered iteration are BST strengths; O(1) average is the hash table bet — note the words "expected" and "average".',
                        },
                    ],
                },
                {
                    'title': 'Graphs, BFS and DFS',
                    'slug': 'graphs-bfs-dfs',
                    'objective': 'Model a problem as a graph and traverse it breadth-first and depth-first.',
                    'duration': 15,
                    'body': """# Graphs: structures with no single root

A **graph** = set of **vertices** (nodes) connected by **edges**. Trees
were graphs with strict rules (one root, no cycles); graphs drop them.
The vocabulary:

- **Neighbor / adjacent:** joined by an edge. **Degree:** number of an
  edge's attachments to a vertex.
- **Directed (digraph):** edges are one-way arrows (follow lists, links).
- **Weighted:** edges carry costs (roads, latency, prices).
- **Path:** a walk along edges; **cycle:** a path returning to its start.
- **Connected:** every vertex reachable from every other.

## Storing a graph
```python
# adjacency list: each vertex maps to its neighbors — the usual choice
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C', 'E'],
    'E': ['D'],
}
```
An **adjacency matrix** (`bool n×n grid`) answers "is X–Y an edge?" in
O(1) but costs O(V²) memory; the list costs O(V+E) and iterates real
neighbors only — the same array-vs-hash reasoning from earlier chapters.

## BFS — the level-by-level explorer
**Breadth-First Search**: start node into a **queue**; repeatedly pop a
vertex, visit its unvisited neighbors, enqueue them. Explores in rings:
all distance-1 nodes, then distance-2… Consequence: **BFS finds the
fewest-edges path** between two nodes in an unweighted graph — social-network
"degrees of separation", maze shortest exits, web crawlers' frontier.

## DFS — the deep-diver
**Depth-First Search**: follow one branch **all the way down** before
backtracking — recursion does it for free, or an explicit stack. Uses:
puzzle/maze solving, detecting cycles, topological ordering (build
systems: a package must be installed before its dependents), and
"is this graph connected?"

```python
def bfs(graph, start):
    seen, order, queue = {start}, [start], [start]
    while queue:
        v = queue.pop(0)                 # a real deque is cheaper
        for w in graph[v]:
            if w not in seen:
                seen.add(w); order.append(w); queue.append(w)
    return order

def dfs(graph, v, seen=None):
    seen = seen or set()
    if v in seen:
        return
    seen.add(v)
    print(v)                             # pre-order: touch on entry
    for w in graph[v]:
        dfs(graph, w, seen)
```

Both are **O(V + E)** — every vertex and edge touched once — and both
need the `seen` set because cycles would otherwise trap the walk forever
(a tree never needed that; graphs do).

## Cost comparison with what you know
Reach a vertex: hash table O(1) *given the key*, BFS O(distance), DFS
O(depth). Graph traversal is the general case: arrays, trees and even
state-space puzzles are graphs you can BFS/DFS.

## Common mistakes
- Forgetting `seen` on cyclic graphs → infinite loop.
- Using DFS when the problem says "shortest" — DFS has no distance
  guarantee; BFS owns unweighted shortest paths.
- Mixing directions: in directed graphs, A→B does not mean B→A.

## Lesson summary
Graphs are vertices plus edges; store as adjacency lists; BFS queues
outward and gives shortest edge-count paths; DFS recurses deep for
cycles and connectivity; both cost O(V+E).""",
                    'exercises': [
                        {
                            'slug': 'run-bfs',
                            'title': 'BFS visit order',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'Complete bfs(graph, start) as in the lesson (queue + seen '
                                'set) and print the visit order for the ABCDE graph from '
                                'the lesson code, starting at A, as space-separated '
                                'letters. Expected: A B C D E'
                            ),
                            'xp_reward': 120,
                            'starter_code': (
                                "graph = {'A': ['B', 'C'], 'B': ['A', 'D'], "
                                "'C': ['A', 'D'], 'D': ['B', 'C', 'E'], 'E': ['D']}\n"
                                '\n'
                                'def bfs(graph, start):\n'
                                '    # queue + seen set, append order as you enqueue\n'
                                '    return order\n'
                                '\n'
                                "print(' '.join(bfs(graph, 'A')))\n"
                            ),
                            'solution_code': (
                                "graph = {'A': ['B', 'C'], 'B': ['A', 'D'], "
                                "'C': ['A', 'D'], 'D': ['B', 'C', 'E'], 'E': ['D']}\n"
                                '\n'
                                'def bfs(graph, start):\n'
                                "    seen, order, queue = {start}, [start], [start]\n"
                                '    while queue:\n'
                                '        v = queue.pop(0)\n'
                                '        for w in graph[v]:\n'
                                '            if w not in seen:\n'
                                '                seen.add(w); order.append(w); queue.append(w)\n'
                                '    return order\n'
                                '\n'
                                "print(' '.join(bfs(graph, 'A')))\n"
                            ),
                            'expected_output': 'A B C D E',
                            'test_cases': [{'input': '', 'expected_output': 'A B C D E'}],
                            'explain': 'Rings: A, then B C, then D, then E. Order within a ring follows neighbor-list order.',
                        },
                        {
                            'slug': 'dfs-uses',
                            'title': 'BFS or DFS job match',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL tasks where DFS (not BFS) is the classic tool.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Detecting a cycle in a graph', 'is_correct': True},
                                {'id': 'b', 'text': 'Topological ordering for build dependencies', 'is_correct': True},
                                {'id': 'c', 'text': 'Fewest-steps route between two users', 'is_correct': False},
                                {'id': 'd', 'text': 'Solving a maze by trying one corridor to its dead end first', 'is_correct': True},
                            ],
                            'explain': 'Shortest edge-count (c) is BFS\'s signature guarantee; cycle detection, topo-sort and commit-to-a-corridor are depth-first behaviors.',
                        },
                        {
                            'slug': 'adjacency-cost',
                            'title': 'Storage costs',
                            'exercise_type': 'output_prediction',
                            'instructions': 'How many entries does an adjacency list hold for an UNDIRECTED graph with 4 edges? (Each edge stored at BOTH endpoints. Number only.)',
                            'xp_reward': 40,
                            'expected_output': '8',
                            'explain': '2 entries per undirected edge — that is why the list size is O(V + E) with E counted this way.',
                        },
                        {
                            'slug': 'seen-set-reason',
                            'title': 'Why graphs need seen',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Tree traversals never needed a visited set, but graph traversals do. Why?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Graphs can contain cycles, so the walk can return to a node it already processed', 'is_correct': True},
                                {'id': 'b', 'text': 'Graphs are always bigger than trees', 'is_correct': False},
                                {'id': 'c', 'text': 'Edges carry weights', 'is_correct': False},
                                {'id': 'd', 'text': 'Python recursion is limited', 'is_correct': False},
                            ],
                            'explain': 'Without seen, A→B→A→B… spins forever; trees have exactly one path to each node, so re-entry is impossible.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 9 Quiz',
                    'slug': 'hashing-graphs-quiz',
                    'objective': 'Check hashing mechanics and graph traversal recall.',
                    'duration': 10,
                    'body': """# Chapter 9 Quiz

Six questions on hash functions, collisions, load factor, adjacency
storage and BFS/DFS behavior.""",
                    'exercises': [
                        {
                            'slug': 'q9-index-step',
                            'title': 'From key to slot',
                            'exercise_type': 'fill_blank',
                            'instructions': 'A table has 7 slots. A key hashes to 23. Which slot index is used? (digit)',
                            'xp_reward': 40,
                            'solution_code': '2',
                            'explain': '23 % 7 = 2 — the modulo squeezes any hash into the slot range.',
                        },
                        {
                            'slug': 'q9-chaining-shape',
                            'title': 'Chaining picture',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In chaining, colliding entries are stored…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'in a small list hanging off that slot', 'is_correct': True},
                                {'id': 'b', 'text': 'by moving everything to a BST', 'is_correct': False},
                                {'id': 'c', 'text': 'in the next empty slot found by probing', 'is_correct': False},
                                {'id': 'd', 'text': 'rejected until the table grows', 'is_correct': False},
                            ],
                            'explain': 'Option c describes open addressing — the rival strategy, not chaining.',
                        },
                        {
                            'slug': 'q9-load-factor',
                            'title': 'Load factor',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Load factor = items / slots. 6 items in a 12-slot table? Answer as a decimal like 0.5',
                            'xp_reward': 40,
                            'expected_output': '0.5',
                            'explain': 'Past ~0.7 tables resize to keep chains short and O(1) honest.',
                        },
                        {
                            'slug': 'q9-bfs-guarantee',
                            'title': 'BFS promise',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In an UNWEIGHTED graph, BFS from S to every vertex guarantees…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'the path with the fewest edges to each vertex', 'is_correct': True},
                                {'id': 'b', 'text': 'the alphabetically first path', 'is_correct': False},
                                {'id': 'c', 'text': 'the minimum total weight path', 'is_correct': False},
                                {'id': 'd', 'text': 'visiting each vertex exactly twice', 'is_correct': False},
                            ],
                            'explain': 'Weights break the guarantee — with edge costs you need Dijkstra (a weighted BFS), beyond this course\'s scope but worth Googling.',
                        },
                        {
                            'slug': 'q9-graph-terms',
                            'title': 'Term matching',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct graph term definitions.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Degree of a vertex: number of edges touching it', 'is_correct': True},
                                {'id': 'b', 'text': 'Cycle: a path that starts and ends at the same vertex', 'is_correct': True},
                                {'id': 'c', 'text': 'Digraph: graph where every vertex has two children', 'is_correct': False},
                                {'id': 'd', 'text': 'Connected: every vertex reachable from every other', 'is_correct': True},
                            ],
                            'explain': 'A digraph has ONE-WAY edges (directed), not binary children — tree vocabulary leaking into graph terms is a classic trap.',
                        },
                        {
                            'slug': 'q9-traversal-cost',
                            'title': 'BFS/DFS cost',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Correct statement about BFS and DFS on a graph with V vertices and E edges:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Both run in O(V + E) with an adjacency list', 'is_correct': True},
                                {'id': 'b', 'text': 'BFS is O(V²) always; DFS is O(E)', 'is_correct': False},
                                {'id': 'c', 'text': 'Both are O(log n)', 'is_correct': False},
                                {'id': 'd', 'text': 'DFS is faster because it skips edges', 'is_correct': False},
                            ],
                            'explain': 'They differ in visit ORDER, not work done: each vertex and edge is touched once either way.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 10 ════════════════════
        {
            'title': 'Algorithmic Problem Solving',
            'slug': 'problem-solving',
            'description': 'Recursion, divide & conquer, greedy strategies and dynamic programming — the four thinking patterns.',
            'lessons': [
                {
                    'title': 'Recursion',
                    'slug': 'recursion',
                    'objective': 'Write recursive functions with a sound base case and trace the call stack.',
                    'duration': 15,
                    'body': """# Functions that call themselves

**Recursion** defines something in terms of a smaller version of itself:
the factorial of n is n × the factorial of (n−1). Every recursive
function needs exactly two ingredients:

1. **Base case** — the smallest input answered directly, no recursion.
2. **Recursive case** — call yourself on a STRICTLY smaller problem.

```python
def factorial(n):
    if n <= 1:                 # base case: 0! = 1! = 1
        return 1
    return n * factorial(n - 1)  # recursive case shrinks n
```

## The call stack, visibly
Calling `factorial(4)` opens nested frames, each waiting for the one
below to return:

```
factorial(4) → 4 * factorial(3)
  factorial(3) → 3 * factorial(2)
    factorial(2) → 2 * factorial(1)
      factorial(1) → returns 1        # base case hits bottom
    returns 2 * 1 = 2
  returns 3 * 2 = 6
returns 4 * 6 = 24
```

Frames pile up **down**, answers cascade **back up**. This is the same
LIFO structure as chapter 5's stack — recursion is a stack you do not
have to build yourself, which is why every recursive function can be
rewritten with an explicit stack loop (and vice versa).

## Two classic traps
- **No base case, or one never reached:** `factorial(-1)` skips `n <= 1`
  only if written as `n == 1`… then -1, -2, -3 forever → `RecursionError`
  (Python stops at 1000 frames; C++ usually segfaults first).
- **Not shrinking:** `fib(n)` must call `fib(n-1)`/`fib(n-2)`, never
  `fib(n)` again.

## Tree recursion: Fibonacci, unmasked

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

`fib(5)` spawns TWO branches per call. The call tree for fib(5) has 15
nodes — and fib(3) gets computed twice, fib(2) three times. Exponential
(~2ⁿ) despite tiny input. Keep that in mind: the next lesson's DP exists
precisely to kill this recomputation.

Every structure in this course is recursive at heart — linked lists
("node + smaller list"), trees ("root + smaller trees"), merge sort
("half + half") — so recursion is not an extra topic; it is how you
*talk* to those structures.

## Common mistakes
- Forgetting to `return` the recursive call's value (Python silently
  hands back None at the top).
- Recursion depth on million-element inputs — Python has no tail-call
  optimisation; a loop is the safe tool for big linear walks.
- Trusting "it shrinks by 1" when the input is a float — base case may
  never be hit exactly.

## Lesson summary
Base case + strictly-shrinking recursive case, frames waiting on a
hidden stack, watch out for double-branching blowup — and remember every
recursive definition can be made iterative.""",
                    'exercises': [
                        {
                            'slug': 'implement-recsum',
                            'title': 'Recursive list sum',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'Write rsum(a) recursively: base case empty list → 0, '
                                'else first element + rsum of the rest. Then print '
                                'rsum([4, 7, 2, 8]). Expected: 21'
                            ),
                            'context': 'a[1:] is the smaller list — the strictly-shrinking recursive case.',
                            'xp_reward': 120,
                            'starter_code': (
                                'def rsum(a):\n'
                                '    # base case + first + rsum(rest)\n'
                                '    return 0\n'
                                '\n'
                                'print(rsum([4, 7, 2, 8]))\n'
                            ),
                            'solution_code': (
                                'def rsum(a):\n'
                                '    if not a:\n'
                                '        return 0\n'
                                '    return a[0] + rsum(a[1:])\n'
                                '\n'
                                'print(rsum([4, 7, 2, 8]))\n'
                            ),
                            'expected_output': '21',
                            'test_cases': [{'input': '', 'expected_output': '21'}],
                            'explain': 'If you returned rsum(a[1:]) without adding a[0], you built the stack but dropped every value on the way back up.',
                        },
                        {
                            'slug': 'fib-call-count',
                            'title': 'Dry-run the fib tree',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Naive fib above: how many TOTAL calls (including the first) does fib(3) make? (number only)',
                            'xp_reward': 50,
                            'expected_output': '5',
                            'explain': 'fib(3) → fib(2) → fib(1), fib(0), and fib(1): five frames. The duplication starts immediately.',
                        },
                        {
                            'slug': 'recursion-requirements',
                            'title': 'The two ingredients',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct statements about recursion.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Every call must work on a strictly smaller problem', 'is_correct': True},
                                {'id': 'b', 'text': 'A reachable base case is mandatory', 'is_correct': True},
                                {'id': 'c', 'text': 'Recursive code always runs faster than loops', 'is_correct': False},
                                {'id': 'd', 'text': 'Each pending call costs a stack frame', 'is_correct': True},
                            ],
                            'explain': 'Recursion trades frame overhead for clarity — "faster" is the opposite of the truth on deep linear walks.',
                        },
                    ],
                },
                {
                    'title': 'Divide & Conquer and Greedy Strategies',
                    'slug': 'dc-greedy',
                    'objective': 'Recognise the split-and-solve pattern and the take-the-best-now pattern — and when greedy fails.',
                    'duration': 15,
                    'body': """# Two strategies you already half-know

## Divide & conquer, in the wild
The recipe — **split the problem into independent halves, solve each,
combine** — has been hiding in plain sight all course:

| Algorithm | Split | Combine |
|---|---|---|
| Binary search (ch 6) | discard half by index | none needed |
| Merge sort (ch 7) | halves by position | merge sorted lists |
| Quick sort (ch 7) | partition by pivot | none (in place) |
| Tree traversals (ch 8) | left / right subtree | print order |
| BFS/DFS (ch 9) | neighbour subgraphs | seen set |

The interview skill is spotting NEW problems that fit: counting
inversions, closest pair of points, large integer multiplication — all
"split, recurse, combine".

## Greedy: choose the best right now
A **greedy** algorithm builds an answer step by step, each step taking
the locally best choice, never revisiting. It is spectacular when the
problem has the **greedy-choice property** (local bests compose into a
global best):

**Coin change (canonical coins 1, 5, 10, 25):** to make 63 cents, take
the largest coin that fits, repeatedly: 25+25+10+1+1+1 = 6 coins. For
real currency this is provably optimal.

**Activity selection:** meetings with start/end times, maximise count in
one room: always take the meeting that **ends earliest**, repeat.
Sorting by end time makes the proof a two-line exchange argument.

## When greedy fails — memorise the counterexample
Coins {1, 3, 4}, target 6. Greedy: 4 + 1 + 1 = **3 coins**. Optimal:
3 + 3 = **2 coins**. Greedy took the attractive 4 and got stuck.

The lesson: greedy is not a strategy you *choose* because it is simple;
it is a property you must **verify** (exchange argument, or hunt for a
small counterexample like this one). No verification → you are shipping
a heuristic, not an algorithm.

## C++ parallel
`std::sort` then a single scan is the shape of most greedy solutions in
interview code; priority queues (`std::priority_queue`) power the
famous greedy classics (Huffman coding, Dijkstra\'s weighted shortest
path — greedy with a twist, and your syllabus only needs the name).

## Common mistakes
- Greedy on anything asking for an exact optimum without proof.
- Forgetting D&C needs the pieces to be **independent** — "split in
  half, but the answer needs cross-half info" means a smarter combine
  (that is exactly merge sort\'s trick, and inversion counting\'s).
- Re-running the split on already-sorted halves (binary search) and
  claiming O(log n) while scanning like linear search.

## Lesson summary
D&C = split/recurse/combine (you have implemented five examples);
greedy = locally-best steps, only legitimate after a proof — the {1,3,4}
coins target 6 counterexample is the cheapest way to test the claim.""",
                    'exercises': [
                        {
                            'slug': 'greedy-coin-fail',
                            'title': 'Greedy trap',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Coins {1, 3, 4}, target 6, greedy takes the largest fitting coin first. How many coins does GREEDY use? (number only)',
                            'xp_reward': 50,
                            'expected_output': '3',
                            'explain': '4+1+1 = 3 coins, while 3+3 = 2 beats it — greedy can lose even with all-positive coins.',
                        },
                        {
                            'slug': 'activity-rule',
                            'title': 'Meeting-room rule',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'To maximise non-overlapping meetings in one room, the greedy rule is to always take the meeting that…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'ends earliest', 'is_correct': True},
                                {'id': 'b', 'text': 'starts earliest', 'is_correct': False},
                                {'id': 'c', 'text': 'is shortest', 'is_correct': False},
                                {'id': 'd', 'text': 'has the most attendees', 'is_correct': False},
                            ],
                            'explain': 'Earliest finish leaves the most room behind it; earliest START and shortest can both block longer chains.',
                        },
                        {
                            'slug': 'dc-matching',
                            'title': 'Pattern matching',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL algorithms that are genuinely divide & conquer.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Merge sort', 'is_correct': True},
                                {'id': 'b', 'text': 'Binary search', 'is_correct': True},
                                {'id': 'c', 'text': 'Bubble sort', 'is_correct': False},
                                {'id': 'd', 'text': 'Quick sort', 'is_correct': True},
                            ],
                            'explain': 'Bubble sort never splits — it is incremental comparison-exchange, the odd one out.',
                        },
                    ],
                },
                {
                    'title': 'Dynamic Programming: Recursion with Memory',
                    'slug': 'dp-intro',
                    'objective': 'Add memoisation to naive fib and explain overlapping subproblems.',
                    'duration': 15,
                    'body': """# The fix for the fib explosion

**Overlapping subproblems:** a recursive solution that solves the SAME
smaller problem many times — fib(5) computing fib(3) twice was the
smallest view of it. **Dynamic programming (DP)** is the family of
techniques that solve each subproblem ONCE and reuse the answer.

The entry-level form is literally one idea — **memoisation**:

```python
def fib(n, cache={}):
    if n <= 1:
        return n
    if n in cache:               # computed before? reuse
        return cache[n]
    cache[n] = fib(n - 1, cache) + fib(n - 2, cache)
    return cache[n]
```

Same calls, but every value computed once: fib(50) that would take
millions of naked calls now takes ~50 additions and finishes
instantly. **O(2ⁿ) → O(n)** by remembering. Python even automates the
wrapper: `from functools import cache`.

The other DP form is **bottom-up**: fill a table from the smallest
subproblems upward (iterative fib: keep the last two numbers, walk to n).
Top-down (memoised recursion) is easier to discover; bottom-up is easier
to tune and never risks the stack.

## When is a problem DP-shaped?
Two checklist questions:
1. Does an optimal answer build from optimal answers of smaller pieces?
   (optimal substructure)
2. Do the same smaller pieces appear in multiple branches?
   (overlapping subproblems)

Longest common subsequence, coin-change *minimum coins* (the exact
problem greedy got wrong!), knapsack, edit distance, path counting in a
grid — all yes/yes. Interview DP starts from recognising this shape, not
from clever math.

## DP versus the other strategies
- **Brute force** recomputes everything (naive fib).
- **D&C** splits into INDEPENDENT parts (merge sort) — nothing to reuse.
- **Greedy** commits to one path per step (and needs a proof).
- **DP** keeps answers to every subproblem it has ever seen.

## Common mistakes
- Memoising with a mutable default in a function whose *other* arguments
  change (the cache key is wrong) — `cache={}` per-exercise is fine only
  because fib\'s input is just n.
- Applying DP where subproblems DON\'T overlap (merge sort) — the cache
  would just waste memory.
- Trying to DP a problem without optimal substructure — e.g. "longest
  path without repeating nodes" is NP-hard territory, substructure fails.

## Lesson summary
DP = recursion + reuse. Spot the two checklist properties, then either
memoise top-down or fill a table bottom-up; fib is the "hello world"
whose 2ⁿ → n jump proves the idea.""",
                    'exercises': [
                        {
                            'slug': 'implement-memo-fib',
                            'title': 'Memoised fib',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'Complete fib(n) with a dict cache so each n is computed '
                                'once, then print fib(10), fib(20), fib(30) on separate '
                                'lines. Expected: 55, 6765, 832040.'
                            ),
                            'xp_reward': 120,
                            'starter_code': (
                                'def fib(n, cache={}):\n'
                                '    if n <= 1:\n'
                                '        return n\n'
                                '    # check cache, compute, store, return\n'
                                '    return 0\n'
                                '\n'
                                'print(fib(10))\n'
                                'print(fib(20))\n'
                                'print(fib(30))\n'
                            ),
                            'solution_code': (
                                'def fib(n, cache={}):\n'
                                '    if n <= 1:\n'
                                '        return n\n'
                                '    if n in cache:\n'
                                '        return cache[n]\n'
                                '    cache[n] = fib(n - 1, cache) + fib(n - 2, cache)\n'
                                '    return cache[n]\n'
                                '\n'
                                'print(fib(10))\n'
                                'print(fib(20))\n'
                                'print(fib(30))\n'
                            ),
                            'expected_output': '55\n6765\n832040',
                            'test_cases': [{'input': '', 'expected_output': '55\n6765\n832040'}],
                            'explain': 'Without the cache branch this is the naive exponential fib — the whole point is the two lines that read and write cache[n].',
                        },
                        {
                            'slug': 'dp-checklist',
                            'title': 'DP-shaped?',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL problems suited to dynamic programming.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Minimum coins for a target amount', 'is_correct': True},
                                {'id': 'b', 'text': 'Longest common subsequence of two strings', 'is_correct': True},
                                {'id': 'c', 'text': 'Sorting an array of names', 'is_correct': False},
                                {'id': 'd', 'text': 'Counting paths in a grid moving right/down', 'is_correct': True},
                            ],
                            'explain': 'Sorting has no subproblem answers to combine into an optimum — the other three all rebuild big answers from reused small ones.',
                        },
                        {
                            'slug': 'memo-speedup',
                            'title': 'The complexity jump',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Naive fib is ~O(2ⁿ). Memoised fib is:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(n) time, O(n) space', 'is_correct': True},
                                {'id': 'b', 'text': 'still O(2ⁿ), just tidier', 'is_correct': False},
                                {'id': 'c', 'text': 'O(log n)', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n²)', 'is_correct': False},
                            ],
                            'explain': 'Each of n+1 distinct inputs computed once with O(1) work after the cache hit — the cache costs space to buy the speed.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 10 Quiz',
                    'slug': 'problem-solving-quiz',
                    'objective': 'Check the four design patterns and when each applies.',
                    'duration': 10,
                    'body': """# Chapter 10 Quiz

Six questions on recursion mechanics, divide & conquer, greedy proofs
and the DP checklist.""",
                    'exercises': [
                        {
                            'slug': 'q10-base-case',
                            'title': 'Missing base case',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A recursive function whose recursive case never approaches the base case will…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'grow frames until the stack limit (RecursionError / crash)', 'is_correct': True},
                                {'id': 'b', 'text': 'silently return 0', 'is_correct': False},
                                {'id': 'c', 'text': 'skip the recursive calls', 'is_correct': False},
                                {'id': 'd', 'text': 'run once, then cache', 'is_correct': False},
                            ],
                            'explain': 'Frames pile up with nobody ever answering — Python raises at ~1000 deep, C++ typically segfaults.',
                        },
                        {
                            'slug': 'q10-dc-independence',
                            'title': 'D&C requirement',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Divide & conquer needs the subproblem answers to be…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'combined afterwards — the split parts solved independently', 'is_correct': True},
                                {'id': 'b', 'text': 'shared through a global mutable cache', 'is_correct': False},
                                {'id': 'c', 'text': 'always equal in size', 'is_correct': False},
                                {'id': 'd', 'text': 'greedy at every level', 'is_correct': False},
                            ],
                            'explain': 'Equal halves are the common case, not a requirement (quick sort splits unevenly); the contract is independent solve + combine.',
                        },
                        {
                            'slug': 'q10-greedy-proof',
                            'title': 'Before trusting greedy',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You may safely use a greedy algorithm when…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'you have shown local-optimal steps compose into a global optimum', 'is_correct': True},
                                {'id': 'b', 'text': 'it is the simplest option in the room', 'is_correct': False},
                                {'id': 'c', 'text': 'the input is sorted', 'is_correct': False},
                                {'id': 'd', 'text': 'it ran fast on your tests', 'is_correct': False},
                            ],
                            'explain': 'Speed and passing tests never prove CORRECTNESS — the {1,3,4} coin set ran fast and wrong.',
                        },
                        {
                            'slug': 'q10-fib-after',
                            'title': 'One number saved',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Memoised fib(6) with the lesson code: how many times is the BODY of fib (past the cache/base checks) actually COMPUTE a new value for n=6 or below? Count distinct n values computed. Number only, remember n=0,1 hit base.',
                            'xp_reward': 50,
                            'expected_output': '5',
                            'explain': 'Distinct computed values: fib(2)…fib(6) — five; 0 and 1 return from the base case. That is the whole trick: n work, not 2ⁿ.',
                        },
                        {
                            'slug': 'q10-strategy-match',
                            'title': 'Match problem to strategy',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct pairings.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Finding a word in a sorted dictionary page by page: divide & conquer (binary-style)', 'is_correct': True},
                                {'id': 'b', 'text': 'Editing one string into another with min operations: DP', 'is_correct': True},
                                {'id': 'c', 'text': 'Making change with real coins using fewest coins: greedy', 'is_correct': True},
                                {'id': 'd', 'text': 'Visiting a tree children-before-parent: level order', 'is_correct': False},
                            ],
                            'explain': 'Children-before-parent is POST-order — depth-first, not breadth. A pattern-matching trap, not a knowledge one.',
                        },
                        {
                            'slug': 'q10-recursion-iterative',
                            'title': 'Rewrite rule',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Any recursive function can be rewritten as a loop plus an explicit ____ (one lowercase word — the structure holding pending frames).',
                            'xp_reward': 40,
                            'solution_code': 'stack',
                            'explain': 'The call stack IS a stack; managing it yourself turns recursion into iteration.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 11 ════════════════════
        {
            'title': 'Final Practical Project',
            'slug': 'final-project',
            'description': 'Design and build a Student Records Management System, choosing structures by required operations.',
            'lessons': [
                {
                    'title': 'Project Brief: Student Records Management System',
                    'slug': 'project-brief',
                    'objective': 'Design the system: pick structures for each required operation and justify the costs.',
                    'duration': 20,
                    'body': """# The project this whole course was for

Build the core of a **Student Records Management System** for a college
of up to 10,000 students. The exercises in this chapter are the graded
milestones; this brief is the design document you implement against.

## Required operations (the customer's list)
1. **Add/update** a student record by ID — O(1) expected.
2. **Look up** one student by ID — O(1) expected.
3. **List all students sorted by grade** — cheap re-computation
   acceptable (O(n log n) on demand), since it runs once per report.
4. **Range report:** all students with grade between X and Y.
5. **Queue of pending record requests** — first submitted, first served.
6. **Undo last record change** — most recent first.

## The design table (write this BEFORE code — it is rubric item 1)

| Operation | Structure chosen | Cost justification |
|---|---|---|
| add/update/find by ID | hash table (dict) keyed by ID | O(1) expected; IDs unordered — order irrelevant |
| sorted-by-grade listing | sort the values on demand, or BST by grade | O(n log n) per report vs O(log n + k) BST walk |
| range report X–Y | BST/sorted structure by grade — dict is WRONG here | dict cannot answer ranges; ordered structure can |
| pending requests | queue (deque) | FIFO is the stated policy |
| undo history | stack | LIFO is literally what "undo" means |

Every entry is a course concept earned in chapters 3–9: this table IS
the exam of "choose the data structure by required operations."

## Record shape
A record is a dict: `{'id': 'S1', 'name': 'Amina', 'grade': 88}`.
Grade statistics (count, max, min, average) come free by scanning
values once — O(n), remember constants do not matter in Big-O.

## Hints
- Milestone 1 (add/find) is ~8 lines: a dict, an `addOrUpdate`, a `find`.
- For range reports do NOT sort the whole list per query if you can
  sort once and bisect — chapter 6's binary search finds the window.
- The undo stack stores the previous value (or None if the key was new).
- Test edge cases the way chapter 1 taught: empty system, single
  student, duplicate ID update, range with no matches.

## Grading rubric (what "done" means)
- **Correctness 40%** — all milestones run; lookups and updates exact.
- **Structure choices 30%** — the design table: right structure per
  operation, honest Big-O justification (a wrong-but-fast-looking answer
  loses here; a justified one does not).
- **Complexity analysis 15%** — stated costs match the implementation
  (no claiming O(1) for your range report built on a dict scan).
- **Edge cases & testing 15%** — empty input, duplicate IDs, no-match
  ranges behave sanely.

## Common design mistakes seen in past attempts
- Choosing a linked list for "find by ID" because "insertion is easy" —
  the operation list says lookups dominate; that is a hash table.
- Claiming range queries are O(log n) on a plain dict — they are O(n).
- Reimplementing the queue as a list with `pop(0)` and missing that it
  is O(n) per pop (chapter 5's note).

## Lesson summary
Read operations → choose structures → justify costs → then code. The
milestones below grade exactly that chain.""",
                    'exercises': [
                        {
                            'slug': 'design-table-range',
                            'title': 'Design call: range report',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'For operation 4 ("all students with grade between X and Y", frequent), which primary structure fits best?',
                            'xp_reward': 60,
                            'choices': [
                                {'id': 'a', 'text': 'A BST (or sorted array + binary search) keyed by grade', 'is_correct': True},
                                {'id': 'b', 'text': 'A hash table keyed by grade', 'is_correct': False},
                                {'id': 'c', 'text': 'A singly linked list, unsorted', 'is_correct': False},
                                {'id': 'd', 'text': 'A stack of grades', 'is_correct': False},
                            ],
                            'explain': 'Ranges need ORDER, which only the BST/sorted family keeps queryable; the hash table throws order away for O(1) exact lookups.',
                        },
                        {
                            'slug': 'design-table-undo',
                            'title': 'Design call: undo',
                            'exercise_type': 'multiple_choice',
                            'instructions': '"Undo the most recent record change, newest first" demands which structure?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Stack', 'is_correct': True},
                                {'id': 'b', 'text': 'Queue', 'is_correct': False},
                                {'id': 'c', 'text': 'Hash table', 'is_correct': False},
                                {'id': 'd', 'text': 'Binary tree', 'is_correct': False},
                            ],
                            'explain': 'Most-recent-first is the LIFO contract itself — a queue would undo the OLDEST change.',
                        },
                        {
                            'slug': 'design-analysis-claim',
                            'title': 'Honest analysis',
                            'exercise_type': 'multiple_select',
                            'instructions': 'A student submits: "find-by-ID uses a dict: O(1) expected; range-by-grade uses the same dict: O(log n); pending requests use deque: O(1) append/pop." Select ALL correct verdicts.',
                            'xp_reward': 60,
                            'choices': [
                                {'id': 'a', 'text': 'find-by-ID claim is correct', 'is_correct': True},
                                {'id': 'b', 'text': 'range-by-grade claim is wrong: scanning a dict is O(n)', 'is_correct': True},
                                {'id': 'c', 'text': 'deque claim is correct', 'is_correct': True},
                                {'id': 'd', 'text': 'range-by-grade would also be O(log n) with a plain unsorted array', 'is_correct': False},
                            ],
                            'explain': 'Rubric item: analysis must MATCH the code — claiming O(log n) on an order-free structure is exactly the inflation the rubric punishes.',
                        },
                    ],
                },
                {
                    'title': 'Build the Core (Graded Milestones)',
                    'slug': 'project-milestones',
                    'objective': 'Implement the system core: registry with O(1) lookup, report sorting, and range query.',
                    'duration': 30,
                    'body': """# Milestones, graded by the sandbox

Each milestone is a runnable piece of your system. Write them the way
you would in the real project file — functions, then a demo `print`.

## Milestone 1: the registry
`add_or_update(sid, name, grade)` maintains a dict keyed by student ID
(insert O(1) expected, update in place), and the system answers
"how many students?" and "what is Amina\'s grade?" instantly.

## Milestone 2: the honor roll
Report 3 in the brief: return names sorted by grade descending, ties
broken alphabetically — one `sorted` call with a key tuple is enough,
and its O(n log n) is the price you justified in the design table.

## Milestone 3: the range report
With students kept in a list sorted by grade ONCE, use binary search
(chapter 6 — `bisect` is that exact algorithm industrialised) to find
the X–Y window in O(log n + k). Compare against the naive O(n) scan and
you have your complexity-analysis paragraph written.

The three exercises below ARE these milestones; passing all three with
the design table from the brief completes the project. If you want the
full stretch version, add the undo stack and request queue to your own
repo and run the edge-case checklist from chapter 1.""",
                    'exercises': [
                        {
                            'slug': 'ms1-registry',
                            'title': 'Milestone 1: registry',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'Using a dict keyed by student ID, add_or_update the '
                                'records S1/Amina/88, S2/Bilal/74, then UPDATE S1 to '
                                'grade 91. Print the count of students, then Amina\'s '
                                'grade, each on its own line. Expected: 2 then 91.'
                            ),
                            'context': 'One dict, two operations: assignment inserts AND updates.',
                            'xp_reward': 120,
                            'starter_code': (
                                'db = {}\n'
                                '\n'
                                'def add_or_update(sid, name, grade):\n'
                                '    # store/replace the record\n'
                                '    pass\n'
                                '\n'
                                'def grade_of(sid):\n'
                                '    # O(1) lookup\n'
                                '    return None\n'
                                '\n'
                                'add_or_update("S1", "Amina", 88)\n'
                                'add_or_update("S2", "Bilal", 74)\n'
                                'add_or_update("S1", "Amina", 91)\n'
                                'print(len(db))\n'
                                'print(grade_of("S1"))\n'
                            ),
                            'solution_code': (
                                'db = {}\n'
                                '\n'
                                'def add_or_update(sid, name, grade):\n'
                                '    db[sid] = {"name": name, "grade": grade}\n'
                                '\n'
                                'def grade_of(sid):\n'
                                '    rec = db.get(sid)\n'
                                '    return rec["grade"] if rec else None\n'
                                '\n'
                                'add_or_update("S1", "Amina", 88)\n'
                                'add_or_update("S2", "Bilal", 74)\n'
                                'add_or_update("S1", "Amina", 91)\n'
                                'print(len(db))\n'
                                'print(grade_of("S1"))\n'
                            ),
                            'expected_output': '2\n91',
                            'test_cases': [{'input': '', 'expected_output': '2\n91'}],
                            'explain': 'If the count printed 3, the update appended instead of replacing — dict assignment keyed by ID handles both jobs.',
                        },
                        {
                            'slug': 'ms2-honor-roll',
                            'title': 'Milestone 2: honor roll',
                            'exercise_type': 'code',
                            'difficulty': 'medium',
                            'instructions': (
                                'Sort records by grade DESCENDING, ties alphabetical, '
                                'and print one name per line. Records: '
                                'Amina 91, Bilal 74, Sana 91, Dani 60. '
                                'Expected: Amina, Sana (91 tie alphabetical), then Bilal, Dani.'
                            ),
                            'xp_reward': 120,
                            'starter_code': (
                                'records = [("Amina", 91), ("Bilal", 74), ("Sana", 91), ("Dani", 60)]\n'
                                '\n'
                                '# sort by -grade then name; print names one per line\n'
                                'for name, grade in []:\n'
                                '    print(name)\n'
                            ),
                            'solution_code': (
                                'records = [("Amina", 91), ("Bilal", 74), ("Sana", 91), ("Dani", 60)]\n'
                                '\n'
                                'ordered = sorted(records, key=lambda r: (-r[1], r[0]))\n'
                                'for name, grade in ordered:\n'
                                '    print(name)\n'
                            ),
                            'expected_output': 'Amina\nSana\nBilal\nDani',
                            'test_cases': [{'input': '', 'expected_output': 'Amina\nSana\nBilal\nDani'}],
                            'explain': 'The key (-grade, name) is the standard two-criterion sort idiom: negate for descending, string stays ascending.',
                        },
                        {
                            'slug': 'ms3-range-report',
                            'title': 'Milestone 3: range report',
                            'exercise_type': 'code',
                            'difficulty': 'hard',
                            'instructions': (
                                'Grades are kept SORTED ascending: [55, 60, 74, 88, 91, 93]. '
                                'Use the bisect module (binary search!) to print how many '
                                'grades fall in the range 70–90 inclusive. Expected: 2'
                            ),
                            'context': 'bisect_left(a, x) = first index with value >= x; bisect_right(a, x) = first index with value > x.',
                            'xp_reward': 150,
                            'starter_code': (
                                'import bisect\n'
                                '\n'
                                'grades = [55, 60, 74, 88, 91, 93]\n'
                                'lo, hi = 70, 90\n'
                                '\n'
                                '# count via two bisect calls\n'
                                'print(0)\n'
                            ),
                            'solution_code': (
                                'import bisect\n'
                                '\n'
                                'grades = [55, 60, 74, 88, 91, 93]\n'
                                'lo, hi = 70, 90\n'
                                '\n'
                                'print(bisect.bisect_right(grades, hi) - bisect.bisect_left(grades, lo))\n'
                            ),
                            'expected_output': '2',
                            'test_cases': [{'input': '', 'expected_output': '2'}],
                            'explain': 'bisect_right(90)=4 (55,60,74,88 below-or-equal… first >90), bisect_left(70)=2 → window [74, 88]. O(log n) — the range report the design table promised.',
                        },
                    ],
                },
            ],
        },
    ],
    # ════════════════════ Final Assessment ════════════════════
    'assessment': [
        {
            'slug': 'fa-01-program-equation',
            'title': 'The core equation',
            'exercise_type': 'multiple_choice',
            'instructions': 'The famous formulation "good software = X + Y" pairs which two things?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'data structures and algorithms', 'is_correct': True},
                {'id': 'b', 'text': 'speed and memory', 'is_correct': False},
                {'id': 'c', 'text': 'syntax and semantics', 'is_correct': False},
                {'id': 'd', 'text': 'recursion and iteration', 'is_correct': False},
            ],
            'explain': 'Chapter 1: algorithms act on structures; the pairing decides the cost.',
        },
        {
            'slug': 'fa-02-adt-meaning',
            'title': 'ADT definition',
            'exercise_type': 'multiple_choice',
            'instructions': 'An Abstract Data Type specifies…',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'WHAT operations exist and guarantee, not HOW they are built', 'is_correct': True},
                {'id': 'b', 'text': 'exact memory layout and pointers', 'is_correct': False},
                {'id': 'c', 'text': 'the fastest implementation available', 'is_correct': False},
                {'id': 'd', 'text': 'only the programming language to use', 'is_correct': False},
            ],
            'explain': 'The contract/implementation split is what lets list exist in ten languages.',
        },
        {
            'slug': 'fa-03-big-o-nested',
            'title': 'Nested loop cost',
            'exercise_type': 'output_prediction',
            'instructions': 'An outer loop runs n times; its inner loop also runs n times per outer pass. Order of growth, written O(n^__), digit only.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '2',
            'explain': 'n × n work: quadratic — chapter 2\'s loop-counting rule.',
        },
        {
            'slug': 'fa-04-drop-constants',
            'title': 'Dropping the small stuff',
            'exercise_type': 'multiple_choice',
            'instructions': 'An algorithm runs 3n² + 50n + 200 operations. Its Big-O is:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'O(n²)', 'is_correct': True},
                {'id': 'b', 'text': 'O(3n² + 50n + 200)', 'is_correct': False},
                {'id': 'c', 'text': 'O(n)', 'is_correct': False},
                {'id': 'd', 'text': 'O(n³)', 'is_correct': False},
            ],
            'explain': 'Keep the dominant term, drop coefficients — that IS the Big-O simplification recipe.',
        },
        {
            'slug': 'fa-05-array-vs-list',
            'title': 'Array vs linked list',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL true comparisons of dynamic arrays vs linked lists.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Index access: array O(1), linked list O(n)', 'is_correct': True},
                {'id': 'b', 'text': 'Insert at a known middle node: list O(1) after arrival, array O(n) shifting', 'is_correct': True},
                {'id': 'c', 'text': 'Arrays win every operation', 'is_correct': False},
                {'id': 'd', 'text': 'Linked lists give cheap random jumps to position k', 'is_correct': False},
            ],
            'explain': 'Contiguity buys indexing; pointers buy splice-in-place. Each side wins its own game.',
        },
        {
            'slug': 'fa-06-two-pointer-shrink',
            'title': 'Two-pointer setting',
            'exercise_type': 'multiple_choice',
            'instructions': 'The two-pointer technique (heads and tails closing) applies to which kind of input?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'sorted (or otherwise monotonic) arrays', 'is_correct': True},
                {'id': 'b', 'text': 'any unsorted collection', 'is_correct': False},
                {'id': 'c', 'text': 'hash tables', 'is_correct': False},
                {'id': 'd', 'text': 'graphs with cycles', 'is_correct': False},
            ],
            'explain': 'The decision "move left or move right" needs order to be sound — chapter 3\'s precondition.',
        },
        {
            'slug': 'fa-07-stack-use',
            'title': 'Stack job',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL tasks naturally solved with a STACK.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Undo / redo history', 'is_correct': True},
                {'id': 'b', 'text': 'Balancing brackets', 'is_correct': True},
                {'id': 'c', 'text': 'Ticket line served first-come-first-served', 'is_correct': False},
                {'id': 'd', 'text': 'Reversing a sequence', 'is_correct': True},
            ],
            'explain': 'The ticket line is the textbook QUEUE job — LIFO would serve the last customer first.',
        },
        {
            'slug': 'fa-08-queue-output',
            'title': 'Queue dry-run',
            'exercise_type': 'output_prediction',
            'instructions': 'Empty queue. enqueue A, B, C; dequeue once; enqueue D; then dequeue twice. Which two items come out, comma-separated?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': 'B, C',
            'explain': 'FIFO: A left first; then B, then C. D waits behind them.',
        },
        {
            'slug': 'fa-09-binary-precondition',
            'title': 'Binary search price of admission',
            'exercise_type': 'multiple_choice',
            'instructions': 'Binary search is CORRECT only when the data is:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'sorted, with direct index access', 'is_correct': True},
                {'id': 'b', 'text': 'any list, halved recursively', 'is_correct': False},
                {'id': 'c', 'text': 'stored in a hash table', 'is_correct': False},
                {'id': 'd', 'text': 'smaller than 1000 items', 'is_correct': False},
            ],
            'explain': 'Elimination logic ("all left of mid is smaller") needs sortedness; midpoint jumps need arrays, not linked lists.',
        },
        {
            'slug': 'fa-10-bs-comparisons',
            'title': 'Halving count',
            'exercise_type': 'output_prediction',
            'instructions': 'Worst case: how many comparisons does binary search need on 16 sorted items? (Halve 16 down to the final probe. Number only.)',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '5',
            'explain': '16→8→4→2→1 probes: ⌊log₂16⌋+1 = 5. Chapter 6\'s counting pattern.',
        },
        {
            'slug': 'fa-11-stability',
            'title': 'Stability meaning',
            'exercise_type': 'multiple_choice',
            'instructions': 'In sorting, "stable" guarantees:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'equal keys keep their original relative order', 'is_correct': True},
                {'id': 'b', 'text': 'the sort never exceeds O(n log n)', 'is_correct': False},
                {'id': 'c', 'text': 'no extra memory is used', 'is_correct': False},
                {'id': 'd', 'text': 'the array is already sorted', 'is_correct': False},
            ],
            'explain': 'Stability is about equal elements only — why multi-key reports sort secondary keys first.',
        },
        {
            'slug': 'fa-12-merge-cost',
            'title': 'Merge vs quick',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL true statements about merge sort vs quick sort.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Merge guarantees O(n log n) worst case; quick can hit O(n²)', 'is_correct': True},
                {'id': 'b', 'text': 'Merge typically costs O(n) extra memory', 'is_correct': True},
                {'id': 'c', 'text': 'Quick is usually the faster average-case, in-place choice', 'is_correct': True},
                {'id': 'd', 'text': 'Merge needs a pivot value', 'is_correct': False},
            ],
            'explain': 'Merge splits by POSITION — no pivot exists there; that positional split is exactly why its cost never degrades.',
        },
        {
            'slug': 'fa-13-bubble-pass',
            'title': 'Bubble pass guarantee',
            'exercise_type': 'multiple_choice',
            'instructions': 'After ONE full pass of bubble sort on any array, what is certainly true?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'The largest element sits at the end', 'is_correct': True},
                {'id': 'b', 'text': 'The array is fully sorted', 'is_correct': False},
                {'id': 'c', 'text': 'The smallest element is at the front', 'is_correct': False},
                {'id': 'd', 'text': 'Exactly one swap happened', 'is_correct': False},
            ],
            'explain': 'Adjacent swapping carries the max rightward until it settles — pass 1\'s one guaranteed trophy.',
        },
        {
            'slug': 'fa-14-insertion-key',
            'title': 'Insertion sort mechanics',
            'exercise_type': 'fill_blank',
            'instructions': 'Insertion sort repeatedly takes the next element (the "key") and SHIFTS larger elements of the sorted prefix one slot to the ____ (one lowercase word: left or right?).',
            'xp_reward': 10,
            'is_final_assessment': True,
            'solution_code': 'right',
            'explain': 'Shifting right opens the gap where the key lands — a[ j+1 ] = a[ j ] in the loop.',
        },
        {
            'slug': 'fa-15-tree-height',
            'title': 'Tree height',
            'exercise_type': 'output_prediction',
            'instructions': 'Root 5 → children 3, 8 → 3 has children 1, 4. Height in EDGES from root to deepest leaf? Number only.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '2',
            'explain': 'Two edges down: 5→3→1 (or →4).',
        },
        {
            'slug': 'fa-16-bst-invalid',
            'title': 'Validate the BST',
            'exercise_type': 'multiple_choice',
            'instructions': 'Root 10 with right child 15, whose LEFT child is 7. Verdict?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Not a BST: 7 is inside 10\'s right subtree but smaller than 10', 'is_correct': True},
                {'id': 'b', 'text': 'A BST: every parent beats its own children correctly', 'is_correct': False},
                {'id': 'c', 'text': 'A BST: left children must simply exist', 'is_correct': False},
                {'id': 'd', 'text': 'Cannot tell without weights', 'is_correct': False},
            ],
            'explain': 'The contract binds whole SUBTREES, not direct children — option b is the trap the chapter warned about.',
        },
        {
            'slug': 'fa-17-traversal-order',
            'title': 'Sorted output',
            'exercise_type': 'fill_blank',
            'instructions': 'On a BST, the ____-order traversal (left → node → right) prints values sorted. One lowercase word.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'solution_code': 'in',
            'explain': 'In-order: smaller subtree first, then node, then larger — recursively.',
        },
        {
            'slug': 'fa-18-hash-index',
            'title': 'Hash arithmetic',
            'exercise_type': 'output_prediction',
            'instructions': 'Table of 11 slots, hash(key) = 47. Which slot index? Number only.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '3',
            'explain': '47 % 11 = 3 — modulo maps any hash into slot range.',
        },
        {
            'slug': 'fa-19-collision-strategies',
            'title': 'Handling collisions',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL legitimate hash-collision strategies.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Chaining: a small list per slot', 'is_correct': True},
                {'id': 'b', 'text': 'Open addressing: probe for the next free slot', 'is_correct': True},
                {'id': 'c', 'text': 'Deleting the older key', 'is_correct': False},
                {'id': 'd', 'text': 'Rehashing into a bigger table when load factor climbs', 'is_correct': True},
            ],
            'explain': 'Dropping data is never collision handling; a-c are the standard toolkit, with resizing keeping chains short.',
        },
        {
            'slug': 'fa-20-graph-bfs',
            'title': 'BFS guarantee',
            'exercise_type': 'multiple_choice',
            'instructions': 'In an unweighted graph, BFS from S reaches every vertex by:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'a path with the fewest possible edges', 'is_correct': True},
                {'id': 'b', 'text': 'the deepest available branch first', 'is_correct': False},
                {'id': 'c', 'text': 'random edge selection', 'is_correct': False},
                {'id': 'd', 'text': 'minimum total weight', 'is_correct': False},
            ],
            'explain': 'Ring-by-ring expansion = distance order; weights (d) need Dijkstra instead.',
        },
        {
            'slug': 'fa-21-traversal-cost',
            'title': 'Graph work bound',
            'exercise_type': 'multiple_choice',
            'instructions': 'BFS and DFS on an adjacency-list graph with V vertices, E edges cost:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'O(V + E) each', 'is_correct': True},
                {'id': 'b', 'text': 'O(V²) each', 'is_correct': False},
                {'id': 'c', 'text': 'O(E log E)', 'is_correct': False},
                {'id': 'd', 'text': 'O(1) amortised', 'is_correct': False},
            ],
            'explain': 'Each vertex enqueued/returned once and each edge examined once — order differs, work does not.',
        },
        {
            'slug': 'fa-22-recursion-illness',
            'title': 'The recursive symptom',
            'exercise_type': 'multiple_choice',
            'instructions': 'A recursive function that never terminates almost always lacks…',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'a base case the recursive calls actually reach', 'is_correct': True},
                {'id': 'b', 'text': 'enough RAM', 'is_correct': False},
                {'id': 'c', 'text': 'a return in the recursive case', 'is_correct': False},
                {'id': 'd', 'text': 'global variables', 'is_correct': False},
            ],
            'explain': 'Either no base case exists, or the argument never walks toward it — chapter 10\'s two ingredients.',
        },
        {
            'slug': 'fa-23-dp-definition',
            'title': 'DP essentials',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL true statements about dynamic programming.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'It needs overlapping subproblems and optimal substructure', 'is_correct': True},
                {'id': 'b', 'text': 'Memoisation is its top-down form', 'is_correct': True},
                {'id': 'c', 'text': 'It guarantees O(1) answers', 'is_correct': False},
                {'id': 'd', 'text': 'Bottom-up DP fills a table from smallest cases upward', 'is_correct': True},
            ],
            'explain': 'DP buys polynomial time (often O(n) or O(n²) from exponential), never magic O(1).',
        },
        {
            'slug': 'fa-24-greedy-verdict',
            'title': 'Greedy verdict',
            'exercise_type': 'output_prediction',
            'instructions': 'Coins {1, 3, 4} making 6: how many coins does the GREEDY largest-first method use? Number only.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '3',
            'explain': '4+1+1: three — optimal is 3+3, two. The counterexample you must never forget: greedy without proof is a guess.',
        },
        {
            'slug': 'fa-25-project-choice',
            'title': 'Final design judgment',
            'exercise_type': 'multiple_choice',
            'instructions': 'A system needs: instant lookup by ID AND frequent "grade between X and Y" reports. The best primary setup is:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'dict keyed by ID PLUS an ordered structure (sorted grades/BST) — each serves its query', 'is_correct': True},
                {'id': 'b', 'text': 'dict only — it can do both with scans', 'is_correct': False},
                {'id': 'c', 'text': 'linked list only — insertion is O(1)', 'is_correct': False},
                {'id': 'd', 'text': 'stack — records arrive over time', 'is_correct': False},
            ],
            'explain': 'The project\'s closing lesson: real systems pair structures, one per question the data must answer.',
        },
        {
            'slug': 'fa-26-big-o-compare',
            'title': 'Choose the faster growth class',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which complexity grows SLOWEST (best) for large n?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'O(n log n)', 'is_correct': True},
                {'id': 'b', 'text': 'O(n²)', 'is_correct': False},
                {'id': 'c', 'text': 'O(2ⁿ)', 'is_correct': False},
                {'id': 'd', 'text': 'O(n log² n) with a squared log factor', 'is_correct': False},
            ],
            'explain': 'n log n beats any quadratic, and quadratic beats exponential — chapter 2\'s growth ladder.',
        },
    ],
}
