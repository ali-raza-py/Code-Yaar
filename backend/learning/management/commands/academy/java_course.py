"""Java Programming — Code Yaar Academy course content specification.

Ten chapters from "what is the JVM" to object-oriented design, exceptions,
collections and lambdas, closing with a console Library Management project.
Java is not executed by the Code Yaar sandbox, so every check is
answer-graded server-side (multiple choice / multiple select / output
prediction / fill in the blank) — nothing pretends to compile for the
learner. Each chapter ends with a Chapter Quiz lesson, and the course
closes with a 24-question final assessment spanning the whole syllabus.
"""

COURSE = {
    'slug': 'java-programming',
    'title': 'Java Programming',
    'subtitle': 'Write once, run anywhere: Java from first program to OOP design.',
    'description': (
        'Java powers Android apps, bank back ends, big-data tools and '
        'countless university courses. This course starts with how Java '
        'runs (the JVM and byte code), builds the language fundamentals — '
        'variables, types, control flow, arrays and strings — then works '
        'through the object-oriented core every Java interview expects: '
        'classes, inheritance, polymorphism, encapsulation and abstraction. '
        'You finish with exceptions, the collections framework, lambdas and '
        'a console Library Management project.'
    ),
    'difficulty': 'beginner',
    'language': 'java',
    'prerequisites': (
        'Some prior programming experience helps (variables, loops, '
        'functions) — the C++ Fundamentals or Python Foundations course on '
        'Code Yaar is enough. Pure beginners should go slightly slower and '
        'type every example into a real JDK.'
    ),
    'track': {
        'slug': 'core-programming',
        'title': 'Programming Foundations',
        'category': 'programming',
        'description': (
            'The languages and thinking that everything else is built on: '
            'C++, Python and Java, plus the data structures and algorithms '
            'they share.'
        ),
    },
    'objectives': [
        'Explain how source, byte code and the JVM make Java portable.',
        'Compile and run programs with javac and java from the terminal.',
        'Declare variables correctly with primitives, reference types and conversions.',
        'Control program flow with if/else, switch, loops and arrays.',
        'Use String methods and understand string immutability.',
        'Design classes with fields, constructors, methods and access modifiers.',
        'Apply inheritance, polymorphism, encapsulation and abstraction.',
        'Handle failures responsibly with try/catch/finally and checked vs unchecked exceptions.',
        'Choose the right collection: ArrayList, HashMap, HashSet and friends.',
        'Read and write basic lambda expressions and stream pipelines.',
    ],
    'certification': {'passing_score': 70},
    'modules': [
        # ════════════════════ Chapter 1 ════════════════════
        {
            'title': 'Introduction to Java',
            'slug': 'java-intro',
            'description': 'Why Java exists, how the JVM runs your code, and your first compiled program.',
            'lessons': [
                {
                    'title': 'Why Java? Write Once, Run Anywhere',
                    'slug': 'java-why',
                    'objective': 'Describe Java\u2019s portability model: source \u2192 byte code \u2192 JVM.',
                    'duration': 10,
                    'body': """# A language built around a machine you install

C++ compiles to machine code for **one** processor and **one** operating
system. Rebuild everything to move it. Java flipped that: compile **once**
to **byte code**, and let a per-platform program — the **Java Virtual
Machine (JVM)** — execute the byte code wherever it runs.

```
Hello.java  --javac-->  Hello.class (byte code)  --JVM-->  runs
 (source)               (portable)               (per-OS translator)
```

"Write once, run anywhere" (WORA) is the slogan; the honest version is
"compile once, run anywhere **that has a JVM**." That JVM exists for
Windows, Linux, macOS and Android — which is exactly why Java became the
default language of servers, Android (historically) and university CS
programs.

## What Java is good at
- **Back-end services**: banks, e-commerce, Android tooling; Spring is
  Java's biggest framework.
- **Big data**: Hadoop and Spark run on the JVM.
- **Learning CS**: strong typing and explicit structure catch beginner
  mistakes early; huge documentation and community.
- **Cross-platform desktop**: one codebase, three operating systems.

## Trade-offs to know before you start
- **Verbosity**: `public static void main(String[] args)` says a lot in
  five words; Python gets to zero boilerplate.
- **Startup cost**: the JVM warms up; tiny scripts favour other tools.
- **Strictness**: every value has a declared type; forgetting a
  semicolon stops compilation — annoying now, forgiving at scale later.

## Java versions you will meet
Java 8 (2014) introduced lambdas and streams; Java 11 and 17 are the long
term support releases most companies run; Java 21 is the current LTS.
This course targets modern Java (17+) but every concept predates it.

## Common mistakes
- Confusing **JVM** (runs byte code), **JRE** (JVM + core libraries) and
  **JDK** (JRE + compiler and tools). You need the **JDK** to develop.
- Believing Java is "slower C++". For most server workloads the JIT
  compiler inside the JVM makes hot code remarkably fast.
- Downloading "Java" from java.com (the runtime) instead of a JDK from
  Adoptium/Temurin or Oracle.

## Lesson summary
Java trades some terseness for portability and safety: you write source,
`javac` emits byte code, and a JVM on any platform runs it. Install a JDK
next.""",
                    'exercises': [
                        {
                            'slug': 'wora-meaning',
                            'title': 'What WORA really claims',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What exactly makes a Java program portable across operating systems?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The same byte code (.class) can be executed by a JVM on any platform', 'is_correct': True},
                                {'id': 'b', 'text': 'The source file is sent to each computer and recompiled there', 'is_correct': False},
                                {'id': 'c', 'text': 'Java compiles directly to each CPU\u2019s machine code at build time', 'is_correct': False},
                                {'id': 'd', 'text': 'Windows and Linux share one Java compiler binary', 'is_correct': False},
                            ],
                            'explain': 'One compile produces byte code; each platform\u2019s JVM does the translating — that\u2019s the whole trick.',
                        },
                        {
                            'slug': 'jdk-jre-jvm',
                            'title': 'Install the right thing',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'To DEVELOP Java programs (compile and run), what must you install?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The JDK — it includes the compiler and the JRE', 'is_correct': True},
                                {'id': 'b', 'text': 'Only the JVM', 'is_correct': False},
                                {'id': 'c', 'text': 'Only the JRE', 'is_correct': False},
                                {'id': 'd', 'text': 'The Spring framework', 'is_correct': False},
                            ],
                            'explain': 'JDK ⊃ JRE ⊃ JVM. Development needs javac, which lives only in the JDK.',
                        },
                        {
                            'slug': 'bytecode-definition',
                            'title': 'Fill the pipeline',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Java source is compiled by javac into an intermediate language called ____ ____ (two lowercase words) that the JVM executes.',
                            'xp_reward': 40,
                            'solution_code': 'byte code',
                            'explain': 'Byte code (also written "bytecode") — not machine code; that\u2019s why the .class file moves between platforms.',
                        },
                    ],
                },
                {
                    'title': 'Setting Up: JDK, javac and java',
                    'slug': 'install-jdk',
                    'objective': 'Install a JDK and compile/run a Java file from the terminal.',
                    'duration': 10,
                    'body': """# The toolchain in three commands

1. **Install a JDK.** Adoptium Temurin (free, open) or Oracle JDK. On
   Windows use the MSI installer; tick "Set JAVA_HOME" and "Add to PATH"
   if offered. Verify:

```
java -version
javac -version
```

Both should print something like `openjdk version "17.0.x"`. If Windows
says "not recognized", PATH setup failed — the usual install gotcha.

2. **Write the source in a file named after the public class.** Java is
   strict: a `public class Hello` MUST live in `Hello.java`.

3. **Compile, then run — two separate commands:**

```
javac Hello.java     # produces Hello.class (byte code)
java Hello           # JVM loads Hello.class and starts at main()
```

Notice `java Hello` has **no `.class` extension** — you name the class,
not the file. Running `java Hello.class` is a classic beginner error.

## Where each artifact lives

| File | Produced by | Contains |
|---|---|---|
| `Hello.java` | you | source code |
| `Hello.class` | `javac` | byte code |
| console output | `java` | what `System.out.println` emitted |

Recompiling overwrites the `.class` — stale byte code is a known trap
after edits (if output looks old, check you re-ran `javac`).

## IDEs vs terminal
IntelliJ IDEA (community edition is free), Eclipse or VS Code with the
Java extension run both steps with one click. Learn the two terminal
commands first anyway: interview questions, build servers and course
graders all speak `javac`/`java`, and errors make sense once you know
which step produced them.

## Common mistakes
- File named `hello.java` while the class is `Hello` — Java is
  **case-sensitive**, filenames must match exactly.
- Running `javac Hello` (missing `.java`) or `java Hello.java`.
- Compiling inside one folder, running from another — `cd` to where the
  `.class` is, or use `-d` output paths deliberately.

## Lesson summary
Install JDK → verify `javac` → write `Name.java` with `public class Name`
→ `javac Name.java` → `java Name`. Two commands, one rule: filenames
mirror public class names.""",
                    'exercises': [
                        {
                            'slug': 'compile-command',
                            'title': 'Command that compiles',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command turns App.java into byte code?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'javac App.java', 'is_correct': True},
                                {'id': 'b', 'text': 'java App.java', 'is_correct': False},
                                {'id': 'c', 'text': 'java App', 'is_correct': False},
                                {'id': 'd', 'text': 'compile App.class', 'is_correct': False},
                            ],
                            'explain': 'javac = compiler (source in, .class out). java = runner; it never compiles.',
                        },
                        {
                            'slug': 'run-command',
                            'title': 'Run it right',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'After compiling, the correct way to RUN the program whose public class is App:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'java App', 'is_correct': True},
                                {'id': 'b', 'text': 'java App.class', 'is_correct': False},
                                {'id': 'c', 'text': 'java App.java', 'is_correct': False},
                                {'id': 'd', 'text': 'javac App', 'is_correct': False},
                            ],
                            'explain': 'The JVM wants the CLASS NAME, extensionless — App.class confuses it, App.java makes it complain.',
                        },
                        {
                            'slug': 'filename-rule',
                            'title': 'The filename law',
                            'exercise_type': 'fill_blank',
                            'instructions': 'A file containing public class MyApp must be named ______.java — write only the part before the dot (exact case).',
                            'xp_reward': 40,
                            'solution_code': 'MyApp',
                            'explain': 'Public class name and filename match exactly, case included — myapp.java fails to compile.',
                        },
                    ],
                },
                {
                    'title': 'Your First Program, Line by Line',
                    'slug': 'first-program',
                    'objective': 'Dissect every token of a Hello World program and its output.',
                    'duration': 12,
                    'body': """# Five lines that say everything

```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

Compile with `javac Hello.java`, run with `java Hello`. Expected output:

```
Hello, World!
```

Now read it like a engineer, not a copy-paster:

- `public class Hello` — every Java program lives in a **class**; Java
  has no free-floating functions. `public` exposes it; `Hello` must
  match the filename.
- `public static void main(String[] args)` — the **entry point**. The
  JVM looks for exactly this signature:
  - `public` — the JVM (outside your class) must call it;
  - `static` — callable without creating a `Hello` object first;
  - `void` — it returns nothing to the operating system;
  - `String[] args` — an array of command-line arguments.
- `System.out.println(...)` — `System` is a class, `out` a static print
  stream inside it, `println` a method that writes text **plus a line
  break**. `print` is the same without the line break.
- `"Hello, World!"` — a **String literal** in double quotes. Single
  quotes are only for one-character values (`'H'`) — using them around
  words is beginner-error #1.
- Semicolons end statements; braces `{}` delimit blocks. The opening
  brace may sit on the next line — that's **style**, not law — but
  mismatched braces are compile errors the compiler reports as
  `';' expected` on a confused line.

## Where does the text go?
`System.out` is the **standard output stream** — your terminal. Redirect
(`java Hello > out.txt`) and the same code writes a file; you never
"target the console" in the code itself.

## Common mistakes
- `main` with wrong spelling, capitalisation (`Main`), or missing
  `String[] args` → compiles, then fails to run: "Main method not found."
- Extra or missing braces from editing — count them when a fresh error
  appears after a change.
- Using `print_line` or `console.log` out of C++/JavaScript muscle —
  Java's spellings are `println` and `System.out.println`.

## Lesson summary
Class wraps everything; the fixed main signature is the door the JVM
knocks on; System.out.println writes a line to standard output. From
here, every chapter adds one more Java concept to those five lines.""",
                    'exercises': [
                        {
                            'slug': 'main-signature',
                            'title': 'The exact door',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which is the signature the JVM searches for as the entry point?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'public static void main(String[] args)', 'is_correct': True},
                                {'id': 'b', 'text': 'public void main(String args)', 'is_correct': False},
                                {'id': 'c', 'text': 'static void Main(String[] args)', 'is_correct': False},
                                {'id': 'd', 'text': 'public static int main(String[] args)', 'is_correct': False},
                            ],
                            'explain': 'All four parts matter: case (main not Main), static, void (not int), and the String array parameter.',
                        },
                        {
                            'slug': 'println-output',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': 'main runs: System.out.print("A"); System.out.println("B"); System.out.println("C"); What appears? Write each output line exactly.',
                            'xp_reward': 40,
                            'expected_output': 'AB\nC',
                            'explain': 'print does NOT break the line, so A and B share a line; each println then ends its own line.',
                        },
                        {
                            'slug': 'double-quotes-rule',
                            'title': 'Quote discipline',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why does System.out.println(\'Hi\'); fail to compile?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Single quotes hold exactly one char, not a multi-character string', 'is_correct': True},
                                {'id': 'b', 'text': 'println needs an object, never text', 'is_correct': False},
                                {'id': 'c', 'text': 'H must be lowercase in literals', 'is_correct': False},
                                {'id': 'd', 'text': 'It is fine and compiles', 'is_correct': False},
                            ],
                            'explain': "'H' is a char; \"Hi\" is a String. The compiler sees a char where the quoted word cannot fit.",
                        },
                        {
                            'slug': 'no-free-functions',
                            'title': 'Everything lives in a class',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about the Hello program.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'main must sit inside a class — Java has no standalone functions', 'is_correct': True},
                                {'id': 'b', 'text': 'The file must be named Hello.java', 'is_correct': True},
                                {'id': 'c', 'text': 'static lets the JVM call main without a Hello object', 'is_correct': True},
                                {'id': 'd', 'text': 'Changing main to Main still runs, because Java ignores case', 'is_correct': False},
                            ],
                            'explain': 'Java is case-sensitive everywhere — Main is a different identifier the JVM will not find.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 1 Quiz',
                    'slug': 'java-intro-quiz',
                    'objective': 'Check the portability story, toolchain commands and first-program anatomy.',
                    'duration': 8,
                    'body': """# Chapter 1 Quiz

Five questions on JVM portability, JDK/JRE/JVM, javac and java, and the
anatomy of the Hello World program.""",
                    'exercises': [
                        {
                            'slug': 'q1-class-file',
                            'title': 'One public class rule',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A .java file may contain at most one class that is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'public, and it must match the filename', 'is_correct': True},
                                {'id': 'b', 'text': 'static, and it must be named Main', 'is_correct': False},
                                {'id': 'c', 'text': 'private', 'is_correct': False},
                                {'id': 'd', 'text': 'abstract only', 'is_correct': False},
                            ],
                            'explain': 'The constraint is specifically on the public class — extra package-private classes are legal but rare.',
                        },
                        {
                            'slug': 'q1-artifact-order',
                            'title': 'Pipeline order',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Order: .java → .class → output. Which tool sits between .java and .class? Write the command name (lowercase, 5 letters).',
                            'xp_reward': 40,
                            'expected_output': 'javac',
                            'explain': 'javac compiles; java runs. Five letters, c at the end = compiler.',
                        },
                        {
                            'slug': 'q1-jvm-job',
                            'title': 'JVM\u2019s actual job',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What does the JVM do with your .class file?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Executes the byte code, translating it for the host platform', 'is_correct': True},
                                {'id': 'b', 'text': 'Recompiles the source on every start', 'is_correct': False},
                                {'id': 'c', 'text': 'Converts it to a Windows .exe', 'is_correct': False},
                                {'id': 'd', 'text': 'Uploads it to the Java registry', 'is_correct': False},
                            ],
                            'explain': 'The source is gone by then — the JVM only knows byte code.',
                        },
                        {
                            'slug': 'q1-args-array',
                            'title': 'What is args for',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'main\u2019s String[] args parameter receives…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'command-line arguments after the class name', 'is_correct': True},
                                {'id': 'b', 'text': 'filenames in the folder', 'is_correct': False},
                                {'id': 'c', 'text': 'user keyboard input while running', 'is_correct': False},
                                {'id': 'd', 'text': 'compiler warnings', 'is_correct': False},
                            ],
                            'explain': 'java App hello 42 → args holds ["hello", "42"]. Keyboard input is Scanner\u2019s job (chapter 3).',
                        },
                        {
                            'slug': 'q1-true-false-toolchain',
                            'title': 'Toolchain truths',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The JDK contains the JRE plus development tools', 'is_correct': True},
                                {'id': 'b', 'text': 'Java source compiles to machine code for the current CPU', 'is_correct': False},
                                {'id': 'c', 'text': 'A .class file is portable across operating systems', 'is_correct': True},
                                {'id': 'd', 'text': 'Android historically used Java as a main app language', 'is_correct': True},
                            ],
                            'explain': 'b is the C++ model; Java stops at byte code and hands the platform step to the JVM.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 2 ════════════════════
        {
            'title': 'Variables and Data Types',
            'slug': 'java-types',
            'description': 'Declaration and assignment, the eight primitives, reference types, and conversions between them.',
            'lessons': [
                {
                    'title': 'Declaring and Using Variables',
                    'slug': 'variables',
                    'objective': 'Declare, assign, and name variables; distinguish final constants.',
                    'duration': 12,
                    'body': """# A box with a type and a name

A Java **variable** is a named box whose kind of content is fixed at
declaration:

```java
int age = 25;          // declaration + assignment in one
String city = "Karachi";
age = 26;              // re-assign: allowed
city = 42;             // COMPILE ERROR: 42 is not a String
```

Three pieces: **type** (`int`), **name** (`age`), **value** (`25`).
Unlike Python, the type belongs to the variable forever — Java is
**statically typed**. Unlike C++, `String` (capital S) is not a
primitive; it is a class, so `city` is a **reference** to an object.

## Naming law and culture
- Legal: letters, digits, `_`, `$`; cannot start with a digit; no
  keywords (`class`, `int`, `public`…).
- Convention: **camelCase** for variables/methods (`totalPrice`),
  **PascalCase** for classes (`MyApp`), **UPPER_SNAKE** for constants
  (`MAX_SIZE`).
- `int 2go` ❌ (starts with digit), `int class` ❌ (keyword),
  `int MAX` for a mutable counter ❌ (legal, but reviewers will flinch).

## final = a promise
```java
final double PI = 3.14159;
PI = 3.14;   // COMPILE ERROR: cannot assign a value to final variable
```
`final` makes reassignment illegal after the first value — Java's word
for "constant". The compiler enforces it, so it is a documentation tool
too: readers know the value never drifts.

## Uninitialised local variables
```java
int count;
count = count + 1;   // COMPILE ERROR: variable count might not have been initialized
```
Local variables must be assigned **before first use**. Fields inside
classes do get defaults (0, false, null) — the distinction trips up
everyone once.

## var (Java 10+)
`var price = 9.99;` infers `double` at compile time. The variable is
still static — `price = "cheap";` still fails. Use it when the right
hand makes the type obvious; spell types out otherwise.

## Common mistakes
- `int a, b = 5;` — assigns only b; a is uninitialised.
- Reusing a name in the same scope: `int x; int x;` → duplicate variable.
- Assigning a larger value silently: `int big = 3_000_000_000;` →
  literal out of int range; the compiler says so (use `long`).

## Lesson summary
Type + name + value, type never changes, final freezes the value, locals
must be initialised before use — and naming conventions are how Java
code reads as Java.""",
                    'exercises': [
                        {
                            'slug': 'static-typing-reassign',
                            'title': 'What reassignment is legal',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Given `String name = "Ali";`, which line compiles?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'name = "Sara";', 'is_correct': True},
                                {'id': 'b', 'text': 'name = 7;', 'is_correct': False},
                                {'id': 'c', 'text': 'int name = 7;', 'is_correct': False},
                                {'id': 'd', 'text': 'String name = true;', 'is_correct': False},
                            ],
                            'explain': 'The type is fixed, the value may change: another String is fine — redeclaring or switching kind is not.',
                        },
                        {
                            'slug': 'final-error',
                            'title': 'final consequence',
                            'exercise_type': 'output_prediction',
                            'instructions': '`final int ID = 1; ID = 2; System.out.println(ID);` — what happens? Answer one word: runs or errors',
                            'xp_reward': 40,
                            'expected_output': 'errors',
                            'explain': 'Reassigning a final variable is a compile error — the program never even runs to print.',
                        },
                        {
                            'slug': 'var-still-static',
                            'title': 'var semantics',
                            'exercise_type': 'multiple_choice',
                            'instructions': '`var x = 5;` — what is x\u2019s type?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'int, fixed at compile time from the value 5', 'is_correct': True},
                                {'id': 'b', 'text': 'anything — var makes it dynamic like JavaScript', 'is_correct': False},
                                {'id': 'c', 'text': 'double always', 'is_correct': False},
                                {'id': 'd', 'text': 'Object', 'is_correct': False},
                            ],
                            'explain': 'var is type INFERENCE, not dynamic typing — x = "five" still fails to compile.',
                        },
                        {
                            'slug': 'naming-choices',
                            'title': 'Legal and conventional',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL variable declarations that are BOTH legal and follow Java naming convention.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'int totalPrice = 0;', 'is_correct': True},
                                {'id': 'b', 'text': 'double MAX_SIZE = 9.9;', 'is_correct': True},
                                {'id': 'c', 'text': 'int Total_Price = 0;', 'is_correct': False},
                                {'id': 'd', 'text': 'int 2ndPlace = 0;', 'is_correct': False},
                            ],
                            'explain': 'c is legal but snake/Pascal mix is not the camelCase convention; d is outright illegal (leading digit).',
                        },
                    ],
                },
                {
                    'title': 'The Eight Primitive Types',
                    'slug': 'primitive-types',
                    'objective': 'Pick the right primitive for whole numbers, decimals and truth values.',
                    'duration': 15,
                    'body': """# Small, fixed-size, not objects

Primitives store raw values directly — fast and compact. Java's eight:

| Type | Size | Range / values | Typical use |
|---|---|---|---|
| `byte` | 1 | −128…127 | raw data, file formats |
| `short` | 2 | −32,768…32,767 | rare; legacy protocols |
| `int` | 4 | about ±2.1 billion | counters, indexes — default |
| `long` | 8 | about ±9.2 × 10¹⁸ | ids, timestamps, money-in-cents |
| `float` | 4 | ~7 decimal digits | graphics; rarely elsewhere |
| `double` | 8 | ~15–16 digits | default decimal choice |
| `char` | 2 | one UTF-16 code unit, `'A'` | single characters |
| `boolean` | — | `true` / `false` | conditions only — never int-trickery |

Literals that matter:

```java
long population = 9_000_000_000L;   // L suffix — 9 billions overflows int
double tax = 0.085;
float ratio = 1.5f;                 // f suffix — decimal literal defaults to double
int big = 2_000_000;                // underscores allowed, cosmetic only
char heart = '\u2665';              // Unicode escape works
```

## Overflow: the silent wrap
```java
int max = Integer.MAX_VALUE;   // 2147483647
max = max + 1;                 // -2147483648 — no exception, just wrapped
```
Whole numbers that exceed the range **roll over** without warning.
`long` is the fix when numbers can grow; detecting overflow is the
interview follow-up.

## Money warning
`double` is binary floating point: `0.1 + 0.2` prints `0.30000000000000004`.
Fine for measurements; for currency use `long` cents or `java.math.BigDecimal`.

## Primitives vs their wrapper classes
Every primitive has a boxed twin: `int`↔`Integer`, `double`↔`Double`,
`boolean`↔`Boolean`… You meet them whenever collections demand objects
(chapter 8) or code says `Integer.valueOf`. **Autoboxing** converts
automatically — and `null` unboxed to `int` throws a NullPointerException,
a bug that costs careers.

## Default values
Fields default to 0 / false / null; **locals have no default** — the
compiler's "might not have been initialized" is protecting you.

## Common mistakes
- `int n = 3000000000;` — literal exceeds int; append L or use long.
- `float f = 3.14;` — the literal is double; needs `3.14f`.
- char holding a "string": `char c = "A";` — double quotes, compile error.
- Using int as true/false (`if (score)`); Java conditions must be boolean.

## Lesson summary
int and double are defaults; long for big counts, char for one character,
boolean strictly for truth; suffixes L/f matter; primitives never round
money safely.""",
                    'exercises': [
                        {
                            'slug': 'choose-the-type',
                            'title': 'Right primitive for the job',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which type stores a country\u2019s population (about 240 million) most appropriately?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'int — it fits comfortably below 2.1 billion', 'is_correct': True},
                                {'id': 'b', 'text': 'byte — populations are small', 'is_correct': False},
                                {'id': 'c', 'text': 'char — it is text', 'is_correct': False},
                                {'id': 'd', 'text': 'boolean — it is a fact', 'is_correct': False},
                            ],
                            'explain': '240M < 2^31−1 ≈ 2.14B, so int is the conventional pick; long becomes necessary past ~2.1B.',
                        },
                        {
                            'slug': 'int-overflow-result',
                            'title': 'Wrap prediction',
                            'exercise_type': 'output_prediction',
                            'instructions': 'int x = Integer.MAX_VALUE; x = x + 1; System.out.println(x); — what prints? (No L suffix involved.)',
                            'xp_reward': 50,
                            'expected_output': '-2147483648',
                            'explain': 'Signed int wraps to its minimum — silently. Overflow checks need Math.addExact or a wider type.',
                        },
                        {
                            'slug': 'float-suffix',
                            'title': 'Why 1.5f',
                            'exercise_type': 'fill_blank',
                            'instructions': 'float ratio = 1.5____; — which single lowercase suffix character makes this literal legal? (the float suffix)',
                            'xp_reward': 40,
                            'solution_code': 'f',
                            'explain': 'Decimal literals default to double; the f (or F) suffix marks it a float.',
                        },
                        {
                            'slug': 'double-vs-money',
                            'title': 'Currency call',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Storing bank account amounts in double risks what?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Rounding error: binary floating point cannot represent 0.1 exactly', 'is_correct': True},
                                {'id': 'b', 'text': 'Nothing — double is precise to 15 digits so money is safe', 'is_correct': False},
                                {'id': 'c', 'text': 'Overflow at $2.1 billion only', 'is_correct': False},
                                {'id': 'd', 'text': 'double cannot hold decimals', 'is_correct': False},
                            ],
                            'explain': 'The famous 0.1 + 0.2 != 0.3: exactness, not just precision — use cents-in-long or BigDecimal.',
                        },
                    ],
                },
                {
                    'title': 'Type Conversion and Reading Input',
                    'slug': 'type-conversion',
                    'objective': 'Widen, cast, parse strings to numbers, and read a line with Scanner.',
                    'duration': 15,
                    'body': """# Moving values between types

## Widening: free and automatic
Smaller → bigger type, Java inserts nothing but safety:

```java
int tickets = 500;
long sold = tickets;        // int to long: automatic, no data loss
double price = sold;        // long to double: automatic (precision may blur for huge values)
```

## Narrowing: you must cast, and you may lose data
```java
double rating = 4.9;
int stars = (int) rating;   // 4 — the .9 is TRUNCATED, not rounded
int big = 70000;
short small = (short) big;  // wraps silently: 70000-65536 = 4464
```

The cast `(int)` says "I accept the risk". Truncation always rounds
**toward zero**; wrapping follows the target type's range.

## Arithmetic decides the result type
```java
int a = 7, b = 2;
System.out.println(a / b);          // 3   integer division!
System.out.println(a / (double) b); // 3.5 cast one side first
System.out.println(7 / 2 * 2);      // 6   (3 * 2), not 7
```

The integer-division trap: `7 / 2` is 3 because both operands are ints.
Cast **before** the operation — casting the result of `a / b` back to
double gives you 3.0, not 3.5.

## Parsing text (the other direction)
Numbers typed by users and stored in files arrive as **Strings**:

```java
int age = Integer.parseInt("25");        // String -> int
 double d = Double.parseDouble("3.14"); // String -> double
String s = String.valueOf(42);           // anything -> String
int bad = Integer.parseInt("25.5");      // NumberFormatException at RUNTIME
```

`parseInt` throws when the text is not a clean integer — validating or
try/catch-ing (chapter 7) is part of every real input path.

## Reading from the keyboard: Scanner
```java
import java.util.Scanner;

Scanner in = new Scanner(System.in);
System.out.print("Name? ");
String name = in.nextLine();     // reads a whole line
System.out.print("Age? ");
int age = in.nextInt();          // reads one int
System.out.println(name + " is " + age);
```

Watch the mixing trap: after `nextInt()`, the leftover newline stays
unread, so a following `nextLine()` returns "" — the classic "my
program skipped the input" bug. Fix: consume the newline once
(`in.nextLine();`) before the line read.

## Common mistakes
- `int x = 10.5;` without a cast → "possible loss of precision".
- Expecting `a / b` to be fractional because the **variable names**
  suggest measurements — Java checks types, not intent.
- Calling `nextLine()` right after `nextInt()` and blaming Scanner for
  the empty read.

## Lesson summary
Widening is free, narrowing needs a cast (truncation/wrapping risk),
integer division happens unless one operand is a double, and every input
boundary is really parseText + Scanner with their two famous traps.""",
                    'exercises': [
                        {
                            'slug': 'int-division-predict',
                            'title': 'Integer division',
                            'exercise_type': 'output_prediction',
                            'instructions': 'System.out.println(9 / 2); — what prints? (single token)',
                            'xp_reward': 40,
                            'expected_output': '4',
                            'explain': 'Both int: truncate toward zero — 4, not 4.5. Cast one side to double for the real quotient.',
                        },
                        {
                            'slug': 'cast-order',
                            'title': 'Cast placement',
                            'exercise_type': 'output_prediction',
                            'instructions': 'int a = 7, b = 2; System.out.println((double)(a / b)); — what prints exactly?',
                            'xp_reward': 50,
                            'expected_output': '3.0',
                            'explain': 'a / b happens FIRST (int 3), then the cast widens it to 3.0 — Java prints the .0 for doubles. Cast inside: (double) a / b gives 3.5.',
                        },
                        {
                            'slug': 'truncation-value',
                            'title': 'Truncate, do not round',
                            'exercise_type': 'fill_blank',
                            'instructions': 'int n = (int) 9.99; System.out.println(n); — what is the value? (integer, no decimal point)',
                            'xp_reward': 40,
                            'solution_code': '9',
                            'explain': 'Casting to int drops everything after the decimal point — even .99.',
                        },
                        {
                            'slug': 'parseexception-when',
                            'title': 'When parsing fails',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Integer.parseInt("12.5") …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'throws NumberFormatException at runtime', 'is_correct': True},
                                {'id': 'b', 'text': 'returns 12 silently', 'is_correct': False},
                                {'id': 'c', 'text': 'is a compile error', 'is_correct': False},
                                {'id': 'd', 'text': 'returns 12.5 as an int', 'is_correct': False},
                            ],
                            'explain': 'The compiler only sees a String — the failure surfaces at runtime, which is why input paths validate.',
                        },
                        {
                            'slug': 'scanner-nextline-trap',
                            'title': 'The skipped input',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why does nextLine() often return an empty string right after nextInt()?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'nextInt leaves the trailing newline, which nextLine then consumes as the whole line', 'is_correct': True},
                                {'id': 'b', 'text': 'nextInt closes the scanner', 'is_correct': False},
                                {'id': 'c', 'text': 'nextLine cannot follow nextInt ever', 'is_correct': False},
                                {'id': 'd', 'text': 'The keyboard buffer is full', 'is_correct': False},
                            ],
                            'explain': 'Token readers stop AT the newline; line readers eat it. One extra in.nextLine() clears it.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 2 Quiz',
                    'slug': 'java-types-quiz',
                    'objective': 'Check variables, primitives and conversions recall.',
                    'duration': 8,
                    'body': """# Chapter 2 Quiz

Six questions on declaration rules, the primitive table, overflow,
conversions and Scanner basics.""",
                    'exercises': [
                        {
                            'slug': 'q2-default-int',
                            'title': 'Which is the default whole type',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Name the primitive that whole-number literals like 42 default to. (lowercase type name)',
                            'xp_reward': 40,
                            'solution_code': 'int',
                            'explain': 'int — which is exactly why long values need the L suffix beyond ±2.1 billion.',
                        },
                        {
                            'slug': 'q2-boolean-not-int',
                            'title': 'Java boolean discipline',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In Java, `if (1)` …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'does not compile — conditions must be boolean', 'is_correct': True},
                                {'id': 'b', 'text': 'is true, like C++', 'is_correct': False},
                                {'id': 'c', 'text': 'is false', 'is_correct': False},
                                {'id': 'd', 'text': 'throws at runtime', 'is_correct': False},
                            ],
                            'explain': 'C/C++ truthiness does not cross over: Java wants true/false, and the compiler enforces it.',
                        },
                        {
                            'slug': 'q2-char-size',
                            'title': 'Why char is 2 bytes',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Java char is 2 bytes (not 1 like C++) because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'it stores a UTF-16 code unit, covering far more than ASCII', 'is_correct': True},
                                {'id': 'b', 'text': 'alignment wastes a byte', 'is_correct': False},
                                {'id': 'c', 'text': 'it can also hold small ints', 'is_correct': False},
                                {'id': 'd', 'text': 'historical accident with no consequence', 'is_correct': False},
                            ],
                            'explain': 'Unicode-first design: most world scripts need more than 256 values.',
                        },
                        {
                            'slug': 'q2-long-suffix',
                            'title': 'Big literal fix',
                            'exercise_type': 'fill_blank',
                            'instructions': 'long mask = 8_000_000_000____; — which single suffix character (uppercase, as written in the lesson) makes the literal fit a long?',
                            'xp_reward': 40,
                            'solution_code': 'L',
                            'explain': 'L suffix: the literal is long from birth. Without it the int literal overflows and compilation fails.',
                        },
                        {
                            'slug': 'q2-uninitialised',
                            'title': 'Uninitialised local',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inside a method: `int x; System.out.println(x);` — outcome?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Compile error: variable x might not have been initialized', 'is_correct': True},
                                {'id': 'b', 'text': 'Prints 0 (fields default)', 'is_correct': False},
                                {'id': 'c', 'text': 'Prints null', 'is_correct': False},
                                {'id': 'd', 'text': 'Prints garbage memory', 'is_correct': False},
                            ],
                            'explain': 'Locals get NO defaults — that is deliberate: garbage values are a C++ habit Java blocks.',
                        },
                        {
                            'slug': 'q2-widening-safe',
                            'title': 'Safe assignment',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL assignments legal WITHOUT a cast.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'long x = 100;', 'is_correct': True},
                                {'id': 'b', 'text': 'double d = 5f;', 'is_correct': True},
                                {'id': 'c', 'text': 'int n = 5.0;', 'is_correct': False},
                                {'id': 'd', 'text': 'int m = 2147483647L;', 'is_correct': False},
                            ],
                            'explain': 'Narrowing (double→int, long→int) always needs a cast, even when the VALUE would fit (d).',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 3 ════════════════════
        {
            'title': 'Operators and Control Flow',
            'slug': 'java-control-flow',
            'description': 'Arithmetic and logic operators, decisions with if/switch, and the three loop forms.',
            'lessons': [
                {
                    'title': 'Operators You Must Own',
                    'slug': 'operators',
                    'objective': 'Use arithmetic, comparison, logical and bitwise operators with correct precedence.',
                    'duration': 15,
                    'body': r"""# The vocabulary inside expressions

## Arithmetic
```java
int a = 10, b = 3;
a + b;  // 13
a - b;  // 7
a * b;  // 30
a / b;  // 3   integer division again
a % b;  // 1   remainder
```

`%` (modulo) is more than trivia: `n % 2` tests even/odd, `n % 60`
converts seconds to minutes, `i % array.length` wraps around a circular
buffer — the same trick the DSA course's circular queue used.

`++` and `--`: **prefix changes before use, postfix after**:

```java
int i = 5;
System.out.println(i++);   // prints 5, THEN i becomes 6
System.out.println(++i);   // i becomes 7 first, prints 7
```

## Comparison and logic — boolean territory
`== != < > <= >=` produce booleans. Then:

| Operator | Name | Truth |
|---|---|---|
| `&&` | AND | both sides true |
| `\|\|` | OR | at least one true |
| `!` | NOT | flips |

The critical behaviour is **short-circuiting**: in `x != 0 && 10 / x > 1`,
if `x` IS 0 the left side fails and the right side **never runs** — no
division by zero. `&&` guards the second expression; `||` does the same
for "already true, stop asking". The non-short-circuit versions `&` and
`|` evaluate both sides and are for bitwise use, not conditions.

## Precedence ladder (top → bottom)
`!` → arithmetic (`* / %` before `+ -`) → comparisons (`< <= > >=`)
equality (`== !=`) → `&&` → `||` → assignment. Memorise one rule
instead of the whole ladder: **bracket anything you are not 100% sure
of** — reviewers do too.

## Compound and ternary
```java
total += price;           // total = total + price (also -= *= /= %)
String label = age >= 18 ? "adult" : "minor";   // ternary = one-line if
```

The ternary is an **expression** — it produces a value — so it slots
into assignments and prints where a full if/else block cannot.

## Common mistakes
- `=` vs `==` inside conditions — Java's compile error actually helps
  here (condition must be boolean; assignment of an int fails).
- Expecting `x != null && x.length() > 0` to crash when x is null —
  short-circuit means the guard works; that pattern is the point.
- `a % b` with negative a: Java's remainder keeps the dividend's sign
  (`-7 % 3 == -1`), unlike mathematical modulo.

## Lesson summary
Arithmetic + `%` for cycles and parity, prefix/postfix discipline,
short-circuit `&&`/`||` as guarding patterns, and brackets when in doubt.""",
                    'exercises': [
                        {
                            'slug': 'modulo-chain',
                            'title': 'Modulo in sequence',
                            'exercise_type': 'output_prediction',
                            'instructions': 'System.out.println(10 % 3 + 10 / 3); — what prints?',
                            'xp_reward': 40,
                            'expected_output': '4',
                            'explain': '10%3 = 1 and 10/3 = 3; both same precedence, left to right: 1 + 3 = 4.',
                        },
                        {
                            'slug': 'postfix-predict',
                            'title': 'Postfix moment',
                            'exercise_type': 'output_prediction',
                            'instructions': 'int n = 4; System.out.println(n++ + n); — what prints? (remember: println of the sum; then n is 5 but unused)',
                            'xp_reward': 50,
                            'expected_output': '9',
                            'explain': 'n++ contributes 4, THEN n becomes 5, and the second n reads 5: 4 + 5 = 9. The sequencing happens inside the expression.',
                        },
                        {
                            'slug': 'short-circuit-guard',
                            'title': 'Why && saves the crash',
                            'exercise_type': 'multiple_choice',
                            'instructions': 's is null. What does `s != null && s.length() > 0` evaluate to?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'false — left side fails, right side never runs', 'is_correct': True},
                                {'id': 'b', 'text': 'NullPointerException from length()', 'is_correct': False},
                                {'id': 'c', 'text': 'true — null passes a length test', 'is_correct': False},
                                {'id': 'd', 'text': 'compile error', 'is_correct': False},
                            ],
                            'explain': '&& short-circuits on false: the second operand is skipped. This exact guard is idiomatic Java.',
                        },
                        {
                            'slug': 'ternary-usage',
                            'title': 'Ternary nature',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The expression `cond ? x : y` …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'evaluates to x when cond is true, else y — it produces a value', 'is_correct': True},
                                {'id': 'b', 'text': 'is a statement like if/else and cannot assign', 'is_correct': False},
                                {'id': 'c', 'text': 'evaluates BOTH branches always', 'is_correct': False},
                                {'id': 'd', 'text': 'only works with ints', 'is_correct': False},
                            ],
                            'explain': 'Ternary is an expression with one value out; only the taken branch runs, any types fit the context.',
                        },
                    ],
                },
                {
                    'title': 'Decisions: if / else and switch',
                    'slug': 'conditionals',
                    'objective': 'Chain conditions and use switch correctly — including the fallthrough trap.',
                    'duration': 12,
                    'body': """# Branching on truth

```java
int score = 72;

if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else if (score >= 70) {
    System.out.println("C");   // <-- this one runs
} else {
    System.out.println("F");
}
```

`else if` chains are **top-down first-match**: once a branch runs, the
rest is skipped — order them most-specific first or a broad condition
steals the match (the DSA course's linear search, but for rules).

## switch: value dispatch
```java
int day = 3;
String name;
switch (day) {
    case 1: name = "Monday";    break;
    case 2: name = "Tuesday";   break;
    case 3: name = "Wednesday"; break;
    default: name = "weekday?";
}
System.out.println(name);   // Wednesday
```

Rules that matter:
- `break` ends a case. Without it, execution **falls through** into the
  next case — sometimes deliberate (stacking cases that share code:
  `case 1: case 2: case 3: …`), a silent bug otherwise.
- `default` runs when nothing matched (convention: last).
- Classic switch works on `int/char/String/enum` — not on ranges or
  arbitrary objects.
- **Modern switch expressions** (Java 14+) replace fallthrough with
  arrows and yield values:

```java
String name = switch (day) {
    case 1 -> "Monday";
    case 2 -> "Tuesday";
    case 3 -> "Wednesday";
    default -> "???";
};
```

No break needed, value assigned directly — the form you will see in
recent codebases and should at least recognise.

## Choosing
- Boolean logic, ranges (`score >= 90`) → if/else.
- Many exact values of one variable → switch (cleaner and JIT-friendly).
- Two branches of the same type → maybe ternary, if one line stays readable.

## Common mistakes
- Missing `break` and hunting the "impossible output" for an hour.
- Forgetting `default` and letting unmatched values slide silently.
- Comparing booleans with `== flag` instead of `flag` / `!flag` —
  legal but noise; reviewers mark it.
- Floating-point equality (`if (x == 0.1)`) — use a tolerance or BigDecimal.

## Lesson summary
if/else if for first-match rule cascades, switch for exact-value
routing, arrows for modern switch expressions — and break is load-bearing.""",
                    'exercises': [
                        {
                            'slug': 'else-if-order',
                            'title': 'First match wins',
                            'exercise_type': 'output_prediction',
                            'instructions': 'score = 95; chain above: if(>=90) "A" else if(>=80) "B" else if(>=70) "C" else "F". What prints? (one letter)',
                            'xp_reward': 40,
                            'expected_output': 'A',
                            'explain': 'Top-down: 95 >= 90 hits A and the chain stops — B and C conditions are never even asked.',
                        },
                        {
                            'slug': 'fallthrough-predict',
                            'title': 'Missing break consequence',
                            'exercise_type': 'output_prediction',
                            'instructions': 'x = 1; switch(x){ case 1: System.out.print("one "); case 2: System.out.print("two "); case 3: System.out.print("three "); break; } — exact output?',
                            'xp_reward': 50,
                            'expected_output': 'one two three ',
                            'explain': 'Fallthrough: after case 1 matches, execution RUNS ON through cases 2 and 3 until the break — trailing space included.',
                        },
                        {
                            'slug': 'switch-values',
                            'title': 'What switch accepts',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL types a classic switch CAN select on.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'int', 'is_correct': True},
                                {'id': 'b', 'text': 'String', 'is_correct': True},
                                {'id': 'c', 'text': 'char', 'is_correct': True},
                                {'id': 'd', 'text': 'double', 'is_correct': False},
                            ],
                            'explain': 'Floating point is excluded — exact equality on doubles is precisely the trap switch refuses to encourage.',
                        },
                        {
                            'slug': 'switch-expression-form',
                            'title': 'Arrow switch benefit',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The modern `case 3 -> "Wednesday";` switch expression form…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'produces a value and needs no break per case', 'is_correct': True},
                                {'id': 'b', 'text': 'runs faster at the CPU level', 'is_correct': False},
                                {'id': 'c', 'text': 'allows float cases', 'is_correct': False},
                                {'id': 'd', 'text': 'replaces if/else entirely', 'is_correct': False},
                            ],
                            'explain': 'It is about safety and expressiveness: no fallthrough, and the whole switch IS an expression.',
                        },
                    ],
                },
                {
                    'title': 'Loops: for, while, do-while',
                    'slug': 'loops',
                    'objective': 'Pick the right loop, control it with break/continue, and trace outputs.',
                    'duration': 15,
                    'body': """# Repetition with three tools

```java
for (int i = 0; i < 5; i++) {        // known count / sequence
    System.out.print(i);             // 01234
}

while (tries < 3) {                  // condition-driven, may run zero times
    tries++;
}

do {                                  // MUST run at least once
    guess = readGuess();
} while (guess != secret);
```

Selection guide: counting a fixed range → `for`; "repeat while/since
unknown, possibly never" → `while`; "ask first, then decide" (menus,
input prompts) → `do-while`.

## The for-header anatomy
`for (init; condition; update)` — init runs once; condition checked
BEFORE each iteration; update after each body. `i < 5` with `i++` from 0
→ body runs for 0,1,2,3,4 — five times, last index 4. Off-by-one errors
live entirely in that comparison line: `< length` visits all, `<= length`
crashes on the last step (index == length).

## break and continue
```java
for (int i = 0; i < items.length; i++) {
    if (items[i] == null) continue;   // skip THIS item, next iteration
    if (items[i] == target) break;    // abandon the whole loop
}
```

`break` exits; `continue` jumps to the next iteration's condition check.
(DSA course cameo: that loop is a linear search with input hygiene.)

## Nested loops
Outer × inner = total iterations: two loops of n → n² work — exactly the
double-loop pattern whose cost the complexity chapter derived. Printing
a 4×4 grid: `for row { for col { print cell } println() }` — the outer
loop advances lines, the inner columns.

## for-each (enhanced for)
```java
int[] nums = {4, 8, 15};
for (int n : nums) { total += n; }    // clean sweep, no index, no bounds bug
```

Use it when you only READ elements; use a classic for when you need the
index, want to modify the array, or must skip/stop by position.

## Common mistakes
- `while (true)` with no break path = hang (the infinite-loop lab is
  chapter-2 era fun, but production incidents too).
- Modifying the loop variable inside the body — the update clause still
  runs, doubling your step and confusing reviewers.
- do-while needing a semicolon after the condition (unlike while/for).
- Off-by-one: iterating `i <= arr.length` → ArrayIndexOutOfBounds.

## Lesson summary
for counts, while waits, do-while promises one run; break leaves,
continue skips; nesting multiplies cost; for-each removes index bugs.""",
                    'exercises': [
                        {
                            'slug': 'for-loop-output',
                            'title': 'Trace a for',
                            'exercise_type': 'output_prediction',
                            'instructions': 'for (int i = 1; i <= 4; i++) System.out.print(i * i); — exact output?',
                            'xp_reward': 40,
                            'expected_output': '14916',
                            'explain': 'Squares 1,4,9,16 printed with no separator: 14916. Tracing the bounds (1..4 inclusive) is the whole skill.',
                        },
                        {
                            'slug': 'while-zero-times',
                            'title': 'Zero-iteration question',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'int k = 10; while (k < 5) { System.out.print(k); k--; } — how many times does the body run?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '0 — the condition fails before the first pass', 'is_correct': True},
                                {'id': 'b', 'text': '1', 'is_correct': False},
                                {'id': 'c', 'text': '5', 'is_correct': False},
                                {'id': 'd', 'text': 'forever', 'is_correct': False},
                            ],
                            'explain': 'while checks FIRST: 10 < 5 is false, body never runs. do-while is the form that guarantees one run.',
                        },
                        {
                            'slug': 'do-while-guarantee',
                            'title': 'do-while identity',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which is the only one of the three loops guaranteed to execute its body at least once?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'do-while', 'is_correct': True},
                                {'id': 'b', 'text': 'while', 'is_correct': False},
                                {'id': 'c', 'text': 'for', 'is_correct': False},
                                {'id': 'd', 'text': 'for-each', 'is_correct': False},
                            ],
                            'explain': 'Its condition is tested after the body — the menu/input-prompt loop exists because of that one line of syntax order.',
                        },
                        {
                            'slug': 'continue-counts',
                            'title': 'continue arithmetic',
                            'exercise_type': 'output_prediction',
                            'instructions': 'int c = 0; for (int i = 0; i < 6; i++) { if (i % 2 == 0) continue; c++; } System.out.println(c); — what prints?',
                            'xp_reward': 50,
                            'expected_output': '3',
                            'explain': 'Even i (0,2,4) skip the increment; odd 1,3,5 count it: 3. continue goes to the update clause, it does NOT exit the loop.',
                        },
                        {
                            'slug': 'foreach-when',
                            'title': 'for-each limits',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL tasks where a plain for-each loop is the RIGHT tool.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Sum every value in an int array', 'is_correct': True},
                                {'id': 'b', 'text': 'Print every name in a String array', 'is_correct': True},
                                {'id': 'c', 'text': 'Double every element (write back by position)', 'is_correct': False},
                                {'id': 'd', 'text': 'Compare each element with the NEXT one', 'is_correct': False},
                            ],
                            'explain': 'Write-back and neighbour comparison need the index (and for-each’s variable is a copy) — that is classic-for territory.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 3 Quiz',
                    'slug': 'java-control-flow-quiz',
                    'objective': 'Check operators, branching and loop mechanics.',
                    'duration': 8,
                    'body': """# Chapter 3 Quiz

Six questions on modulo and short-circuit logic, if/switch behavior and
loop bounds.""",
                    'exercises': [
                        {
                            'slug': 'q3-modulo-negative',
                            'title': 'Sign of the remainder',
                            'exercise_type': 'output_prediction',
                            'instructions': 'System.out.println(-7 % 3); — what prints in Java?',
                            'xp_reward': 50,
                            'expected_output': '-1',
                            'explain': 'Java keeps the dividend\u2019s sign: -7 % 3 = -1 (mathematical modulo would say 2).',
                        },
                        {
                            'slug': 'q3-guard-or-null',
                            'title': '|| guard order',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'To safely print "empty" for a possibly-null String s, which is correct?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'if (s == null || s.isEmpty())', 'is_correct': True},
                                {'id': 'b', 'text': 'if (s.isEmpty() || s == null)', 'is_correct': False},
                                {'id': 'c', 'text': 'if (s != null || s.isEmpty())', 'is_correct': False},
                                {'id': 'd', 'text': 'if (s == null && s.isEmpty())', 'is_correct': False},
                            ],
                            'explain': 'The null test must come FIRST — short-circuit on true skips isEmpty() for null. b NPEs; d can never both.',
                        },
                        {
                            'slug': 'q3-switch-default',
                            'title': 'default role',
                            'exercise_type': 'fill_blank',
                            'instructions': 'The switch case that runs when no other case matches is labelled ______ (one lowercase keyword).',
                            'xp_reward': 40,
                            'solution_code': 'default',
                            'explain': 'default — its absence means unmatched values do nothing at all.',
                        },
                        {
                            'slug': 'q3-loop-times',
                            'title': 'Iteration count',
                            'exercise_type': 'output_prediction',
                            'instructions': 'for (int i = 2; i < 10; i += 3) System.out.print(i); — how many characters print? (number only)',
                            'xp_reward': 40,
                            'expected_output': '3',
                            'explain': 'i = 2, 5, 8 (next 12 >= 10 stops): three iterations, output \u201c258\u201d.',
                        },
                        {
                            'slug': 'q3-break-vs-continue',
                            'title': 'break or continue',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct statements.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'break exits the loop entirely', 'is_correct': True},
                                {'id': 'b', 'text': 'continue starts the next iteration', 'is_correct': True},
                                {'id': 'c', 'text': 'continue exits the loop entirely', 'is_correct': False},
                                {'id': 'd', 'text': 'break can also exit switch cases', 'is_correct': True},
                            ],
                            'explain': 'break\u2019s second home is switch fallthrough prevention \u2014 same verb, different cage.',
                        },
                        {
                            'slug': 'q3-nested-cost',
                            'title': 'Nesting cost',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Two nested loops each running 1..n do how many total body executions?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'n² — order n squared', 'is_correct': True},
                                {'id': 'b', 'text': '2n', 'is_correct': False},
                                {'id': 'c', 'text': 'n', 'is_correct': False},
                                {'id': 'd', 'text': '2^n', 'is_correct': False},
                            ],
                            'explain': 'Outer n times × inner n times = n² — the exact multiplication the Big-O chapter drilled.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 4 ════════════════════
        {
            'title': 'Arrays and Strings',
            'slug': 'java-arrays-strings',
            'description': 'Fixed-length arrays and 2D grids; the String API, immutability, equality and StringBuilder.',
            'lessons': [
                {
                    'title': 'Arrays: Fixed-Length Containers',
                    'slug': 'arrays',
                    'objective': 'Create, traverse, sort arrays and stay inside their bounds.',
                    'duration': 15,
                    'body': """# One type, fixed count, zero-based

```java
int[] nums = new int[5];              // five slots: 0 0 0 0 0
int[] primes = {2, 3, 5, 7};          // literal — length inferred: 4
String[] cities = new String[3];      // refs default to null

nums[0] = 42;                          // index: 0 .. length-1
System.out.println(primes.length);     // 4 — a FIELD, no parentheses
```

Key facts to internalise:
- **length never changes.** Growable collections arrive in chapter 8;
  an array is the fixed skeleton they are built from.
- Defaults: numbers 0, `boolean` false, references `null` — fields,
  unlike locals, always start initialised.
- `nums.length` is a property (no `()`); `s.length()` on Strings IS a
  method. That mismatch is a beloved exam trap.

## Traversal and the bounds wall
```java
for (int i = 0; i < primes.length; i++) {   // < length: last i == 3
    System.out.print(primes[i]);
}
for (int p : primes) { System.out.print(p); }  // same output, no index
```

Going one step too far — `primes[4]` — throws
`ArrayIndexOutOfBoundsException: index 4 out of bounds for length 4`
at runtime, right at the access. The message tells you the illegal
index; `-i` style errors (negative) mean a decrement past zero.

## Handy helpers
```java
import java.util.Arrays;

int[] data = {5, 1, 9, 3};
Arrays.sort(data);                     // 1 3 5 9 — in place, O(n log n)
Arrays.fill(data, 0);                  // wipe to zeros
int idx = Arrays.binarySearch(data, 0);// -1: absent (array must be sorted!)
String txt = Arrays.toString(data);    // "[0, 0, 0, 0]"
```

Binary search only makes sense on sorted data — the precondition from
the searching chapter, now with a helper that returns a NEGATIVE
insertion point instead of a boolean when the value is absent.

## Arrays are objects (shallow!)
Assignment copies the **reference**, not the contents:

```java
int[] a = {1, 2, 3};
int[] b = a;        // b and a are the SAME array
b[0] = 99;          // a[0] is now 99 too
int[] c = a.clone();  // a real copy
```

Passing an array into a method lets the method mutate the original —
the aliasing behavior (and bug class) interviewers probe.

## 2D arrays: arrays of arrays
```java
int[][] grid = new int[3][4];      // 3 rows, each an int[4]
grid[1][2] = 7;                     // row 1, column 2
for (int r = 0; r < grid.length; r++)
    for (int col = 0; col < grid[r].length; col++)
        System.out.print(grid[r][col] + " ");
```

Rows can have different lengths (jagged arrays) — `grid[r].length` per
row, not one global column count.

## Common mistakes
- `<= arr.length` loops (the off-by-one classic).
- Expecting `b = a` to copy contents.
- Sorting then mutating unsorted-style, or binarySearch on unsorted
  data and blaming the library.
- Mixing `.length` (arrays) with `.length()` (Strings).

## Lesson summary
Fixed length, zero-based, defaults by kind, reference semantics on
assignment, Arrays.* for the utilities, and nested loops for grids.""",
                    'exercises': [
                        {
                            'slug': 'array-default-value',
                            'title': 'Fresh slots',
                            'exercise_type': 'output_prediction',
                            'instructions': 'int[] a = new int[3]; System.out.println(a[2]); — what prints?',
                            'xp_reward': 40,
                            'expected_output': '0',
                            'explain': 'Array elements are fields: int defaults to 0 (refs would be null).',
                        },
                        {
                            'slug': 'array-aliasing',
                            'title': 'Who changed the copy',
                            'exercise_type': 'output_prediction',
                            'instructions': 'int[] x = {1,2}; int[] y = x; y[0] = 9; System.out.println(x[0]); — what prints?',
                            'xp_reward': 50,
                            'expected_output': '9',
                            'explain': 'y received the reference: one array, two names. clone() would have made a true copy.',
                        },
                        {
                            'slug': 'bounds-exception',
                            'title': 'The wall',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'int[] t = new int[4]; System.out.println(t[4]); — outcome?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'ArrayIndexOutOfBoundsException at runtime', 'is_correct': True},
                                {'id': 'b', 'text': '0 — defaults everywhere', 'is_correct': False},
                                {'id': 'c', 'text': 'Compile error', 'is_correct': False},
                                {'id': 'd', 'text': 'Grows the array first', 'is_correct': False},
                            ],
                            'explain': 'Valid indexes 0..3; the JVM checks on access. The compiler cannot see all runtime indexes, hence runtime defence.',
                        },
                        {
                            'slug': 'binary-search-precondition',
                            'title': 'Sort first',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Arrays.binarySearch on an UNSORTED array …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'may return a wrong index or negative even when the value exists', 'is_correct': True},
                                {'id': 'b', 'text': 'throws IllegalStateException', 'is_correct': False},
                                {'id': 'c', 'text': 'sorts automatically', 'is_correct': False},
                                {'id': 'd', 'text': 'always works, just slower', 'is_correct': False},
                            ],
                            'explain': 'The algorithm’s correctness PROOF needs sortedness; garbage-in gives wrong-but-silent answers.',
                        },
                    ],
                },
                {
                    'title': 'Strings: Immutable and Method-Rich',
                    'slug': 'strings-api',
                    'objective': 'Use core String methods, understand immutability and equals vs ==.',
                    'duration': 15,
                    'body': """# Strings are objects with a strict no-mutation policy

```java
String city = "Karachi";
city.length();            // 7 — method (compare array .length field)
city.charAt(0);           // 'K'
city.substring(0, 3);     // "Kar"  — [0, 3) : start inclusive, end exclusive
city.toUpperCase();       // "KARACHI"
city.indexOf("a");        // 2 — first match, or -1 if absent
city.startsWith("Ka");   // true
city.contains("rac");    // true
city.replace("a", "@")    // "K@r@chi" — a NEW string
city.trim();              // removes leading/trailing whitespace
```

## Immutability, concretely
`city.toUpperCase()` does not touch `city` — it **returns a new
String**; discarding the result changes nothing:

```java
String s = "hi";
s.toUpperCase();          // result thrown away
System.out.println(s);    // hi — not HI
```

Why Java insists: strings get shared (string literals are interned into
one pool), used as map keys, passed across threads. A value that can
never change is safe to share everywhere and hash once.

## equals vs == — the most Java-specific bug
```java
String a = "java";
String b = "java";
String c = new String("java");

a == b        // true  — SAME pooled object
a == c        // false — different objects, same letters!
a.equals(c)   // true  — compares CONTENTS
```

`==` compares references (identity); `.equals` compares characters.
Literals often share the pool, so `==` "works" in toy examples and
betrays you the moment a String is built at runtime (`new`, substring
of long parts, concatenation). The rule: **String equality is always
`.equals`**, with the null guard as a habit:

```java
if (input != null && input.equals("yes")) { … }
// or the null-proof form: "yes".equals(input)
```

`equalsIgnoreCase("JAVA")` exists for user text.

## Concatenation
`+` builds a new String each time — fine for a line of output, wasteful
in a big loop (next lesson). `String.join(", ", "a", "b")` and
`"Total: " + price` (auto `String.valueOf`) cover most needs.

## Common mistakes
- `s.toUpperCase();` alone, then "the method is broken".
- `if (s == "yes")` surviving review and failing on input data.
- `substring(3, 0)` or other reversed ranges → exception; end must be
  ≥ start and ≤ length.
- Null-guarding backwards: calling `s.equals("x")` when s may be null —
  flip to `"x".equals(s)`.

## Lesson summary
Methods return NEW strings; length() vs length; equals for content,
== for identity; `"literal".equals(maybeNull)` is the defensive idiom.""",
                    'exercises': [
                        {
                            'slug': 'substring-window',
                            'title': 'Half-open window',
                            'exercise_type': 'output_prediction',
                            'instructions': 'System.out.println("programming".substring(3, 6)); — exact output?',
                            'xp_reward': 40,
                            'expected_output': 'ram',
                            'explain': 'Indexes [3,6): characters r,a,m — end index exclusive is String’s universal window rule.',
                        },
                        {
                            'slug': 'immutable-result',
                            'title': 'Discarded return',
                            'exercise_type': 'output_prediction',
                            'instructions': 'String s = "abc"; s.replace("a", "x"); System.out.println(s); — what prints?',
                            'xp_reward': 50,
                            'expected_output': 'abc',
                            'explain': 'replace returned "xbc" which nobody stored; s is untouched — immutability in one line.',
                        },
                        {
                            'slug': 'equals-vs-identity',
                            'title': 'new String verdict',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'String p = "hi"; String q = new String("hi"); What do p == q and p.equals(q) report?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': '== false, equals true', 'is_correct': True},
                                {'id': 'b', 'text': '== true, equals true', 'is_correct': False},
                                {'id': 'c', 'text': '== false, equals false', 'is_correct': False},
                                {'id': 'd', 'text': '== throws', 'is_correct': False},
                            ],
                            'explain': 'new forces a distinct object: identity differs, content matches. This exact pair is the interview version.',
                        },
                        {
                            'slug': 'null-safe-equals',
                            'title': 'Null-safe form',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'answer may be null. Which comparison NEVER throws?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '"yes".equals(answer)', 'is_correct': True},
                                {'id': 'b', 'text': 'answer.equals("yes")', 'is_correct': False},
                                {'id': 'c', 'text': 'answer == "yes"', 'is_correct': False},
                                {'id': 'd', 'text': 'answer.contains("yes")', 'is_correct': False},
                            ],
                            'explain': 'Calling ON the literal means null sits in the argument seat; equals(null) is defined as false.',
                        },
                        {
                            'slug': 'indexof-absent',
                            'title': 'Not found code',
                            'exercise_type': 'fill_blank',
                            'instructions': 'String.indexOf returns ____ (a small negative number, digit with sign) when the search text is absent.',
                            'xp_reward': 40,
                            'solution_code': '-1',
                            'explain': '-1 — the same "negative means absent" convention binarySearch extends further.',
                        },
                    ],
                },
                {
                    'title': 'Building Strings Efficiently',
                    'slug': 'string-builder',
                    'objective': 'Recognise the quadratic + chain problem and use StringBuilder.',
                    'duration': 12,
                    'body': """# Why loops of `+` get slow

`+` on Strings compiles to "create a StringBuilder, append both, toString"
—one shot is fine. Inside a loop, however, EVERY iteration rebuilds the
whole accumulated text into a new String:

```java
String csv = "";
for (int i = 0; i < 10000; i++) {
    csv += i + ",";      // copy ~0+1+2+…+n chars = O(n²) work
}
```

That is quadratic time and a fresh garbage pile per round — the DSA
course's cost analysis applied to a one-line accumulator. The fix keeps
ONE growable buffer:

```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i).append(',');    // append returns the SAME builder: chainable
}
String csv = sb.toString();      // convert once, at the end
```

O(n) total. Rules of thumb:
- One join or two → `+` is perfectly readable; the compiler batches it.
- Loop accumulating text → `StringBuilder` (or `String.join` / streams
  with `Collectors.joining`).
- `StringBuffer` is the ancient thread-safe twin — prefer StringBuilder.

## Useful extras
```java
sb.insert(0, "#");     // shift right and place at index 0
sb.reverse();          // in-place reversal — palindrome checks live here
sb.deleteCharAt(0);    // remove one
sb.length();           // current size without converting
```

Reversing a String idiomatically: `new StringBuilder(s).reverse().toString()`.

## Formatting while we are here
```java
System.out.printf("Score: %.1f%% of %d%n", 82.57, 100);  // Score: 82.6% of 100
String tag = String.format("%s-%04d", "STU", 42);        // STU-0042
```

`%s` string, `%d` int, `%.1f` one-decimal float, `%04d` zero-padded
width 4, `%n` platform newline. `printf` prints, `String.format`
returns the text.

## Common mistakes
- Keeping `+=` in loops that touch thousands of lines (file parsing,
  report building) — measurable seconds of waste.
- Forgetting the final `.toString()` and passing the builder around
  where a String was expected.
- Trying `sb == sb2` — builders use identity; compare their toStrings.

## Lesson summary
`+` per loop iteration = O(n²); StringBuilder = one buffer, chainable
appends, convert at the end — plus printf-style format specifiers.""",
                    'exercises': [
                        {
                            'slug': 'builder-growth',
                            'title': 'Why StringBuilder wins',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Accumulating n pieces with `text += piece` costs about O(n²) because…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'each += copies all characters accumulated so far into a new String', 'is_correct': True},
                                {'id': 'b', 'text': 'the + operator is secretely slow per character', 'is_correct': False},
                                {'id': 'c', 'text': 'strings are stored on disk', 'is_correct': False},
                                {'id': 'd', 'text': 'the JVM recompiles each loop', 'is_correct': False},
                            ],
                            'explain': '1+2+3+…+n copies = n(n+1)/2: the triangular sum you derived in the complexity chapter.',
                        },
                        {
                            'slug': 'reverse-idiom',
                            'title': 'Reverse one-liner',
                            'exercise_type': 'fill_blank',
                            'instructions': 'String r = new StringBuilder(s).reverse().______(); — method that converts the builder back to a String (exact camelCase method name).',
                            'xp_reward': 40,
                            'solution_code': 'toString',
                            'explain': 'toString() ends the pipeline; without it r is a StringBuilder, not a String.',
                        },
                        {
                            'slug': 'printf-width',
                            'title': 'Format prediction',
                            'exercise_type': 'output_prediction',
                            'instructions': 'String.format("%s-%04d", "STU", 42); — exact resulting text?',
                            'xp_reward': 50,
                            'expected_output': 'STU-0042',
                            'explain': '%04d: pad to width 4 with zeros: 0042.',
                        },
                        {
                            'slug': 'append-chain',
                            'title': 'append returns',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'sb.append(1).append(2).append(3) works because append returns…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the same StringBuilder, enabling chaining', 'is_correct': True},
                                {'id': 'b', 'text': 'a new builder each time', 'is_correct': False},
                                {'id': 'c', 'text': 'a String immediately', 'is_correct': False},
                                {'id': 'd', 'text': 'an int count', 'is_correct': False},
                            ],
                            'explain': 'The fluent-builder pattern: mutate self, hand self back — same idea behind Stream intermediate ops later.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 4 Quiz',
                    'slug': 'java-arrays-strings-quiz',
                    'objective': 'Check arrays, String API, equality and builder usage.',
                    'duration': 8,
                    'body': """# Chapter 4 Quiz

Six questions on array mechanics, string methods/immutability, and
efficient text building.""",
                    'exercises': [
                        {
                            'slug': 'q4-length-mismatch',
                            'title': 'length or length()',
                            'exercise_type': 'output_prediction',
                            'instructions': 'int[] a = {1,2,3}; String s = "abcd"; System.out.println(a.length + s.length()); — what prints?',
                            'xp_reward': 40,
                            'expected_output': '7',
                            'explain': 'Array field 3 + String method 4: the two spellings cooperate arithmetically.',
                        },
                        {
                            'slug': 'q4-jagged',
                            'title': 'Jagged grid',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'int[][] g = new int[3][]; g[0] = new int[5]; g[1] = new int[2]; — which is true?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Legal: rows are independent arrays and may differ in length', 'is_correct': True},
                                {'id': 'b', 'text': 'Illegal: all rows must match column count', 'is_correct': False},
                                {'id': 'c', 'text': 'g[2] is also int[0] automatically', 'is_correct': False},
                                {'id': 'd', 'text': 'g.length would be 5', 'is_correct': False},
                            ],
                            'explain': '2D arrays are ARRAYS OF ARRAYS — row 2 staying null is the honest answer, and g.length is 3 (rows).',
                        },
                        {
                            'slug': 'q4-intern-==',
                            'title': 'Literal sharing',
                            'exercise_type': 'output_prediction',
                            'instructions': 'System.out.println("a" + "b" == "ab"); — beware: left-to-right, "a"+"b" first. Does the comparison print true or false?',
                            'xp_reward': 50,
                            'expected_output': 'true',
                            'explain': 'Both compile to pooled literals with the same characters: == sees one interned "ab". equals is still THE rule — never rely on pooling.',
                        },
                        {
                            'slug': 'q4-builder-when',
                            'title': 'Pick the tool',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Building one CSV line from 3 fields — best choice?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'a or a(+ b(+ c(+ d — simple + is fine here', 'is_correct': True},
                                {'id': 'b', 'text': 'StringBuilder, always mandatory', 'is_correct': False},
                                {'id': 'c', 'text': 'a for-loop of +=', 'is_correct': False},
                                {'id': 'd', 'text': 'printf', 'is_correct': False},
                            ],
                            'explain': 'No loop, few pieces: + compiles to one builder anyway and reads cleanly. Premature StringBuilder is noise.',
                        },
                        {
                            'slug': 'q4-trim',
                            'title': 'Whitespace remover',
                            'exercise_type': 'fill_blank',
                            'instructions': 'String input = "  hello  "; input.___() yields "hello" (method name, exact case).',
                            'xp_reward': 40,
                            'solution_code': 'trim',
                            'explain': 'trim() — the front-desk of every input validation path.',
                        },
                        {
                            'slug': 'q4-sort-side',
                            'title': 'Sort effect',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Arrays.sort(int[]) …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'sorts in place; the original array is reordered', 'is_correct': True},
                                {'id': 'b', 'text': 'returns a new sorted array', 'is_correct': False},
                                {'id': 'c', 'text': 'needs a List, not an array', 'is_correct': False},
                                {'id': 'd', 'text': 'is O(n²) on average', 'is_correct': False},
                            ],
                            'explain': 'In place and dual-pivot quicksort-based for primitives: average O(n log n).',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 5 ════════════════════
        {
            'title': 'Object-Oriented Programming: Classes and Objects',
            'slug': 'oop-classes',
            'description': 'Blueprints and instances, fields and methods, constructors, and static vs instance members.',
            'lessons': [
                {
                    'title': 'Classes: Blueprints, Objects: Buildings',
                    'slug': 'classes-objects',
                    'objective': 'Define a class with fields and methods and use multiple objects of it.',
                    'duration': 15,
                    'body': """# Modelling things instead of scripting steps

Procedural code (chapters 1–4) manipulates data with functions. **Object-
oriented** code bundles data WITH the operations on it into a **class** —
a blueprint — and runs the program as objects talking to objects.

```java
public class Student {          // the blueprint
    String name;                // fields (data)
    int age;
    double grade;

    void introduce() {          // method (behaviour)
        System.out.println("Hi, I am " + name + ", grade " + grade);
    }

    boolean isSenior() {        // another method
        return grade >= 90;
    }
}
```

Using it:

```java
Student a = new Student();       // object #1 (instance)
a.name = "Amina";
a.grade = 91;
a.introduce();                   // Hi, I am Amina, grade 91.0

Student b = new Student();       // object #2 — completely separate data
b.name = "Bilal";
b.grade = 74;
System.out.println(a.isSenior() + " " + b.isSenior());  // true false
```

Anatomy of `new Student()`:
- `Student` (left of `=`): the **type** of the variable.
- `new Student()`: allocates a fresh object from the blueprint and calls
  a **constructor** (next lesson).
- `a`: a **reference** — like an array variable, it points at the object.
  `Student c = a;` copies the pointer; c and a are one student (same
  aliasing surprise as chapter 4!).

## Why classes?
1. **Grouping:** name/age/grade travel together; functions took three
   arguments every time — an object takes one.
2. **Invariants near rules:** the method that changes `grade` can
   validate it (with encapsulation, chapter 6, enforcing this).
3. **Vocabulary:** your program has `Student`s because the problem does.

## null is the empty pointer
```java
Student s;                       // local: MUST initialise before use
Student s = null;                // OK: references may be null
s.introduce();                   // NullPointerException — no object there
```

Calling a method on null is Java's most common runtime crash; guards
(`if (s != null)`) or design (never store null students) prevent it.

## Common mistakes
- Confusing the class (one blueprint) with objects (many buildings):
  fields live in the OBJECT, method code lives in the CLASS.
- `Student x; x.name = ...` — compile error (uninitialised local).
- Expecting `b = a` to duplicate the student.
- Forgetting capitals: `student s = new Student()` fails — type names
  are PascalCase and case-sensitive.

## Lesson summary
Class = fields + methods blueprint; `new` makes an instance; variables
hold references; null references crash on use.""",
                    'exercises': [
                        {
                            'slug': 'blueprint-vs-instance',
                            'title': 'Where data lives',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Two Student objects exist. Changing a.name on one …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'affects only that object — fields are per-instance', 'is_correct': True},
                                {'id': 'b', 'text': 'renames the class default for everyone', 'is_correct': False},
                                {'id': 'c', 'text': 'affects the other object too', 'is_correct': False},
                                {'id': 'd', 'text': 'is illegal', 'is_correct': False},
                            ],
                            'explain': 'Every object gets its own field copies — the essence of instances.',
                        },
                        {
                            'slug': 'reference-copy',
                            'title': 'Alias behaviour',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Student x = new Student(); x.age = 20; Student y = x; y.age = 21; System.out.println(x.age); — what prints?',
                            'xp_reward': 50,
                            'expected_output': '21',
                            'explain': 'y copied the reference: one object, two names. Printing x.age sees y\u2019s write.',
                        },
                        {
                            'slug': 'npe-culprit',
                            'title': 'Crash cause',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Student s = null; s.introduce(); throws…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'NullPointerException — the reference has no object', 'is_correct': True},
                                {'id': 'b', 'text': 'compile error', 'is_correct': False},
                                {'id': 'c', 'text': 'ClassCastException', 'is_correct': False},
                                {'id': 'd', 'text': 'silently does nothing', 'is_correct': False},
                            ],
                            'explain': 'The compiler trusts that s may point somewhere at runtime; the JVM discovers it does not.',
                        },
                    ],
                },
                {
                    'title': 'Constructors',
                    'slug': 'constructors',
                    'objective': 'Write constructors, overload them, and know the default one.',
                    'duration': 12,
                    'body': """# Controlled birth for objects

A **constructor** is the special method `new` calls — same name as the
class, no return type:

```java
public class Student {
    String name;
    int age;

    public Student(String name, int age) {   // our constructor
        this.name = name;                     // this. = field, bare = parameter
        this.age = age;
    }
}

Student s = new Student("Amina", 20);         // fields ready immediately
```

Why bother when chapter 5 lesson 1 assigned fields directly?
- **No half-built objects:** a Student cannot exist without a name.
- **Validation in one place:** `if (age < 0) throw new IllegalArgumentException();`
  inside the constructor protects every creation path at once.

## `this` — the receiver
`this` is the object the method runs ON. When parameter and field share
a name, `this.name = name;` disambiguates: left side field, right side
argument. The compiler resolves it by that rule — no magic.

## Overloading and the default
Constructors can be overloaded by **parameter list**:

```java
public Student(String name)           { this(name, 18); }  // this(...) = call sibling
public Student(String name, int age)  { this.name = name; this.age = age; }
public Student()                      { this("Unknown", 18); }
```

Rules to remember:
- Write **no** constructor → Java supplies a no-argument default.
- Write **any** constructor → the default VANISHES. Code doing
  `new Student()` after you added a two-arg constructor gets the
  compile error "constructor Student in class Student cannot be
  applied to given types" — the most common beginner wall here.
- `this(...)` must be the FIRST statement when delegating.
- Constructors have no return type — not even void; `public void
  Student()` silently creates an ordinary METHOD, a sneaky bug.

## Common mistakes
- Forgetting `this.` and writing `name = name;` — assigns the parameter
  to itself; the field stays null. (Some IDEs flag it; compilers do not.)
- Calling a constructor like a method: `s.Student("x", 20)` — no; only
  `new` triggers it, once, at creation.
- Arg order flipped by same types: `new Student(20, "Amina")` fails
  compile (good), `new Student("A", "B")` where both are Strings will
  NOT (types can't save you from yourself — name parameters well).

## Lesson summary
Constructors guarantee valid initial state; `this` is the receiver and
`this(...)` sibling delegation; declaring any constructor removes the
default one.""",
                    'exercises': [
                        {
                            'slug': 'default-gone',
                            'title': 'Missing no-arg call',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Student has ONLY public Student(String name, int age). What does `new Student()` do?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Compile error — the implicit default no longer exists', 'is_correct': True},
                                {'id': 'b', 'text': 'Runs with null/0 fields', 'is_correct': False},
                                {'id': 'c', 'text': 'Runtime exception', 'is_correct': False},
                                {'id': 'd', 'text': 'Calls the two-arg one with blanks', 'is_correct': False},
                            ],
                            'explain': 'The free default constructor is conditional on you declaring NONE — define one and the freebie vanishes.',
                        },
                        {
                            'slug': 'this-assignment',
                            'title': 'The self-assignment trap',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Constructor body is `name = name;` (field and parameter both called name). Result?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Parameter assigned to itself; the field stays null', 'is_correct': True},
                                {'id': 'b', 'text': 'Field set correctly — Java links names by position', 'is_correct': False},
                                {'id': 'c', 'text': 'Compile error: duplicate name', 'is_correct': False},
                                {'id': 'd', 'text': 'Infinite recursion', 'is_correct': False},
                            ],
                            'explain': 'Bare name resolves to the nearest scope — the parameter. this.name targets the field explicitly.',
                        },
                        {
                            'slug': 'void-constructor-bug',
                            'title': 'The sneaky void',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What is wrong with `public void Student() { … }` written intending a constructor?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The return type makes it a regular METHOD named Student', 'is_correct': True},
                                {'id': 'b', 'text': 'Nothing — void is required on constructors', 'is_correct': False},
                                {'id': 'c', 'text': 'Constructors cannot be public', 'is_correct': False},
                                {'id': 'd', 'text': 'Methods cannot share the class name', 'is_correct': False},
                            ],
                            'explain': 'Constructors have NO return type token at all. With void it compiles, new ignores it, fields stay empty — hours lost.',
                        },
                        {
                            'slug': 'delegation-order',
                            'title': 'this(...) placement',
                            'exercise_type': 'fill_blank',
                            'instructions': 'When a constructor delegates to a sibling with this(...), that call must be the ____ statement (one lowercase word: first/last).',
                            'xp_reward': 40,
                            'solution_code': 'first',
                            'explain': 'First — Java requires sibling delegation before any other statement.',
                        },
                    ],
                },
                {
                    'title': 'static: Belongs to the Class',
                    'slug': 'static-members',
                    'objective': 'Explain static fields/methods, shared state, and the main connection.',
                    'duration': 12,
                    'body': """# One copy for everyone

`static` means **per class, not per object**. All instances share the
ONE variable; static methods run without any instance (hence `public
static void main` — the JVM has no object to call main ON).

```java
public class Student {
    String name;                     // per object
    static int enrolled = 0;         // shared counter, ONE copy

    public Student(String name) {
        this.name = name;
        enrolled++;                  // every construction touches the class field
    }

    static int classSize() { return enrolled; }   // no instance needed
}

Student a = new Student("Amina");
Student b = new Student("Bilal");
System.out.println(Student.enrolled);      // 2 — via the class name
System.out.println(Student.classSize());   // 2
System.out.println(a.enrolled);            // 2 too — same single variable!
```

The `a.enrolled` line is Java's most educational smell: legal, but it
reads "Amina's count" while it is the CLASS's count. Style guides force
`Student.enrolled` so the sharedness is visible.

## The static rules that cause bugs
- A static method **cannot** touch instance fields (which object's
  `name` should it use?) — compile error, not mystery.
- An instance method CAN read statics — no restriction that way.
- Static mutable state is global state in disguise: tests leak into
  each other, threads race on it. Reach for it for true constants
  (`static final double PI`) and counters/factories, not convenience.

## static final = constant
```java
static final int MAX_NAME = 50;   // one value, immutable, class-level
```

The `final` freezes the single shared copy; UPPER_SNAKE signals it.

## When does something deserve static?
Ask: "does this operation need any object's data?"
- `Math.max(a, b)` needs no Math instance — Math isn't even creatable.
- `s.introduce()` obviously needs WHICH student — instance.
- `Student.enrolled` is class-level bookkeeping — static field.

## Common mistakes
- Instance counter declared static: every object "shares" the count and
  nobody can tell whose number is whose.
- `NullPointerException` from a static context calling something that
  should have been instance: "cannot make a static reference to the
  non-static field" is the compiler saving you from ambiguity.
- Mutating shared statics from several threads with no synchronisation.

## Lesson summary
static = one class-level copy callable without objects; static methods
see only statics; use it for constants and genuine class-level data,
with care everywhere else.""",
                    'exercises': [
                        {
                            'slug': 'static-share-count',
                            'title': 'Shared field arithmetic',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Using the enrolled example exactly: create THREE Students, print Student.enrolled. (number only)',
                            'xp_reward': 40,
                            'expected_output': '3',
                            'explain': 'Every constructor increments the single class-level counter.',
                        },
                        {
                            'slug': 'static-cannot-see-instance',
                            'title': 'Compile-time boundary',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A static method references the instance field name. Result?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Compile error: cannot make a static reference to a non-static field', 'is_correct': True},
                                {'id': 'b', 'text': 'Uses the first-created object\u2019s name', 'is_correct': False},
                                {'id': 'c', 'text': 'Uses null silently', 'is_correct': False},
                                {'id': 'd', 'text': 'Runtime NPE only', 'is_correct': False},
                            ],
                            'explain': 'There IS no receiver object inside a static method — the question "whose name?" has no answer, so the compiler rejects it.',
                        },
                        {
                            'slug': 'main-why-static',
                            'title': 'Why main is static',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'main must be static because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the JVM starts it before any object of the class exists', 'is_correct': True},
                                {'id': 'b', 'text': 'static methods run faster', 'is_correct': False},
                                {'id': 'c', 'text': 'main is in java.lang', 'is_correct': False},
                                {'id': 'd', 'text': 'arguments cannot be passed to instance methods', 'is_correct': False},
                            ],
                            'explain': 'Booting needs an object to call main on; static = callable on nothing but the class — the chicken-and-egg solved.',
                        },
                        {
                            'slug': 'constant-declaration',
                            'title': 'Freezing the shared copy',
                            'exercise_type': 'fill_blank',
                            'instructions': 'To declare a class-level constant, combine static with which other keyword? (lowercase)',
                            'xp_reward': 40,
                            'solution_code': 'final',
                            'explain': 'static final — shared AND unchangeable: the Java constant pair.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 5 Quiz',
                    'slug': 'oop-classes-quiz',
                    'objective': 'Check classes, constructors and static recall.',
                    'duration': 8,
                    'body': """# Chapter 5 Quiz

Six questions on blueprints vs buildings, constructor rules, and
class-level state.""",
                    'exercises': [
                        {
                            'slug': 'q5-new-job',
                            'title': 'new does…',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL things `new Student("Ali", 20)` performs.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Allocates a fresh object', 'is_correct': True},
                                {'id': 'b', 'text': 'Calls the matching constructor', 'is_correct': True},
                                {'id': 'c', 'text': 'Returns a reference to the new object', 'is_correct': True},
                                {'id': 'd', 'text': 'Copies an existing prototype object', 'is_correct': False},
                            ],
                            'explain': 'Allocate → initialise → hand back reference. Java creates from blueprints, not by prototyping copies.',
                        },
                        {
                            'slug': 'q5-redeclare-default',
                            'title': 'Restoring new Student()',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'After adding Student(String,int) you still want new Student() to work. Write…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'an explicit no-argument constructor yourself', 'is_correct': True},
                                {'id': 'b', 'text': 'a method named Student with void return', 'is_correct': False},
                                {'id': 'c', 'text': 'nothing — defaults never leave', 'is_correct': False},
                                {'id': 'd', 'text': 'a static block', 'is_correct': False},
                            ],
                            'explain': 'Declare any constructor and the compiler stops gifting the default — re-declaring it is the fix.',
                        },
                        {
                            'slug': 'q5-this-meaning',
                            'title': 'this points at',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inside an instance method, `this` is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the object the method was invoked on', 'is_correct': True},
                                {'id': 'b', 'text': 'the class itself', 'is_correct': False},
                                {'id': 'c', 'text': 'the most recent object created', 'is_correct': False},
                                {'id': 'd', 'text': 'a keyword that frees memory', 'is_correct': False},
                            ],
                            'explain': 'a.introduce() → inside, this == a. The hidden receiver argument made visible.',
                        },
                        {
                            'slug': 'q5-static-output',
                            'title': 'Two names, one static',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Student.enrolled is 2. Student x = new Student("A",19); System.out.println(x.enrolled + " " + Student.enrolled); — exact output?',
                            'xp_reward': 50,
                            'expected_output': '3 3',
                            'explain': 'The constructor bumped the single shared count to 3; both expressions read that one variable.',
                        },
                        {
                            'slug': 'q5-field-method-shape',
                            'title': 'Blueprint anatomy',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which line is FIELDS (not methods)?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'String name; int age;', 'is_correct': True},
                                {'id': 'b', 'text': 'void introduce() { … }', 'is_correct': False},
                                {'id': 'c', 'text': 'new Student()', 'is_correct': False},
                                {'id': 'd', 'text': 'public class Student', 'is_correct': False},
                            ],
                            'explain': 'Declarations of stored data are fields; bodies with behaviour are methods.',
                        },
                        {
                            'slug': 'q5-class-vs-object-data',
                            'title': 'Where per-object data sits',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Each object’s own copy of a field is said to be stored on the ____ (one lowercase word: class or ____).',
                            'xp_reward': 40,
                            'solution_code': 'object',
                            'explain': 'On the object/instance — versus static’s single class-level copy.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 6 ════════════════════
        {
            'title': 'Object-Oriented Programming: Inheritance and Polymorphism',
            'slug': 'oop-inheritance',
            'description': 'extends and super, overriding vs overloading, runtime polymorphism, and Object itself.',
            'lessons': [
                {
                    'title': 'Inheritance: extends and super',
                    'slug': 'inheritance-basics',
                    'objective': 'Build a class hierarchy, reuse fields/methods, and call the parent constructor.',
                    'duration': 15,
                    'body': """# Standing on an existing class

```java
public class Animal {
    String name;
    int age;

    public Animal(String name, int age) {
        this.name = name; this.age = age;
    }

    void eat() { System.out.println(name + " eats"); }
}

public class Dog extends Animal {        // Dog IS-A Animal
    String breed;

    public Dog(String name, int age, String breed) {
        super(name, age);                 // run Animal's constructor FIRST
        this.breed = breed;
    }

    void bark() { System.out.println(name + " woofs"); }   // NEW behaviour
}
```

`extends` hands the child every accessible member of the parent: Dog
objects carry name, age and eat() without repeating a line. Rules:

- **Single inheritance only.** A class extends ONE class (Java's
  answer to C++'s diamond mess). Multiple SHAPES of behaviour come
  from interfaces (chapter 7).
- **Constructors are NOT inherited** — but the child MUST invoke one,
  explicitly via `super(...)` (first statement) or implicitly the
  no-arg one. When the parent lacks a no-arg constructor, forgetting
  `super(...)` is the compile error "constructor Animal in class
  Animal cannot be applied to given types".
- `super.eat()` calls the parent's version from inside an override.

## The IS-A test
Inherit only when the substitution sentence makes sense: "a Dog is an
Animal" ✅. "a Car is an Engine" ❌ — a car HAS-A engine: that is
composition (a field holding an Engine), and composition is usually the
better tool. Interviewers love this distinction; so does refactoring.

## protected: the family channel
`private` hides from everyone; `protected` opens to subclasses (and
same package) — used for fields/methods that children legitimately
need, like an internal helper `protected void growl()`.

## Object: everyone's great-grandparent
Any class without `extends` implicitly extends `java.lang.Object`, so
every object already has `toString()`, `equals()`, `hashCode()`,
`getClass()`. You have been INHERITING from day one — chapter 5's
"bare" Student already answered `s.toString()` with the ugly
`Student@1a2b3c` default.

## Common mistakes
- Extending for code convenience ("I wanted its fields") — fragile
  coupling; ask the IS-A question.
- `super(...)` not first, or calling `this(...)` AND `super(...)` —
  one delegation per constructor.
- Trying to inherit from two classes; the compiler refuses — compose
  or implement interfaces instead.

## Lesson summary
extends reuses a parent's members; super(...) satisfies the parent
constructor first; inheritance claims IS-A, otherwise compose; and
Object backs the whole tree.""",
                    'exercises': [
                        {
                            'slug': 'extends-members',
                            'title': 'What Dog gets',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Given the Dog/Animal code above, a Dog instance has access to which of these?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'the name and age fields', 'is_correct': True},
                                {'id': 'b', 'text': 'eat()', 'is_correct': True},
                                {'id': 'c', 'text': 'bark()', 'is_correct': True},
                                {'id': 'd', 'text': 'Animal\u2019s constructor as its own', 'is_correct': False},
                            ],
                            'explain': 'Fields and methods flow down; constructors are called (super) but never inherited.',
                        },
                        {
                            'slug': 'super-missing-error',
                            'title': 'The classic compile error',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Animal has ONLY Animal(String,int). Dog\u2019s constructor body starts with assignments, no super(...). Result?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Compile error: implicit super() call finds no no-arg Animal constructor', 'is_correct': True},
                                {'id': 'b', 'text': 'Compiles; name/age stay null', 'is_correct': False},
                                {'id': 'c', 'text': 'Runtime NPE on eat()', 'is_correct': False},
                                {'id': 'd', 'text': 'Java auto-picks the String,int constructor', 'is_correct': False},
                            ],
                            'explain': 'Every constructor must chain to a parent one; the implicit super() only works when a no-arg parent constructor exists.',
                        },
                        {
                            'slug': 'has-a-not-is-a',
                            'title': 'Car and Engine',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A Car contains an Engine. The right modelling is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'class Car { Engine engine; } — composition (HAS-A)', 'is_correct': True},
                                {'id': 'b', 'text': 'class Car extends Engine — inheritance (IS-A)', 'is_correct': False},
                                {'id': 'c', 'text': 'class Engine extends Car — reverse inheritance', 'is_correct': False},
                                {'id': 'd', 'text': 'Both modelings are equally correct', 'is_correct': False},
                            ],
                            'explain': 'A car is NOT an engine — it holds one. Extending would give Car methods like startCombustion it must not answer to.',
                        },
                        {
                            'slug': 'implicit-object',
                            'title': 'Everyone\u2019s ancestor',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Student has no extends clause. System.out.println(new Student("A",20)); uses the inherited default toString. Does it print "A" or something like Student@6d06d69c? Answer with the class-name prefix only, e.g. Word@hex → write the part before @.',
                            'xp_reward': 40,
                            'expected_output': 'Student',
                            'explain': 'Default Object.toString = ClassName@hashcode — which is why overriding toString is a chapter-7 ritual.',
                        },
                    ],
                },
                {
                    'title': 'Overriding vs Overloading',
                    'slug': 'override-overload',
                    'objective': 'Distinguish the two same-name strategies and their rules.',
                    'duration': 12,
                    'body': """# Same name, different games

**Overloading** — SAME class (or inherited), same method NAME,
DIFFERENT parameter list. The compiler picks by arguments:

```java
int add(int a, int b) { return a + b; }
double add(double a, double b) { return a + b; }     // overload
String add(String a, String b) { return a + b; }     // overload
```

Return type alone does NOT create an overload — `int f()` and
`double f()` with identical params is a compile error; the caller
couldn't disambiguate.

**Overriding** — a SUBCLASS rewrites the parent's implementation. Same
name, same parameters, same-or-covariant return:

```java
class Animal {
    void speak() { System.out.println("generic noise"); }
}
class Dog extends Animal {
    @Override
    void speak() { System.out.println("woof"); }      // override
}
class Puppy extends Dog {
    @Override
    void speak() { super.speak(); System.out.println("yip"); }  // extend parent
}
```

The `@Override` annotation is free insurance: misspell the parent's
signature and the compiler shouts instead of silently creating a new
method.

Rules that bite:
- **private methods cannot be overridden** (invisible to children —
  you just made an unrelated new method).
- **static methods are hidden, not overridden**: the CALLING class
  decides, not the object (the next lesson's polymorphism contrast).
- Cannot reduce visibility: public parent method stays public in the
  child; protected→private is rejected.
- Can throw fewer/narrower checked exceptions, never broader ones.

## The one-sentence difference
Overloading = **compile-time** choice by arguments (same class).
Overriding = **runtime** choice by object (subclass replaces behaviour).

## Common mistakes
- "Overloading by return type only" attempts (compile error).
- Changing one parameter type and thinking you overrode — you
  overloaded; @Override catches this instantly.
- Calling `this.speak()` expecting parent version — that is
  `super.speak()`; this recursion stacks overflows.

## Lesson summary
Overload = same name, different args, compiler picks. Override =
replace parent body, object picks at runtime; @Override or suffer.""",
                    'exercises': [
                        {
                            'slug': 'which-version-runs',
                            'title': 'Compile choice',
                            'exercise_type': 'output_prediction',
                            'instructions': 'add(2, 3) with the two overloads above present — which return type does the chosen method have, spelled in lowercase as Java primitives do?',
                            'xp_reward': 40,
                            'expected_output': 'int',
                            'explain': 'Exact match int,int wins overload resolution before widening (double) is even considered.',
                        },
                        {
                            'slug': 'private-not-overridden',
                            'title': 'The invisible parent method',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Parent has private helper(); child declares void helper() { … }. At runtime calling helper() on the child object runs…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'the child\u2019s — it is a brand-new method; parent\u2019s private one stays parent-only', 'is_correct': True},
                                {'id': 'b', 'text': 'the parent\u2019s — private is still overridden', 'is_correct': False},
                                {'id': 'c', 'text': 'both, chained', 'is_correct': False},
                                {'id': 'd', 'text': 'neither — compile error', 'is_correct': False},
                            ],
                            'explain': 'Overriding requires visibility; the child\u2019s method merely reuses the name. @Override would have flagged the intent mismatch.',
                        },
                        {
                            'slug': 'super-in-override',
                            'title': 'super.speak() meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In Puppy.speak(), the line super.speak() executes…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Dog\u2019s speak (which itself prints woof, or chains further up via ITS super)', 'is_correct': True},
                                {'id': 'b', 'text': 'Animal\u2019s speak directly, always', 'is_correct': False},
                                {'id': 'c', 'text': 'Puppy\u2019s again — recursion', 'is_correct': False},
                                {'id': 'd', 'text': 'the Object default', 'is_correct': False},
                            ],
                            'explain': 'super = parent\u2019s CURRENT override: Puppy calls Dog.speak; it is Dog that chains to Animal if coded so.',
                        },
                        {
                            'slug': 'annotation-value',
                            'title': '@Override purpose',
                            'exercise_type': 'fill_blank',
                            'instructions': 'The annotation that makes the compiler verify you really matched a parent method is @____ (one word, PascalCase as written).',
                            'xp_reward': 40,
                            'solution_code': 'Override',
                            'explain': '@Override — a compiler-checked promise, not documentation.',
                        },
                    ],
                },
                {
                    'title': 'Polymorphism: One Variable, Many Shapes',
                    'slug': 'polymorphism',
                    'objective': 'Use parent-typed references to subclass objects and predict dynamic dispatch.',
                    'duration': 15,
                    'body': """# The reference type and the object type split

```java
Animal a = new Dog("Rex", 3, "Labrador");   // legal: Dog IS-A Animal
a.eat();        // ✅ Animal method — available on the reference type
a.bark();       // ❌ COMPILE ERROR — Animal reference doesn't know bark

Dog d = (Dog) a;      // cast down once you KNOW the true object
d.bark();             // ✅ now the compiler allows it
```

Two questions every expression answers:
1. **What calls does the compiler allow?** → the **reference type**
   (left side).
2. **Which implementation actually runs?** → the **object type**
   (right side, created by `new`).

That split is **polymorphism**:

```java
Animal a = new Dog("Rex", 3, "Lab");
a.speak();      // woof — Dog's override runs, not Animal's
```

The JVM looks up the method in the REAL object's class at runtime
("dynamic dispatch") — a jump table by object type, not a fixed
address by variable type. This is why `speak()` can be written once
for `Animal` and behave per species.

## The killer app: arrays of animals
```java
Animal[] shelter = { new Dog("Rex", 3, "Lab"), new Cat("Mimi", 1),
                     new Bird("Kiwi", 2) };
for (Animal an : shelter) {
    an.speak();      // woof, meow, tweet — no if-chain anywhere
}
```

Add a Snake next month: write the class with its speak() override and
drop it into the array — **every existing loop works unchanged**. Open
for extension, closed for modification: the open/closed principle in
its purest Java form, and the reason OOP beats switch-cases.

## instanceof: asking the real type
```java
if (a instanceof Dog d) {        // pattern matching (Java 16+): test + cast
    d.bark();                     // d is safely typed Dog here
}
```

Older style: `if (a instanceof Dog) { ((Dog) a).bark(); }`. Reaching
for instanceof inside loops usually signals a missing override — if
you're testing types to decide behaviour, polymorphism should BE the
decision.

## Static is the exception
Static methods bind to the **reference type** (hiding, not overriding):

```java
class A { static String tag() { return "A"; } }
class B extends A { static String tag() { return "B"; } }
A x = new B();
x.tag();        // "A" — chosen by the reference, at compile time
```

## Common mistakes
- `a.bark()` compile error confusion ("the object HAS bark!") —
  the reference gates what you may even call.
- Casting down without checking — ClassCastException when the wrong
  species appears.
- Overriding a static method "dynamically": it doesn't work that way.

## Lesson summary
Reference type = what you may ask; object type = what answers. Dynamic
dispatch makes shelter loops species-agnostic; instanceof is the
emergency hatch, not the design.""",
                    'exercises': [
                        {
                            'slug': 'dispatch-predict',
                            'title': 'Which speak',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Animal a = new Puppy("Pip", 1); Puppy overrides speak printing "yip", Dog printing "woof", Animal "generic noise"; Puppy\u2019s body calls super.speak() first. a.speak() prints what lines? Give the final line only: yip or woof or generic noise.',
                            'xp_reward': 50,
                            'expected_output': 'yip',
                            'explain': 'Object type Puppy decides: "woof" prints first (via super chain), "yip" last. The final line is yip.',
                        },
                        {
                            'slug': 'compile-gate',
                            'title': 'The reference veto',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Animal a = new Dog(...); a.bark(); (bark exists only in Dog) …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'compile error — Animal type does not declare bark', 'is_correct': True},
                                {'id': 'b', 'text': 'runs fine, Dog has it', 'is_correct': False},
                                {'id': 'c', 'text': 'ClassCastException', 'is_correct': False},
                                {'id': 'd', 'text': 'prints nothing', 'is_correct': False},
                            ],
                            'explain': 'The compiler only trusts the left-hand type. Cast to Dog (or check instanceof) to unlock subclass extras.',
                        },
                        {
                            'slug': 'open-closed-loop',
                            'title': 'Adding a species',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why does the shelter loop print correctly when Snake is added later?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'an() calls speak() on the reference type; each object dispatches to its own override', 'is_correct': True},
                                {'id': 'b', 'text': 'the loop must be extended with if (a instanceof Snake)', 'is_correct': False},
                                {'id': 'c', 'text': 'static binding resolves at compile time per array slot', 'is_correct': False},
                                {'id': 'd', 'text': 'Java auto-rewrites Animal for new subclasses', 'is_correct': False},
                            ],
                            'explain': 'That is the open/closed payoff: the loop code is CLOSED to edits, the hierarchy OPEN to new classes.',
                        },
                        {
                            'slug': 'static-hiding-trap',
                            'title': 'Static dispatch result',
                            'exercise_type': 'output_prediction',
                            'instructions': 'A x = new B(); with both classes having static tag() returning "A" and "B" — what does x.tag() return (single letter)?',
                            'xp_reward': 50,
                            'expected_output': 'A',
                            'explain': 'Statics bind by reference type: hiding, not overriding. The object\u2019s B-ness is ignored.',
                        },
                        {
                            'slug': 'instanceof-usage',
                            'title': 'Safe downcast',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct uses of instanceof / pattern matching.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'if (a instanceof Dog d) d.bark(); casts and binds in one step', 'is_correct': True},
                                {'id': 'b', 'text': 'if (((Dog) a).xxx) without any check, as always-safe practice', 'is_correct': False},
                                {'id': 'c', 'text': 'a instanceof Animal is true when a was built as new Dog(...)', 'is_correct': True},
                                {'id': 'd', 'text': 'instanceof returns false for null references', 'is_correct': True},
                            ],
                            'explain': 'Blind downcasts throw ClassCastException when wrong; instanceof guards them — and null instanceof anything is false, never an error.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 6 Quiz',
                    'slug': 'oop-inheritance-quiz',
                    'objective': 'Check inheritance mechanics, override rules and polymorphic dispatch.',
                    'duration': 8,
                    'body': """# Chapter 6 Quiz

Six questions on hierarchies, super, overriding, and who-runs-what.""",
                    'exercises': [
                        {
                            'slug': 'q6-parent-count',
                            'title': 'How many parents',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In Java (classes only), a class can directly extend…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'exactly one class (plus interfaces via implements)', 'is_correct': True},
                                {'id': 'b', 'text': 'up to two for mixins', 'is_correct': False},
                                {'id': 'c', 'text': 'as many as needed (multiple inheritance)', 'is_correct': False},
                                {'id': 'd', 'text': 'none — composition only', 'is_correct': False},
                            ],
                            'explain': 'Single class inheritance; the multi-shape need is met by implementing many interfaces.',
                        },
                        {
                            'slug': 'q6-object-methods',
                            'title': 'Free inheritors',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL methods every Java object has from Object.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'toString()', 'is_correct': True},
                                {'id': 'b', 'text': 'equals(Object)', 'is_correct': True},
                                {'id': 'c', 'text': 'hashCode()', 'is_correct': True},
                                {'id': 'd', 'text': 'length()', 'is_correct': False},
                            ],
                            'explain': 'length() belongs to String only — Object\u2019s big three are toString/equals/hashCode (plus getClass, clone, finalizers history).',
                        },
                        {
                            'slug': 'q6-constructor-not-inherited',
                            'title': 'Constructor truth',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which statement about constructors in inheritance is correct?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'They are not inherited; child constructors must call a parent one via super(...)', 'is_correct': True},
                                {'id': 'b', 'text': 'They flow down like methods', 'is_correct': False},
                                {'id': 'c', 'text': 'The parent constructor reruns on every child method call', 'is_correct': False},
                                {'id': 'd', 'text': 'Children may skip the parent entirely', 'is_correct': False},
                            ],
                            'explain': 'Construction is always a chain to Object — skipping is not an option; inheritance is not in the list.',
                        },
                        {
                            'slug': 'q6-visibility-rule',
                            'title': 'Override visibility',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Parent method is public. The child override may be…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'public only — visibility cannot shrink', 'is_correct': True},
                                {'id': 'b', 'text': 'protected or private too', 'is_correct': False},
                                {'id': 'c', 'text': 'package-private', 'is_correct': False},
                                {'id': 'd', 'text': 'any visibility', 'is_correct': False},
                            ],
                            'explain': 'Code that compiled calling parent.method() must still compile with a child object — shrinking access would break substitution (LSP).',
                        },
                        {
                            'slug': 'q6-super-vs-this',
                            'title': 'Which super where',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inside a constructor, super(...); means ___ ; inside a method, super.method(...) means ___ .',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'call the parent constructor; call the parent version of the method', 'is_correct': True},
                                {'id': 'b', 'text': 'call this class\u2019s other constructor; call Object\u2019s version', 'is_correct': False},
                                {'id': 'c', 'text': 'they are synonyms', 'is_correct': False},
                                {'id': 'd', 'text': 'both create new objects', 'is_correct': False},
                            ],
                            'explain': 'this(...) = sibling constructor same class; super(...) = parent constructor. In methods super = parent implementation.',
                        },
                        {
                            'slug': 'q6-final-output',
                            'title': 'Mixed chain output',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Animal.speak prints "noise". Dog overrides printing super.speak() then "woof". new Dog().speak() prints which LAST line? (one word)',
                            'xp_reward': 40,
                            'expected_output': 'woof',
                            'explain': 'Order: noise first (chained call returns before Dog\u2019s own print executes).',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 7 ════════════════════
        {
            'title': 'OOP: Encapsulation, Abstraction and Interfaces',
            'slug': 'oop-encapsulation',
            'description': 'private fields with guards, abstract classes, interfaces as contracts, and the modern interface toolkit.',
            'lessons': [
                {
                    'title': 'Encapsulation: Hide the Gears',
                    'slug': 'encapsulation',
                    'objective': 'Protect invariants with private fields, getters/setters and validation.',
                    'duration': 15,
                    'body': """# The four access levels — and why "private by default"

| Modifier | Same class | Same package | Subclass | Everywhere |
|---|---|---|---|---|
| `private` | ✅ | ❌ | ❌ | ❌ |
| (default, package-private) | ✅ | ✅ | ❌* | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

The professional recipe: **fields private, behaviour public**. Anyone
can read or change a student's state — but only through methods you
control:

```java
public class Student {
    private String name;
    private double grade;              // the invariant: 0.0 .. 100.0

    public Student(String name, double grade) {
        setName(name);
        setGrade(grade);               // route through the guard, once
    }

    public double getGrade() { return grade; }

    public void setGrade(double g) {
        if (g < 0 || g > 100) {
            throw new IllegalArgumentException("grade out of range: " + g);
        }
        grade = g;
    }

    public void addBonus(double pts) { // behaviour may bend rules safely
        grade = Math.min(100, grade + pts);
    }
}
```

With chapter 5's public field version, `s.grade = 9999;` was legal and
silently poisoned every later report. Encapsulation makes that state
**unrepresentable** — the compiler or the exception blocks it. That is
the whole idea: **protect the invariants, not the variables**.

Getters/setters are called **accessors/mutators**; `getX`/`setX`
naming is the JavaBeans convention every framework (Spring, Android
data binding) leans on.

## Immutability: maximum encapsulation
```java
public final class Point {              // final: no subclass meddling
    private final double x, y;          // final: frozen after construction
    public Point(double x, double y) { this.x = x; this.y = y; }
    public double getX() { return x; }
    public double getY() { return y; }
    // NO setters — state cannot change after birth
}
```

Immutable objects are inherently thread-safe, safe as map keys, and
cheap to share — `String`, `Integer` and friends are all built this
way. When values conceptually never change, make that structural.

## Why not just public fields (C++ habit)?
1. Validation hook (above).
2. Implementation freedom: store grade as int cents later, getters
   unchanged — callers never notice.
3. Read-only or write-only views (no setter, or setter without getter).
4. Debugging: breakpoint one method instead of every field write.

## Common mistakes
- Setter that bypasses its own guard (`grade = grade + pts;` in the
  constructor assigning the field directly, skipping validation).
- Getters returning MUTABLE internals of immutable-looking objects
  (an array field's `getXs() { return xs; }` hands out the real array —
  clone it).
- `private` on the class itself (only nested classes may be private —
  top-level classes are public or package-private).

## Lesson summary
private fields + public guarded methods = invariants enforced;
immutability adds final on class, fields; the access table is the
vocabulary this design speaks.""",
                    'exercises': [
                        {
                            'slug': 'private-field-benefit',
                            'title': 'What private buys',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Making grade private with a validating setter primarily achieves…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'impossible invalid states — every change passes the guard', 'is_correct': True},
                                {'id': 'b', 'text': 'faster field access', 'is_correct': False},
                                {'id': 'c', 'text': 'less typing in main()', 'is_correct': False},
                                {'id': 'd', 'text': 'automatic thread safety of reads', 'is_correct': False},
                            ],
                            'explain': 'Encapsulation is about CONTROL of change, not secrecy for its own sake — and it buys implementation freedom besides.',
                        },
                        {
                            'slug': 'access-table-subclass',
                            'title': 'Who can see protected',
                            'exercise_type': 'multiple_select',
                            'instructions': 'A protected field is visible from…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'the class itself', 'is_correct': True},
                                {'id': 'b', 'text': 'subclasses (even in other packages)', 'is_correct': True},
                                {'id': 'c', 'text': 'other classes in the same package', 'is_correct': True},
                                {'id': 'd', 'text': 'any class anywhere', 'is_correct': False},
                            ],
                            'explain': 'protected = package + family; public = everyone — d describes public.',
                        },
                        {
                            'slug': 'immutable-final-pair',
                            'title': 'Freezing a field',
                            'exercise_type': 'fill_blank',
                            'instructions': 'To make an instance field unchangeable after construction, mark it ____ (one lowercase keyword).',
                            'xp_reward': 40,
                            'solution_code': 'final',
                            'explain': 'final fields: assignable exactly once (constructor), then frozen — the backbone of immutability.',
                        },
                        {
                            'slug': 'leaky-getter',
                            'title': 'The leak',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'private int[] scores; public int[] getScores() { return scores; } — what leaks?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Callers get the REAL array and can mutate it outside any guard', 'is_correct': True},
                                {'id': 'b', 'text': 'Nothing — private fields stay safe through getters', 'is_correct': False},
                                {'id': 'c', 'text': 'A compile error prevents this', 'is_correct': False},
                                {'id': 'd', 'text': 'Only reading is possible for callers', 'is_correct': False},
                            ],
                            'explain': 'Returning a mutable object re-opens the door the setter closed; return scores.clone().',
                        },
                    ],
                },
                {
                    'title': 'Abstract Classes',
                    'slug': 'abstract-classes',
                    'objective': 'Use abstract to force subclass completion of a partial blueprint.',
                    'duration': 12,
                    'body': """# Blueprints with deliberate holes

Some concepts are incomplete by nature: every Shape draws, but there is
no such thing as a generic drawing. `abstract` encodes that:

```java
public abstract class Shape {
    String color;

    public Shape(String color) { this.color = color; }

    abstract double area();                    // no body — subclasses MUST fill

    void describe() {                          // shared concrete code
        System.out.println(color + " shape, area " + area());
    }
}

public class Circle extends Shape {
    private final double r;
    public Circle(double r) { super("red"); this.r = r; }
    @Override double area() { return Math.PI * r * r; }
}
```

Rules:
- `abstract` methods have NO body — every concrete subclass must
  override all of them or IT must stay abstract.
- **You cannot `new Shape(...)`** — the compiler blocks instantiating
  incomplete blueprints. Shape variables/arrays are still fine
  (polymorphism: `Shape s = new Circle(2);`).
- Abstract classes CAN have fields, constructors (called via super
  from children), and concrete methods — a partial implementation
  subclasses finish.
- `abstract` + `final` together is contradiction (nobody could ever
  complete it): compile error.

## Template method, the abstract superpower
describe() above calls the abstract area() — the parent defines the
SKELETON of an algorithm, children fill the steps. The shape hierarchy
never rewrites describe(); adding Triangle is pure area(). (You will
meet this pattern again in Spring and every framework's lifecycle hooks.)

## Abstract class vs interface — the design call
- **Abstract class**: IS-A with shared STATE (fields) and shared CODE.
  Shape carries color and describe().
- **Interface** (next lesson): CAN-DO contract, no instance fields —
  Drawable, Comparable, Serializable.
- Pick abstract class when subclasses genuinely share implementation;
  pick interface when you're specifying an ability unrelated classes can
  each provide. Interfaces can be implemented alongside everything;
  an abstract class consumes the single extends slot.

## Common mistakes
- `new Shape("red")` — blocked precisely because abstract protects you
  from an area() that answers nothing.
- Forgetting @Override on the concrete side → "abstract method not
  implemented" compile error (the compiler finishing your contract).
- Giving an abstract method a body — the whole point is that it has
  none; remove `abstract` if you have something to implement.

## Lesson summary
abstract = incomplete blueprint: un-bodyable methods children MUST
implement, non-instantiable parents, shared fields and skeleton
methods allowed.""",
                    'exercises': [
                        {
                            'slug': 'abstract-cannot-new',
                            'title': 'Instantiate verdict',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Shape is abstract with abstract area(). Which line does NOT compile?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Shape s = new Shape("red");', 'is_correct': True},
                                {'id': 'b', 'text': 'Shape s = new Circle(2);', 'is_correct': False},
                                {'id': 'c', 'text': 'Circle c = new Circle(2);', 'is_correct': False},
                                {'id': 'd', 'text': 'Shape[] box = new Circle[3];', 'is_correct': False},
                            ],
                            'explain': 'Abstract types may be references, arrays-of-subtype upcasts, but never new-ed — the hole in the blueprint must be filled first.',
                        },
                        {
                            'slug': 'abstract-vs-interface',
                            'title': 'Choose the tool',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Animal hierarchy sharing name, age and eat() code should use…; unrelated classes each able to "be drawn" should use…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'abstract class; interface', 'is_correct': True},
                                {'id': 'b', 'text': 'interface; abstract class', 'is_correct': False},
                                {'id': 'c', 'text': 'both must be abstract classes', 'is_correct': False},
                                {'id': 'd', 'text': 'concrete classes only', 'is_correct': False},
                            ],
                            'explain': 'Shared STATE+CODE down one family → abstract. An ability across families → interface.',
                        },
                        {
                            'slug': 'half-implemented-shape',
                            'title': 'Partial child rule',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'class Blob extends Shape but leaves the inherited abstract area() unimplemented. Then Blob is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'a compile error unless declared abstract itself', 'is_correct': True},
                                {'id': 'b', 'text': 'fine; area() defaults to 0', 'is_correct': False},
                                {'id': 'c', 'text': 'fine but not instantiable ever', 'is_correct': False},
                                {'id': 'd', 'text': 'auto-overridden by Object', 'is_correct': False},
                            ],
                            'explain': 'Inherited holes must be filled or re-declared: complete the method or mark the class abstract.',
                        },
                    ],
                },
                {
                    'title': 'Interfaces: Contracts Anyone Can Sign',
                    'slug': 'interfaces',
                    'objective': 'Declare and implement interfaces, and read default/static/private interface members.',
                    'duration': 15,
                    'body': """# A promise, not a parent

An **interface** lists behaviours with no state:

```java
public interface Drawable {
    void draw();                       // implicitly public abstract

    default void drawTwice() {         // Java 8+: implementations inherit
        draw(); draw();
    }
}

public interface Resizable {
    void resize(double factor);
}

public class Icon implements Drawable, Resizable {   // COMMA list — many!
    public void draw()  { System.out.println("icon"); }
    public void resize(double f) { /* … */ }
}
```

Key differences from abstract classes:
- A class implements ANY number of interfaces (extends is single;
  implements is plural) — this is Java's sanctioned answer to C++'s
  diamond of mixins.
- Interfaces cannot hold instance state: only `public static final`
  constants as fields.
- Methods are abstract by default (no `abstract` keyword needed) —
  but interfaces may also ship `default` (implementations inherit and
  may override), `static` helpers (`InterfaceName.util()`), and
  `private` helper methods inside defaults (Java 9+).

## Interfaces as types
```java
Drawable d = new Icon();               // polymorphism over contracts
d.drawTwice();

void paintAll(List<Drawable> items) {  // any signatory, any class
    for (Drawable x : items) x.draw();
}
```

Framework code is built on this: Spring, JUnit and Android ALL accept
interface-typed things; concrete class names appear only at the
creation site ("program to an interface, not an implementation").

## The famous seeded interfaces
- `Comparable<T>` — `int compareTo(T other)`: how sort learns YOUR
  order. `Arrays.sort(names)` works because String implements it.
- `Runnable` — `void run()`: the thread contract (chapter-level cameo).
- `Iterable<T>` — for-each over your own container requires it.

## default resolved: the diamond rule
If two implemented interfaces give the same `default` method, the
compiler forces you to override it and choose (or call
`Drawable.super.method()` explicitly). Rare, but the rule prevents
silent ambiguity.

## Modern shorthand: sealed interfaces (Java 17)
`sealed interface Shape permits Circle, Square` limits implementors —
switch expressions over it become exhaustiveness-checked. Recognise
the name; the exam world is still pre-sealed mostly.

## Common mistakes
- Putting fields with state in interfaces (only constants allowed).
- Forgetting `public` when IMPLEMENTING interface methods — they are
  public in the contract, and an override may not shrink visibility
  (classic "attempting to assign weaker access privileges" error).
- Implementing just the ones you remember from a multi-method contract
  — the compiler lists every missing one; answer the list.

## Lesson summary
Interfaces = signable behaviour contracts, unlimited signatures per
class, default/static allowed, the backbone of framework programming.""",
                    'exercises': [
                        {
                            'slug': 'interface-state-rule',
                            'title': 'Field verdict',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which declaration is LEGAL inside an interface body?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'int MAX = 10;  (implicitly public static final)', 'is_correct': True},
                                {'id': 'b', 'text': 'private String name;', 'is_correct': False},
                                {'id': 'c', 'text': 'protected int count = 0; as instance field', 'is_correct': False},
                                {'id': 'd', 'text': 'A constructor', 'is_correct': False},
                            ],
                            'explain': 'Interfaces hold no per-object state — `int MAX = 10;` is actually a constant (static final), the only legal "field".',
                        },
                        {
                            'slug': 'multi-implement',
                            'title': 'Signature capacity',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'class Icon implements Drawable, Resizable, Clickable — how many interfaces may a class implement?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Unlimited — implements takes a comma list', 'is_correct': True},
                                {'id': 'b', 'text': 'One, matching extends', 'is_correct': False},
                                {'id': 'c', 'text': 'Two, like diamond inheritance', 'is_correct': False},
                                {'id': 'd', 'text': 'Only interfaces in its own package', 'is_correct': False},
                            ],
                            'explain': 'State-free contracts cannot conflict structurally, so Java allows many — the mixin need met safely.',
                        },
                        {
                            'slug': 'default-inherited',
                            'title': 'Who must code drawTwice',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Drawable has default drawTwice(). Icon implements Drawable and does NOT override it. Calls to icon.drawTwice() …',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'run the interface default, which in turn calls Icon’s draw()', 'is_correct': True},
                                {'id': 'b', 'text': 'compile error: interface method must be implemented', 'is_correct': False},
                                {'id': 'c', 'text': 'throw AbstractMethodError', 'is_correct': False},
                                {'id': 'd', 'text': 'run Drawable\u2019s copy statically, ignoring Icon.draw', 'is_correct': False},
                            ],
                            'explain': 'defaults are inherited implementations — and dynamic dispatch still sends draw() to the object\u2019s version.',
                        },
                        {
                            'slug': 'comparable-contract',
                            'title': 'compareTo return',
                            'exercise_type': 'multiple_select',
                            'instructions': 'For a.compareTo(b) inside Comparable, select ALL conventional returns.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'negative when a sorts BEFORE b', 'is_correct': True},
                                {'id': 'b', 'text': 'zero when they are equivalent in order', 'is_correct': True},
                                {'id': 'c', 'text': 'positive when a sorts AFTER b', 'is_correct': True},
                                {'id': 'd', 'text': 'true when a is smaller', 'is_correct': False},
                            ],
                            'explain': 'int three-way comparison (negative/0/positive) — booleans would break sort\u2019s ordering logic.',
                        },
                        {
                            'slug': 'weaker-access-trap',
                            'title': 'The access compile error',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Writing `void draw() { … }` (package-private) while implementing a public interface method gives…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'compile error: attempting to assign weaker access privileges', 'is_correct': True},
                                {'id': 'b', 'text': 'a warning; runs fine', 'is_correct': False},
                                {'id': 'c', 'text': 'silent success with private-like access', 'is_correct': False},
                                {'id': 'd', 'text': 'a runtime exception', 'is_correct': False},
                            ],
                            'explain': 'Contract methods are public; implementors may never narrow that. Add public — IDEs auto-generate it for a reason.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 7 Quiz',
                    'slug': 'oop-encapsulation-quiz',
                    'objective': 'Check access levels, abstract rules and interface mechanics.',
                    'duration': 8,
                    'body': """# Chapter 7 Quiz

Six questions on guarding state, abstract skeletons and signed
contracts.""",
                    'exercises': [
                        {
                            'slug': 'q7-private-by-default-philosophy',
                            'title': 'Field default',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Recommended access level for instance fields in well-encapsulated Java:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'private, always — expose behaviour, not storage', 'is_correct': True},
                                {'id': 'b', 'text': 'public for convenience', 'is_correct': False},
                                {'id': 'c', 'text': 'protected for future subclasses', 'is_correct': False},
                                {'id': 'd', 'text': 'whatever the IDE defaulted', 'is_correct': False},
                            ],
                            'explain': 'Fields are the wiring; getters/setters are the service hatch. protected/public fields leak invariants.',
                        },
                        {
                            'slug': 'q7-abstract-body',
                            'title': 'Abstract body law',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Abstract methods have no ____ (one lowercase noun — what concrete methods have inside braces).',
                            'xp_reward': 40,
                            'solution_code': 'body',
                            'explain': 'No body: declaration only — implementation is the subclass\u2019s debt.',
                        },
                        {
                            'slug': 'q7-interface-methods',
                            'title': 'Interface member inventory',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL members an interface may legally contain (modern Java).',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'abstract methods', 'is_correct': True},
                                {'id': 'b', 'text': 'default methods with bodies', 'is_correct': True},
                                {'id': 'c', 'text': 'static methods with bodies', 'is_correct': True},
                                {'id': 'd', 'text': 'instance fields', 'is_correct': False},
                            ],
                            'explain': 'Only constants ride as "fields"; per-object state stays out of contracts.',
                        },
                        {
                            'slug': 'q7-super-shape',
                            'title': 'Constructor chain start',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Circle extends Shape (Shape has a constructor). new Circle(2) first runs…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Shape\u2019s constructor (via explicit super or implicit no-arg), then Circle\u2019s body', 'is_correct': True},
                                {'id': 'b', 'text': 'Circle\u2019s body, Shape\u2019s after', 'is_correct': False},
                                {'id': 'c', 'text': 'Object\u2019s only — Shape skipped', 'is_correct': False},
                                {'id': 'd', 'text': 'neither — constructors are decorative', 'is_correct': False},
                            ],
                            'explain': 'Parents before children, always: construction walks DOWN the hierarchy and initialises UP (the DSA stack analogy).',
                        },
                        {
                            'slug': 'q7-drawable-dispatch',
                            'title': 'paintAll works because',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'paintAll(List<Drawable>) can call x.draw() on mixed classes because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the interface guarantees every element has draw() — the contract replaces the common ancestor', 'is_correct': True},
                                {'id': 'b', 'text': 'all classes share Object so draw exists there', 'is_correct': False},
                                {'id': 'c', 'text': 'the compiler auto-copies draw implementations', 'is_correct': False},
                                {'id': 'd', 'text': 'it cannot; type must be identical', 'is_correct': False},
                            ],
                            'explain': 'That is the payoff of programming to interfaces: shared behaviour WITHOUT shared parentage.',
                        },
                        {
                            'slug': 'q7-sealed-what',
                            'title': 'Sealed meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'sealed interface Shape permits Circle, Square means…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'only those named types may implement it', 'is_correct': True},
                                {'id': 'b', 'text': 'no class may implement it (it is frozen)', 'is_correct': False},
                                {'id': 'c', 'text': 'implementations must be final', 'is_correct': False},
                                {'id': 'd', 'text': 'methods cannot be overridden', 'is_correct': False},
                            ],
                            'explain': 'A closed guest list — enables exhaustive switch and precise algebraic-style types.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 8 ════════════════════
        {
            'title': 'Exception Handling',
            'slug': 'java-exceptions',
            'description': 'The throwable family, checked vs unchecked, try/catch/finally, and failing on purpose.',
            'lessons': [
                {
                    'title': 'The Throwable Family and try/catch',
                    'slug': 'exceptions-basics',
                    'objective': 'Read a stack trace, catch precisely, and use finally correctly.',
                    'duration': 15,
                    'body': """# When normal flow breaks

```
                Throwable
                /      \\
         Error        Exception
        (OOM, stack   /        \\
         overflow)  Checked   Unchecked (RuntimeExceptions:
                    (IOException,  NPE, IAE, IndexOOB…)
                    SQLException)
```

- **Error**: the JVM itself in trouble — you do not catch these.
- **Checked exceptions**: the compiler CHECKS that you handled them
  (try/catch) or declared them (throws) — "this file might not exist"
  is part of the method's contract.
- **Unchecked (RuntimeException +)**: programmer mistakes — null
  dereference, bad index, bad argument. No forced handling; prevented
  by guards, not catch blocks.

Handling:

```java
try {
    int[] a = new int[3];
    System.out.println(a[5]);              // throws ArrayIndexOutOfBounds
} catch (ArrayIndexOutOfBoundsException e) {
    System.out.println("bad index: " + e.getMessage());
} catch (RuntimeException e) {             // broader SECOND
    System.out.println("something else: " + e);
} finally {
    System.out.println("always runs");    // cleanup: close, flush, unlock
}
```

Rules:
- Catch blocks match **top to bottom, most specific first** — putting
  RuntimeException before its subclass makes the subclass line dead
  code (and actually a compile error, because unreachable).
- `finally` runs even if the try **returns or throws** — the one place
  "guaranteed" code lives (try-with-resources automates it now).
- A catch that does `System.out.println("error")` and moves on is
  **swallowing**: the program continues on assumptions it knows are
  broken. Either handle meaningfully (retry, fallback, clear message)
  or rethrow.

## Anatomy of a stack trace

```
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 3
    at Demo.main(Demo.java:4)
```

Read it bottom-up for the CALL CHAIN but the FIRST line is the verdict:
class, message, then YOUR file/line (topmost frame that is your code).
"Index 5 out of bounds for length 3" already tells you loop bound or
index math — chapters 3–4 meet chapter 8 in that one string.

## multi-catch and rethrow
```java
try { risky(); }
catch (IOException | SQLException e) {     // same handling, one block
    log(e); throw new RuntimeException("failed", e);   // wrap + rethrow, keep cause
}
```

Wrapping preserves the cause chain (`e.getCause()`) — production logs
read chains, not bare messages.

## Common mistakes
- try-wrapping entire methods because the compiler nagged once.
- `catch (Exception e) {}` with the empty body — the silent-killer
  idiom.
- Throwing Error subclasses (never) or using exceptions for normal
  control flow ("try parse, catch means empty input") — guards first.
- Forgetting that finally's return would swallow a pending exception
  (another reason finally = cleanup ONLY, no return inside).

## Lesson summary
Throwable splits Error/Exception, Exception into checked/unchecked;
catch specific-first; finally is the guaranteed cleanup; stack traces
are read from the topmost line of YOUR code.""",
                    'exercises': [
                        {
                            'slug': 'checked-compiler-enforcement',
                            'title': 'What the compiler forces',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Calling a method declared `void read() throws IOException` without try/catch or your own throws …',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'compile error — checked exceptions must be handled or declared', 'is_correct': True},
                                {'id': 'b', 'text': 'runs; IOException ignored', 'is_correct': False},
                                {'id': 'c', 'text': 'runtime crash only when file missing', 'is_correct': False},
                                {'id': 'd', 'text': 'auto-wrapped into RuntimeException', 'is_correct': False},
                            ],
                            'explain': 'That enforcement is the whole point of checked: file-absence is EXPECTED, so the contract makes you face it.',
                        },
                        {
                            'slug': 'catch-order',
                            'title': 'Order of catches',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'catch (RuntimeException e) appears BEFORE catch (NullPointerException e) in the same try — result?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Compile error: the NPE catch is unreachable (NPE is a RuntimeException)', 'is_correct': True},
                                {'id': 'b', 'text': 'NPE still routes to its own block', 'is_correct': False},
                                {'id': 'c', 'text': 'Both run for an NPE', 'is_correct': False},
                                {'id': 'd', 'text': 'Runs, generic block always wins', 'is_correct': False},
                            ],
                            'explain': 'Java actually rejects the shadowed catch at compile time — a mercy: the bug is real but silent in many languages.',
                        },
                        {
                            'slug': 'finally-runs',
                            'title': 'finally promise',
                            'exercise_type': 'output_prediction',
                            'instructions': 'try { return "A"; } finally { System.out.print("F"); } — inside a method whose result main prints with println. What is the total visible output? (letters in order, no spaces)',
                            'xp_reward': 50,
                            'expected_output': 'FA',
                            'explain': 'finally executes BEFORE the pending return completes: F prints, then "A" reaches println → FA.',
                        },
                        {
                            'slug': 'npe-category',
                            'title': 'Which branch',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'NullPointerException is classified as…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'unchecked (a RuntimeException) — no forced handling', 'is_correct': True},
                                {'id': 'b', 'text': 'checked — must catch or declare', 'is_correct': False},
                                {'id': 'c', 'text': 'an Error', 'is_correct': False},
                                {'id': 'd', 'text': 'a warning', 'is_correct': False},
                            ],
                            'explain': 'Forcing every null-deref into a catch would bloat code; Java treats them as bugs to PREVENT with guards.',
                        },
                    ],
                },
                {
                    'title': 'Throwing, Declaring and try-with-resources',
                    'slug': 'throw-throws',
                    'objective': 'Fail deliberately with good messages, and close resources safely.',
                    'duration': 15,
                    'body': r"""# Failing like a professional

```java
public void setGrade(double g) {
    if (g < 0 || g > 100) {
        throw new IllegalArgumentException("grade out of range: " + g);
    }
    grade = g;
}

public Student parse(String line) throws ParseException {   // declare checked
    if (!line.matches("\\d+ .*")) {
        throw new ParseException("bad record: " + line);    // YOUR class
    }
}
```

- `throw` creates AND launches one exception; the method stops there.
- `throws X` on the signature is the **contract** — checked ones push
  responsibility to the caller; unchecked ones just document.
- Custom exceptions: `class ParseException extends Exception`
  (checked) or `extends RuntimeException` (unchecked). Name them for
  the PROBLEM (InsufficientFundsException), not the mechanism.

Message quality counts: `"grade out of range: " + g` shows the
offender; `"error"` wastes a log line. Stack traces are your product's
user-facing text during incidents.

## try-with-resources (Java 7) — the modern close
```java
try (BufferedReader r = new BufferedReader(new FileReader("data.txt"))) {
    System.out.println(r.readLine());
}   // r.close() runs automatically, even if the body throws
```

Any `AutoCloseable` (streams, files, DB connections…) closes exactly
once, in reverse declaration order, no nested finally forest. Before
it existed, every file-reading tutorial shipped 10 lines of close-
possibly-throwing boilerplate; the compiler now owns that chore.

## When to choose which
- **Expected, caller-recoverable** (missing file, bad network) →
  checked, declared in throws.
- **Bug / invalid state** (null, bad argument) → unchecked, guard
  early, fail fast with a precise IllegalArgumentException / NPE.
- **Unavoidable at runtime** (business rule: insufficient funds) →
  custom unchecked is the modern trend (checked hype cooled after
  Java 8 lambdas made them awkward — Streams can't throw checked
  without wrapper gymnastics).

## finally vs try-with-resources note
finally remains right for NON-closeable cleanup (flags, timers);
resources → try-with-resources, always.

## Common mistakes
- Throwing bare `new Exception("oops")` — no type information for
  catchers; define or pick the precise class.
- Catching your own just-thrown exception in the same method via an
  outer try ("handling" that hides the real bug).
- Logged-then-swallowed exceptions in libraries — the caller deserves
  the failure you cannot fix.
- Closing inside try with individual catch(IOException) per close —
  try-with-resources deleted that ritual.

## Lesson summary
throw launches, throws declares, custom types name the problem; messages
carry the offending value; AutoCloseable + try-with-resources is the
close discipline now.""",
                    'exercises': [
                        {
                            'slug': 'throw-stops-flow',
                            'title': 'After the throw',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A method unconditionally executes `throw new IllegalArgumentException("x");` on line 3. Line 4 of that method…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'is unreachable — a compile error when the throw cannot be skipped', 'is_correct': True},
                                {'id': 'b', 'text': 'always runs after logging', 'is_correct': False},
                                {'id': 'c', 'text': 'runs only if caught below in the same method', 'is_correct': False},
                                {'id': 'd', 'text': 'runs twice', 'is_correct': False},
                            ],
                            'explain': 'throw exits like a return with an error label; Java\u2019s unreachable-code rule even rejects dead statements after unconditional throws. Inside an if, line 4 is fine.',
                        },
                        {
                            'slug': 'twr-close-guarantee',
                            'title': 'try-with-resources contract',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The body of a try-with-resources block throws. The declared resource…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'is closed automatically, and the body exception propagates (with close errors suppressed onto it)', 'is_correct': True},
                                {'id': 'b', 'text': 'stays open — close skipped when throwing', 'is_correct': False},
                                {'id': 'c', 'text': 'is closed but the original exception is replaced by the close error', 'is_correct': False},
                                {'id': 'd', 'text': 'must be closed in a finally anyway', 'is_correct': False},
                            ],
                            'explain': 'Reverse-order close guaranteed; the BODY exception remains primary, close failures attach as suppressed.',
                        },
                        {
                            'slug': 'custom-exception-parent',
                            'title': 'Declaring your type',
                            'exercise_type': 'fill_blank',
                            'instructions': 'To make InsufficientFundsException a CHECKED exception, extend ____ (the class name, exact case — not RuntimeException).',
                            'xp_reward': 40,
                            'solution_code': 'Exception',
                            'explain': 'extends Exception = checked; extends RuntimeException = unchecked. The parent decides the category.',
                        },
                        {
                            'slug': 'message-quality',
                            'title': 'Best throw site',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which throw gives the most debuggable failure?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'throw new IllegalArgumentException("grade out of range: " + g)', 'is_correct': True},
                                {'id': 'b', 'text': 'throw new Exception()', 'is_correct': False},
                                {'id': 'c', 'text': 'throw new RuntimeException("error")', 'is_correct': False},
                                {'id': 'd', 'text': 'return -1; instead of throwing', 'is_correct': False},
                            ],
                            'explain': 'Precise type + the offending value: future-you reads logs at 2 a.m. and thanks this line.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 8 Quiz',
                    'slug': 'java-exceptions-quiz',
                    'objective': 'Check hierarchy fluency and handling decisions.',
                    'duration': 8,
                    'body': """# Chapter 8 Quiz

Six questions on the throwable tree, catch mechanics, throwing and
resource safety.""",
                    'exercises': [
                        {
                            'slug': 'q8-not-a-runtime-exception',
                            'title': 'Odd one out',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which is NOT a RuntimeException (unchecked)?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'IOException', 'is_correct': True},
                                {'id': 'b', 'text': 'NullPointerException', 'is_correct': False},
                                {'id': 'c', 'text': 'IllegalArgumentException', 'is_correct': False},
                                {'id': 'd', 'text': 'ArrayIndexOutOfBoundsException', 'is_correct': False},
                            ],
                            'explain': 'IOException hangs directly off Exception (checked) — the classic must-handle-or-declare one; b–d are unchecked siblings.',
                        },
                        {
                            'slug': 'q8-finally-exception',
                            'title': 'finally with no exception',
                            'exercise_type': 'multiple_select',
                            'instructions': 'finally executes its block…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'when try completes normally', 'is_correct': True},
                                {'id': 'b', 'text': 'when an exception was thrown and caught', 'is_correct': True},
                                {'id': 'c', 'text': 'when an exception was thrown and NOT caught (runs during unwinding)', 'is_correct': True},
                                {'id': 'd', 'text': 'only when an exception occurred', 'is_correct': False},
                            ],
                            'explain': 'always is the entire contract (exceptions: System.exit / power loss aside).',
                        },
                        {
                            'slug': 'q8-throws-clause',
                            'title': 'throws meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': '`void store() throws SQLException` promises…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'callers must handle SQLException or declare it onward', 'is_correct': True},
                                {'id': 'b', 'text': 'the method always throws', 'is_correct': False},
                                {'id': 'c', 'text': 'the method catches it internally', 'is_correct': False},
                                {'id': 'd', 'text': 'SQLException becomes unchecked', 'is_correct': False},
                            ],
                            'explain': 'throws is propagation permission, not a prediction — the compiler enforces it down the chain.',
                        },
                        {
                            'slug': 'q8-swallow-harm',
                            'title': 'Why swallowing hurts',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'catch (Exception e) { } with no action primarily risks…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'program continuing on state known to be broken, with no trace', 'is_correct': True},
                                {'id': 'b', 'text': 'slower compilation', 'is_correct': False},
                                {'id': 'c', 'text': 'the JVM retrying automatically', 'is_correct': False},
                                {'id': 'd', 'text': 'memory leaks from the exception object only', 'is_correct': False},
                            ],
                            'explain': 'The exception WAS the diagnosis; deleting it leaves the symptom to wander into production.',
                        },
                        {
                            'slug': 'q8-npe-prevention',
                            'title': 'Idiomatic NPE defence',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL legitimate habits to avoid NullPointerExceptions.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'guard: if (s != null) before use', 'is_correct': True},
                                {'id': 'b', 'text': 'flip equals to "literal".equals(maybeNull)', 'is_correct': True},
                                {'id': 'c', 'text': 'wrap every single statement in try/catch', 'is_correct': False},
                                {'id': 'd', 'text': 'return empty collections instead of null from methods', 'is_correct': True},
                            ],
                            'explain': 'try/catch-per-line treats prevention as cure — NPEs are guarded against, not harvested.',
                        },
                        {
                            'slug': 'q8-error-catch',
                            'title': 'Error policy',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'StackOverflowError should normally be handled by…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'fixing the runaway recursion — not by catching it', 'is_correct': True},
                                {'id': 'b', 'text': 'a try/catch around the recursive call', 'is_correct': False},
                                {'id': 'c', 'text': 'retrying once', 'is_correct': False},
                                {'id': 'd', 'text': 'declaring throws StackOverflowError', 'is_correct': False},
                            ],
                            'explain': 'Errors signal JVM-level collapse; catching them is emergency bandaid at best. (And unchecked Errors never need throws anyway.)',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 9 ════════════════════
        {
            'title': 'Collections Framework',
            'slug': 'java-collections',
            'description': 'ArrayList, HashMap, HashSet and friends: growable containers, generics, and picking the right one.',
            'lessons': [
                {
                    'title': 'Lists and Generics',
                    'slug': 'lists-generics',
                    'objective': 'Use ArrayList with wrapper types and generics; explain its costs vs arrays.',
                    'duration': 15,
                    'body': """# Containers that grow

Arrays are fixed (chapter 4). Real programs collect unknown counts —
that is the **collections framework**, headed by three interfaces:
`List` (ordered, duplicates), `Set` (unique), `Map` (keys→values,
next lesson).

```java
import java.util.ArrayList;
import java.util.List;

List<String> names = new ArrayList<>();     // the diamond: type from left side
names.add("Amina");
names.add("Bilal");
names.add(1, "Sana");        // insert AT index 1 — shifts the rest
names.get(0);                 // "Amina"
names.remove("Bilal");        // by value (true if it was present)
names.size();                 // 2 — method, unlike array .length
names.set(0, "Amina K");      // replace at index
```

Declare with the **interface on the left** (`List<String>`) and the
implementation on the right: swapping ArrayList for LinkedList later
touches one line, not the program.

## Generics, honestly
`ArrayList<String>` can only hold Strings — `names.add(42)` is a
compile error, and `String s = names.get(0)` needs no cast. Before
Java 5 ("raw" lists) the compiler trusted nothing and every get needed
a cast that could blow up at runtime; generics moved that checking to
compile time.

Primitives cannot be elements: `ArrayList<int>` ❌ — you hold
`Integer` (autoboxed, chapter 2's wrapper). The cost: boxing allocates
objects, so huge numeric arrays stay `int[]`.

## ArrayList vs LinkedList
| Operation | ArrayList | LinkedList |
|---|---|---|
| get(i) | O(1) | O(n) walk |
| add at end | ~O(1) amortised (doubling resize) | O(1) |
| add/remove in middle | O(n) shift | O(n) search, O(1) relink |
| memory per element | lean (contiguous refs) | heavy (2 pointers each) |

The honest verdict: LinkedList's O(1)-middle win needs you to already
BE at the node (Iterators); from scratch, ArrayList wins ~always, which
matches real codebases' dominance. DSA chapter 3 vs 4, packaged.

## Other List facts
- `Arrays.asList(1, 2, 3)` — fixed-size list backed by an array (add ❌
  UnsupportedOperationException); `new ArrayList<>(List.of(...))` for a
  growable copy. `List.of(...)` (Java 9+) is the immutable literal.
- Iterating: for-each, `for (String n : names)`, or indexed loop.
- `names.sort(null)` sorts in natural order (next lesson's Comparable).

## Common mistakes
- `names.size` (missing parens) — arrays and collections spell
  length differently, an exam favourite.
- Modifying a list DURING a for-each loop (structural change →
  ConcurrentModificationException; use removeIf or an Iterator).
- Storing ints in ArrayList expecting int[] performance.

## Lesson summary
List = growable indexed sequence; generics buy compile-time element
checking and cast-free gets; ArrayList is the default, LinkedList the
specialty; interface-typed variables keep options open.""",
                    'exercises': [
                        {
                            'slug': 'insert-shift-effect',
                            'title': 'add(index, x) effect',
                            'exercise_type': 'output_prediction',
                            'instructions': 'List starts [Amina, Bilal]; then names.add(1, "Sana"). What does System.out.println(names) print? (exactly as Java prints lists)',
                            'xp_reward': 40,
                            'expected_output': '[Amina, Sana, Bilal]',
                            'explain': 'Insert AT 1 pushes Bilal right — brackets with comma-space are ArrayList\u2019s toString shape.',
                        },
                        {
                            'slug': 'generic-promise',
                            'title': 'What generics enforce',
                            'exercise_type': 'multiple_select',
                            'instructions': 'With List<String> names, select ALL true outcomes.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'names.add(42) fails at compile time', 'is_correct': True},
                                {'id': 'b', 'text': 'names.get(0) needs no cast to String', 'is_correct': True},
                                {'id': 'c', 'text': 'the list is faster than raw lists', 'is_correct': False},
                                {'id': 'd', 'text': 'ArrayList<int> becomes legal', 'is_correct': False},
                            ],
                            'explain': 'Generics are compile-time safety — speed unchanged, primitives still need Integer boxing.',
                        },
                        {
                            'slug': 'arraylist-costs',
                            'title': 'Middle-insert cost',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inserting at index 0 of an n-element ArrayList costs…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'O(n) — every element shifts one slot right', 'is_correct': True},
                                {'id': 'b', 'text': 'O(1) — pointers do the work', 'is_correct': False},
                                {'id': 'c', 'text': 'O(log n) — it binary-searches the gap', 'is_correct': False},
                                {'id': 'd', 'text': 'O(n²) per insert', 'is_correct': False},
                            ],
                            'explain': 'Contiguity is the bargain: cheap get, expensive splice — DSA chapter 3 again.',
                        },
                        {
                            'slug': 'concurrent-modification',
                            'title': 'The for-each trap',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'for (String s : names) { if (s.isEmpty()) names.remove(s); } throws…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'ConcurrentModificationException — the list changed during iteration', 'is_correct': True},
                                {'id': 'b', 'text': 'NullPointerException', 'is_correct': False},
                                {'id': 'c', 'text': 'nothing; it removes correctly', 'is_correct': False},
                                {'id': 'd', 'text': 'compile error', 'is_correct': False},
                            ],
                            'explain': 'Use names.removeIf(String::isEmpty) (or an Iterator’s remove) — the loop detects the out-of-band edit.',
                        },
                    ],
                },
                {
                    'title': 'Maps and Sets',
                    'slug': 'maps-sets',
                    'objective': 'Store key→value pairs and unique elements with HashMap/HashSet.',
                    'duration': 15,
                    'body': """# Keyed lookup, uniqueness

```java
import java.util.HashMap;   // or Map, Set via interfaces
Map<String, Integer> marks = new HashMap<>();
marks.put("Amina", 91);
marks.put("Bilal", 74);
marks.put("Amina", 95);            // UPDATE: keys stay unique
marks.get("Amina");                // 95
marks.get("Ghost");                // null — absent key
marks.getOrDefault("Ghost", 0);   // 0 — the null-safe habit
marks.containsKey("Bilal");       // true
marks.size();                      // 2
marks.remove("Bilal");

for (Map.Entry<String, Integer> e : marks.entrySet()) {
    System.out.println(e.getKey() + " -> " + e.getValue());
}
for (String k : marks.keySet())      { … }   // keys only
for (Integer v : marks.values())     { … }   // values only
```

HashMap = the chapter-9-of-DSA hash table, industrial: expected O(1)
put/get, no order guarantee, keys SHOULD be immutable (a key whose
hashCode changes after insertion is unreachable — one of Java's
scariest silent bugs).

**Set** = Map's keys with nothing else: `HashSet<String> seen = new
HashSet<>(); seen.add("x")` returns **false** if already present —
dedup and "have I seen this?" in one call.

```java
List<Integer> nums = List.of(3, 1, 3, 2, 1);
Set<Integer> unique = new HashSet<>(nums);      // [1, 2, 3] any order
System.out.println(unique.size());              // 3
```

## Choosing from the family
| Need | Pick | Why |
|---|---|---|
| ordered duplicates, indexes | ArrayList | O(1) get |
| unique membership tests | HashSet | O(1) contains |
| key→value, fast get | HashMap | O(1) by key |
| keys in SORTED order | TreeMap / TreeSet | O(log n), red-black trees |
| insertion ORDER preserved | LinkedHashMap / LinkedHashSet | hash + list hybrid |

TreeMap bridges chapters: sorted keys, range views
(`tailMap(x)` = the "between X and Y" report from DSA's project,
free). HashMap order is unpredictable but O(1); do not "memorise"
a HashMap dump — a classic interview trap.

## Wrapper caution returns
`Map<int, …>` illegal — keys/values are objects: `Integer`. And
`Integer a = 200, b = 200; a == b` is false (pooled cache only −128…127):
**objects compare with equals, always.**

## Common mistakes
- get() then assume non-null — use getOrDefault or containsKey.
- Iterating a HashMap and claiming order (it has none).
- Mutating an object used as a key (breaks hashCode contract).
- new HashMap<>(someMap) thinking it deep-copies values (it copies
  references!).

## Lesson summary
HashMap: expected O(1), unordered, getOrDefault; HashSet: uniqueness
with O(1) contains; sorted/insertion-order cousins when the question
needs order.""",
                    'exercises': [
                        {
                            'slug': 'map-update-size',
                            'title': 'Put twice, size once',
                            'exercise_type': 'output_prediction',
                            'instructions': 'put("A",1); put("B",2); put("A",9); — map.size()? (number only)',
                            'xp_reward': 40,
                            'expected_output': '2',
                            'explain': 'Keys unique: second A updated value, not headcount. get("A") is 9.',
                        },
                        {
                            'slug': 'absent-key-null',
                            'title': 'Missing key result',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'HashMap<String,Integer> m without key "Ghost": m.get("Ghost") returns…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'null', 'is_correct': True},
                                {'id': 'b', 'text': '0', 'is_correct': False},
                                {'id': 'c', 'text': 'throws NoSuchElementException', 'is_correct': False},
                                {'id': 'd', 'text': 'empty string', 'is_correct': False},
                            ],
                            'explain': 'get answers null for absence (why getOrDefault exists). TreeMap/TreeSet also null-ish; only some APIs throw.',
                        },
                        {
                            'slug': 'set-dedup-count',
                            'title': 'HashSet arithmetic',
                            'exercise_type': 'output_prediction',
                            'instructions': 'new HashSet<>(List.of(1,2,2,3,3,3)).size()? (number only)',
                            'xp_reward': 40,
                            'expected_output': '3',
                            'explain': 'Uniqueness: one each of 1,2,3.',
                        },
                        {
                            'slug': 'choose-map-flavor',
                            'title': 'Sorted report tool',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A grade report must print keys A→Z and answer "range X–Y" efficiently:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'TreeMap — sorted keys, O(log n) navigation', 'is_correct': True},
                                {'id': 'b', 'text': 'HashMap — fastest lookups solve everything', 'is_correct': False},
                                {'id': 'c', 'text': 'LinkedHashMap — insertion order is alphabetical', 'is_correct': False},
                                {'id': 'd', 'text': 'ArrayList of pairs — sort before each query', 'is_correct': False},
                            ],
                            'explain': 'Sorted-key needs = tree maps: order and ranges are their advertised feature.',
                        },
                        {
                            'slug': 'hashmap-order-trap',
                            'title': 'Iteration truth',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'HashMap iteration order is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'unspecified — depends on hashes and capacity, never rely on it', 'is_correct': True},
                                {'id': 'b', 'text': 'insertion order', 'is_correct': False},
                                {'id': 'c', 'text': 'sorted key order', 'is_correct': False},
                                {'id': 'd', 'text': 'reverse insertion', 'is_correct': False},
                            ],
                            'explain': 'b is LinkedHashMap, c is TreeMap — three maps, three orders, one classic interview discriminator.',
                        },
                    ],
                },
                {
                    'title': 'Sorting Collections',
                    'slug': 'sorting-collections',
                    'objective': 'Sort with Comparable and Comparator, including custom orders.',
                    'duration': 12,
                    'body': """# Ordering things on purpose

```java
List<String> names = new ArrayList<>(List.of("Sana", "Amina", "Bilal"));
names.sort(null);                     // natural order: String.compareTo

List<Integer> nums = new ArrayList<>(List.of(5, 3, 9));
nums.sort(Comparator.naturalOrder());
nums.sort(Comparator.reverseOrder()); // 9, 5, 3
```

## Comparable: a class's DEFAULT ranking
```java
public class Student implements Comparable<Student> {
    public int compareTo(Student other) {
        return Double.compare(grade, other.grade);   // ascending
    }
}
```

`Collections.sort(roster)` now works on Students with no extra
arguments: natural order = the compareTo you signed. Use
`Double.compare`/`Integer.compare`, not subtraction —
`a - b` overflows on extreme ints (the same overflow lesson from
binary-search midpoints). String's `compareTo` is
lexicographic: `"apple".compareTo("Banana")` > 0 because
uppercase letters precede lowercase in Unicode — case matters, so
compare `String.CASE_INSENSITIVE_ORDER` or fold case first.

## Comparator: ad-hoc second orders
```java
byName = Comparator.comparing(s -> s.name);
byGradeDesc = Comparator.comparingDouble((Student s) -> s.grade).reversed();
byThen = byGradeDesc.thenComparing(byName);     // ties broken by name
roster.sort(byThen);
```

A class can have ONE natural order but unlimited Comparators — grade
rank today, name rank tomorrow, no class edits. (Chapter 7's honor-roll
tie logic in library form.)

## Binary searching sorted lists
```java
int at = Collections.binarySearch(orderedNames, "Sana");
// >= 0: index found; < 0: insertion point, -(pos+1) — like Arrays' helper
```

Requires sortedness (the precondition repeats everywhere in this
syllabus for a reason).

## Common mistakes
- Sorting and then mutating list contents in place (order silently
  breaks — binarySearch starts lying).
- compareTo that treats different values as equal inconsistently with
  equals — TreeSet then "loses" elements.
- Comparator subtracting doubles/ints for ordering (overflow/precision
  — use compare).
- Forgetting List.of(...) is IMMUTABLE: sort throws
  UnsupportedOperationException — wrap in new ArrayList<>(...).

## Lesson summary
Comparable = one natural order via compareTo; Comparator = unlimited
ad-hoc orders with chaining; binarySearch inherits the sorted-data
contract.""",
                    'exercises': [
                        {
                            'slug': 'comparator-reverse-output',
                            'title': 'Reverse order output',
                            'exercise_type': 'output_prediction',
                            'instructions': 'nums [5,3,9] sorted with Comparator.reverseOrder(); println(nums)? (Java list format)',
                            'xp_reward': 40,
                            'expected_output': '[9, 5, 3]',
                            'explain': 'Descending: 9,5,3 — brackets and comma-space from ArrayList.toString.',
                        },
                        {
                            'slug': 'case-compare-trap',
                            'title': 'Uppercase first',
                            'exercise_type': 'multiple_choice',
                            'instructions': '"apple".compareTo("Banana") is…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'positive — all lowercase letters sort after uppercase ones', 'is_correct': True},
                                {'id': 'b', 'text': 'negative — a < b alphabetically', 'is_correct': False},
                                {'id': 'c', 'text': '0', 'is_correct': False},
                                {'id': 'd', 'text': 'compile error', 'is_correct': False},
                            ],
                            'explain': 'Unicode puts A–Z before a–z: "B" (66) < "a" (97) — case-insensitive comparators exist because nobody wants this by default.',
                        },
                        {
                            'slug': 'immutable-list-sort',
                            'title': 'List.of sorting',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'List.of(3,1,2).sort(null) …',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'throws UnsupportedOperationException — immutable lists refuse edits', 'is_correct': True},
                                {'id': 'b', 'text': 'sorts fine', 'is_correct': False},
                                {'id': 'c', 'text': 'compile error', 'is_correct': False},
                                {'id': 'd', 'text': 'returns a new sorted list', 'is_correct': False},
                            ],
                            'explain': 'Immutability enforced at runtime for interface-legal calls; copy first: new ArrayList<>(List.of(...)).',
                        },
                        {
                            'slug': 'then-comparing-chain',
                            'title': 'Tie-break chain',
                            'exercise_type': 'multiple_select',
                            'instructions': 'gradeDesc.thenComparing(byName) guarantees…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'higher grades come first', 'is_correct': True},
                                {'id': 'b', 'text': 'equal grades are alphabetically ordered by name', 'is_correct': True},
                                {'id': 'c', 'text': 'names sort before grades globally', 'is_correct': False},
                                {'id': 'd', 'text': 'the original list class changed source code', 'is_correct': False},
                            ],
                            'explain': 'thenComparing only activates on TIES of the first comparator — the honor-roll rule as one expression.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 9 Quiz',
                    'slug': 'java-collections-quiz',
                    'objective': 'Check list/map/set mechanics and choice reasoning.',
                    'duration': 8,
                    'body': """# Chapter 9 Quiz

Six questions on the framework: choosing containers, generics law and
ordering.""",
                    'exercises': [
                        {
                            'slug': 'q9-unique-tool',
                            'title': 'Uniqueness enforcer',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Track distinct visitor IPs, fastest "have I seen this?" check:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'HashSet', 'is_correct': True},
                                {'id': 'b', 'text': 'ArrayList + contains', 'is_correct': False},
                                {'id': 'c', 'text': 'LinkedList', 'is_correct': False},
                                {'id': 'd', 'text': 'TreeMap', 'is_correct': False},
                            ],
                            'explain': 'contains on ArrayList is O(n) per visit; HashSet makes it O(1) and enforces uniqueness by nature.',
                        },
                        {
                            'slug': 'q9-diamond',
                            'title': 'Diamond meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Map<String, Integer> m = new HashMap<>(); the <> on the right…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'infers the type arguments from the left-hand declaration', 'is_correct': True},
                                {'id': 'b', 'text': 'creates a raw untyped map', 'is_correct': False},
                                {'id': 'c', 'text': 'allows any key type later', 'is_correct': False},
                                {'id': 'd', 'text': 'is shorthand for Object,Object', 'is_correct': False},
                            ],
                            'explain': 'Java 7 diamond inference — writing the types twice was the pre-Java-7 ritual it replaced.',
                        },
                        {
                            'slug': 'q9-entryset-job',
                            'title': 'entrySet purpose',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Iterating BOTH keys and values uses for (Map.Entry<K,V> e : m.____()) — method name, camelCase lowercase start.',
                            'xp_reward': 40,
                            'solution_code': 'entrySet',
                            'explain': 'entrySet() — keySet()+get(key) per round also works but re-hashes; entrySet is the efficient pair view.',
                        },
                        {
                            'slug': 'q9-integer-cache',
                            'title': 'Boxed equality',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Integer a = 200, b = 200: a == b and a.equals(b) report…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'false, true', 'is_correct': True},
                                {'id': 'b', 'text': 'true, true', 'is_correct': False},
                                {'id': 'c', 'text': 'false, false', 'is_correct': False},
                                {'id': 'd', 'text': 'true, false', 'is_correct': False},
                            ],
                            'explain': 'The −128..127 interning cache makes small == tests lie usefully; 200s expose it — another proof objects compare with equals.',
                        },
                        {
                            'slug': 'q9-comparable-count',
                            'title': 'Natural orders per class',
                            'exercise_type': 'fill_blank',
                            'instructions': 'A class may implement Comparable<ItsOwnType> how many times? (spelled-out digit, lowercase)',
                            'xp_reward': 40,
                            'solution_code': 'one',
                            'explain': 'One natural order; every other ranking is a Comparator.',
                        },
                        {
                            'slug': 'q9-list-vs-array-shape',
                            'title': 'Growth mechanics',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about ArrayList growth.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'It resizes by allocating a bigger array and copying', 'is_correct': True},
                                {'id': 'b', 'text': 'Append cost amortises to O(1) because resizes double', 'is_correct': True},
                                {'id': 'c', 'text': 'It stores primitive ints directly with no boxing', 'is_correct': False},
                                {'id': 'd', 'text': 'It can hold null elements', 'is_correct': True},
                            ],
                            'explain': 'The doubling amortisation argument is exactly the DSA course\u2019s dynamic-array analysis.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 10 ════════════════════
        {
            'title': 'File Handling and Packages',
            'slug': 'java-files-packages',
            'description': 'Read and write files safely, organise code into packages, and use the classpath.',
            'lessons': [
                {
                    'title': 'Reading and Writing Files',
                    'slug': 'file-io',
                    'objective': 'Use Files, Paths, BufferedReader and PrintWriter to persist data.',
                    'duration': 15,
                    'body': r"""# Talking to the disk

Everything so far lived in RAM — when the JVM exits, the data vanishes.
**File handling** is how a program makes data survive. Java splits file
work into two families:

1. **NIO.2 one-liners** (`java.nio.file`): `Files.readString`, `Files.writeString`,
   `Files.readAllLines` — tiny helpers for whole-file work.
2. **Streams and readers** (`java.io`): `BufferedReader`, `PrintWriter`,
   `FileInputStream` — byte-by-byte / line-by-line work for large files.

## Reading a whole file (the modern way)

```java
import java.nio.file.*;
import java.io.IOException;

public class ReadNote {
    public static void main(String[] args) throws IOException {
        Path p = Paths.get("note.txt");
        String content = Files.readString(p);   // whole file as one String
        System.out.println(content);
    }
}
```

Line by line: `Files.readString(p)` loads the entire file. If `note.txt`
does not exist, an `IOException` (specifically `NoSuchFileException`) is
thrown — that is why `main` declares `throws IOException`. Unhandled I/O
errors stop the program, exactly like any uncaught exception.

## Writing a whole file

```java
Files.writeString(p, "saved at exit\n");            // overwrites
Files.writeString(p, "another line\n", StandardOpenOption.APPEND);
```

`writeString` replaces the file by default; pass `APPEND` to add to it.
Choosing overwrite vs append wrong is the #1 data-loss bug in student
projects — decide explicitly every time.

## Line-by-line with BufferedReader

For a file you must process without loading fully:

```java
try (BufferedReader br = Files.newBufferedReader(Paths.get("marks.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {   // null marks end of file
        System.out.println(line.toUpperCase());
    }
}   // br.close() runs automatically — try-with-resources
```

`readLine()` returns one line, or `null` when the stream is exhausted —
the classic sentinel-terminated loop. The `try (...)` header guarantees
the file handle is closed even if an exception is thrown mid-read; a
leaked handle can lock the file and exhaust OS resources.

## Expected behaviour
Given `marks.txt` containing `ali 45` and `sara 52` on two lines, the
loop prints `ALI 45` then `SARA 52`, and the file is closed for you.

## Common mistakes
- Calling `Files.readString` on a huge log file and wondering why the
  program runs out of heap. Stream large files line by line.
- Forgetting to close readers/writers when NOT using try-with-resources —
  buffered output may never reach the disk. Always prefer the `try (...)`
  form.
- Using `\\` in Windows paths inside a normal string. `"data\notes.txt"`
  is a compile error (`\n` escape!); write `"data\\notes.txt"` or use
  `Paths.get("data", "notes.txt")`, which is portable.

## Lesson summary
Whole files: `Files.readString` / `Files.writeString` (with `APPEND` to
add). Big files: `BufferedReader.readLine()` in a loop until `null`,
inside try-with-resources so handles always close. Every read can throw
`IOException` — handle it or declare it.""",
                    'exercises': [
                        {
                            'slug': 'readwhole-method',
                            'title': 'Whole-file read',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which call returns an entire UTF-8 text file as one String?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Files.readString(path)', 'is_correct': True},
                                {'id': 'b', 'text': 'Files.readLine(path)', 'is_correct': False},
                                {'id': 'c', 'text': 'new String(path.getContent())', 'is_correct': False},
                                {'id': 'd', 'text': 'Files.open(path)', 'is_correct': False},
                            ],
                            'explain': 'NIO.2 added readString/writeString in Java 11 for one-call whole-file text I/O.',
                        },
                        {
                            'slug': 'append-flag',
                            'title': 'Not overwriting',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'By default Files.writeString(p, text) ___. To add instead, pass which option?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'overwrites the file; StandardOpenOption.APPEND', 'is_correct': True},
                                {'id': 'b', 'text': 'appends; no option needed', 'is_correct': False},
                                {'id': 'c', 'text': 'overwrites; StandardOpenOption.CREATE', 'is_correct': False},
                                {'id': 'd', 'text': 'throws if the file exists; READ_ONLY', 'is_correct': False},
                            ],
                            'explain': 'CREATE makes the file if missing; APPEND adds to the end. Default truncates.',
                        },
                        {
                            'slug': 'readline-sentinel',
                            'title': 'End-of-file sentinel',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'In the loop  while ((line = br.readLine()) != __) { ... }  '
                                'which value signals end of file? Answer with the exact Java literal '
                                '(lower-case, five letters).'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'null',
                            'explain': 'readLine() returns null once the stream is exhausted.',
                        },
                        {
                            'slug': 'twr-why',
                            'title': 'Why try-with-resources',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about  try (BufferedReader br = ...) { }.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'br.close() runs automatically when the block exits', 'is_correct': True},
                                {'id': 'b', 'text': 'close() runs even if an exception is thrown inside', 'is_correct': True},
                                {'id': 'c', 'text': 'br can still be used normally after the block', 'is_correct': False},
                                {'id': 'd', 'text': 'It removes the need for a manual close in a finally block', 'is_correct': True},
                            ],
                            'explain': 'The resource is closed and unusable afterwards — that guarantee is the whole point.',
                        },
                    ],
                },
                {
                    'title': 'File and Path API Essentials',
                    'slug': 'path-api',
                    'objective': 'Inspect and manage files with Path, exists, create, delete, copy.',
                    'duration': 12,
                    'body': r"""# Paths, not just strings

A `Path` is an object-oriented handle on a location in a file system —
built from strings but parsed correctly for your OS:

```java
Path p = Paths.get("reports", "2026", "jan.txt");  // reports/2026/jan.txt
p.getFileName();          // jan.txt
p.getParent();            // reports/2026
p.startsWith("reports");  // true
p.toAbsolutePath();       // C:\Users\you\CodeYaar\reports\2026\jan.txt
```

Building paths from parts (`Paths.get("a", "b")`) instead of hand-writing
`"a\\b"` or `"a/b"` is what makes the same code work on Windows, Linux
and macOS. Relative paths resolve against the **working directory** —
where you launched the JVM — which is why a file "exists but my program
can\'t find it": it was looking somewhere else.

## The handy static methods on Files

```java
Files.exists(p);                          // boolean
Files.createDirectories(p.getParent());   // mkdir -p
Files.createFile(p);                      // touch (fails if exists)
Files.delete(p);                          // fails if missing
Files.copy(src, dst, StandardCopyOption.REPLACE_EXISTING);
Files.size(p);                            // bytes
```

`createDirectories` creates every missing parent (like `mkdir -p`);
`createFile` is the equivalent of `touch` but throws
`FileAlreadyExistsException` if the name is taken. `delete` throws
`NoSuchFileException` on a missing file — check with `Files.exists` or
use `Files.deleteIfExists`, which returns a boolean instead.

## Serialization bonus: objects to bytes

A class marked `implements Serializable` can be written whole:

```java
try (ObjectOutputStream out = new ObjectOutputStream(
        new FileOutputStream("student.dat"))) {
    out.writeObject(new Student("Amina", 3.6));   // object -> bytes
}
```

`readObject()` reverses it. The fields travel, methods do not, and if the
class changes shape the stored bytes may no longer load — plain text CSV
is usually the more robust student-project choice.

## Common mistakes
- Assuming a relative path points at the `.java` file. It points at the
  working directory of the JVM. Print `Path.of("").toAbsolutePath()` to
  see where you really are.
- Calling `Files.delete` without checking existence, then catching an
  unexpected exception. Use `deleteIfExists` for idempotent cleanup.
- Serialising classes you later edit, then blaming Java when old `.dat`
  files refuse to load.

## Lesson summary
Compose paths with `Paths.get(part, part…)` for portability, manage
files with `Files.exists/create/copy/delete`, and treat serialization as
a fragile convenience — text formats survive refactors better.""",
                    'exercises': [
                        {
                            'slug': 'path-parts-portable',
                            'title': 'Portable path building',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which creates data/notes.txt that works on Windows AND Linux?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Paths.get("data", "notes.txt")', 'is_correct': True},
                                {'id': 'b', 'text': 'Paths.get("data\\notes.txt")', 'is_correct': False},
                                {'id': 'c', 'text': 'Paths.get("data//notes.txt")', 'is_correct': False},
                                {'id': 'd', 'text': 'new Path("data", "notes.txt")', 'is_correct': False},
                            ],
                            'explain': 'Paths joins the parts with the OS-correct separator; \"Path\" is an interface so you cannot new it.',
                        },
                        {
                            'slug': 'mkdir-p-method',
                            'title': 'Create nested folders',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which creates the folders a/b/c including every missing parent?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Files.createDirectories(Paths.get("a","b","c"))', 'is_correct': True},
                                {'id': 'b', 'text': 'Files.createDirectory(...) on the full path', 'is_correct': False},
                                {'id': 'c', 'text': 'Files.makePath(...)', 'is_correct': False},
                                {'id': 'd', 'text': 'Paths.mkdirAll(...)', 'is_correct': False},
                            ],
                            'explain': 'createDirectory (singular) fails if the parent is missing — the plural form is the mkdir -p.',
                        },
                        {
                            'slug': 'delete-safe',
                            'title': 'Quiet cleanup',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Delete a temp file without exploding when it is already gone:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Files.deleteIfExists(p)', 'is_correct': True},
                                {'id': 'b', 'text': 'Files.delete(p)', 'is_correct': False},
                                {'id': 'c', 'text': 'Files.remove(p)', 'is_correct': False},
                                {'id': 'd', 'text': 'p.delete()', 'is_correct': False},
                            ],
                            'explain': 'delete() throws NoSuchFileException; deleteIfExists returns false instead.',
                        },
                        {
                            'slug': 'serialisable-what-travels',
                            'title': 'Serialization scope',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Writing a Serializable object with ObjectOutputStream stores ALL of:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The values of its non-transient instance fields', 'is_correct': True},
                                {'id': 'b', 'text': 'Its methods\u2019 bytecode', 'is_correct': False},
                                {'id': 'c', 'text': 'Static fields', 'is_correct': False},
                                {'id': 'd', 'text': 'Enough type info to cast back on readObject()', 'is_correct': True},
                            ],
                            'explain': 'Code lives in the .class files; serialization is about an object\u2019s state only (minus static/transient).',
                        },
                    ],
                },
                {
                    'title': 'Packages, Access Control and the Classpath',
                    'slug': 'packages-classpath',
                    'objective': 'Organise classes into packages, apply access modifiers, compile with -d and run with -cp.',
                    'duration': 15,
                    'body': r"""# Packages = folders with a name contract

A **package** groups related classes and prevents name collisions —
`com.school.reports.Student` vs `com.shop.inventory.Student`. The first
line of the file declares the package; the folder layout on disk must
mirror it exactly:

```
src/
  com/school/reports/Report.java     -> package com.school.reports;
  com/school/students/Student.java   -> package com.school.students;
  Main.java                          -> (default package, avoid in real projects)
```

Using a class from another package requires an `import` (or a fully
qualified name every time):

```java
import com.school.students.Student;    // once at top
import com.school.students.*;          // whole package (prefer specific)
```

`import` does NOT copy anything — it is a shortcut that lets you write
`Student` instead of `com.school.students.Student`. `java.lang` is
imported automatically (that is why `String` needs no import).

## Access modifiers: who can see what

| Modifier | class | same package | subclass | everywhere |
|---|---|---|---|---|
| `private` | yes | no | no | no |
| (default / package-private) | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

Defaulting fields to `private` with getters/setters is the encapsulation
rule from chapter 7 — packages exist so that *inside* a module classes
can share package-private helpers while the module\u2019s public API stays small.

## Compiling across packages

Plain `javac Main.java` cannot resolve `import com.school...` — the
compiler finds classes by mapping package names to folders on a
**classpath**:

```bash
javac -d out src/com/school/students/Student.java src/com/school/reports/Report.java Main.java
java -cp out Main
```

- `-d out` writes `.class` files into `out/`, recreating the package
  folder structure (`out/com/school/students/Student.class`).
- `-cp out` (classpath) tells the JVM where to search: starting at `out`,
  `com.school.students.Student` resolves to
  `out/com/school/students/Student.class`.

Get either wrong and you meet the two famous errors:
`package com.school.students does not exist` (compiler could not find
sources) and `ClassNotFoundException` / `NoClassDefFoundError` (runtime
could not find the `.class`).

## Jar files

`jar cfe school.jar Main -C out .` bundles the compiled tree into one
file; `java -jar school.jar` runs it (`e` = entry point). Libraries you
add later (JUnit, drivers) are just jars on your classpath.

## Common mistakes
- Moving a `.java` file without updating its `package` line, or vice
  versa — the mirror rule is enforced by tools, not suggestions.
- Using `import` and still writing the fully qualified name; either
  style works, mixing is noise.
- Running `java Main` from inside the folder instead of the classpath
  root: `java` expects `java -cp <root> com.school.Main`.

## Lesson summary
Packages mirror folders, imports are name shortcuts, the four access
levels gate visibility, and `-d`/`-cp` keep compile-time and run-time
class lookup pointed at the same tree.""",
                    'exercises': [
                        {
                            'slug': 'package-folder-mirror',
                            'title': 'Mirror rule',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A file says  package com.school.reports;  Where must it sit relative to the source root?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'com/school/reports/ as the folders say', 'is_correct': True},
                                {'id': 'b', 'text': 'Anywhere \u2014 the package line is just a label', 'is_correct': False},
                                {'id': 'c', 'text': 'In the source root, package only matters for jars', 'is_correct': False},
                                {'id': 'd', 'text': 'In a folder named after the class', 'is_correct': False},
                            ],
                            'explain': 'Tooling locates classes by package name, so folder structure must match it exactly.',
                        },
                        {
                            'slug': 'implicit-import',
                            'title': 'Free import',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which package is imported automatically into every Java file?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'java.lang', 'is_correct': True},
                                {'id': 'b', 'text': 'java.util', 'is_correct': False},
                                {'id': 'c', 'text': 'java.io', 'is_correct': False},
                                {'id': 'd', 'text': 'java.core', 'is_correct': False},
                            ],
                            'explain': 'String, System, Math all live in java.lang \u2014 no import needed.',
                        },
                        {
                            'slug': 'widest-access',
                            'title': 'Visibility order',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct statements about access levels.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'protected is wider than package-private', 'is_correct': True},
                                {'id': 'b', 'text': 'private members are visible to subclasses', 'is_correct': False},
                                {'id': 'c', 'text': 'package-private is the default when you write no modifier', 'is_correct': True},
                                {'id': 'd', 'text': 'public is the widest level', 'is_correct': True},
                            ],
                            'explain': 'Order: private < package-private < protected < public. Subclasses do NOT see private.',
                        },
                        {
                            'slug': 'classpath-flag',
                            'title': 'Where to look',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'To run  java Main  with compiled classes living in folder  out , '
                                'the command is  java __ out Main  \u2014 which two-letter flag (with dash) '
                                'sets the classpath? Answer exactly, lower-case, with the leading dash.'
                            ),
                            'xp_reward': 40,
                            'solution_code': '-cp',
                            'explain': '-cp (or -classpath) points the JVM at the root of the class tree.',
                        },
                        {
                            'slug': 'missing-class-error',
                            'title': 'Runtime vs compile failure',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Compilation succeeded but  java -cp out Main  cannot find class Main. Which error?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'ClassNotFoundException (wrapped in ErrorOnMainThread / NoClassDefFoundError)', 'is_correct': True},
                                {'id': 'b', 'text': 'package Main does not exist', 'is_correct': False},
                                {'id': 'c', 'text': 'NullPointerException', 'is_correct': False},
                                {'id': 'd', 'text': 'IOException', 'is_correct': False},
                            ],
                            'explain': '"does not exist" is the compiler complaining; the JVM answer is ClassNotFound/NoClassDefFound \u2014 wrong classpath root.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 10 Quiz',
                    'slug': 'java-files-packages-quiz',
                    'objective': 'Check mastery of file I/O, Path API, packages and classpath.',
                    'duration': 10,
                    'body': """# Chapter 10 quiz

Five questions on files, paths, packages and the classpath. Answer from
what the lessons covered \u2014 read the explanations afterwards either way.""",
                    'exercises': [
                        {
                            'slug': 'q10-append-vs-create',
                            'title': 'Write options',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which keeps existing content and adds to the end of the file?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'StandardOpenOption.APPEND', 'is_correct': True},
                                {'id': 'b', 'text': 'StandardOpenOption.TRUNCATE_EXISTING', 'is_correct': False},
                                {'id': 'c', 'text': 'StandardOpenOption.READ', 'is_correct': False},
                                {'id': 'd', 'text': 'Files.addLine()', 'is_correct': False},
                            ],
                            'explain': 'TRUNCATE_EXISTING (the default with CREATE) wipes; APPEND keeps and adds.',
                        },
                        {
                            'slug': 'q10-works-everywhere',
                            'title': 'private scope',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Class A has private int x. Class B (same package) does  new A().x = 5;  What happens?',
                            'xp_reward': 50,
                            'expected_output': 'compile error',
                            'choices': [],
                            'explain': 'private means ONLY inside the declaring class \u2014 same package does not help.',
                        },
                        {
                            'slug': 'q10-readline-null',
                            'title': 'Loop terminator',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In line-by-line reading, the signal that the file has ended is readLine() returning:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'null', 'is_correct': True},
                                {'id': 'b', 'text': 'empty string', 'is_correct': False},
                                {'id': 'c', 'text': '-1', 'is_correct': False},
                                {'id': 'd', 'text': '"EOF"', 'is_correct': False},
                            ],
                            'explain': 'Empty string means a blank line \u2014 still data. Only null means no more lines.',
                        },
                        {
                            'slug': 'q10-d-flag',
                            'title': 'javac output',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In  javac -d out ...  what does -d control?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Where .class files are written, mirroring packages', 'is_correct': True},
                                {'id': 'b', 'text': 'Which source files to delete after compiling', 'is_correct': False},
                                {'id': 'c', 'text': 'The debug level of the compiler', 'is_correct': False},
                                {'id': 'd', 'text': 'The maximum class-file size', 'is_correct': False},
                            ],
                            'explain': '-d builds the package folder tree under the destination; -cp later points at its root.',
                        },
                        {
                            'slug': 'q10-jar-run',
                            'title': 'Running a jar',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'The flag used in  java __ app.jar  to run a jar\u2019s declared main class '
                                'is which two-letter flag? Answer exactly, lower-case, with a plain ASCII dash.'
                            ),
                            'xp_reward': 50,
                            'solution_code': '-jar',
                            'explain': 'jar cfe sets the entry point; java -jar executes the archive.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 11 ════════════════════
        {
            'title': 'Final Project: Library Management System',
            'slug': 'java-final-project',
            'description': 'Combine OOP, collections, exceptions and file I/O into a console Library Management System with a grading rubric.',
            'lessons': [
                {
                    'title': 'The Brief: Library Management System',
                    'slug': 'lms-brief',
                    'objective': 'Understand the requirements, data model and menu contract of the project.',
                    'duration': 12,
                    'body': r"""# What you are building

A console application a small library can actually run: the clerk adds
books, members borrow and return them, overdue days are reported, and
everything survives a restart because it is saved to a text file. This
is the exact shape of the "Console-Based Student Management System"
family of student projects — swap the entity and the same design works.

## Functional requirements

1. **Books** — title, author, ISBN, total copies, available copies.
2. **Members** — member ID, name, list of currently borrowed ISBNs.
3. **Borrow** — by ISBN; fails with a clear message if none available.
4. **Return** — records the return; computes days kept.
5. **Search** — by title (case-insensitive substring) and by author.
6. **Report** — count of overdue loans (kept longer than 14 days).
7. **Persistence** — on every mutation, save `books.txt` and
   `members.txt`; load them at startup. A missing file is fine (empty
   library); a corrupt line is skipped with a warning, not a crash.

## The data model (decide this first)

```
Book        { String isbn, title, author; int total, available; }
Member      { int id; String name; List<String> borrowed; }
Loan        { String isbn; int memberId; LocalDate borrowedOn; }
Library     { Map<String,Book> books; Map<Integer,Member> members; List<Loan> loans; }
```

`Library` is the service class everything else talks to — the "god
object" of the app, deliberately kept to one file. ISBN is the natural
key, hence `HashMap<String, Book>`: O(1) lookup for borrow/return, while
search scans values (chapter-9 trade-off: indexes optimise one question,
scans answer any question).

## The menu contract (test against this!)

```
1) Add book  2) Register member  3) Borrow  4) Return
5) Search    6) Overdue report   7) Save    8) Exit
Choice: 3
ISBN to borrow: 978-1
Borrowed for member #4. 0 copies left.
```

Every invalid input (bad number, unknown ISBN, no copies) must print a
friendly one-line message and return to the menu — the program must
never show a stack trace to the clerk. That is the exception-handling
requirement in practice.

## Persistence format (keep it dead simple)

One record per line, fields separated by `|`:

```
978-1|Clean Code|Robert Martin|3|2
4|Amina|978-1,978-2
```

Split with `line.split("\\|")`, join with a small `toLine()` method on
each class. Text beats serialization here: you can open the file, spot
the corruption, and the format survives you editing the classes.

## Common mistakes
- Starting with the menu loop. Start with the classes and their
  `toLine()`/`fromLine()` — the UI is the last 10%.
- Letting `available` drift from the truth by updating it in two places.
  Borrow/return should go through exactly one method that touches both
  the counter and the loan list.
- Saving only at Exit. A crash then eats the whole session; save on
  every mutation (or at least every borrow/return).

## Lesson summary
Three entity classes plus a Library service, HashMaps for the primary
lookups, a pipe-delimited text format for persistence, and a menu loop
that treats every bad input as a handled case.""",
                    'exercises': [
                        {
                            'slug': 'lms-why-hashmap',
                            'title': 'Structure choice',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL good reasons books are stored in a HashMap keyed by ISBN.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Borrow/return need O(1) lookup by ISBN', 'is_correct': True},
                                {'id': 'b', 'text': 'ISBN uniqueness is enforced by the map keys', 'is_correct': True},
                                {'id': 'c', 'text': 'It keeps books sorted by title automatically', 'is_correct': False},
                                {'id': 'd', 'text': 'It uses less memory than any ArrayList', 'is_correct': False},
                            ],
                            'explain': 'HashMap gives fast keyed access and duplicate protection \u2014 but no order and real memory overhead.',
                        },
                        {
                            'slug': 'lms-corrupt-line',
                            'title': 'Loading policy',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A saved line has 2 fields instead of 5. The required behaviour is:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Skip it, warn, keep loading the rest', 'is_correct': True},
                                {'id': 'b', 'text': 'Throw and abort startup', 'is_correct': False},
                                {'id': 'c', 'text': 'Silently pad missing fields with defaults', 'is_correct': False},
                                {'id': 'd', 'text': 'Rewrite the whole file as empty', 'is_correct': False},
                            ],
                            'explain': 'The brief says one bad line must not crash the app \u2014 catch, warn, continue.',
                        },
                        {
                            'slug': 'lms-split-regex',
                            'title': 'The escape in split',
                            'exercise_type': 'output_prediction',
                            'instructions': 'String[] f = "978-1|Clean Code|Robert Martin|3|2".split("\\\\|");  What is f.length?',
                            'xp_reward': 40,
                            'expected_output': '5',
                            'choices': [],
                            'explain': 'split takes a REGEX; \\\\| (regex \"escaped pipe\") splits on the literal | into 5 fields.',
                        },
                    ],
                },
                {
                    'title': 'Building It: Step-by-Step Plan',
                    'slug': 'lms-build-plan',
                    'objective': 'Follow a six-stage build order with checkpoints you can test at each stage.',
                    'duration': 15,
                    'body': r"""# Ship it in six stages

Each stage ends with something runnable — never write all five classes
then hit compile for the first time.

## Stage 1 — entities (≈1 hour)
`Book`, `Member`, `Loan`: private fields, constructor, getters,
`toString()`, `toLine()`, and a static `fromLine(String)` that throws
`IllegalArgumentException` on a malformed line. **Checkpoint:** a `main`
that builds three Books, prints `toLine()`, reads each back with
`fromLine()` and compares.

## Stage 2 — the Library service (≈1.5 hours)
```java
public class Library {
    private final Map<String, Book> books = new HashMap<>();
    private final Map<Integer, Member> members = new HashMap<>();
    private final List<Loan> loans = new ArrayList<>();

    public void addBook(Book b)    { if (books.containsKey(b.getIsbn()))
        throw new DuplicateIsbnException(b.getIsbn()); books.put(...); }
    public void borrow(String isbn, int memberId) { /* lookup both,
        check available > 0, decrement, add Loan, add to member */ }
    public int returnBook(String isbn, int memberId) { /* find loan,
        increment available, remove, return days kept */ }
    public List<Book> searchByTitle(String q) { /* values(), case-insensitive contains */ }
    public List<Loan> overdue(int daysAllowed) { /* loans where borrowedOn older than cutoff */ }
}
```
Custom `DuplicateIsbnException extends RuntimeException` — chapter 8.
**Checkpoint:** a test `main` that borrows, returns, and asserts
available counts and the overdue list with fixed dates.

## Stage 3 — persistence (≈1 hour)
`save(Library, dir)` writes both files (one `toLine()` per record,
try-with-resources `PrintWriter`); `load(dir)` returns a fresh Library,
wrapping `fromLine` failures in a skip-and-warn loop. **Checkpoint:**
run, add data, Exit, re-run — data survives. Edit one line to garbage
and confirm the warning + graceful load.

## Stage 4 — the menu (≈1 hour)
A `while (true)` loop over a `Scanner`: read choice, dispatch to
Library methods, print one-line results. Wrap the body in
`try { ... } catch (LibraryException | InputMismatchException e) {
System.out.println("✗ " + e.getMessage()); }` so bad input loops back.
**Checkpoint:** walk the full happy path AND every error message by hand.

## Stage 5 — polish (≈30 min)
Menu formatting, `search` by author too, a "list all books" view,
confirm-before-exit if there are unsaved changes.

## Stage 6 — self-test with the rubric below
Grind every rubric row against your own program before submitting.

## Line-by-line focus: returnBook
The trickiest method because it must keep three structures in sync:
find the `Loan` (or throw `NotBorrowedException`), remove it from
`loans`, remove the ISBN from the member\u2019s `borrowed` list, increment
`available`, return `ChronoUnit.DAYS.between(loan.getBorrowedOn(),
LocalDate.now())`. Miss one of the five steps and the library slowly
lies to itself.

## Common mistakes
- Mutating `available` from the UI instead of inside the service —
  invisible desync bugs. Rule: only Library methods touch state.
- Using `contains` on a List of ids with the wrong type (`int` vs
  `Integer` boxing, chapter 3) — `borrowed.contains(4)` can surprise you;
  test it.
- Writing the overdue report with string dates. `LocalDate` +
  `isBefore(cutoff)` is the whole feature.

## Lesson summary
Entities → service → persistence → menu → polish → rubric self-test,
each stage independently runnable, with all state changes funnelled
through Library methods.""",
                    'exercises': [
                        {
                            'slug': 'lms-stage-order',
                            'title': 'Build order',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why is the service (Library) built and tested before the menu loop?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'So logic bugs get found without UI noise, and the menu just calls tested methods', 'is_correct': True},
                                {'id': 'b', 'text': 'Java requires main to be compiled last', 'is_correct': False},
                                {'id': 'c', 'text': 'The menu cannot use HashMaps', 'is_correct': False},
                                {'id': 'd', 'text': 'It makes the file format smaller', 'is_correct': False},
                            ],
                            'explain': 'Separation of concerns: test the model, then bolt on a thin UI.',
                        },
                        {
                            'slug': 'lms-sync-steps',
                            'title': 'returnBook bookkeeping',
                            'exercise_type': 'multiple_select',
                            'instructions': 'A correct returnBook must do ALL of:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Remove the Loan from loans', 'is_correct': True},
                                {'id': 'b', 'text': 'Remove the ISBN from the member\u2019s borrowed list', 'is_correct': True},
                                {'id': 'c', 'text': 'Increment the book\u2019s available counter', 'is_correct': True},
                                {'id': 'd', 'text': 'Delete the Book from the books map', 'is_correct': False},
                            ],
                            'explain': 'Three structures stay in sync; the book itself obviously remains.',
                        },
                        {
                            'slug': 'lms-overdue-type',
                            'title': 'Date arithmetic',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Cleanest way to compute days kept in modern Java:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'ChronoUnit.DAYS.between(borrowedOn, LocalDate.now())', 'is_correct': True},
                                {'id': 'b', 'text': '(now - borrowed) / 86400 on Strings', 'is_correct': False},
                                {'id': 'c', 'text': 'new Date().minus(borrowed)', 'is_correct': False},
                                {'id': 'd', 'text': 'Days between the two yyyy-MM-dd texts', 'is_correct': False},
                            ],
                            'explain': 'java.time does calendar math correctly, DST and leap years included.',
                        },
                    ],
                },
                {
                    'title': 'Rubric, Extensions and Submission',
                    'slug': 'lms-rubric',
                    'objective': 'Self-assess the project against a 100-point rubric and choose an extension.',
                    'duration': 10,
                    'body': r"""# How this project is graded

## Rubric (100 points)

| Area | Pts | Full credit means |
|---|---|---|
| Correctness | 30 | Every menu item behaves per the brief; borrow/return keep all structures consistent |
| OOP design | 20 | Private fields + accessors; entities separate from Library; a custom exception type |
| Collections choice | 10 | Maps for keyed lookups, lists where order matters; you can justify each |
| Exception safety | 10 | No stack trace reachable from the menu; corrupt file line skipped with warning |
| Persistence | 15 | Data survives restart; format documented in a README comment |
| Code quality | 10 | Naming, small methods (<25 lines), no duplicated logic blocks |
| Extension | 5 | One of the extensions below implemented and working |

**Partial credit is honest:** if `available` drifts after 20
borrow/return cycles, correctness loses points even if the demo looked
fine — test with a 20-operation script.

## Self-testing script (run this before submitting)
1. Add 3 books, register 2 members, Exit, relaunch → all present.
2. Borrow every copy of one ISBN → 4th borrow gives the friendly "no
copies" message, not a crash.
3. Return someone else's ISBN → clear error, state unchanged.
4. Edit `books.txt`, break line 2, relaunch → warning printed, other
   books loaded.
5. Search "clean" → finds "Clean Code" regardless of case.
6. Fake a `borrowedOn` of 30 days ago in the file → overdue report
   lists exactly that loan.

## Extensions (pick one, 5 points)
- **Fines:** Rs 1/day overdue, `Member.balance`, shown at return.
- **Reservations:** waiting queue per ISBN (`Queue<Integer>` — the DSA
  course shows why), auto-offer on return.
- **Export:** a `report.csv` dump of open loans for spreadsheets.
- **Sort views:** title / author / ISBN ordering via `Comparator` and
  `TreeMap`.

## Submission checklist
Source files (one package folder tree), a 5-line README explaining how
to compile (`javac -d out src/...`) and run (`java -cp out ...`), and
sample `books.txt`/`members.txt` from your final test.

## Lesson summary
The rubric rewards boring correctness and clean structure over feature
count — chase the 20-operation consistency script first, extension
points last.""",
                    'exercises': [
                        {
                            'slug': 'lms-rubric-weighting',
                            'title': 'What the rubric values',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which single failure costs the MOST rubric points?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'available counts drifting after borrow/return cycles', 'is_correct': True},
                                {'id': 'b', 'text': 'Menu text without box-drawing characters', 'is_correct': False},
                                {'id': 'c', 'text': 'Using ArrayList where a Map is suggested', 'is_correct': False},
                                {'id': 'd', 'text': 'Not implementing any extension', 'is_correct': False},
                            ],
                            'explain': 'Correctness is 30 pts; state drift is a correctness bug. Design/collections items cost less.',
                        },
                        {
                            'slug': 'lms-ext-queue',
                            'title': 'Reservation structure',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A per-book waiting queue that offers the next member first uses:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Queue (FIFO) of member ids', 'is_correct': True},
                                {'id': 'b', 'text': 'Stack (LIFO) of member ids', 'is_correct': False},
                                {'id': 'c', 'text': 'Random shuffle on return', 'is_correct': False},
                                {'id': 'd', 'text': 'SortedSet by member name', 'is_correct': False},
                            ],
                            'explain': 'First to reserve is first to receive \u2014 textbook FIFO, exactly chapter 5\u2019s queue.',
                        },
                        {
                            'slug': 'lms-readme-why',
                            'title': 'Documentation',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL reasons the README is part of the grade.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The grader must reproduce compile/run commands exactly', 'is_correct': True},
                                {'id': 'b', 'text': 'The file format needs documenting to test persistence', 'is_correct': True},
                                {'id': 'c', 'text': 'It replaces unit tests entirely', 'is_correct': False},
                                {'id': 'd', 'text': 'It proves the code compiles by itself', 'is_correct': False},
                            ],
                            'explain': 'Docs transfer context; code quality is still graded from the source.',
                        },
                    ],
                },
            ],
        },
    ],
    'assessment': [
        {
            'slug': 'fa-j01-jdk-jre',
            'title': 'JDK vs JRE',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which statement about JDK and JRE is correct?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'The JDK contains the JRE plus compilers and tools', 'is_correct': True},
                {'id': 'b', 'text': 'The JRE contains javac', 'is_correct': False},
                {'id': 'c', 'text': 'They are two names for the same thing', 'is_correct': False},
                {'id': 'd', 'text': 'The JVM replaces the JDK on production only', 'is_correct': False},
            ],
            'explain': 'JDK > JRE > JVM: development kit bundles the runtime, which bundles the virtual machine.',
        },
        {
            'slug': 'fa-j02-bytecode-portable',
            'title': 'Why bytecode travels',
            'exercise_type': 'multiple_choice',
            'instructions': '"Compile once, run anywhere" works because javac produces:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Platform-neutral bytecode run by a platform-specific JVM', 'is_correct': True},
                {'id': 'b', 'text': 'Machine code for the current CPU', 'is_correct': False},
                {'id': 'c', 'text': 'Source code recompiled at runtime', 'is_correct': False},
                {'id': 'd', 'text': 'A .NET assembly', 'is_correct': False},
            ],
            'explain': 'The portability lives in the bytecode + per-platform JVM, not in the OS being ignored.',
        },
        {
            'slug': 'fa-j03-main-signature',
            'title': 'Entry point',
            'exercise_type': 'fill_blank',
            'instructions': (
                'Complete the exact method header Java looks for:  '
                'public static void main(String[] args)  \u2014 answer with the whole '
                'header INCLUDING the parameter but without body braces, exactly as shown '
                'in lessons (case-sensitive).'
            ),
            'xp_reward': 10,
            'is_final_assessment': True,
            'solution_code': 'public static void main(String[] args)',
            'explain': 'Any deviation (non-static, wrong param type) compiles but is not the entry point.',
        },
        {
            'slug': 'fa-j04-primitive-vs-wrapper',
            'title': 'int vs Integer',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL true differences between int and Integer.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Integer can be null; int cannot', 'is_correct': True},
                {'id': 'b', 'text': 'Collections like ArrayList hold Integer, not int', 'is_correct': True},
                {'id': 'c', 'text': 'int is stored on the stack as a raw value', 'is_correct': True},
                {'id': 'd', 'text': 'Integer is always faster in loops', 'is_correct': False},
            ],
            'explain': 'Boxing adds an object layer: convenient, but slower and nullable.',
        },
        {
            'slug': 'fa-j05-division',
            'title': 'Integer division',
            'exercise_type': 'output_prediction',
            'instructions': 'What does  System.out.println(7 / 2);  print?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '3',
            'explain': 'Both operands are int, so the result truncates toward zero.',
        },
        {
            'slug': 'fa-j06-mod-negative',
            'title': 'Modulo sign',
            'exercise_type': 'output_prediction',
            'instructions': 'What does  System.out.println(-7 % 3);  print?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '-1',
            'explain': 'Java\u2019s % keeps the sign of the dividend (unlike Python).',
        },
        {
            'slug': 'fa-j07-string-immutable',
            'title': 'String equality',
            'exercise_type': 'output_prediction',
            'instructions': 'String s = "ja"; s += "va";  What does  System.out.println(s == "java");  print?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': 'false',
            'explain': '== compares references; the concatenated object is not the literal. Use .equals().',
        },
        {
            'slug': 'fa-j08-concat-order',
            'title': 'String + number',
            'exercise_type': 'output_prediction',
            'instructions': 'What does  System.out.println("2" + 3 + 4);  print?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '234',
            'explain': 'Left to right: "2"+3 -> "23", then "23"+4 -> "234". Parentheses change it.',
        },
        {
            'slug': 'fa-j09-scanner-nextint',
            'title': 'Scanner mismatch',
            'exercise_type': 'multiple_choice',
            'instructions': 'Typing "abc" at  Scanner.nextInt()  throws:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'InputMismatchException', 'is_correct': True},
                {'id': 'b', 'text': 'NumberFormatException', 'is_correct': False},
                {'id': 'c', 'text': 'IOException', 'is_correct': False},
                {'id': 'd', 'text': 'It returns 0', 'is_correct': False},
            ],
            'explain': 'nextInt throws InputMismatchException; Integer.parseInt throws NumberFormatException.',
        },
        {
            'slug': 'fa-j10-switch-fallthrough',
            'title': 'Missing break',
            'exercise_type': 'output_prediction',
            'instructions': 'switch(x){case 1: System.out.print("A"); case 2: System.out.print("B"); break;}  with x=1 prints?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': 'AB',
            'explain': 'Classic fall-through: without break, execution continues into the next case.',
        },
        {
            'slug': 'fa-j11-array-index',
            'title': 'Off-by-one',
            'exercise_type': 'multiple_choice',
            'instructions': 'int[] a = new int[5];  What is a[5]?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'ArrayIndexOutOfBoundsException at runtime', 'is_correct': True},
                {'id': 'b', 'text': '0 \u2014 arrays default-fill past the end', 'is_correct': False},
                {'id': 'c', 'text': 'Compile error', 'is_correct': False},
                {'id': 'd', 'text': 'null', 'is_correct': False},
            ],
            'explain': 'Valid indices are 0..length-1; Java bounds-checks every access.',
        },
        {
            'slug': 'fa-j12-array-length',
            'title': 'length vs length()',
            'exercise_type': 'fill_blank',
            'instructions': (
                'Arrays expose a FIELD (no parentheses) whose single word names the size; '
                'Strings use a METHOD length(). Answer with the exact field name, lower-case, one word.'
            ),
            'xp_reward': 10,
            'is_final_assessment': True,
            'solution_code': 'length',
            'explain': 'arr.length (no parentheses, it is a field) vs s.length() (a method).',
        },
        {
            'slug': 'fa-j13-overload-vs-override',
            'title': 'Two similar words',
            'exercise_type': 'multiple_choice',
            'instructions': 'Same name, different parameter lists, same class is:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Overloading', 'is_correct': True},
                {'id': 'b', 'text': 'Overriding', 'is_correct': False},
                {'id': 'c', 'text': 'Hiding', 'is_correct': False},
                {'id': 'd', 'text': 'Covariance', 'is_correct': False},
            ],
            'explain': 'Overload = same class, different signature (compile-time). Override = subclass replaces parent method (runtime).',
        },
        {
            'slug': 'fa-j14-runtime-polymorphism',
            'title': 'Which method runs',
            'exercise_type': 'output_prediction',
            'instructions': 'Animal a = new Dog(); a.speak() \u2014 Dog overrides speak printing "Woof", Animal prints "Generic". Output?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': 'Woof',
            'explain': 'Instance methods bind to the actual object type \u2014 that is polymorphism.',
        },
        {
            'slug': 'fa-j15-super-rule',
            'title': 'Constructor order',
            'exercise_type': 'multiple_choice',
            'instructions': 'Creating a subclass object runs constructors in which order?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'Parent first, then child', 'is_correct': True},
                {'id': 'b', 'text': 'Child first, then parent', 'is_correct': False},
                {'id': 'c', 'text': 'Only the child\u2019s', 'is_correct': False},
                {'id': 'd', 'text': 'Alphabetical by class name', 'is_correct': False},
            ],
            'explain': 'An object initialises from the top of the hierarchy down; super() runs first.',
        },
        {
            'slug': 'fa-j16-abstract-instantiable',
            'title': 'Abstract rules',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL true statements about abstract classes.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'They cannot be instantiated directly', 'is_correct': True},
                {'id': 'b', 'text': 'They may contain both abstract and concrete methods', 'is_correct': True},
                {'id': 'c', 'text': 'They can have constructors', 'is_correct': True},
                {'id': 'd', 'text': 'A class with an abstract method may omit the abstract keyword', 'is_correct': False},
            ],
            'explain': 'If any method is abstract, the class MUST be declared abstract \u2014 the compiler enforces it.',
        },
        {
            'slug': 'fa-j17-interface-default',
            'title': 'Default methods',
            'exercise_type': 'multiple_choice',
            'instructions': 'A Java 8+ interface method with a body, inheritable by implementors without override, is marked:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'default', 'is_correct': True},
                {'id': 'b', 'text': 'static', 'is_correct': False},
                {'id': 'c', 'text': 'final', 'is_correct': False},
                {'id': 'd', 'text': 'abstract', 'is_correct': False},
            ],
            'explain': 'default methods let interfaces evolve without breaking existing implementors.',
        },
        {
            'slug': 'fa-j18-checked-vs-unchecked',
            'title': 'Exception taxonomy',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which is a CHECKED exception (compiler forces handling)?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'IOException', 'is_correct': True},
                {'id': 'b', 'text': 'NullPointerException', 'is_correct': False},
                {'id': 'c', 'text': 'ArrayIndexOutOfBoundsException', 'is_correct': False},
                {'id': 'd', 'text': 'ClassCastException', 'is_correct': False},
            ],
            'explain': 'Checked = direct/indirect subclasses of Exception except RuntimeException. The rest here are runtime.',
        },
        {
            'slug': 'fa-j19-finally-runs',
            'title': 'finally semantics',
            'exercise_type': 'output_prediction',
            'instructions': 'try { return 1; } finally { System.out.print("F"); }  \u2014 what does the whole method print before returning?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': 'F',
            'explain': 'finally runs even across a return \u2014 the value is staged, then finally executes.',
        },
        {
            'slug': 'fa-j20-arraylist-vs-linkedlist',
            'title': 'List choice',
            'exercise_type': 'multiple_choice',
            'instructions': 'Frequent get(i) by index, rare middle insertions \u2014 pick:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'ArrayList', 'is_correct': True},
                {'id': 'b', 'text': 'LinkedList', 'is_correct': False},
                {'id': 'c', 'text': 'Either is equally fast', 'is_correct': False},
                {'id': 'd', 'text': 'Neither supports get(i)', 'is_correct': False},
            ],
            'explain': 'ArrayList: O(1) random access. LinkedList: O(n) to reach an index. Same ADT, different cost.',
        },
        {
            'slug': 'fa-j21-hashmap-duplicate-key',
            'title': 'put on existing key',
            'exercise_type': 'output_prediction',
            'instructions': 'Map m = new HashMap(); m.put("a",1); m.put("a",2);  What does m.size() print?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'expected_output': '1',
            'explain': 'Keys are unique: the second put replaces the value (and returns the old one).',
        },
        {
            'slug': 'fa-j22-iteration-modification',
            'title': 'ConcurrentModification',
            'exercise_type': 'multiple_choice',
            'instructions': 'Removing an element from an ArrayList inside an enhanced for-loop usually throws:',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'ConcurrentModificationException', 'is_correct': True},
                {'id': 'b', 'text': 'IndexOutOfBoundsException', 'is_correct': False},
                {'id': 'c', 'text': 'Nothing \u2014 it works fine', 'is_correct': False},
                {'id': 'd', 'text': 'ClassCastException', 'is_correct': False},
            ],
            'explain': 'Use an Iterator\u2019s remove(), removeIf, or iterate backwards \u2014 the for-each fail-fast guard trips otherwise.',
        },
        {
            'slug': 'fa-j23-try-resources',
            'title': 'try-with-resources',
            'exercise_type': 'multiple_select',
            'instructions': 'Select ALL requirements/behaviours of  try (Resource r = ...) { }.',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'The resource must implement AutoCloseable', 'is_correct': True},
                {'id': 'b', 'text': 'close() is called even if the block throws', 'is_correct': True},
                {'id': 'c', 'text': 'r is usable after the try block', 'is_correct': False},
                {'id': 'd', 'text': 'It replaces a manual close in finally', 'is_correct': True},
            ],
            'explain': 'Scoped, guaranteed closure \u2014 that is why every file lesson in this course used it.',
        },
        {
            'slug': 'fa-j24-classpath-resolve',
            'title': 'Class lookup at runtime',
            'exercise_type': 'multiple_choice',
            'instructions': 'With  java -cp out com.school.Main , how does the JVM locate Main\u2019s class file?',
            'xp_reward': 10,
            'is_final_assessment': True,
            'choices': [
                {'id': 'a', 'text': 'out/com/school/Main.class \u2014 package maps to folders', 'is_correct': True},
                {'id': 'b', 'text': 'It re-reads Main.java and compiles it', 'is_correct': False},
                {'id': 'c', 'text': 'Anywhere on the hard drive by filename search', 'is_correct': False},
                {'id': 'd', 'text': 'Only from the current directory, ignoring -cp', 'is_correct': False},
            ],
            'explain': 'The classpath root + dotted package = folder path. Same mirror rule as the source tree.',
        },
    ],
}
