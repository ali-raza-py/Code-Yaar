"""Course 5 — Problem Solving and Data Structures in Python.

Think like a programmer: break problems down, choose the right structure,
and measure your solution. Because implementations are written in Python,
code exercises here ARE executed and graded by the real server-side sandbox,
and the final assessment mixes reasoning questions with runnable checks.
"""

COURSE = {
    'slug': 'problem-solving-dsa',
    'title': 'Problem Solving and Data Structures in Python',
    'subtitle': 'Break problems down, pick the right structure, measure the cost.',
    'description': (
        'A practical introduction to algorithmic thinking. You will learn a '
        'repeatable problem-solving process, work with arrays, strings, '
        'dictionaries, stacks and queues, reason about Big-O complexity, and '
        'implement each idea in Python. Code exercises are executed and graded '
        'by the real sandbox.'
    ),
    'difficulty': 'intermediate',
    'language': 'python',
    'prerequisites': 'The Python Programming Foundations course (functions, lists, dicts).',
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
        'Apply a four-step process to an unfamiliar problem.',
        'Choose between list, string, dict, stack and queue for a task.',
        'Implement common array and string algorithms in Python.',
        'Use dictionaries for counting and membership in O(1).',
        'Explain Big-O notation and compare two solutions.',
        'Model undo/history problems with a stack.',
    ],
    'modules': [
        {
            'title': 'The Problem-Solving Process',
            'slug': 'process',
            'description': 'Understand, plan, implement, review.',
            'lessons': [
                {
                    'title': 'Understand and Plan Before You Code',
                    'slug': 'understand-plan',
                    'objective': 'Restate a problem with inputs, outputs and edge cases before coding.',
                    'duration': 10,
                    'body': (
                        '# Four steps\n\n'
                        '1. **Understand** — restate the problem; list inputs, expected '
                        'output, and edge cases (empty? one item? duplicates? negatives?).\n'
                        '2. **Plan** — describe the approach in words or pseudocode before '
                        'writing syntax.\n'
                        '3. **Implement** — code the plan in small pieces; test each.\n'
                        '4. **Review** — check correctness on edge cases, then improve.\n\n'
                        'Example: *"Find the largest number in a list."*\n'
                        '- Input: a list of numbers. Edge case: the list may be empty.\n'
                        '- Plan: assume the first item is the largest, scan the rest, '
                        'replace whenever a bigger one appears.\n\n'
                        'Writing two or three **manual test cases** first (e.g. '
                        '`[3,1,4] -> 4`, `[] -> error/None`) catches vague thinking.\n\n'
                        '## Common mistakes\n'
                        'Starting to code before knowing what should happen to an empty '
                        'input — most bugs live in undefined edge cases.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'edge-cases-quiz',
                            'title': 'Most valuable first question',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Before coding "reverse the words in a sentence", which question matters most?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Which colour should the output be?', 'is_correct': False},
                                {'id': 'b', 'text': 'What should happen for an empty or whitespace-only string?', 'is_correct': True},
                                {'id': 'c', 'text': 'Should we use a for or a while loop?', 'is_correct': False},
                                {'id': 'd', 'text': 'How large is the Python library?', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Arrays and Strings',
            'slug': 'arrays-strings',
            'description': 'Sequential data and the scans you perform on it.',
            'lessons': [
                {
                    'title': 'Scanning and Accumulating',
                    'slug': 'scan-accumulate',
                    'objective': 'Sum, count and track values with a single pass.',
                    'duration': 14,
                    'body': (
                        '# The one-pass scan\n\n'
                        'Most array problems are a **scan with an accumulator**:\n\n'
                        '```python\ndef total(xs):\n    running = 0          # accumulator\n'
                        '    for x in xs:\n        running += x\n    return running\n```\n\n'
                        'Variants: count how many items pass a test, find the maximum, '
                        'check whether any item matches.\n\n'
                        'Strings are scanned the same way — characters in order:\n\n'
                        '```python\ndef count_char(s, ch):\n    n = 0\n    for c in s:\n'
                        '        if c == ch:\n            n += 1\n    return n\n```\n\n'
                        'Two pointers (one at each end moving inward) reverse or check '
                        'palindromes without extra memory.\n\n'
                        '## Common mistakes\n'
                        'Initialising a max accumulator to `0` — wrong for lists of '
                        'negative numbers; seed it with the first element instead.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'sum-evens',
                            'title': 'Sum of even numbers',
                            'exercise_type': 'code',
                            'instructions': (
                                'Write a program that prints the sum of the even numbers '
                                'in the list `[1, 2, 3, 4, 5, 6]`. Your code must print '
                                'a single number.'
                            ),
                            'context': 'Scan-and-accumulate with a filter — the bread and butter of array work.',
                            'constraints': 'Use a loop; do not hard-code the answer.',
                            'expected_output': '12',
                            'starter_code': 'nums = [1, 2, 3, 4, 5, 6]\n# print the sum of the even numbers\n',
                            'solution_code': 'nums = [1, 2, 3, 4, 5, 6]\ntotal = 0\nfor n in nums:\n    if n % 2 == 0:\n        total += n\nprint(total)',
                            'test_cases': [{'input': '', 'expected_output': '12'}],
                            'explain': 'Even numbers 2 + 4 + 6 = 12. The accumulator only adds items passing the n % 2 == 0 test.',
                            'xp_reward': 100,
                        },
                        {
                            'slug': 'palindrome-pointers',
                            'title': 'Two-pointer check',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Reversing a list in place with two pointers swaps elements from…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'the middle outward to both ends', 'is_correct': False},
                                {'id': 'b', 'text': 'both ends inward until they meet', 'is_correct': True},
                                {'id': 'c', 'text': 'random positions', 'is_correct': False},
                                {'id': 'd', 'text': 'only the first and last elements once', 'is_correct': False},
                            ],
                        },
                    ],
                },
                {
                    'title': 'Finding Things: Linear Search',
                    'slug': 'linear-search',
                    'objective': 'Search an unsorted sequence item by item.',
                    'duration': 10,
                    'body': (
                        '# Linear search\n\n'
                        'The simplest search: look at each item until you find the target '
                        'or run out of items.\n\n'
                        '```python\ndef find_first(xs, target):\n    for i, x in enumerate(xs):\n'
                        '        if x == target:\n            return i        # position found\n'
                        '    return -1             # not present\n```\n\n'
                        'Worst case examines all `n` items — we call that **O(n)** time. '
                        'It needs no assumption about order, so it works on every list.\n\n'
                        'Returning a sentinel (`-1`) versus raising an error is a design '
                        'choice; document it.\n\n'
                        '## Common mistakes\n'
                        'Forgetting the "not found" path — a function that silently '
                        'returns `None` at the end surprises its callers.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'first-above-10',
                            'title': 'First value above 10',
                            'exercise_type': 'code',
                            'instructions': (
                                'Given `scores = [4, 9, 12, 7, 15]`, print the FIRST '
                                'score greater than 10 using a loop.'
                            ),
                            'expected_output': '12',
                            'starter_code': 'scores = [4, 9, 12, 7, 15]\n# print the first score above 10\n',
                            'solution_code': 'for s in scores:\n    if s > 10:\n        print(s)\n        break',
                            'test_cases': [{'input': '', 'expected_output': '12'}],
                            'explain': 'Scanning left to right, 12 is the first score above 10; break stops the scan immediately.',
                            'xp_reward': 100,
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Dictionaries and Hashing',
            'slug': 'dicts-hashing',
            'description': 'Constant-time membership, counting and grouping.',
            'lessons': [
                {
                    'title': 'Counting with a Dictionary',
                    'slug': 'counting',
                    'objective': 'Build a frequency table with dict lookups.',
                    'duration': 14,
                    'body': (
                        '# Why dicts are fast\n\n'
                        'A Python `dict` maps keys to values using **hashing**: the key\'s '
                        'hash picks a slot, so lookups and membership tests average '
                        '**O(1)** — no scanning.\n\n'
                        '## Frequency table\n\n'
                        '```python\ndef letter_counts(word):\n    counts = {}\n'
                        '    for ch in word:\n        counts[ch] = counts.get(ch, 0) + 1\n'
                        '    return counts\n\nprint(letter_counts("banana"))\n'
                        "# {'b': 1, 'a': 3, 'n': 2}\n```\n\n"
                        '`get(key, 0)` reads a key with a default, avoiding KeyError.\n\n'
                        'Membership `ch in counts` is O(1), the same test inside a loop '
                        'over a *list* would be O(n) — a classic speedup: turn "have I '
                        'seen this?" into a set.\n\n'
                        '## Common mistakes\n'
                        'Mutating a dict while iterating its keys. Iterate a copy '
                        '(`list(d.items())`) or build a new dict instead.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'count-as',
                            'title': 'Count the letter a',
                            'exercise_type': 'code',
                            'instructions': (
                                'Print how many times the letter "a" appears in the word '
                                '"apple" using a loop.'
                            ),
                            'expected_output': '1',
                            'starter_code': 'word = "apple"\n# print the number of "a" characters\n',
                            'solution_code': 'word = "apple"\nn = 0\nfor ch in word:\n    if ch == "a":\n        n += 1\nprint(n)',
                            'test_cases': [{'input': '', 'expected_output': '1'}],
                            'xp_reward': 100,
                        },
                        {
                            'slug': 'dict-membership-cost',
                            'title': 'Cost of `key in dict`',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'On average, checking `key in my_dict` takes…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'O(1) time', 'is_correct': True},
                                {'id': 'b', 'text': 'O(n) time', 'is_correct': False},
                                {'id': 'c', 'text': 'O(log n) time', 'is_correct': False},
                                {'id': 'd', 'text': 'time proportional to the value size', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Complexity Thinking',
            'slug': 'big-o',
            'description': 'Compare solutions by how their cost grows.',
            'lessons': [
                {
                    'title': 'Big-O in Plain Terms',
                    'slug': 'big-o-basics',
                    'objective': 'Classify loops by growth rate and compare two solutions.',
                    'duration': 12,
                    'body': (
                        '# Growth, not stopwatch seconds\n\n'
                        '**Big-O** describes how an algorithm\'s work grows as the input '
                        'size `n` grows. It ignores constants and focuses on the '
                        'dominant term.\n\n'
                        '| Shape | Example |\n|-------|---------|\n'
                        '| O(1) | dict lookup |\n| O(n) | one scan of a list |\n'
                        '| O(n log n) | built-in `sorted()` |\n'
                        '| O(n²) | nested loop over the same list |\n\n'
                        '```python\nfor x in xs:            # O(n)\n    print(x)\n\n'
                        'for x in xs:            # O(n * n) = O(n²)\n    for y in xs:\n'
                        '        print(x, y)\n```\n\n'
                        'Doubling `n` doubles O(n) work but quadruples O(n²) work — that '
                        'is why the nested "is there a duplicate?" scan loses to a '
                        'set-based one for large lists.\n\n'
                        '## Common mistakes\n'
                        'Arguing your O(n²) code is fine because "n is small on my '
                        'machine". Inputs grow; choose the shape that scales.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'nested-loop-order',
                            'title': 'Classify the nested loop',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A loop over n items that itself loops over the same n items is…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'O(n)', 'is_correct': False},
                                {'id': 'b', 'text': 'O(n log n)', 'is_correct': False},
                                {'id': 'c', 'text': 'O(n²)', 'is_correct': True},
                                {'id': 'd', 'text': 'O(2n)', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'dup-check-pick',
                            'title': 'Faster duplicate check',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'For a large list, which finds any duplicate fastest?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Compare every pair with two nested loops', 'is_correct': False},
                                {'id': 'b', 'text': 'Add items to a set and stop when an add finds the item already present', 'is_correct': True},
                                {'id': 'c', 'text': 'Sort, then look at the first item only', 'is_correct': False},
                                {'id': 'd', 'text': 'Count items with len()', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Stacks and Queues',
            'slug': 'stacks-queues',
            'description': 'Order your work: last-in-first-out vs first-in-first-out.',
            'lessons': [
                {
                    'title': 'LIFO Stacks and FIFO Queues',
                    'slug': 'stack-queue',
                    'objective': 'Model undo with a stack and scheduling with a queue.',
                    'duration': 12,
                    'body': (
                        '# Two ordering disciplines\n\n'
                        'A **stack** is last-in-first-out (LIFO) — like a pile of plates. '
                        'Python lists are stacks via `append` / `pop`:\n\n'
                        '```python\nundo = []\nundo.append("typed A")   # push\n'
                        'undo.append("typed B")\nlast = undo.pop()        # "typed B" — most recent\n```\n\n'
                        'Undo history, browser back-stacks and matching brackets all '
                        'want "the most recent thing first" → stack.\n\n'
                        'A **queue** is first-in-first-out (FIFO) — a ticket line. Use '
                        '`collections.deque` with `append` and `popleft`:\n\n'
                        '```python\nfrom collections import deque\nline = deque(["first", "second"])\n'
                        'next_up = line.popleft()    # "first"\n```\n\n'
                        'Print jobs, task schedulers and breadth-first search want '
                        '"fair order" → queue.\n\n'
                        '## Common mistakes\n'
                        'Using `list.pop(0)` as a queue — it shifts every remaining item, '
                        'costing O(n) per dequeue; `deque.popleft()` is O(1).\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'undo-pops',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'What does this print?\n\n```python\nundo = []\n'
                                'undo.append("a")\nundo.append("b")\nprint(undo.pop())\n```'
                            ),
                            'expected_output': 'b',
                            'explain': 'pop() removes the LAST appended item — LIFO: "b" came after "a".',
                            'xp_reward': 60,
                        },
                        {
                            'slug': 'queue-structure',
                            'title': 'Choose the structure',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A printer must serve jobs in the order they arrived. Use a…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'stack (LIFO)', 'is_correct': False},
                                {'id': 'b', 'text': 'queue (FIFO)', 'is_correct': True},
                                {'id': 'c', 'text': 'dict of priorities', 'is_correct': False},
                                {'id': 'd', 'text': 'set of job ids', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'bracket-balance',
                            'title': 'Last bracket must close first',
                            'exercise_type': 'code',
                            'instructions': (
                                'For the expression `"(a*(b+c))"`, print the character '
                                'that the FIRST closing bracket `)` matches. Hint: track '
                                'opening brackets in a stack; the one that matches a '
                                'closer is always the most recent opener.'
                            ),
                            'expected_output': '(',
                            'starter_code': 'expr = "(a*(b+c))"\n# print the opener matched by the first closer\n',
                            'solution_code': 'expr = "(a*(b+c))"\nstack = []\nfor ch in expr:\n    if ch == "(":\n        stack.append(ch)\n    elif ch == ")":\n        print(stack.pop())\n        break',
                            'test_cases': [{'input': '', 'expected_output': '('}],
                            'explain': 'Scanning with a stack, the first closer matches the most recent opener — the "(" before "b".',
                            'xp_reward': 120,
                        },
                    ],
                },
            ],
        },
    ],
    'assessment': [
        {
            'slug': 'dsa-final-process',
            'title': 'First step of the process',
            'exercise_type': 'multiple_choice',
            'instructions': 'What should you do first when facing an unfamiliar coding problem?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'Start typing code and figure it out as you go', 'is_correct': False},
                {'id': 'b', 'text': 'Restate the inputs, outputs and edge cases', 'is_correct': True},
                {'id': 'c', 'text': 'Copy a solution from the internet', 'is_correct': False},
                {'id': 'd', 'text': 'Choose a programming language', 'is_correct': False},
            ],
        },
        {
            'slug': 'dsa-final-max-seed',
            'title': 'Seeding the maximum accumulator',
            'exercise_type': 'multiple_choice',
            'instructions': 'To find the largest number safely in a possibly-negative list, the accumulator should start at…',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': '0', 'is_correct': False},
                {'id': 'b', 'text': 'the first element of the list', 'is_correct': True},
                {'id': 'c', 'text': '-1', 'is_correct': False},
                {'id': 'd', 'text': 'the list length', 'is_correct': False},
            ],
        },
        {
            'slug': 'dsa-final-count',
            'title': 'Count the vowels',
            'exercise_type': 'code',
            'instructions': (
                'Print how many vowels (a, e, i, o, u) appear in the word '
                '"education". Lowercase only.'
            ),
            'expected_output': '5',
            'starter_code': 'word = "education"\n# print the vowel count\n',
            'solution_code': 'word = "education"\nvowels = "aeiou"\nn = 0\nfor ch in word:\n    if ch in vowels:\n        n += 1\nprint(n)',
            'test_cases': [{'input': '', 'expected_output': '5'}],
            'xp_reward': 20,
        },
        {
            'slug': 'dsa-final-big-o',
            'title': 'Big-O of sorted()',
            'exercise_type': 'multiple_choice',
            'instructions': 'Python\'s built-in sorted(list) is…',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'O(n)', 'is_correct': False},
                {'id': 'b', 'text': 'O(n log n)', 'is_correct': True},
                {'id': 'c', 'text': 'O(n²)', 'is_correct': False},
                {'id': 'd', 'text': 'O(1)', 'is_correct': False},
            ],
        },
        {
            'slug': 'dsa-final-queue-cost',
            'title': 'Why deque over list for queues',
            'exercise_type': 'multiple_choice',
            'instructions': 'list.pop(0) is avoided for queues because removing the front element…',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'is O(n) — every remaining item must shift', 'is_correct': True},
                {'id': 'b', 'text': 'raises IndexError on lists', 'is_correct': False},
                {'id': 'c', 'text': 'reverses the list', 'is_correct': False},
                {'id': 'd', 'text': 'is slower only when the list is empty', 'is_correct': False},
            ],
        },
    ],
}
