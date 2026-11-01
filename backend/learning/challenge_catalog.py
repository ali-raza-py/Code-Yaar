"""Canonical content for the six Practice challenges.

This module is the single, database-fed source of truth for the standalone
coding challenges surfaced under /challenges. Each challenge is a self-contained
program problem: the learner writes code that reads from standard input and
writes to standard output, so submissions are genuinely executed and graded by
the same sandbox that handles course exercises (``learning.services.sandbox``).

``sample_tests`` are visible in the workspace and drive "Run". ``hidden_tests``
are used only by "Submit" and are never returned to a client. Every reference
solution below is exercised against both test sets by the seed command's tests.

Adding a language is additive: give the challenge ``languages`` entries and a
matching ``starter_code_cpp`` / ``solution_code_cpp``; the workspace selector and
the API pick them up automatically.
"""

TWO_SUM = {
    'slug': 'two-sum',
    'title': 'Two Sum',
    'description': 'Find the two numbers in an array that add up to a target and return their indices.',
    'difficulty': 'beginner',
    'topic': 'Arrays',
    'estimated_minutes': 20,
    'xp_reward': 75,
    'languages': ['python'],
    'problem_statement': (
        'You are given an array of integers and a target integer. Find the two '
        'distinct elements whose sum equals the target and report their '
        'positions in the array. Exactly one valid pair exists for each input '
        'that has a solution; if no pair adds up to the target, report that no '
        'solution exists.\n\n'
        'A brute-force scan of every pair is O(n\u00b2). Aim for a single pass.'
    ),
    'requirements': [
        'Read the array of integers from the first input line (space-separated).',
        'Read the target from the second input line.',
        'Print the two indices (0-based) separated by a space, smaller index first.',
        'Print -1 if no two numbers add up to the target.',
        'The same element may not be used twice.',
    ],
    'input_description': (
        'Line 1: space-separated integers \u2014 the array.\n'
        'Line 2: a single integer \u2014 the target sum.'
    ),
    'output_description': (
        'A single line: the two 0-based indices separated by one space, in '
        'ascending order, or -1 when no valid pair exists.'
    ),
    'constraints': [
        '0 \u2264 len(array) \u2264 10\u2075',
        '-10\u2079 \u2264 array[i], target \u2264 10\u2079',
        'Exactly one answer is guaranteed when a solution exists.',
    ],
    'examples': [
        {
            'input': '2 7 11 15\n9',
            'output': '0 1',
            'explanation': 'nums[0] + nums[1] = 2 + 7 = 9, so the answer is indices 0 and 1.',
        },
        {
            'input': '3 2 4\n6',
            'output': '1 2',
            'explanation': '2 + 4 = 6, found at indices 1 and 2.',
        },
    ],
    'starter_code': '''import sys


def two_sum(nums, target):
    # Return the two indices (smaller first) whose values add up to target,
    # or None if no such pair exists.
    return None


data = sys.stdin.read().splitlines()
nums = [int(x) for x in data[0].split()] if data and data[0].strip() else []
target = int(data[1]) if len(data) > 1 else 0

result = two_sum(nums, target)
print(f"{result[0]} {result[1]}" if result else "-1")
''',
    'solution_code': '''import sys


def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            j = seen[target - n]
            return (j, i) if j < i else (i, j)
        seen[n] = i
    return None


data = sys.stdin.read().splitlines()
nums = [int(x) for x in data[0].split()] if data and data[0].strip() else []
target = int(data[1]) if len(data) > 1 else 0

result = two_sum(nums, target)
print(f"{result[0]} {result[1]}" if result else "-1")
''',
    'hints': [
        'A pair (a, b) with a + b = target means, for each value a, you are really asking: have I already seen (target - a)?',
        'Store every value you have visited so far in a dictionary keyed by the value, pointing at its index.',
        'Check for (target - current) in that dictionary before inserting the current value \u2014 that also stops you from reusing the same element.',
    ],
    'solution_explanation': (
        'Walk the array once, keeping a hash map from each seen value to its '
        'index. For the current value n, the complement is target - n. If the '
        'complement is already in the map you have found the pair (return the '
        'earlier index first); otherwise record n and continue. Checking '
        'membership before inserting the current value prevents pairing an '
        'element with itself and correctly handles duplicates such as [3, 3].'
    ),
    'time_complexity': 'O(n) \u2014 a single pass with O(1) hash lookups.',
    'space_complexity': 'O(n) \u2014 the hash map stores up to n values.',
    'sample_tests': [
        {'input': '2 7 11 15\n9', 'expected_output': '0 1'},
        {'input': '3 2 4\n6', 'expected_output': '1 2'},
    ],
    'hidden_tests': [
        {'input': '3 3\n6', 'expected_output': '0 1'},
        {'input': '1 5 3 7 2\n9', 'expected_output': '3 4'},
        {'input': '-1 -2 -3 -4 -5\n-8', 'expected_output': '2 4'},
        {'input': '0 4 3 0\n0', 'expected_output': '0 3'},
        {'input': '1 2 3 4\n100', 'expected_output': '-1'},
    ],
}


