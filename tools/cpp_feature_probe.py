"""Probe which textbook C++ constructs really compile+run under the host g++.

The Sindh Board Class X textbook (Unit 3) teaches <conio.h> getch()/getche(),
getchar(), gets(), puts(). Modern g++/C++17 treats some of these as deprecated
or removed, and console-only functions cannot read piped stdin in a sandbox.
This tells us, per construct, whether a Run button can honestly be offered.

Run:  python tools/cpp_feature_probe.py
"""
import os
import subprocess
import sys
import tempfile

GPP = os.environ.get('CXX', r'C:\MinGW\bin\g++.exe')

CASES = {
    'cout-basic': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ cout << "MY FIRST PROGRAM"; return 0; }\n', ''),

    'cout-endl-tab': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ cout << "a\\tb\\nc\\td"; return 0; }\n', ''),

    'cin-two-numbers': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ int a,b; cin >> a >> b; cout << a + b; return 0; }\n', '3 4\n'),

    'puts-from-stdio': (
        '#include <cstdio>\nint main(){ puts("Hello"); return 0; }\n', ''),

    'getchar-stdin': (
        '#include <cstdio>\nint main(){ int c = getchar(); printf("%d", c); return 0; }\n',
        'A\n'),

    'gets-call': (
        '#include <cstdio>\nint main(){ char ch[20]; gets(ch); printf("%s", ch); return 0; }\n',
        'Pakistan\n'),

    'conio-header': (
        '#include <conio.h>\nint main(){ return 0; }\n', ''),

    'getch-call': (
        '#include <iostream>\n#include <conio.h>\nusing namespace std;\n'
        'int main(){ cout << "Continue(Y/N)?"; char c = getch(); '
        'cout << "|" << c << "|"; return 0; }\n', 'Y\n'),

    'getche-call': (
        '#include <iostream>\n#include <conio.h>\nusing namespace std;\n'
        'int main(){ char c = getche(); cout << "|" << c << "|"; return 0; }\n', 'Y\n'),

    'conio-getch-only': (
        '#include <conio.h>\nint main(){ char c = getch(); return c; }\n', 'Y\n'),

    'old-iostream-dot-h': (
        '#include <iostream.h>\nint main(){ cout << "x"; return 0; }\n', ''),

    'void-main': (
        '#include <iostream>\nusing namespace std;\n'
        'void main(){ cout << "ok"; }\n', ''),

    'switch-statement': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ int d; cin >> d; switch(d){ case 1: cout << "Monday"; break; '
        'default: cout << "Invalid"; } return 0; }\n', '1\n'),

    'do-while': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ int i = 1; do { cout << i; i++; } while (i <= 3); return 0; }\n', ''),

    'goto-statement': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ int i = 0;\nloop: i++; cout << i; if (i < 3) goto loop; return 0; }\n', ''),

    'user-function-return': (
        '#include <iostream>\nusing namespace std;\n'
        'int add(int a, int b){ int c; c = a + b; return c; }\n'
        'int main(){ int x, y = 3, z = 4; x = add(y, z); cout << x; return 0; }\n', ''),

    'function-declaration-first': (
        '#include <iostream>\nusing namespace std;\n'
        'float avg(int v1, int v2, int v3);\n'
        'int main(){ cout << avg(24, 34, 40); }\n'
        'float avg(int v1, int v2, int v3){ return (v1 + v2 + v3) / 3.0; }\n', ''),

    'global-external-var': (
        '#include <iostream>\nusing namespace std;\n'
        'int g = 5;\nint main(){ cout << g; return 0; }\n', ''),

    'cmath-sqrt-pow': (
        '#include <iostream>\n#include <cmath>\nusing namespace std;\n'
        'int main(){ int a; cin >> a; cout << sqrt(a); return 0; }\n', '16\n'),

    'cstring-strcpy-toupper': (
        '#include <iostream>\n#include <cstring>\n#include <cctype>\nusing namespace std;\n'
        'int main(){ char s[10]; strcpy(s, "abc"); cout << toupper(s[0]); return 0; }\n', ''),

    'string-class': (
        '#include <iostream>\n#include <string>\nusing namespace std;\n'
        'int main(){ string name; cin >> name; cout << name; return 0; }\n', 'Ali\n'),

    'define-const': (
        '#include <iostream>\nusing namespace std;\n#define PI 3.14159\n'
        'int main(){ cout << PI; return 0; }\n', ''),

    'const-keyword': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ const float PI = 3.14159; cout << PI; return 0; }\n', ''),

    'bool-output': (
        '#include <iostream>\nusing namespace std;\n'
        'int main(){ int a = 10, b = 20; cout << (a == b) << (a != b) << (a > b) '
        '<< (a < b) << (a >= b) << (a <= b); return 0; }\n', ''),

    'exit-and-return': (
        '#include <iostream>\n#include <cstdlib>\nusing namespace std;\n'
        'int main(){ cout << "a"; exit(0); }\n', ''),
}


def run_case(name, src, stdin, std):
    with tempfile.TemporaryDirectory(prefix='probe-') as tmp:
        path = os.path.join(tmp, 'main.cpp')
        exe = os.path.join(tmp, 'main.exe')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(src)
        build = subprocess.run(
            [GPP, f'-std={std}', '-o', exe, path],
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120,
        )
        if build.returncode != 0:
            noise = [ln.strip() for ln in (build.stderr or '').splitlines()
                     if ': error:' in ln or 'deprecated' in ln.lower()]
            return 'COMPILE-FAIL', (noise[:1] or ['(see full output)'])[0][:130]
        warnings = [ln for ln in (build.stderr or '').splitlines() if ': warning:' in ln]
        try:
            run = subprocess.run(
                [exe], input=stdin, capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=8, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return 'HANGS', 'no console / blocked reading stdin'
        out = (run.stdout or '').strip()
        if run.returncode != 0:
            return 'RUN-FAIL', f'rc={run.returncode} {(run.stderr or "").strip()[:90]}'
        tag = 'OK' + (' (warn)' if warnings else '')
        return tag, out[:90].replace('\n', ' / ')


for std in ('c++17',):
    print(f'=== -std={std}  ({GPP}) ===')
    for name, (src, stdin) in CASES.items():
        try:
            status, detail = run_case(name, src, stdin, std)
        except Exception as exc:  # noqa: BLE001
            status, detail = 'CRASH', str(exc)[:90]
        print(f'{status:>12}  {name:<26} {detail}')
    print()
