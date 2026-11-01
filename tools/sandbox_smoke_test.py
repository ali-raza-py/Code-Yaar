"""Smoke test for the real sandbox execution paths (Python + C++).

Run:  python tools/sandbox_smoke_test.py
Exits non-zero if any check fails, so it doubles as a cheap CI gate.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402

django.setup()

from learning.services.sandbox import get_sandbox  # noqa: E402

CPP_HELLO = (
    '#include <iostream>\n'
    'using namespace std;\n'
    '\n'
    'int main() {\n'
    '    cout << "Hello, World!";\n'
    '    return 0;\n'
    '}\n'
)

CPP_SUM = (
    '#include <iostream>\n'
    'using namespace std;\n'
    '\n'
    'int main() {\n'
    '    int a, b;\n'
    '    cin >> a >> b;\n'
    '    cout << a + b;\n'
    '    return 0;\n'
    '}\n'
)

CPP_BROKEN = 'int main() { cout << "oops"; }\n'
CPP_LOOP = 'int main() { while (true) {} return 0; }\n'

failures = []


def check(label, condition, detail=''):
    mark = 'ok  ' if condition else 'FAIL'
    print(f'[{mark}] {label} {detail}')
    if not condition:
        failures.append(label)


sandbox = get_sandbox()
print(f'sandbox class : {type(sandbox).__name__}')
print(f'cpp compiler  : {getattr(sandbox, "cpp_exe", None)}')
print(f'languages     : {getattr(sandbox, "supported_languages", lambda: ["n/a"])()}')
print()

check('health_check (python)', sandbox.health_check())

py = sandbox.execute('print(6 * 7)', 'python')
check('python execute', py.status == 'success' and py.output.strip() == '42',
      f'status={py.status} out={py.output!r}')

res = sandbox.execute(CPP_HELLO, 'cpp')
check('cpp compile+run', res.status == 'success' and res.output.strip() == 'Hello, World!',
      f'status={res.status} out={res.output!r} err={res.error!r}')

res = sandbox.execute(CPP_SUM, 'cpp', stdin='15 27\n')
check('cpp stdin (cin)', res.status == 'success' and res.output.strip() == '42',
      f'status={res.status} out={res.output!r}')

tests = [
    {'input': '15 10', 'expected_output': '25'},
    {'input': '3 4', 'expected_output': '7'},
    {'input': '100 1', 'expected_output': '101'},
]
graded = sandbox.run_tests(CPP_SUM, 'cpp', tests)
check('cpp run_tests compile-once', len(graded) == 3 and all(t.status == 'passed' for t in graded),
      str([(t.test_number, t.status, t.actual) for t in graded]))

bad = sandbox.run_tests(CPP_SUM, 'cpp', [{'input': '2 2', 'expected_output': '99'}])
check('cpp run_tests catches wrong output', bad[0].status == 'failed',
      f'status={bad[0].status} msg={bad[0].message!r}')

broken = sandbox.execute(CPP_BROKEN, 'cpp')
check('cpp compile error surfaced', broken.status == 'error' and 'error' in (broken.error or ''),
      f'err={(broken.error or "")[:160]!r}')

loop = sandbox.execute(CPP_LOOP, 'cpp')
check('cpp timeout reported honestly', loop.status == 'timeout', f'status={loop.status}')

unknown = sandbox.execute(CPP_HELLO, 'cobol')
check('unsupported language refused', unknown.status == 'error' and 'C++' in (unknown.error or ''),
      f'err={(unknown.error or "")[:120]!r}')

empty = sandbox.execute('', 'cpp')
check('empty code refused', empty.status == 'error', f'status={empty.status}')

print()
if failures:
    print(f'{len(failures)} check(s) failed: {failures}')
    sys.exit(1)
print('all sandbox checks passed')