VALID_PARENTHASES = {
    'slug': 'valid-parentheses',
    'title': 'Valid Parentheses',
    'description': 'Determine whether a string of brackets is properly nested and balanced.',
    'difficulty': 'beginner',
    'topic': 'Stacks',
    'estimated_minutes': 15,
    'xp_reward': 50,
    'languages': ['python'],
    'problem_statement': (
        'Given a string containing only the six characters ()[]{} decide whether '
        'the brackets are balanced. A string is valid when every opening bracket '
        'is closed by the same type of bracket and in the correct order. An empty '
        'string is considered valid.'
    ),
    'requirements': [
        'Read one line containing a bracket string.',
        'Print true if every bracket is correctly matched and nested.',
        'Print false otherwise.',
        'Handle different bracket types independently.',
        'Treat the empty string as valid.',
    ],
    'input_description': 'A single line holding a string of the characters ( ) [ ] { } (possibly empty).',
    'output_description': 'A single line: true or false.',
    'constraints': [
        '0 \u2264 len(string) \u2264 10\u2074',
        'The string contains only the six bracket characters.',
    ],
    'examples': [
        {'input': '()[]{}', 'output': 'true', 'explanation': 'Three independent, correctly closed pairs.'},
        {'input': '([)]', 'output': 'false', 'explanation': 'The ) closes a ( but the most recent opener was [ , so the order is wrong.'},
    ],
    'starter_code': '''import sys


def is_valid(s):
    # Return True when every bracket in s is correctly matched and nested.
    return False


s = ''.join(sys.stdin.read().split())
print('true' if is_valid(s) else 'false')
''',
    'solution_code': '''import sys


def is_valid(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            return False
    return not stack


s = ''.join(sys.stdin.read().split())
print('true' if is_valid(s) else 'false')
''',
    'hints': [
        'Brackets must close in the reverse order they opened \u2014 that is exactly LIFO behaviour, which a stack models.',
        'Push every opening bracket. On a closing bracket, the top of the stack must be its matching opener.',
        'The string is valid only if every closing bracket matched AND the stack is empty at the end.',
    ],
    'solution_explanation': (
        'Scan left to right. Push each opening bracket onto a stack. For a '
        'closing bracket, pop only if the top of the stack is the matching '
        'opener; otherwise the string is invalid. An opening onto an empty '
        'stack, or a leftover opener once the string ends, both fail. The empty '
        'string trivially satisfies the conditions and is valid.'
    ),
    'time_complexity': 'O(n) \u2014 one pass over the characters.',
    'space_complexity': 'O(n) worst case \u2014 the stack holds at most n openers.',
    'sample_tests': [
        {'input': '()[]{}', 'expected_output': 'true'},
        {'input': '([)]', 'expected_output': 'false'},
    ],
    'hidden_tests': [
        {'input': '{[]}', 'expected_output': 'true'},
        {'input': '', 'expected_output': 'true'},
        {'input': ')', 'expected_output': 'false'},
        {'input': '(((', 'expected_output': 'false'},
        {'input': '[{()}]', 'expected_output': 'true'},
    ],
}


REVERSE_LINKED_LIST = {
    'slug': 'reverse-linked-list',
    'title': 'Reverse a Linked List',
    'description': 'Reverse a singly linked list and print the reversed values.',
    'difficulty': 'intermediate',
    'topic': 'Data Structures',
    'estimated_minutes': 30,
    'xp_reward': 150,
    'languages': ['python'],
    'problem_statement': (
        'A singly linked list is built from the integers on the input line, in '
        'order. Reverse the list by re-pointing the nodes (do not just print the '
        'values backwards) and output the list again from the new head. Think in '
        'terms of three pointers: previous, current, and the next node you must '
        'not lose.'
    ),
    'requirements': [
        'Build a linked list from the space-separated integers on the input line.',
        'Reverse it by mutating the node links.',
        'Print the reversed values, space-separated, on one line.',
        'An empty input prints an empty line.',
        'A single-element list is unchanged.',
    ],
    'input_description': 'A single line of space-separated integers representing the list (may be empty).',
    'output_description': 'One line of space-separated integers: the list in reversed order.',
    'constraints': [
        '0 \u2264 len(list) \u2264 10\u2075',
        '-10\u2079 \u2264 node value \u2264 10\u2079',
    ],
    'examples': [
        {'input': '1 2 3 4 5', 'output': '5 4 3 2 1', 'explanation': 'The links are flipped so 5 becomes the new head.'},
        {'input': '7', 'output': '7', 'explanation': 'A one-node list reverses to itself.'},
    ],
    'starter_code': '''import sys


class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def reverse(head):
    # Re-point the links and return the new head of the reversed list.
    return head


vals = sys.stdin.read().split()
head = None
tail = None
for v in vals:
    node = ListNode(int(v))
    if head is None:
        head = node
    else:
        tail.next = node
    tail = node

out = []
cur = reverse(head)
while cur:
    out.append(str(cur.val))
    cur = cur.next
print(' '.join(out))
''',
    'solution_code': '''import sys


class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev


vals = sys.stdin.read().split()
head = None
tail = None
for v in vals:
    node = ListNode(int(v))
    if head is None:
        head = node
    else:
        tail.next = node
    tail = node

out = []
cur = reverse(head)
while cur:
    out.append(str(cur.val))
    cur = cur.next
print(' '.join(out))
''',
    'hints': [
        'At each node you want cur.next to point backwards, but doing so loses the rest of the list \u2014 grab cur.next into a temporary first.',
        'Keep prev and cur. Each step: remember next, flip cur.next to prev, then advance prev and cur.',
        'When the loop ends, prev is the new head.',
    ],
    'solution_explanation': (
        'Iterate with three pointers. Save cur.next, then rewire cur.next to '
        'point at prev, then slide prev forward to cur and cur forward to the '
        'saved next. Because the next reference is captured before it is '
        'overwritten, no nodes are lost. An empty list (head is None) and a '
        'single-node list are handled by the same loop. The recursive version '
        'reverses the tail first, then makes the current node the successor\u2019s '
        'next, using O(n) call-stack space.'
    ),
    'time_complexity': 'O(n) \u2014 every node is visited once.',
    'space_complexity': 'O(1) iterative (O(n) call stack if done recursively).',
    'sample_tests': [
        {'input': '1 2 3 4 5', 'expected_output': '5 4 3 2 1'},
        {'input': '7', 'expected_output': '7'},
    ],
    'hidden_tests': [
        {'input': '', 'expected_output': ''},
        {'input': '1 2', 'expected_output': '2 1'},
        {'input': '-1 -2 -3', 'expected_output': '-3 -2 -1'},
        {'input': '0 0 1', 'expected_output': '1 0 0'},
    ],
}


BUILD_A_BST = {
    'slug': 'binary-search-tree',
    'title': 'Build a BST',
    'description': 'Implement insert, search and delete for a binary search tree, then answer operations.',
    'difficulty': 'intermediate',
    'topic': 'Trees',
    'estimated_minutes': 45,
    'xp_reward': 200,
    'languages': ['python'],
    'problem_statement': (
        'Start with an empty binary search tree and process a stream of commands. '
        'Insert keeps the BST ordering and ignores duplicate values. Search '
        'reports whether a value is present. Delete removes a value while '
        'preserving BST order \u2014 including the tricky case of a node with two '
        'children. Output only what search and inorder commands produce.'
    ),
    'requirements': [
        'insert v: add v, ignoring a value that already exists.',
        'search v: print true if v is in the tree, else false.',
        'delete v: remove v if present (leaf, one child, or two children).',
        'inorder: print the tree\u2019s in-order traversal, space-separated.',
        'insert and delete print nothing; only search and inorder add output lines.',
    ],
    'input_description': (
        'One command per line: "insert <v>", "search <v>", "delete <v>" or '
        '"inorder". <v> is an integer.'
    ),
    'output_description': 'For every search line print true/false; for every inorder line print the traversal. Lines appear in the order the commands ran.',
    'constraints': [
        '1 \u2264 number of commands \u2264 10\u2074',
        '-10\u2079 \u2264 v \u2264 10\u2079',
        'Deleting a value that is absent is a no-op.',
    ],
    'examples': [
        {
            'input': 'insert 5\ninsert 3\ninsert 8\nsearch 3\nsearch 7\ninorder',
            'output': 'true\nfalse\n3 5 8',
            'explanation': 'After inserting 5, 3 and 8, searching 3 is true, 7 is false, and in-order reads the sorted values.',
        },
    ],
    'starter_code': '''import sys


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def insert(root, val):
    # Return the (possibly new) root with val inserted. Ignore duplicates.
    return root


def contains(root, val):
    return False


def delete(root, val):
    return root


def inorder(root, out):
    return out


root = None
res = []
for ln in sys.stdin.read().splitlines():
    parts = ln.split()
    if not parts:
        continue
    op = parts[0]
    if op == 'insert':
        root = insert(root, int(parts[1]))
    elif op == 'search':
        res.append('true' if contains(root, int(parts[1])) else 'false')
    elif op == 'delete':
        root = delete(root, int(parts[1]))
    elif op == 'inorder':
        res.append(' '.join(inorder(root, [])))
print('\\n'.join(res))
''',
    'solution_code': '''import sys


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def insert(root, val):
    if root is None:
        return Node(val)
    if val < root.val:
        root.left = insert(root.left, val)
    elif val > root.val:
        root.right = insert(root.right, val)
    return root


def contains(root, val):
    cur = root
    while cur:
        if val == cur.val:
            return True
        cur = cur.left if val < cur.val else cur.right
    return False


def delete(root, val):
    if root is None:
        return None
    if val < root.val:
        root.left = delete(root.left, val)
    elif val > root.val:
        root.right = delete(root.right, val)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        succ = root.right
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = delete(root.right, succ.val)
    return root


def inorder(root, out):
    if root:
        inorder(root.left, out)
        out.append(str(root.val))
        inorder(root.right, out)
    return out


root = None
res = []
for ln in sys.stdin.read().splitlines():
    parts = ln.split()
    if not parts:
        continue
    op = parts[0]
    if op == 'insert':
        root = insert(root, int(parts[1]))
    elif op == 'search':
        res.append('true' if contains(root, int(parts[1])) else 'false')
    elif op == 'delete':
        root = delete(root, int(parts[1]))
    elif op == 'inorder':
        res.append(' '.join(inorder(root, [])))
print('\\n'.join(res))
''',
    'hints': [
        'Insert follows the normal search path: go left when smaller, right when larger, and hang the new node where the search would have hit None.',
        'Ignoring duplicates just means: when val equals a node\u2019s value, stop and return that node unchanged.',
        'Deleting a two-child node: copy in the in-order successor (smallest value of the right subtree), then delete that successor node \u2014 which has at most one child.',
    ],
    'solution_explanation': (
        'Insert recurses down the correct side and returns the (unchanged) root, '
        'creating a node where the path ends; equal values return early so '
        'duplicates are never stored. Search walks down by comparison. Delete '
        'finds the node, then splices it out: a node with \u22641 child is replaced '
        'by that child; a node with two children has its value overwritten by '
        'the minimum of its right subtree and then that successor is deleted '
        'from the right subtree, which preserves BST invariants. In-order '
        'traversal (left, node, right) always lists the values sorted.'
    ),
    'time_complexity': 'O(h) per operation, h the tree height (O(log n) balanced, O(n) worst case).',
    'space_complexity': 'O(h) for the recursion stack during insert/delete.',
    'sample_tests': [
        {
            'input': 'insert 5\ninsert 3\ninsert 8\nsearch 3\nsearch 7\ninorder',
            'expected_output': 'true\nfalse\n3 5 8',
        },
    ],
    'hidden_tests': [
        {
            'input': 'insert 10\ninsert 5\ninsert 15\ninsert 5\ninsert 3\ninsert 7\ninsert 15\ninorder\ndelete 10\ninorder\nsearch 10\ndelete 5\ninorder\nsearch 3',
            'expected_output': '3 5 7 10 15\n3 5 7 15\nfalse\n3 7 15\ntrue',
        },
        {
            'input': 'insert 5\ninsert 3\ninsert 8\ninsert 1\ninsert 4\ninorder\nsearch 4\nsearch 6',
            'expected_output': '1 3 4 5 8\ntrue\nfalse',
        },
        {
            'input': 'search 1\ndelete 99\ninsert 42\ndelete 42\ninorder',
            'expected_output': 'false',
        },
    ],
}


LRU_CACHE = {
    'slug': 'lru-cache',
    'title': 'LRU Cache',
    'description': 'Design a Least Recently Used cache with O(1) get and put that evicts the least-recently-used key when full.',
    'difficulty': 'advanced',
    'topic': 'System Design',
    'estimated_minutes': 60,
    'xp_reward': 300,
    'languages': ['python'],
    'problem_statement': (
        'Build a fixed-capacity cache that supports two operations in O(1):\n'
        '\u2022 put key value \u2014 insert or update a key. If the cache is over '
        'capacity, evict the least recently used key.\n'
        '\u2022 get key \u2014 return the value if present (and mark it most recently '
        'used), otherwise return -1.\n'
        'Reading or updating a key makes it the most recently used. The first '
        'input line sets the capacity; each later line is one operation. Print '
        'the result of every get.'
    ),
    'requirements': [
        'First input line is the integer capacity.',
        'Subsequent lines are "put <key> <value>" or "get <key>".',
        'put updates an existing key and marks it most recently used.',
        'When capacity is exceeded, evict the least recently used key.',
        'get marks the key most recently used and prints its value, or prints -1 if absent.',
        'Only get operations produce output.',
    ],
    'input_description': 'Line 1: capacity. Following lines: one put/get operation each.',
    'output_description': 'One line per get: the cached value, or -1 when the key is not present.',
    'constraints': [
        '1 \u2264 capacity \u2264 10\u2074',
        '1 \u2264 number of operations \u2264 10\u2075',
        'Keys and values are integers.',
    ],
    'examples': [
        {
            'input': '2\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2',
            'output': '1\n-1',
            'explanation': 'get 1 returns 1 and marks 1 most-recent; put 3 then evicts 2 (the least recently used), so get 2 returns -1.',
        },
    ],
    'starter_code': '''import sys
from collections import OrderedDict


def main():
    lines = [l for l in sys.stdin.read().splitlines() if l.strip()]
    cap = int(lines[0].split()[0])
    cache = OrderedDict()
    out = []
    for ln in lines[1:]:
        parts = ln.split()
        # Implement put and get as an LRU cache with the given capacity.
        # For every get, append its result (the value, or -1) to out.
        pass
    print('\\n'.join(out))


main()
''',
    'solution_code': '''import sys
from collections import OrderedDict


def main():
    lines = [l for l in sys.stdin.read().splitlines() if l.strip()]
    cap = int(lines[0].split()[0])
    cache = OrderedDict()
    out = []
    for ln in lines[1:]:
        parts = ln.split()
        if parts[0] == 'put':
            key, value = int(parts[1]), int(parts[2])
            if key in cache:
                cache.move_to_end(key)
            cache[key] = value
            if len(cache) > cap:
                cache.popitem(last=False)
        else:  # get
            key = int(parts[1])
            if key in cache:
                cache.move_to_end(key)
                out.append(str(cache[key]))
            else:
                out.append('-1')
    print('\\n'.join(out))


main()
''',
    'hints': [
        'You need both fast key lookup AND a sense of recency order \u2014 a plain dict gives the first, but not the second.',
        'A doubly linked list keeps recency order; pairing it with a hash map gives O(1) access to any node.',
        'In Python an OrderedDict already fuses both: move_to_end marks most-recent and popitem(last=False) evicts the oldest.',
    ],
    'solution_explanation': (
        'The canonical design pairs a hash map (key \u2192 node) with a doubly '
        'linked list ordered from most- to least-recently-used. get looks the '
        'node up in O(1) via the map and moves it to the front; put inserts or '
        'updates and, if the cache overflows, removes the tail (least recently '
        'used) in O(1). Python\u2019s OrderedDict encapsulates exactly this: it keeps '
        'insertion/access order, move_to_end refreshes recency, and '
        'popitem(last=False) evicts the oldest entry \u2014 giving O(1) get and put.'
    ),
    'time_complexity': 'O(1) amortized for both get and put.',
    'space_complexity': 'O(capacity) \u2014 at most `capacity` entries are stored.',
    'sample_tests': [
        {
            'input': '2\nput 1 1\nput 2 2\nget 1\nput 3 3\nget 2',
            'expected_output': '1\n-1',
        },
    ],
    'hidden_tests': [
        {
            'input': '2\nput 1 10\nput 2 20\nget 1\nput 3 30\nget 2\nget 3',
            'expected_output': '10\n-1\n30',
        },
        {
            'input': '2\nput 1 1\nput 1 2\nget 1',
            'expected_output': '2',
        },
        {
            'input': '1\nput 1 1\nget 1\nput 2 2\nget 1\nget 2',
            'expected_output': '1\n-1\n2',
        },
        {
            'input': '3\nget 99\nput 1 1\nget 1',
            'expected_output': '-1\n1',
        },
    ],
}


RATE_LIMITER = {
    'slug': 'rate-limiter',
    'title': 'Rate Limiter',
    'description': 'Implement a sliding-window rate limiter that decides whether each request is allowed or throttled.',
    'difficulty': 'advanced',
    'topic': 'System Design',
    'estimated_minutes': 45,
    'xp_reward': 250,
    'languages': ['python'],
    'problem_statement': (
        'You are the gatekeeper for an API. The rule is a sliding window: no '
        'more than N allowed requests may fall within any trailing window of T '
        'seconds. Requests arrive as integer timestamps in non-decreasing order. '
        'For each request decide whether to ALLOW it \u2014 counting it toward the '
        'window \u2014 or THROTTLE it, which does not count. A throttled request '
        'must not consume quota, so it is never recorded in the window.'
    ),
    'requirements': [
        'First line: two integers N (max requests) and T (window length in seconds).',
        'Each following line is one request timestamp (integer, non-decreasing).',
        'A request at time t is allowed only if fewer than N allowed requests lie in (t - T, t].',
        'Print ALLOWED or THROTTLED for every incoming request.',
        'Throttled requests do not count against the window.',
    ],
    'input_description': 'Line 1: "N T". Later lines: one integer timestamp each.',
    'output_description': 'One line per request: ALLOWED or THROTTLED.',
    'constraints': [
        '1 \u2264 N \u2264 10\u2075',
        '1 \u2264 T \u2264 10\u2075',
        'Timestamps are non-decreasing integers.',
    ],
    'examples': [
        {
            'input': '2 3\n1\n2\n3\n4\n5',
            'output': 'ALLOWED\nALLOWED\nTHROTTLED\nALLOWED\nALLOWED',
            'explanation': 'At t=3 the window (0, 3] already holds requests 1 and 2, so it is throttled. By t=4 the request at 1 has aged out of (1, 4], freeing quota.',
        },
    ],
    'starter_code': '''import sys


def should_allow(t, allowed, max_requests, window):
    # Drop entries that have aged out of the window (t - window, t].
    # If fewer than max_requests remain, append t to allowed and return
    # True (ALLOWED); otherwise return False (THROTTLED) without recording.
    return False


lines = [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]
max_requests, window = map(int, lines[0].split())

allowed = []
out = []
for ln in lines[1:]:
    t = int(ln)
    if should_allow(t, allowed, max_requests, window):
        out.append('ALLOWED')
    else:
        out.append('THROTTLED')
print('\\n'.join(out))
''',
    'solution_code': '''import sys


def should_allow(t, allowed, max_requests, window):
    allowed[:] = [a for a in allowed if a > t - window]
    if len(allowed) < max_requests:
        allowed.append(t)
        return True
    return False


lines = [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]
max_requests, window = map(int, lines[0].split())

allowed = []
out = []
for ln in lines[1:]:
    t = int(ln)
    if should_allow(t, allowed, max_requests, window):
        out.append('ALLOWED')
    else:
        out.append('THROTTLED')
print('\\n'.join(out))
''',
    'hints': [
        'Keep only the timestamps that were actually allowed \u2014 a throttled request should never be stored.',
        'Before judging a new request, forget every allowed timestamp that is no longer inside the trailing window.',
        'The window (t - T, t] means a previous request at time p still counts exactly when p > t - T.',
    ],
    'solution_explanation': (
        'A sliding-window log stores every allowed timestamp in order. For a new '
        'request at t, first evict entries at or before t - T (they are outside '
        'the trailing window). If fewer than N entries remain, the request fits '
        'the quota: record it and ALLOW. Otherwise THROTTLE without recording, so '
        'rejected traffic never steals capacity from future requests. Because '
        'timestamps arrive non-decreasing, evictions can drop from the front. '
        'A fixed-window counter is cheaper but bursty at boundaries; the sliding '
        'log is smooth and is the basis for token-bucket / leaky-bucket variants.'
    ),
    'time_complexity': 'O(total requests) with a deque-style front eviction (this reference is O(N) per request worst case).',
    'space_complexity': 'O(N) \u2014 the window holds at most N allowed timestamps.',
    'sample_tests': [
        {
            'input': '2 3\n1\n2\n3\n4\n5',
            'expected_output': 'ALLOWED\nALLOWED\nTHROTTLED\nALLOWED\nALLOWED',
        },
    ],
    'hidden_tests': [
        {
            'input': '3 1\n1\n1\n1\n1\n2',
            'expected_output': 'ALLOWED\nALLOWED\nALLOWED\nTHROTTLED\nALLOWED',
        },
        {
            'input': '2 5\n1\n2\n3\n4',
            'expected_output': 'ALLOWED\nALLOWED\nTHROTTLED\nTHROTTLED',
        },
        {
            'input': '1 2\n1\n2\n3',
            'expected_output': 'ALLOWED\nTHROTTLED\nALLOWED',
        },
        {
            'input': '5 10',
            'expected_output': '',
        },
    ],
}


CHALLENGES = [
    TWO_SUM,
    VALID_PARENTHASES,
    REVERSE_LINKED_LIST,
    BUILD_A_BST,
    LRU_CACHE,
    RATE_LIMITER,
]
