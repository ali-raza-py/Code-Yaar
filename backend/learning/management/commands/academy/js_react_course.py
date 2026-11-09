"""Course 4: JavaScript & React — the language first, then React.

Ten chapters that follow the syllabus order: core JavaScript (values,
control flow, functions, arrays/objects), then the DOM and events, then
ES6+, async JavaScript, and finally React — components, props/state and
hooks — closing with a React Student Dashboard project. The sandbox
executes Python and C++ only, so every check here is answer-graded
(multiple choice / multiple select / output prediction / fill in the
blank) against real, precisely-analysed code. Each chapter ends with a
Chapter Quiz lesson and the course closes with a 24-question final
assessment.
"""

COURSE = {
    'slug': 'javascript-react',
    'title': 'JavaScript & React',
    'subtitle': 'The language of the web, then the library that organises it.',
    'description': (
        'JavaScript is the only programming language every web browser '
        'speaks, and React is the tool teams use to tame large amounts of '
        'it. This course teaches JavaScript properly first — values, '
        'control flow, functions, arrays, objects, the DOM, events, ES6+ '
        'and asynchronous code — and only then introduces React, so '
        'components and hooks land on solid ground. Every chapter mixes '
        'worked examples with honest, answer-graded checks, and the course '
        'ends by building a React Student Dashboard.'
    ),
    'difficulty': 'beginner',
    'language': 'javascript',
    'prerequisites': (
        'Basic HTML and CSS: you should know what a web page is and have '
        'seen tags like <div>, <p> and attributes. The Web Development '
        'Fundamentals course on Code Yaar prepares you fully.'
    ),
    'track': {
        'slug': 'web',
        'title': 'Web Development',
        'category': 'web',
        'description': (
            'Build for the browser: the languages, the frameworks and the '
            'server side that together make modern websites.'
        ),
    },
    'objectives': [
        'Run JavaScript in the browser console and with Node, and know the difference.',
        'Declare values correctly and explain type coercion and === vs ==.',
        'Control program flow with conditionals, loops and truthiness.',
        'Write functions, understand scope and closures, and use arrow syntax.',
        'Manipulate arrays with map/filter/reduce and model data with objects.',
        'Read and change the DOM and respond to events and forms.',
        'Use ES6+ tools: destructuring, spread, template literals, modules, classes.',
        'Handle asynchronous work with promises, async/await and fetch.',
        'Explain what React solves and build components with props and state.',
        'Use hooks (useState, useEffect) and integrate a real API into a React app.',
    ],
    'certification': {'passing_score': 70},
    'modules': [
        # ════════════════════ Chapter 1 ════════════════════
        {
            'title': 'Introduction to JavaScript',
            'slug': 'js-intro',
            'description': 'Where JavaScript runs, how it got there, and your first live code.',
            'lessons': [
                {
                    'title': 'What Is JavaScript and Where Does It Run?',
                    'slug': 'what-is-javascript',
                    'objective': 'Describe JavaScript\'s role in the browser and name its main runtime environments.',
                    'duration': 10,
                    'body': """# The language the browser speaks

Every web page is three layers working together:

- **HTML** — the structure. What exists on the page (headings, buttons).
- **CSS** — the presentation. How it looks (colours, layout).
- **JavaScript** — the behaviour. What happens when you click, type,
  scroll, or when data arrives from a server.

A login form is HTML. Its styling is CSS. Checking that the password is
long enough *before* sending it, calling the server, and turning the
button green on success — that is JavaScript.

JavaScript was written in ten days in 1995 by Brendan Eich at Netscape
(which is why it has quirks), and it standardised as **ECMAScript** —
"ES6", "ES2015+" etc. are ECMAScript editions, not different languages.
When people say "modern JavaScript" they mean the features ES6 (2015)
and later added.

## Where it runs

1. **Browser engines** — V8 in Chrome/Edge, JavaScriptCore in Safari,
   SpiderMonkey in Firefox. The page's JavaScript runs inside your
   user's browser, on their machine.
2. **Node.js** — V8 pulled out of the browser with an API for files,
   networks and processes. Same language, now it can run servers, build
   tools and scripts. Node is *not* a different language; it is a
   runtime.
3. **Everywhere else** — React Native (phones), Electron (desktop apps),
   and increasingly servers.

The page you will ever edit lives in the browser, so the first chapters
use the **browser console**: right-click → Inspect → Console tab. Type:

```js
console.log("Hello from Code Yaar");
```

`console.log` prints a value — JavaScript's `print`. Everything in this
course's code examples can be pasted into that console and run.

## Interpreted, compiled, both

JavaScript is compiled by the engine just before it runs (JIT — "just in
time"), so it starts instantly like an interpreted language but runs
with compiled speed. You never invoke a compiler: the browser *is* your
runtime. That is the big difference from the Java course — there is no
`javac` step; there is only "does it work in the console?".

## Why it matters

It is the only language that runs in a browser, which makes it
inescapable for web work — and Node made it the default choice for
tooling and quick servers too. Interviewers for any frontend or
full-stack role will probe it.

## Common mistakes
- Expecting JavaScript to behave like Java. Similar name (a 1995
  marketing move), different language: `int x` is nonsense here;
  dynamic types and first-class functions are the core.
- Confusing ECMAScript versions with separate languages. ES6 *is*
  JavaScript, with features.
- Running page code in Node and wondering why `document` doesn't exist.
  The DOM belongs to browsers; Node has files and servers instead.

## Lesson summary
JavaScript = the behaviour layer of the web; ECMAScript = its standard;
browsers and Node = its two main homes; and the console = the lab you
will use for the first half of this course.""",
                    'exercises': [
                        {
                            'slug': 'js-three-layers',
                            'title': 'Structure, style, behaviour',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In the HTML/CSS/JavaScript trio, which layer validates a form field before submitting it?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'JavaScript — it owns behaviour', 'is_correct': True},
                                {'id': 'b', 'text': 'HTML — input tags validate themselves', 'is_correct': False},
                                {'id': 'c', 'text': 'CSS — with :valid selectors', 'is_correct': False},
                                {'id': 'd', 'text': 'The web server', 'is_correct': False},
            ],
                            'explain': 'CSS can STYLe :valid/:invalid states, but the logic that runs the check is JavaScript.',
                        },
                        {
                            'slug': 'js-ecmascript-meaning',
                            'title': 'What ES6 means',
                            'exercise_type': 'multiple_choice',
                            'instructions': '"ES6" is best described as:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'A 2015 edition of the ECMAScript standard that defines JavaScript features', 'is_correct': True},
                                {'id': 'b', 'text': 'A newer language replacing JavaScript', 'is_correct': False},
                                {'id': 'c', 'text': 'A JavaScript library', 'is_correct': False},
                                {'id': 'd', 'text': 'A browser engine', 'is_correct': False},
                            ],
                            'explain': 'ECMAScript is the specification; JavaScript is the language. Editions add features.',
                        },
                        {
                            'slug': 'js-node-vs-browser',
                            'title': 'Two homes',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about Node.js.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'It runs JavaScript outside the browser', 'is_correct': True},
                                {'id': 'b', 'text': 'It uses the V8 engine', 'is_correct': True},
                                {'id': 'c', 'text': 'It gives access to files and networks', 'is_correct': True},
                                {'id': 'd', 'text': 'It is a different language from browser JavaScript', 'is_correct': False},
                            ],
                            'explain': 'Same language and engine; the surrounding API differs (no document, but fs and http).',
                        },
                    ],
                },
                {
                    'title': 'Your First Program: Console, Scripts and Variables',
                    'slug': 'first-program',
                    'objective': 'Run code in the console, attach a script to a page, and store values with let.',
                    'duration': 12,
                    'body': """# Three ways to run the same code

**1. The console.** Inspect → Console → type expressions. Perfect for
trying things; gone when you close the tab.

**2. A `<script>` tag.** In the HTML body:

```html
<button id="join">Join</button>
<script>
  let clicks = 0;
  document.getElementById("join").addEventListener("click", () => {
    clicks++;
    console.log(`Clicked ${clicks} times`);
  });
</script>
```

**3. An external file** (the professional choice):

```html
<script src="app.js" defer></script>
```

`defer` means "download now, run after the HTML is parsed" — without it
a script in `<head>` runs before the buttons it references exist, the
classic "my code can't find the element" bug.

## Variables: `let`, `const`, and the old `var`

```js
let score = 0;          // can be reassigned
score = score + 10;     // fine

const PASS_MARK = 50;   // cannot be reassigned
PASS_MARK = 60;         // TypeError: Assignment to constant variable.

var legacy = 1;         // pre-ES6 keyword — you will see it in old code
```

Rules of the course: **`const` by default, `let` when you must
reassign, never `var` in new code.** `const` does not make the value
immutable — it makes the *binding* immutable. `const user = {}` then
`user.name = "Aya"` is legal; the object itself can change, the name
`user` cannot be pointed elsewhere.

Identifiers are camelCase by convention (`studentName`, not
`student_name`), case-sensitive (`score` ≠ `Score`), and cannot start
with a digit.

## Dynamic typing in action

```js
let x = 5;            // x holds a number
x = "five";           // now the SAME variable holds a string — legal!
x = true;             // and a boolean
```

No declarations of type, and that freedom is the root of both
JavaScript's flexibility and its bugs — which is why chapter 2 gives
you tools (`typeof`, `===`) to check what is actually in the box.

## Template literals

Note the `` `Clicked ${clicks} times` `` above: backtick strings with
`${...}` inside. Modern JavaScript formats with these, not with `+`:

```js
console.log("Score: " + score);          // works, clunky
console.log(`Score: ${score} / ${PASS_MARK}`);  // preferred
```

## Common mistakes
- Forgetting `defer` (or putting the script at the end of `<body>`) and
  getting `Cannot read properties of null`.
- `const` panic: "but I can't change it!" — you cannot *repoint* it;
  changing its object's contents is fine and normal.
- Declaring with neither keyword: `score = 0` without `let` creates a
  global in sloppy mode and throws in strict/modern module code. Always
  declare.

## Lesson summary
Console for experiments, `defer`-ed external scripts for pages,
`const`-by-default variables with camelCase names, backticks for
formatting — the working setup for everything ahead.""",
                    'exercises': [
                        {
                            'slug': 'const-repoint',
                            'title': 'What const forbids',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'const user = { name: "Ali" };  Which line throws an error?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'user = { name: "Sara" }', 'is_correct': True},
                                {'id': 'b', 'text': 'user.name = "Sara"', 'is_correct': False},
                                {'id': 'c', 'text': 'user.age = 20', 'is_correct': False},
                                {'id': 'd', 'text': 'console.log(user.name)', 'is_correct': False},
                            ],
                            'explain': 'const freezes the binding, not the object. Repointing throws; mutating is fine.',
                        },
                        {
                            'slug': 'script-tag-output',
                            'title': 'A complete snippet',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let a = 2; a = a * a; console.log(`a=${a}`);  — what does the console show? (exact text)',
                            'xp_reward': 40,
                            'expected_output': 'a=4',
                            'choices': [],
                            'explain': '2*2=4, and the template literal inserts it: "a=4".',
                        },
                        {
                            'slug': 'defer-why',
                            'title': 'Why defer',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A <head> script without defer that calls getElementById fails because:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The elements do not exist yet when the script runs', 'is_correct': True},
                                {'id': 'b', 'text': 'The browser blocks console.log in head', 'is_correct': False},
                                {'id': 'c', 'text': 'getElementById only works in Node', 'is_correct': False},
                                {'id': 'd', 'text': 'Scripts in head are ignored', 'is_correct': False},
                            ],
                            'explain': 'HTML parses top to bottom; defer waits for the parse to finish before running.',
                        },
                        {
                            'slug': 'naming-camelcase',
                            'title': 'Convention',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'JavaScript identifiers use the convention whose first word is lower-case and '
                                'later words start capitalised, like studentName. Name that convention in '
                                'one lower-case word (two words joined, no space): ______ case.'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'camel',
                            'explain': 'camelCase — the standard for variables and functions; PascalCase is reserved for classes/components.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 1 Quiz',
                    'slug': 'js-intro-quiz',
                    'objective': 'Check mastery of JavaScript\'s role, runtimes and first-program setup.',
                    'duration': 8,
                    'body': """# Chapter 1 quiz

Five questions on where JavaScript runs and how to start a program.
Read every explanation — the ones you skip are the ones the exam
asks about.""",
                    'exercises': [
                        {
                            'slug': 'q1-console-whats-printed',
                            'title': 'Reading order',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let n = 3; n++; console.log(n * 2);  What is printed? (just the value)',
                            'xp_reward': 50,
                            'expected_output': '8',
                            'choices': [],
                            'explain': 'n becomes 4 after ++, doubled is 8.',
                        },
                        {
                            'slug': 'q1-browser-engine',
                            'title': 'Engines',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which JavaScript engine powers Chrome and Edge?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'V8', 'is_correct': True},
                                {'id': 'b', 'text': 'SpiderMonkey', 'is_correct': False},
                                {'id': 'c', 'text': 'JavaScriptCore', 'is_correct': False},
                                {'id': 'd', 'text': 'Chakra', 'is_correct': False},
                            ],
                            'explain': 'V8 (Chrome/Edge); SpiderMonkey is Firefox, JavaScriptCore is Safari.',
                        },
                        {
                            'slug': 'q1-var-verdict',
                            'title': 'Old keyword',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct statements about var in new code.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Avoid it; prefer const and let', 'is_correct': True},
                                {'id': 'b', 'text': 'It still works in browsers today', 'is_correct': True},
                                {'id': 'c', 'text': 'It is a syntax error in modern JavaScript', 'is_correct': False},
                                {'id': 'd', 'text': 'It has confusing function-level scope quirks', 'is_correct': True},
                            ],
                            'explain': 'var is legal but legacy — its scoping surprises are why ES6 added let.',
                        },
                        {
                            'slug': 'q1-var-vs-let',
                            'title': 'Reassignment',
                            'exercise_type': 'output_prediction',
                            'instructions': 'What does  typeof "Code" + " Yaar"  evaluate to as the final printed string?',
                            'xp_reward': 50,
                            'expected_output': 'string Yaar',
                            'choices': [],
                            'explain': 'typeof "Code" is the string "string"; + on strings concatenates: "string Yaar".',
                        },
                        {
                            'slug': 'q1-external-file',
                            'title': 'Linking a file',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the HTML attribute that loads an external script file:  '
                                '<script __="app.js"></script>  — answer with the attribute name only, lower-case.'
                            ),
                            'xp_reward': 50,
                            'solution_code': 'src',
                            'explain': 'src="app.js" links the file; defer controls when it runs.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 2 ════════════════════
        {
            'title': 'Variables, Data Types and Operators',
            'slug': 'js-types',
            'description': 'The seven types, what + really does, === vs ==, and truthiness.',
            'lessons': [
                {
                    'title': 'The Seven Data Types',
                    'slug': 'seven-types',
                    'objective': 'Name the primitive types and objects, and use typeof correctly.',
                    'duration': 14,
                    'body': """# Six primitives, one big box

JavaScript values fall into **primitives** and **everything else
(objects)**:

| Type | Examples | Notes |
|---|---|---|
| string | `"hi"`, `'hi'`, `` `hi` `` | all three quote styles work |
| number | `42`, `3.14`, `NaN`, `Infinity` | ONE numeric type — double, no int/float split |
| boolean | `true`, `false` | |
| undefined | `undefined` | declared, no value yet |
| null | `null` | deliberately "no value" |
| bigint / symbol | `10n`, `Symbol("id")` | rare; you will recognise them on sight |
| **object** | `{...}`, `[...]`, functions, Date | arrays and functions ARE objects |

One `number` type means `1 + 1 === 2` and `0.1 + 0.2 !== 0.3` — floats,
with all the rounding drama that implies.

## typeof — and its famous lie

```js
typeof 42          // "number"
typeof "42"        // "string"
typeof true        // "boolean"
typeof undefined   // "undefined"
typeof function(){} // "function"
typeof null        // "object"   ← BUG from 1995, never fixed (compatibility)
typeof {}          // "object"
typeof []          // "object"   ← arrays are objects too
```

`typeof null === "object"` is a historical accident every interview
expects you to know. For arrays use `Array.isArray(x)`; for null use
`x === null`.

## undefined vs null

`undefined` means "the system's default nothing" — a variable declared
but not assigned, a missing function argument, an absent object
property. `null` means "the programmer's chosen nothing" — you set it
on purpose to say "there is no value here". Compare with `===` and
never confuse the two:

```js
let a;          // undefined
let b = null;   // null
a === b         // false! they are different values
```

## Numbers: useful furniture

```js
Number("42")     // 42   explicit string -> number
parseInt("42px") // 42   reads leading digits
parseFloat("3.5") // 3.5
"7" * "2"        // 14   math operators coerce automatically (but NOT +)
NaN              // "not a number" — and NaN === NaN is FALSE
Number.isNaN(x)  // the correct check; even typeof NaN is "number"
Math.random(), Math.max(3, 9), Math.round(2.6)  // 0..1, 9, 3
```

## Strings

```js
s.length               // a PROPERTY, not a method — no parentheses
"hello".toUpperCase()  // methods return NEW strings; strings never change
" a ".trim()           // "a"
"1,2,3".split(",")     // ["1","2","3"]
"Hello".includes("ell") // true
s.slice(0, 3)           // first three chars
```

Immutability matters: `s.toUpperCase()` does not touch `s`; you must
keep the return value.

## Common mistakes
- Trusting `typeof null` / `typeof []`. Know the two exceptions.
- `let x = 0.1 + 0.2; if (x === 0.3)` — fails on float rounding.
  Compare money in cents (integers), or check `Math.abs(x - 0.3) < 1e-9`.
- Writing `s.toUpperCase()` alone and expecting `s` changed. Reassign or
  chain.
- `== null` to mean "is null" — it ALSO matches undefined. Usually you
  want `=== null`.

## Lesson summary
Primitives are string/number/boolean/undefined/null (+rare bigint/
symbol); objects hold everything else. `typeof` is your probe with two
documented lies, numbers are floats, strings are immutable, and
`undefined` vs `null` is "system nothing" vs "chosen nothing".""",
                    'exercises': [
                        {
                            'slug': 'typeof-null',
                            'title': 'The classic bug',
                            'exercise_type': 'output_prediction',
                            'instructions': 'What does  console.log(typeof null);  print? (one lower-case word)',
                            'xp_reward': 40,
                            'expected_output': 'object',
                            'choices': [],
                            'explain': 'A 1995 implementation bug frozen by backwards compatibility.',
                        },
                        {
                            'slug': 'number-string-plus',
                            'title': 'Coercion contrast',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What are the results of  "5" + 3  and  "5" - 3  respectively?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '"53" and 2', 'is_correct': True},
                                {'id': 'b', 'text': '8 and 2', 'is_correct': False},
                                {'id': 'c', 'text': '"53" and "53"', 'is_correct': False},
                                {'id': 'd', 'text': 'TypeError both times', 'is_correct': False},
                            ],
                            'explain': '+ with a string concatenates; - has no string meaning so both sides become numbers.',
                        },
                        {
                            'slug': 'array-isarray',
                            'title': 'Testing arrays',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Reliable way to check whether x is an array:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Array.isArray(x)', 'is_correct': True},
                                {'id': 'b', 'text': 'typeof x === "array"', 'is_correct': False},
                                {'id': 'c', 'text': 'x instanceof String', 'is_correct': False},
                                {'id': 'd', 'text': 'x.length >= 0', 'is_correct': False},
                            ],
                            'explain': 'typeof says "object" for arrays; isArray is the dedicated tool.',
                        },
                        {
                            'slug': 'string-immutable',
                            'title': 'What changed?',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let s = "code"; s.toUpperCase(); console.log(s);  What prints?',
                            'xp_reward': 40,
                            'expected_output': 'code',
                            'choices': [],
                            'explain': 'toUpperCase returns a new string; s itself is untouched.',
                        },
                    ],
                },
                {
                    'title': 'Operators: ==, ===, and the Ternary',
                    'slug': 'operators',
                    'objective': 'Use comparison, logical and arithmetic operators; explain why === is the default.',
                    'duration': 14,
                    'body': """# Equality: bring the rules, or don't

```js
5 == "5"      // true  — loose: converts types to match ("abstract")
5 === "5"     // false — strict: same type AND same value
5 != "5"      // false
5 !== "5"     // true
```

`==` runs the coercion algorithm (string→number, null→0-ish, …) — it has
a spec table with dozens of cases nobody holds in their head. `===`
compares as-is. The rule: **always write `===`; if you catch yourself
typing `==`, you need a reason.** The one accepted exception is
`x == null`, true exactly when x is null or undefined.

## Truthiness: the cast list

In an `if`, JavaScript converts any value to boolean. Falsy — the
*complete* short list:

```
false, 0, -0, 0n, "", null, undefined, NaN
```

Everything else is truthy — including `"0"`, `[]` and `{}` (the two
most surprising: an empty array and object are TRUTHY).

```js
if (username) { ... }              // guards "", null, undefined in one check
!"5"                               // false
"" || "fallback"                   // "fallback"  — || picks first truthy
true && false                      // && returns first falsy, else last
```

`||` returning a *value* (not true/false) is how default parameters and
fallbacks are written. ES2020 added `??` — nullish coalescing, which
only falls through for null/undefined, not for `0` or `""`:

```js
count || 10    // count=0 gives 10  (probably a bug!)
count ?? 10    // count=0 gives 0   (intended default)
```

## Arithmetic and assignment

```js
7 % 2       // 1  remainder
2 ** 10     // 1024 exponent (right-associative: 2**3**2 = 2**9 = 512)
x += 3      // x = x + 3   (also -=, *=, /=, %=)
x++         // use x, THEN add 1     ++x: add, THEN use
```

Postfix vs prefix bites in expressions: `let a = 1; b = a++;` leaves
`b === 1, a === 2`.

## The ternary

One-line if/else, everywhere in React later:

```js
const label = score >= 50 ? "Pass" : "Fail";
```

## Operator precedence (just enough)

`!` and `**` bind tightest, then `* / %`, `+ -`, comparisons, `&&`,
`||`, `??`. Do not memorise tables — **use parentheses** whenever an
expression mixes `&&` with `||` or spans more than one line.

## Common mistakes
- `==` by reflex. The linter rule is `eqeqeq` for a reason.
- `if (arr.length)` is fine; `if (arr)` is always true — the empty-array
  trap.
- Mixing `&&`/`||` without parentheses and trusting left-to-right.
- `0 || default` overwriting a legitimate zero; use `??`.

## Lesson summary
`===` compares without magic; the falsy list is seven values long and
everything else is truthy; `&&`/`||`/`??` return values not booleans;
parentheses beat precedence-recall.""",
                    'exercises': [
                        {
                            'slug': 'eqeqeq-verdict',
                            'title': 'Strict vs loose',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which pair evaluates to  true  despite different types?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'null == undefined', 'is_correct': True},
                                {'id': 'b', 'text': 'null === undefined', 'is_correct': False},
                                {'id': 'c', 'text': '0 === "0"', 'is_correct': False},
                                {'id': 'd', 'text': 'NaN == NaN', 'is_correct': False},
                            ],
                            'explain': 'Loose == says null and undefined are "equal to each other"; nothing else here passes, not even NaN to itself.',
                        },
                        {
                            'slug': 'falsy-list',
                            'title': 'Who is falsy',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL falsy values.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': '0', 'is_correct': True},
                                {'id': 'b', 'text': '""', 'is_correct': True},
                                {'id': 'c', 'text': '[]', 'is_correct': False},
                                {'id': 'd', 'text': 'NaN', 'is_correct': True},
                                {'id': 'e', 'text': '"false"', 'is_correct': False},
                            ],
                            'explain': 'Empty array and the non-empty string "false" are both truthy — the two classic traps.',
                        },
                        {
                            'slug': 'nullish-choice',
                            'title': '|| vs ??',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let count = 0; console.log(count || 10); console.log(count ?? 10);  What is the SECOND line printed?',
                            'xp_reward': 40,
                            'expected_output': '0',
                            'choices': [],
                            'explain': '|| treats 0 as absent and takes 10; ?? respects 0 as a real value.',
                        },
                        {
                            'slug': 'postfix-value',
                            'title': 'a++ timing',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let a = 1; let b = a++; console.log(b, a);  What prints? (two values, comma and space between)',
                            'xp_reward': 40,
                            'expected_output': '1 2',
                            'choices': [],
                            'explain': 'b took the OLD value 1; a then became 2. (console.log(a,b) would join them with a space.)',
                        },
                        {
                            'slug': 'ternary-syntax',
                            'title': 'One-line branch',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the ternary:  const grade = pass __ "A" : "F";  '
                                'Which single character is missing? Answer with the character alone.'
                            ),
                            'xp_reward': 40,
                            'solution_code': '?',
                            'explain': 'condition ? whenTrue : whenFalse — the question mark opens the expression.',
                        },
                    ],
                },
                {
                    'title': 'Type Conversion and User Input',
                    'slug': 'type-conversion',
                    'objective': 'Convert between types explicitly and read input from a prompt.',
                    'duration': 12,
                    'body': """# Explicit beats magic

Coercion (automatic conversion) surprises people; **conversion** (doing
it on purpose) is just API use:

```js
Number("42")       // 42
String(42)         // "42"
Boolean("")        // false
Boolean(" ")       // true — a space is NOT empty!
"42" + 0           // "420"  (concatenation — the trap)
"42" - 0           // 42     (numeric — the trick, called "unary minus hack")
```

Prefer the named forms (`Number(...)`, `.toString()`) over hacks like
`+"42"`; future-you reads code, not puzzles.

## parseInt's edges

```js
parseInt("42px")     // 42 — reads digits until a non-digit
parseInt("0xff")     // 255 (!) — it recognises hex
parseInt("4.9")      // 4 — truncates, never rounds
parseFloat("3.5e2")  // 350
Number("42px")       // NaN — Number is strict, parseInt is forgiving
```

Use `parseInt(s, 10)` with the explicit radix argument so odd inputs
are never reinterpreted as octal/hex. Or when you require strictness,
`Number(s)` and then check for `NaN`.

## Getting input in a browser

```js
const name = prompt("Your name?", "anonymous");   // returns a STRING or null
const age = Number(prompt("Your age?"));          // convert! always
if (age === undefined || Number.isNaN(age)) { ... }
alert(`Hello ${name}, age ${age}`);
```

`prompt` is the "Hello World" input tool (real UIs use form fields,
chapter 5). Its two hazards: it always returns a **string** (so `"18"`
compared with `<` still works but `+` concatenates — convert first),
and it returns **null** when cancelled (so `Number(prompt(...))` can
give you `0` from `null`! — check for null before converting).

## The input-pipeline pattern

```js
const raw = prompt("Enter a number:");   // 1. get
if (raw === null) throw new Error("cancelled");
const value = Number(raw);               // 2. convert
if (Number.isNaN(value)) { ... }         // 3. validate
// 4. only now: use `value` as a real number
```

Get → convert → validate → use, every single time data crosses a
boundary (input box, URL, file, server). The same discipline protects
you in Django and React later.

## Common mistakes
- Forgetting the `prompt` cancel path returns null, and `Number(null)`
  is `0` — silently wrong data beats a loud crash, the worst bug class.
- `parseInt` without radix on unusual strings.
- Doing maths on form values: `age + 1` with `age="17"` gives `"171"`.

## Lesson summary
Convert on purpose with `Number/String/Boolean`, keep `parseInt(x, 10)`
for forgiving parses, and wrap every `prompt` (or field, or fetch) in
the get→convert→validate pipeline.""",
                    'exercises': [
                        {
                            'slug': 'prompt-type',
                            'title': 'What prompt returns',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The user types 18 into prompt("age?"). The return value is:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The string "18"', 'is_correct': True},
                                {'id': 'b', 'text': 'The number 18', 'is_correct': False},
                                {'id': 'c', 'text': 'A BigInt', 'is_correct': False},
                                {'id': 'd', 'text': 'undefined', 'is_correct': False},
                            ],
                            'explain': 'prompt always hands back text (or null if cancelled) — convert numbers yourself.',
                        },
                        {
                            'slug': 'parsint-edges',
                            'title': 'Reader behaviour',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log(parseInt("4.9"), Number("4.9"));  What prints? (two values separated by a space)',
                            'xp_reward': 40,
                            'expected_output': '4 NaN',
                            'choices': [],
                            'explain': 'parseInt truncates at the dot; Number rejects the partial parse — strict vs forgiving.',
                        },
                        {
                            'slug': 'null-number',
                            'title': 'Silent zero',
                            'exercise_type': 'output_prediction',
                            'instructions': 'User cancels the prompt. console.log(Number(null));  What prints?',
                            'xp_reward': 40,
                            'expected_output': '0',
                            'choices': [],
                            'explain': 'Number(null) is 0 — that is why the pipeline checks for null BEFORE converting.',
                        },
                        {
                            'slug': 'strict-check',
                            'title': 'Detecting bad input',
                            'exercise_type': 'multiple_select',
                            'instructions': 'After  const value = Number(raw),  select ALL correct validity checks.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'if (Number.isNaN(value))', 'is_correct': True},
                                {'id': 'b', 'text': 'if (value === NaN)', 'is_correct': False},
                                {'id': 'c', 'text': 'if (isNaN(value))', 'is_correct': True},
                                {'id': 'd', 'text': 'if (typeof value === "nan")', 'is_correct': False},
                            ],
                            'explain': 'NaN !== NaN, so direct comparison always fails; Number.isNaN / the old isNaN work.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 2 Quiz',
                    'slug': 'js-types-quiz',
                    'objective': 'Check mastery of types, operators and conversion.',
                    'duration': 8,
                    'body': """# Chapter 2 quiz

Five questions on types and operators — the arithmetic of the rest of
the course. Answer precisely; coercion has no room for almost.""",
                    'exercises': [
                        {
                            'slug': 'q2-total-falsy',
                            'title': 'Counting falsies',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'How many distinct falsy values does JavaScript have?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Seven: false, 0 (also -0), 0n, "", null, undefined, NaN', 'is_correct': True},
                                {'id': 'b', 'text': 'Four: false, 0, "", null', 'is_correct': False},
                                {'id': 'c', 'text': 'Two: false and 0', 'is_correct': False},
                                {'id': 'd', 'text': 'Every empty-looking thing', 'is_correct': False},
                            ],
                            'explain': 'The canonical list is short and closed — memorise it, emptiness in general is NOT falsy.',
                        },
                        {
                            'slug': 'q2-chain',
                            'title': 'Chained comparison',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log(1 < 2 < 3);  What prints? (JS has no chained comparisons like Python)',
                            'xp_reward': 50,
                            'expected_output': 'true',
                            'choices': [],
                            'explain': '(1<2) is true -> Number(true)=1, then 1<3 is true. Works, but for the wrong reason — write it in two checks.',
                        },
                        {
                            'slug': 'q2-string-length',
                            'title': 'Property or method',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The number of characters in s is obtained with:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 's.length', 'is_correct': True},
                                {'id': 'b', 'text': 's.length()', 'is_correct': False},
                                {'id': 'c', 'text': 's.size()', 'is_correct': False},
                                {'id': 'd', 'text': 'len(s)', 'is_correct': False},
                            ],
                            'explain': 'length is a property on strings (arrays too); Java\'s s.length() method trips people up.',
                        },
                        {
                            'slug': 'q2-exponent',
                            'title': 'Power order',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log(2 ** 3 ** 2);  What prints?',
                            'xp_reward': 50,
                            'expected_output': '512',
                            'choices': [],
                            'explain': '** is right-associative: 2**(3**2) = 2**9 = 512.',
                        },
                        {
                            'slug': 'q2-empty-array',
                            'title': 'The array trap',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'let arr = [];  if (arr) { console.log("yes"); }  else { console.log("no"); }  '
                                'Which word is printed? Answer in exactly three lower-case letters.'
                            ),
                            'xp_reward': 50,
                            'solution_code': 'yes',
                            'explain': '[] is truthy — test arr.length, never the array itself.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 3 ════════════════════
        {
            'title': 'Conditions and Loops',
            'slug': 'js-control-flow',
            'description': 'if/else chains, switch, ternary branches, and the four loop styles.',
            'lessons': [
                {
                    'title': 'Branching: if / else if / else',
                    'slug': 'if-else',
                    'objective': 'Write correct multi-branch logic and guard clauses.',
                    'duration': 12,
                    'body': r"""# Deciding things

```js
const score = 78;

if (score >= 90) {
  console.log("Grade A");
} else if (score >= 75) {
  console.log("Grade B");
} else if (score >= 60) {
  console.log("Grade C");
} else {
  console.log("Fail");
}
```

Three things the engine guarantees:

1. Branches are tested **top to bottom**; the FIRST true one runs, then
   the whole chain is skipped. A 95-student prints "Grade A" only —
   order your ranges or they will overlap.
2. The condition is converted to boolean (truthiness, chapter 2) —
   `if (score)` means "score is not 0/NaN/…".
3. Braces are optional but never skipped in this course. `if (x)
console.log(1); console.log(2);` runs line 2 ALWAYS — the un-brace bug.

## else is attached to the nearest if

```js
if (a) if (b) console.log("both");
else console.log("a but not b");   // binds to if(b), not if(a)!
```

Braces remove the ambiguity. This is exactly why linters flag
single-statement ifs.

## Guard clauses: bail early

```js
function divide(a, b) {
  if (b === 0) return "Cannot divide by zero";   // guard
  return a / b;                                   // happy path, un-indented
}
```

Handle the exception first and `return`, then the normal flow falls
straight down. Deeply nested `else` pyramids are a code smell; guards
are the cure, and you will see them in every React handler later
(early-return when state is invalid).

## Truthy conditions for real checks

```js
if (user && user.token) { ... }          // old-safe existence chain
if (user?.token) { ... }                 // modern: optional chaining (ES2020)
if (!(age >= 18)) { ... }                // careful: TRUE when age is NaN!
```

Note the last one: `!(age >= 18)` is TRUE when age is NaN — comparisons
with NaN are always false. Validate the number first (chapter 2
pipeline), then branch.

## Common mistakes
- Ranges out of order: `>= 60` before `>= 90` shadows the top grade.
- `=` instead of `===` inside the condition (`if (x = 5)`) —
  assigns 5, which is truthy, always enters. Modern engines do not stop
  you; linters do.
- Forgetting `else if` and writing a second independent `if` — then a
  95-student prints BOTH "Grade A" and "Grade B".

## Lesson summary
Top-to-bottom first-match chains, braces always, guards for early
exits, and validate before comparing — four habits that keep branching
predictable.""",
                    'exercises': [
                        {
                            'slug': 'branch-order',
                            'title': 'First match wins',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let x = 95; if (x >= 60) console.log("C"); else if (x >= 90) console.log("A");  What prints? (one letter)',
                            'xp_reward': 40,
                            'expected_output': 'C',
                            'choices': [],
                            'explain': 'The buggy order matches >=60 first — a classic range-ordering interview trap.',
                        },
                        {
                            'slug': 'assignment-in-if',
                            'title': 'The single =',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'if (flag = true) { run(); }  What happens?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'flag becomes true and run() always executes', 'is_correct': True},
                                {'id': 'b', 'text': 'SyntaxError — assignment is illegal in conditions', 'is_correct': False},
                                {'id': 'c', 'text': 'run() only if flag was already true', 'is_correct': False},
                                {'id': 'd', 'text': 'flag is unchanged', 'is_correct': False},
                            ],
                            'explain': 'It assigns, then truthiness-tests the result (true). That is why we lint for it.',
                        },
                        {
                            'slug': 'unguarded-brace',
                            'title': 'Brace scope',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let ok = false; if (ok) console.log("one"); console.log("two");  What prints? (just the word)',
                            'xp_reward': 40,
                            'expected_output': 'two',
                            'choices': [],
                            'explain': 'Without braces only the NEXT statement is conditional; "two" runs unconditionally.',
                        },
                        {
                            'slug': 'guard-purpose',
                            'title': 'Why guards',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true benefits of the guard-clause style.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The happy path is not buried in nesting', 'is_correct': True},
                                {'id': 'b', 'text': 'Invalid cases exit before any work happens', 'is_correct': True},
                                {'id': 'c', 'text': 'It makes the function run faster at the engine level', 'is_correct': False},
                                {'id': 'd', 'text': 'Each failure gets its own clear early return', 'is_correct': True},
                            ],
                            'explain': 'Guards are about readability and safety, not machine speed.',
                        },
                    ],
                },
                {
                    'title': 'switch and the Ternary Chain',
                    'slug': 'switch-ternary',
                    'objective': 'Use switch with break, and choose between ternary and if.',
                    'duration': 10,
                    'body': r"""# switch: strict-matches multiway

```js
const day = "Sat";
let plan;

switch (day) {
  case "Sat":
  case "Sun":                 // FALLTHROUGH on purpose: share a branch
    plan = "family time";
    break;
  case "Mon":
    plan = "gym";
    break;
  default:
    plan = "study JS";        // like else
}
```

Facts that matter:

- Matching is **strict (`===`)**: `switch("5")` does NOT hit `case 5`.
- Without `break`, execution **falls through** into the next case's
  code too. That is sometimes a feature (stacked cases above) and
  usually a bug (forgetting one break).
- `default` can sit anywhere but conventionally last; only the first
  matching clause runs, then everything falls to breaks.
- In modern JavaScript you can declare `let/const` inside a case only
  when you wrap the case body in `{ }`.

Use switch when one value selects among many fixed options; use
if/else when conditions are ranges or compound (`score >= 90 &&
labs > 3`).

## Ternary as expression

`cond ? a : b` PRODUCES a value, so it fits where a value is required:

```js
const status = age >= 18 ? "adult" : "minor";      // in a declaration
list.forEach(item => el.append(item.done ? "[x]" : "[ ]"));  // in a call
```

Chained ternaries map the if/else-if ladder:

```js
const grade = s >= 90 ? "A" : s >= 75 ? "B" : s >= 60 ? "C" : "F";
```

Legal — and unreadable past two links. Style rule: one ternary per
line; nest at most twice, then write the if/else.

## if vs ternary decision table

| Need | Use |
|---|---|
| run statements / blocks | `if` |
| pick between two VALUES | ternary |
| multi-range logic | if/else-if |
| inline inside JSX attributes | ternary or `&&` (React, chapter 10) |

## Common mistakes
- Missing `break` and hunting a "phantom" extra branch.
- Putting `case "A" || "B"` — nonsense here (evaluates to "A"); stack
  the cases instead.
- Nested ternary soup. Two links is the honest maximum.

## Lesson summary
switch for exact-value fan-outs (strict, remember the breaks, stack
cases for shared branches), ternary when you are choosing a value, and
the courage to rewrite a three-deep ternary as plain ifs.""",
                    'exercises': [
                        {
                            'slug': 'switch-strict',
                            'title': 'Matching rules',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'switch ("5") { case 5: console.log("num"); break; default: console.log("none"); }  prints:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'none — switch matches with ===', 'is_correct': True},
                                {'id': 'b', 'text': 'num — switch coerces', 'is_correct': False},
                                {'id': 'c', 'text': 'TypeError', 'is_correct': False},
                                {'id': 'd', 'text': 'Nothing at all', 'is_correct': False},
                            ],
                            'explain': 'switch uses strict equality, so the string \"5\" never hits the number case.',
                        },
                        {
                            'slug': 'fallthrough-count',
                            'title': 'Without break',
                            'exercise_type': 'output_prediction',
                            'instructions': 'switch(1){case 1: console.log("a"); case 2: console.log("b"); break; case 3: console.log("c");}  Full output? (letters joined, no spaces)',
                            'xp_reward': 40,
                            'expected_output': 'ab',
                            'choices': [],
                            'explain': 'Case 1 matches, no break -> falls into case 2, then break stops it. c never runs.',
                        },
                        {
                            'slug': 'ternary-where',
                            'title': 'Right tool',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL good uses of the ternary operator.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'const label = ok ? "Pass" : "Fail"', 'is_correct': True},
                                {'id': 'b', 'text': 'Choosing a CSS class inside JSX className', 'is_correct': True},
                                {'id': 'c', 'text': 'Replacing a four-branch if/else-if ladder over ranges', 'is_correct': False},
                                {'id': 'd', 'text': 'payout = role === "admin" ? salary * 2 : salary', 'is_correct': True},
                            ],
                            'explain': 'Ternary for VALUES; long range ladders belong in ifs (or switch/lookup).',
                        },
                    ],
                },
                {
                    'title': 'Loops: for, while, do-while',
                    'slug': 'loops',
                    'objective': 'Pick the right loop shape and control it with break/continue.',
                    'duration': 15,
                    'body': r"""# The three classic shapes

```js
// for: you know the count
for (let i = 0; i < 5; i++) {
  console.log(i);              // 0 1 2 3 4
}

// while: you know the STOP condition
let credits = 3;
while (credits > 0) {
  play();
  credits--;
}

// do-while: run at least once, then check
do {
  choice = readMenu();
} while (choice < 1 || choice > 4);
```

The `for` header is three slots — init; test; step — executed:
init once, then (test → body → step) repeatedly until test fails. `i`
declared with `let` in the header exists ONLY inside the loop (scope,
chapter 4). `i < n` not `<=`: for a length-n thing, indices run
0..n-1 — the off-by-one edge every exam includes.

## Anatomy of a safe loop

Every loop needs its exit guarantee. `while (true)` without a reachable
`break` freezes the tab. Compare:

```js
let n = 10;
while (n !== 1) {            // halve-or-3n+1: stops for every n tested,
  n = n % 2 === 0 ? n / 2 : 3 * n + 1;   // but proving it for ALL n is a
}                            // famous open maths problem!
```

If you cannot point at the line that makes the condition false, you
have a bug or a comment waiting.

## break and continue

```js
for (const candidate of list) {
  if (candidate.valid) break;         // leave the loop entirely
  if (candidate.skipped) continue;    // jump to the next iteration
  inspect(candidate);
}
```

`break` exits; `continue` starts the next round (in a `for`, the step
`i++` still runs — unlike some rumours). Both work in every classic
loop; neither works inside `forEach` (use a normal for, or filter).

## Dry-run discipline (tracing)

Read a loop by making a table of variables per iteration — exactly the
DSA course method:

```js
let sum = 0;
for (let i = 1; i <= 4; i += 2) {   // i: 1, 3  (5 fails test)
  sum += i * i;                      // sum: 1, then 10
}
console.log(sum);                    // 1 + 9 = 10
```

Two rows of a trace table beat staring. On paper, every loop becomes
deterministic.

## Common mistakes
- `for (let i = 0; i <= arr.length; i++)` — the `<=` walks into
  `undefined` at index length (then NaN poisons your sum).
- Forgetting the decrement in while (infinite) or writing it in the
  test slot of a for (weird but legal: `for (;n>0;) n--`).
- `break` inside an if that never becomes true — a silent never-breaks
  loop when input shape changes. Guard with a max-iteration backstop.

## Lesson summary
for for counts, while for conditions, do-while for at-least-once;
0-based, half-open bounds; break exits, continue skips; and when in
doubt, trace two iterations in a table before trusting any loop.""",
                    'exercises': [
                        {
                            'slug': 'loop-count',
                            'title': 'How many times',
                            'exercise_type': 'output_prediction',
                            'instructions': 'for (let i = 2; i < 10; i += 3) c++;  How many times does the body run? (just the digit)',
                            'xp_reward': 40,
                            'expected_output': '3',
                            'choices': [],
                            'explain': 'i takes 2, 5, 8 — next is 11 which fails i<10. Three rounds.',
                        },
                        {
                            'slug': 'trace-sum',
                            'title': 'Trace it',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let s = 0; for (let i = 1; i <= 4; i++) { if (i % 2 === 0) continue; s += i; } console.log(s);  Output?',
                            'xp_reward': 40,
                            'expected_output': '5',
                            'choices': [],
                            'explain': 'Odd indices only: 1 + 3 = 5. continue jumps over the body for 2 and 4.',
                        },
                        {
                            'slug': 'dowhile-identity',
                            'title': 'do-while uniqueness',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What can do-while do that while cannot?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Run its body at least once even if the condition starts false', 'is_correct': True},
                                {'id': 'b', 'text': 'Loop without a condition', 'is_correct': False},
                                {'id': 'c', 'text': 'Declare variables in its header', 'is_correct': False},
                                {'id': 'd', 'text': 'Run faster', 'is_correct': False},
                            ],
                            'explain': 'The test happens after the first pass — menu/input loops live for this.',
                        },
                        {
                            'slug': 'break-vs-continue',
                            'title': 'Control verbs',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'break exits the whole loop', 'is_correct': True},
                                {'id': 'b', 'text': 'continue skips to the next iteration', 'is_correct': True},
                                {'id': 'c', 'text': 'continue skips the for step expression', 'is_correct': False},
                                {'id': 'd', 'text': 'break works inside a switch to end matching', 'is_correct': True},
                            ],
                            'explain': 'In a for, continue still runs i++ — that is a favourite trick question.',
                        },
                    ],
                },
                {
                    'title': 'Looping Over Data: for...of and Nested Loops',
                    'slug': 'for-of',
                    'objective': 'Use for...of on arrays and strings, contrast in/of, and escape nesting.',
                    'duration': 12,
                    'body': r"""# for...of: values, cleanly

```js
const marks = [85, 92, 78];
let total = 0;

for (const m of marks) {      // each VALUE, no index arithmetic
  total += m;
}

for (const ch of "Code") {    // strings are iterable too: C o d e
  console.log(ch);
}

for (const [i, m] of marks.entries()) {   // need the index? ask for it
  console.log(`student ${i}: ${m}`);
}
```

`for...of` is the modern default for "do something with each element":
no bounds, no `arr[i]`, works with anything **iterable** (arrays,
strings, Maps, Sets, querySelectorAll results). It throws on plain
objects (`for...of` over `{a:1}` is a TypeError) — objects are not
iterable by default; loop over `Object.keys(obj)` instead (chapter 5).

## of vs in — the interview pair

```js
for (const key in obj)      { ... }   // KEYS of an object (arrays: indices as strings!)
for (const value of array)  { ... }   // VALUES of an iterable

for (const i in [7, 8]) console.log(i);   // prints "0" then "1"  — STRINGS
```

`in` walks enumerable property names (including inherited ones),
`of` walks the iterator's values. Rule of thumb: **in for objects, of
for arrays** — and prefer `Object.entries(obj)` + `of` when you want
today-idiomatic object loops.

## Nested loops (with an exit plan)

```js
outer:                             // label
for (let r = 0; r < rows; r++) {
  for (let c = 0; c < cols; c++) {
    if (grid[r][c] === target) {
      console.log(`found at ${r},${c}`);
      break outer;                 // leaves BOTH loops
    }
  }
}
```

`break` only ever exits its innermost loop; a labelled `break outer`
(or a helper function with an early `return`) is how you leave a
matrix search. Classic grid work — printing a rectangle of `*`, a
multiplication table — is two for loops with the inner bound depending
on the outer variable.

## When NOT to loop manually

Chapter 6 replaces most of these with array methods:
`marks.reduce((t, m) => t + m, 0)` instead of the total loop above.
Manual loops stay for early exits (`break`), side-effect-heavy code,
and index-coupled algorithms (two pointers, from the DSA course).

## Common mistakes
- `for (const x in arr)` expecting values; you get index strings.
- Mutating an array while `for...of` iterates it (iterator confusion —
  like Java's ConcurrentModificationException; loop over a copy).
- Forgetting labels exist and setting three flags to escape nested
  loops. Early-return function is cleaner still.

## Lesson summary
of for values (arrays/strings/iterables), in for keys (objects),
`.entries()` when you need both, labels or helper functions to escape
nesting — and a growing suspicion that an array method will do the job.""",
                    'exercises': [
                        {
                            'slug': 'in-vs-of',
                            'title': 'Pick the loop',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'To print each VALUE of an array idiomatically:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'for (const v of arr)', 'is_correct': True},
                                {'id': 'b', 'text': 'for (const v in arr)', 'is_correct': False},
                                {'id': 'c', 'text': 'for (const v = arr)', 'is_correct': False},
                                {'id': 'd', 'text': 'foreach (v in arr)', 'is_correct': False},
                            ],
                            'explain': 'in gives keys (string indices); of gives values. No foreach syntax exists in JS.',
                        },
                        {
                            'slug': 'of-object-error',
                            'title': 'Plain objects',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'for (const x of {a: 1, b: 2})  will:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'TypeError — plain objects are not iterable', 'is_correct': True},
                                {'id': 'b', 'text': 'Print 1 then 2', 'is_correct': False},
                                {'id': 'c', 'text': 'Print "a" then "b"', 'is_correct': False},
                                {'id': 'd', 'text': 'Print {a:1}', 'is_correct': False},
                            ],
                            'explain': 'Fix it with Object.keys(obj) / Object.entries(obj) — then of works on the array.',
                        },
                        {
                            'slug': 'nested-string-loop',
                            'title': 'Characters',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let out = ""; for (const c of "abc") out += c + c; console.log(out);  Output?',
                            'xp_reward': 40,
                            'expected_output': 'aabbcc',
                            'choices': [],
                            'explain': 'Each character is appended twice: a+a+b+b+c+c.',
                        },
                        {
                            'slug': 'label-break',
                            'title': 'Escaping nesting',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL valid ways to stop BOTH loops of a nested search the moment you find the target.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'break with a loop label', 'is_correct': True},
                                {'id': 'b', 'text': 'Return from an enclosing function', 'is_correct': True},
                                {'id': 'c', 'text': 'Plain break inside the inner loop', 'is_correct': False},
                                {'id': 'd', 'text': 'A flag checked in both loop conditions', 'is_correct': True},
                            ],
                            'explain': 'Plain break exits only the inner loop; label, early return, or a guard flag all leave both.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 3 Quiz',
                    'slug': 'js-control-flow-quiz',
                    'objective': 'Check mastery of branching, switch, and the loop family.',
                    'duration': 8,
                    'body': """# Chapter 3 quiz

Five questions on conditions and loops — including one trace you
should table out on paper first.""",
                    'exercises': [
                        {
                            'slug': 'q3-grade-chain',
                            'title': 'Chain behaviour',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let s = 75; if (s > 90) console.log("A"); else if (s >= 75) console.log("B"); else console.log("C");  Output? (one letter)',
                            'xp_reward': 50,
                            'expected_output': 'B',
                            'choices': [],
                            'explain': '75 fails >90, passes >=75 — first true branch only.',
                        },
                        {
                            'slug': 'q3-while-body',
                            'title': 'Zero-iteration edge',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'let k = 5; while (k < 5) { k++; }  How many times does the body run?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Zero — while tests before the first pass', 'is_correct': True},
                                {'id': 'b', 'text': 'Once', 'is_correct': False},
                                {'id': 'c', 'text': 'Forever', 'is_correct': False},
                                {'id': 'd', 'text': 'SyntaxError', 'is_correct': False},
                            ],
                            'explain': '5 < 5 is false immediately; do-while would have run once — that is the difference.',
                        },
                        {
                            'slug': 'q3-trace-final',
                            'title': 'Full trace',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let x = 0; for (let i = 0; i < 3; i++) { for (let j = 0; j < 2; j++) x++; } console.log(x);  Output?',
                            'xp_reward': 50,
                            'expected_output': '6',
                            'choices': [],
                            'explain': '3 outer rounds x 2 inner = 6 increments.',
                        },
                        {
                            'slug': 'q3-switch-default',
                            'title': 'default role',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'In a switch statement, the clause that runs when no case matches plays the role '
                                'of else. Answer with its exact single lower-case keyword.'
                            ),
                            'xp_reward': 50,
                            'solution_code': 'default',
                            'explain': 'default: is switch\u2019s else.',
                        },
                        {
                            'slug': 'q3-entries',
                            'title': 'Index + value',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which destructures BOTH index and value inside a for...of over an array?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'for (const [i, v] of arr.entries())', 'is_correct': True},
                                {'id': 'b', 'text': 'for (const [i, v] of arr)', 'is_correct': False},
                                {'id': 'c', 'text': 'for (const i, v in arr)', 'is_correct': False},
                                {'id': 'd', 'text': 'for (const v = arr.next())', 'is_correct': False},
                            ],
                            'explain': 'arr.entries() yields [index, value] pairs; the pattern destructures each pair.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 4 ════════════════════
        {
            'title': 'Functions and Scope',
            'slug': 'js-functions',
            'description': 'Declaring functions, parameters and arguments, scope, hoisting and closures.',
            'lessons': [
                {
                    'title': 'Declaring Functions: Three Forms',
                    'slug': 'function-forms',
                    'objective': 'Write declarations, expressions and arrow functions, and choose among them.',
                    'duration': 14,
                    'body': r"""# The three ways to say "do this"

```js
// 1. Function declaration — hoisted, named
function greet(name) {
  return `Hello, ${name}!`;
}

// 2. Function expression — a value, not hoisted
const greet2 = function (name) {
  return `Hello, ${name}!`;
};

// 3. Arrow function — concise expression form
const greet3 = (name) => `Hello, ${name}!`;
```

All three produce a callable; `greet("Ali")` gives `"Hello, Ali!"`.
The differences that matter:

- **Declarations are hoisted**: you may call `greet` before the line
  that declares it (the whole function is lifted). `const` forms are
  NOT — calling `greet2` early throws (temporal dead zone, like `let`).
- **Arrows are expressions when braces are omitted**: the value is
  returned automatically. `x => x * 2` needs no `return`.
- **Arrows have no own `this`** (they borrow the surrounding one) —
  great inside methods, wrong for object methods that need `this`.
  Details in chapter 7's class lesson; for now: React code loves arrows
  because they never steal `this`.

## Parameters with personality

```js
function enroll(student, course = "Python", seats = 30) {
  return `${student} -> ${course} (${seats})`;
}
enroll("Aya");                       // default fills in
enroll("Aya", "React", 12);          // all three used
function sum(...nums) {              // REST: gather into an array
  return nums.reduce((t, n) => t + n, 0);
}
sum(1, 2, 3, 4);                     // nums === [1,2,3,4]
```

- Defaults apply when the argument is **undefined** (missing or passed
  as undefined) — NOT for null/0/"".
- Extra arguments are silently ignored by declared parameters but
  always present: legacy code reads the `arguments` object; modern code
  uses rest (`...nums`).
- Too few arguments gives `undefined` — which is exactly why defaults
  and validation exist.

## Functions are values (first-class)

```js
const ops = { add: (a, b) => a + b, sub: (a, b) => a - b };
function applyTwice(fn, x) { return fn(fn(x)); }   // fn is a parameter
applyTwice(x => x + 1, 5);         // 7 — the fn travels, called twice
const shout = s => s.toUpperCase();   // stored, passed, returned freely
```

Passing a function means passing the CODE, not its result:

```js
list.forEach(item => console.log(item));   // forEach CALLS your fn
list.map(double);                          // map will call double per item
setTimeout(greet, 1000);                   // runs greet after 1s
setTimeout(greet(), 1000);                 // BUG: runs greet NOW, schedules its result
```

The last pair is the most common beginner mistake in JavaScript.

## Returning: one value, but it can be anything

A function returns exactly one thing — make it an object when you need
several (`{ total, count }`, chapter 6 destructures it back). No
`return` statement means the function returns `undefined`.

## Common mistakes
- Writing `const f = greet();` when you meant `const f = greet;`.
- Defaults with null: `f(null)` does NOT use the default — guard with
  `x ?? default` instead.
- Arrow one-liner returning an OBJECT: `id => { id: id }` is parsed as
  a block! Wrap it: `id => ({ id: id })`.

## Lesson summary
Declarations for the standard case, arrow expressions for callbacks
and one-liners, defaults + rest for flexible signatures, and always
question-mark whether you're passing a function or CALLING it too early.""",
                    'exercises': [
                        {
                            'slug': 'arrow-object',
                            'title': 'Parens needed',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which arrow correctly returns an object {id: 1} when given id = 1?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'id => ({ id: id })', 'is_correct': True},
                                {'id': 'b', 'text': 'id => { id: id }', 'is_correct': False},
                                {'id': 'c', 'text': 'id => [id: id]', 'is_correct': False},
                                {'id': 'd', 'text': 'id -> ({ id })', 'is_correct': False},
                            ],
                            'explain': 'Without parens the brace opens a BLOCK and id: is a syntax error inside it.',
                        },
                        {
                            'slug': 'schedule-vs-call',
                            'title': 'The classic bug',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'setTimeout(greet(), 1000) — what happens?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'greet runs immediately; its RESULT is scheduled (and never called)', 'is_correct': True},
                                {'id': 'b', 'text': 'greet runs after 1 second', 'is_correct': False},
                                {'id': 'c', 'text': 'TypeError at the call', 'is_correct': False},
                                {'id': 'd', 'text': 'greet runs every second', 'is_correct': False},
                            ],
                            'explain': 'The parentheses invoke NOW. Pass the function itself: setTimeout(greet, 1000).',
                        },
                        {
                            'slug': 'default-undefined-only',
                            'title': 'When defaults apply',
                            'exercise_type': 'output_prediction',
                            'instructions': 'function f(x = 10) { return x; }  console.log(f(null));  What prints?',
                            'xp_reward': 40,
                            'expected_output': 'null',
                            'choices': [],
                            'explain': 'Defaults only catch undefined — null is a real value. Use x ?? 10 inside.',
                        },
                        {
                            'slug': 'rest-gathers',
                            'title': 'Rest role',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about  function sum(...nums).',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'nums is a real array inside the function', 'is_correct': True},
                                {'id': 'b', 'text': 'sum() with no args gives nums = []', 'is_correct': True},
                                {'id': 'c', 'text': 'nums gathers ONLY the first argument', 'is_correct': False},
                                {'id': 'd', 'text': 'It replaces the old arguments object cleanly', 'is_correct': True},
                            ],
                            'explain': 'Rest packs ALL remaining args into a proper Array (arguments was array-LIKE only).',
                        },
                    ],
                },
                {
                    'title': 'Scope and Hoisting',
                    'slug': 'scope-hoisting',
                    'objective': 'Explain block vs function scope, the temporal dead zone, and hoisting rules.',
                    'duration': 14,
                    'body': r"""# Where a name is visible

**Scope** = the region of code where a name can be used. JavaScript has
three nested levels:

1. **Global** — outside every function/block (module files have
   file-scope instead, chapter 7).
2. **Function scope** — parameters + locals of a function.
3. **Block scope** — `let`/`const` live only inside their `{ }` (the
   big `var` change: `var` leaks to function scope).

```js
let course = "React";              // outer scope
function show() {
  let course = "Django";           // SHADOWS the outer one in here
  console.log(course);             // "Django"
}
show();                            // no error — shadowing is legal
```

Name resolution walks outward: local → enclosing function → … →
global. A name found nowhere is a ReferenceError (or an accidental
implicit global with a plain assignment in sloppy scripts — one reason
modern code runs in strict/module mode).

## The var leaks

```js
function old() {
  if (true) {
    var leaked = 1;      // var ignores the block
  }
  console.log(leaked);   // 1 — visible here!
}
function modern() {
  if (true) {
    let blocked = 1;
  }
  console.log(blocked);  // ReferenceError — as intended
}
```

This is the entire motivation for `let`: loops and if-blocks stop
leaking variables into their whole function.

## Hoisting: the lift before the run

Before executing any scope, the engine registers declarations:

- `function f() {}` — fully lifted (callable anywhere in its scope).
- `let x` / `const x` — registered but UNINITIALISED: touching them
  before the declaration line throws
  (`Cannot access 'x' before initialization`). That pocket is the
  **temporal dead zone (TDZ)**.

```js
console.log(later);        // function runs fine — f is hoisted
function later() { return 42; }

console.log(early);        // ReferenceError — TDZ
let early = 1;
```

Hoisting is not "code runs top-to-bottom moved around" — think
*two passes*: declarations first, then statements. `const` in a
loop header is fine because each iteration gets a fresh binding —
which is what makes the closure in the next lesson behave.

## Closures need scope chains (preview)

```js
function counterFactory() {
  let count = 0;                 // lives on AFTER the function returns
  return () => ++count;          // because IT can still see the chain
}
```

The inner arrow keeps `count` alive — the topic of the next lesson.

## Common mistakes
- Declaring with `let` inside a block then using it outside (works
  with var habits; throws with let — good).
- Reassigning a `const` object's NAME vs its contents (chapter 1).
- "Hoisting makes let undefined early" — no: TDZ THROWS, which is the
  safer design.

## Lesson summary
Scope is nested look-up rings (innermost wins, shadowing allowed),
let/const honour blocks while var leaks, function declarations lift
fully, let/const wait in the TDZ — and the closure preview shows why
the chain matters even after a function returns.""",
                    'exercises': [
                        {
                            'slug': 'shadow-value',
                            'title': 'Which wins',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let x = 1; function f() { let x = 2; return x; } console.log(f() + x);  Output?',
                            'xp_reward': 40,
                            'expected_output': '3',
                            'choices': [],
                            'explain': 'f sees its own 2; global x is still 1. 2 + 1 = 3.',
                        },
                        {
                            'slug': 'var-leak',
                            'title': 'Block behaviour',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'let inside an if-block, used after the block: ',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'ReferenceError — let is block-scoped', 'is_correct': True},
                                {'id': 'b', 'text': 'Works — all scopes are function-wide', 'is_correct': False},
                                {'id': 'c', 'text': 'undefined but no error', 'is_correct': False},
                                {'id': 'd', 'text': 'TypeError only in strict mode', 'is_correct': False},
                            ],
                            'explain': 'With var it would leak (undefined-before/after quirks aside); let closed that door.',
                        },
                        {
                            'slug': 'tdz-rule',
                            'title': 'Temporal dead zone',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about the TDZ.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'It covers let/const between scope start and their declaration', 'is_correct': True},
                                {'id': 'b', 'text': 'Reading a TDZ variable throws ReferenceError', 'is_correct': True},
                                {'id': 'c', 'text': 'It also applies to var declarations', 'is_correct': False},
                                {'id': 'd', 'text': 'It turns use-before-declare bugs into loud errors', 'is_correct': True},
                            ],
                            'explain': 'var hoists as initialised-undefined; let/const hoist UNINITIALISED — touching early is fatal.',
                        },
                        {
                            'slug': 'hoist-call',
                            'title': 'Declaration lift',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log(hi()); function hi() { return "hey"; }  What prints? (one lower-case word)',
                            'xp_reward': 40,
                            'expected_output': 'hey',
                            'choices': [],
                            'explain': 'Whole function declarations hoist — calling first is legal (if surprising).',
                        },
                    ],
                },
                {
                    'title': 'Closures',
                    'slug': 'closures',
                    'objective': 'Identify a closure, explain what it captures, and build practical ones.',
                    'duration': 15,
                    'body': r"""# The function that remembers

A **closure** = a function bundled with the scope it was born in. When
the inner arrow in `counterFactory` (previous lesson) escapes as a
return value, it does not lose `count` — the variable stays alive,
exactly as if the function carried a backpack of its birth scope.

```js
function makeCounter(start = 0) {
  let count = start;                    // normally dies with the call...
  return {
    increment: () => ++count,           // ...but the closures capture it
    get: () => count,
  };
}

const clicks = makeCounter();
clicks.increment();  clicks.increment();
clicks.get();        // 2 — and NOTHING can touch count from outside
clicks.count;        // undefined — private state, enforced by scope
```

Two separate calls of `makeCounter` create two independent backpacks:

```js
const a = makeCounter(10), b = makeCounter(100);
a.increment();   // a: 11, b unaffected
```

That is the whole power trip: **data privacy without classes**. Java
needs `private`; JavaScript closures give the same guarantee with
plain scope — and React hooks (`useState`) are closures over state
under the hood.

## The loop classic (and its fix)

```js
for (var i = 1; i <= 3; i++) {
  setTimeout(() => console.log(i), 100);     // logs 4 4 4 (!)
}
for (let i = 1; i <= 3; i++) {
  setTimeout(() => console.log(i), 100);     // logs 1 2 3
}
```

`var` shares ONE i; by the time the timers fire, i is 4. `let` gives
each iteration a FRESH binding (the loop machinery copies it) — three
different backpacks. If you must support var-era code, the third
pattern is an IIFE factory: `setTimeout(makePrinter(i), 100)` where
`makePrinter(n) { return () => console.log(n); }`.

## Practical closures you will actually write

```js
const withTax = rate => price => price * (1 + rate);   // curried
const vat15 = withTax(0.15);  vat15(1000);             // 1150

function once(fn) {                  // run-at-most-once guard
  let done = false;
  return (...args) => {
    if (done) return;
    done = true;
    return fn(...args);
  };
}
const init = once(() => console.log("booting"));
init(); init();                      // logs exactly once
```

Function factories, memoisation caches, event handlers that remember
state — closures are the plumbing of "modern JavaScript" (and of
chapter 11's async patterns). (Note: `...args` rest works in arrows too —
`arguments` does NOT live inside an arrow.)

## Common mistakes
- Thinking the captured value is a SNAPSHOT — closures capture the
  VARIABLE (live binding), not its value at creation time (that is why
  var-logs-4 happens).
- Reaching for `arguments` inside an arrow — silent TypeError; use rest
  parameters.
- Leaking big objects "into" long-lived closures by accident (the
  backpack keeps everything referenced alive — the modern equivalent of
  old memory-leak interview questions).

## Lesson summary
A closure is a function plus its surviving birth scope: it gives real
privacy, per-iteration bindings with let, function factories, and once
— and understanding the LIVE capture of variables explains every
famous loop bug.""",
                    'exercises': [
                        {
                            'slug': 'closure-privacy',
                            'title': 'What is 2 here',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const c = makeCounter(5) from the lesson; c.increment(); c.increment(); console.log(c.get());  Output?',
                            'xp_reward': 40,
                            'expected_output': '7',
                            'choices': [],
                            'explain': 'Both closures share one count backpack: 5 -> 6 -> 7.',
                        },
                        {
                            'slug': 'closure-private',
                            'title': 'Outside reach',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why is count effectively private in makeCounter?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'No outer code can name it — only the returned closures see that scope', 'is_correct': True},
                                {'id': 'b', 'text': 'const froze it', 'is_correct': False},
                                {'id': 'c', 'text': 'Garbage collector deletes it after the call', 'is_correct': False},
                                {'id': 'd', 'text': 'A #private field hides it', 'is_correct': False},
                            ],
                            'explain': 'Scope itself is the access control — the JS analogue of Java private.',
                        },
                        {
                            'slug': 'loop-var-answer',
                            'title': 'The var loop',
                            'exercise_type': 'output_prediction',
                            'instructions': 'The FIRST loop in the lesson (with var) prints three values like "4 4 4". What is the SECOND value? (just the digit)',
                            'xp_reward': 40,
                            'expected_output': '4',
                            'choices': [],
                            'explain': 'One shared i; every closure reads the SAME final 4.',
                        },
                        {
                            'slug': 'let-fresh-binding',
                            'title': 'Why let fixes it',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Each iteration of a for-let loop gets:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'A fresh binding copied from the previous value', 'is_correct': True},
                                {'id': 'b', 'text': 'A hoisted global', 'is_correct': False},
                                {'id': 'c', 'text': 'The same shared variable as var', 'is_correct': False},
                                {'id': 'd', 'text': 'A frozen constant', 'is_correct': False},
                            ],
                            'explain': 'The spec\u2019s for-let per-iteration copy is what timers capture — 1 2 3.',
                        },
                        {
                            'slug': 'curried-call',
                            'title': 'Function factories',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const add = a => b => a + b;  console.log(add(3)(4));  Output?',
                            'xp_reward': 40,
                            'expected_output': '7',
                            'choices': [],
                            'explain': 'add(3) returns the inner closure with a=3 backpacked; calling it with 4 gives 7.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 4 Quiz',
                    'slug': 'js-functions-quiz',
                    'objective': 'Check mastery of function forms, scope rules and closures.',
                    'duration': 8,
                    'body': """# Chapter 4 quiz

Five questions on functions and scope — the machinery React hooks are
built on, so worth getting permanently right.""",
                    'exercises': [
                        {
                            'slug': 'q4-arrow-implicit',
                            'title': 'Implicit return',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const f = x => x * x;  console.log(f(6));  Output?',
                            'xp_reward': 50,
                            'expected_output': '36',
                            'choices': [],
                            'explain': 'Brace-less arrow body IS the return value.',
                        },
                        {
                            'slug': 'q4-hoist-var',
                            'title': 'var early read',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log(typeof v); var v = 1;  What prints?',
                            'xp_reward': 50,
                            'expected_output': 'undefined',
                            'choices': [],
                            'explain': 'var hoists DECLARED but uninitialised; let would throw (TDZ).',
                        },
                        {
                            'slug': 'q4-closure-survival',
                            'title': 'Why count lives',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A returned closure keeps its outer variable alive because:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The function still references that scope, so GC cannot free it', 'is_correct': True},
                                {'id': 'b', 'text': 'let values are stored globally', 'is_correct': False},
                                {'id': 'c', 'text': 'return makes a copy of every variable', 'is_correct': False},
                                {'id': 'd', 'text': 'closures run a cleanup timer', 'is_correct': False},
                            ],
                            'explain': 'Reachability: the closure\u2019s scope chain is a live reference path.',
                        },
                        {
                            'slug': 'q4-once-count',
                            'title': 'once() behaviour',
                            'exercise_type': 'output_prediction',
                            'instructions': 'Using the lesson\u2019s once(): how many times does the wrapped function run if you call the result 5 times? (just the digit)',
                            'xp_reward': 50,
                            'expected_output': '1',
                            'choices': [],
                            'explain': 'The done flag flips inside the same shared backpack.',
                        },
                        {
                            'slug': 'q4-default-null',
                            'title': 'Defaults scope',
                            'exercise_type': 'multiple_select',
                            'instructions': 'function f(a = 1, b = 2) {...}  Select ALL calls where a default IS used.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'f()', 'is_correct': True},
                                {'id': 'b', 'text': 'f(undefined, 5)', 'is_correct': True},
                                {'id': 'c', 'text': 'f(null, 5)', 'is_correct': False},
                                {'id': 'd', 'text': 'f(0, 0)', 'is_correct': False},
                            ],
                            'explain': 'Only undefined triggers defaults — null and 0 are values the author passed on purpose.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 5 ════════════════════
        {
            'title': 'Arrays and Objects',
            'slug': 'js-arrays-objects',
            'description': 'Array anatomy and methods, object property access and this, JSON and destructuring.',
            'lessons': [
                {
                    'title': 'Arrays: The Daily Methods',
                    'slug': 'array-basics',
                    'objective': 'Create, mutate and read arrays with the methods real code uses.',
                    'duration': 15,
                    'body': r"""# Ordered lists of anything

```js
const names = ["Ali", "Sara", "Bilal"];    // literal syntax, mixed types allowed
names.length          // 3 — a PROPERTY
names[0]              // "Ali"  — 0-based like every language worth its salt
names[99]             // undefined — reading past the end is SILENT
names[99] = "ghost";  // legal! length jumps to 100 with holes. Don't.
```

Arrays grow and shrink freely — no size declaration (unlike Java).
Push/pop/shift/unshift are the four ends:

```js
const q = [1, 2, 3];
q.push(4);        // [1,2,3,4]  add to END     -> returns new length
q.pop();          // [1,2,3]    remove END     -> returns removed item
q.shift();        // [2,3]      remove FRONT  -> returns it (O(n)!)
q.unshift(1);     // [1,2,3]    add to FRONT
```

## Finding and locating

```js
const marks = [45, 92, 78, 92];
marks.includes(92);            // true — value presence
marks.indexOf(92);             // 1    — first index (-1 if absent)
marks.findIndex(m => m >= 90); // 1    — first index by TEST
marks.find(m => m >= 90);      // 92   — the VALUE itself
```

`find` returns the element (or undefined), `findIndex` the position —
both stop at the first match. This pair replaces most hand-written
loops from chapter 3.

## Changing shape

```js
const a = [1, 2], b = [3, 4];
a.concat(b);        // [1,2,3,4]  — a and b UNCHANGED
[...a, ...b];       // same thing, modern way (spread, chapter 7)
a.slice(1);         // copy from index 1: [2]        — non-mutating
a.splice(0, 1);     // REMOVE 1 item at index 0 — MUTATES, returns removed
const nums = [3, 1, 2];
nums.sort();            // [1,2,3] — LEXICAL by default!
nums.sort((x, y) => x - y);   // numeric ascending — always pass this
nums.reverse();         // in-place flip
```

The two landmines, every interview includes one:

1. `sort()` without a comparator turns numbers into strings: `[10, 9,
   1].sort()` → `[1, 10, 9]`. ALWAYS pass `(a, b) => a - b` for
   numbers.
2. `sort`, `reverse`, `splice`, `push`, `pop`, `shift`, `unshift`,
   `fill` all MUTATE the array; `slice`, `concat`, `map`, `filter`,
   `reduce` do NOT. When state must not change (React!), copy first:
   `[...items].sort()` or `items.slice().sort()`.

## Iterating

```js
names.forEach(n => console.log(n));       // side effects only, returns undefined
const upper = names.map(n => n.toUpperCase());   // NEW array, same length
const passing = marks.filter(m => m >= 50);      // NEW array, subset
const total = marks.reduce((t, m) => t + m, 0);  // ONE value (107)
marks.join(", ");        // "45, 92, 78, 92"
"45, 92".split(", ");    // ["45", "92"]  — string method, gives array
```

`map/filter/reduce` are chapter 6's starring trio.

## Arrays are objects (the trivia floor)

```js
Array.isArray(names);    // true  — the RIGHT test
typeof names;            // "object" (chapter 2 lie #2)
names["weird"] = 1;      // legal — arrays accept string keys too!
names.length;            // still 4 — named keys do NOT count
```

An array is an object with a magic `length` and integer-key behaviour;
that is all the explanation interviews want for the oddities above.

## Common mistakes
- Numeric sorts without the comparator.
- Mutating a state array in place, then React not re-rendering
  (chapter 11) because the reference never changed.
- `for (let i = 0; i <= arr.length; i++)` — the `<=` visits undefined.
- Comparing arrays with `==`/`===`: `[1] === [1]` is false — same
  contents, different objects (reference identity, chapter 5).

## Lesson summary
Four ends, find-family by test, the mutate-vs-copy split (and the
always-pass-a-comparator rule for sort), and the trio preview —
map/filter/reduce is how modern JavaScript says "transform this list".""",
                    'exercises': [
                        {
                            'slug': 'sort-default-trap',
                            'title': 'Lexical sort',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log([10, 9, 1].sort().join(","));  Output? (comma-separated, no spaces)',
                            'xp_reward': 40,
                            'expected_output': '1,10,9',
                            'choices': [],
                            'explain': 'Default sort compares STRING forms: "1" < "10" < "9". Pass (a,b)=>a-b for numbers.',
                        },
                        {
                            'slug': 'splice-vs-slice',
                            'title': 'Which mutates',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL methods that CHANGE the original array.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'splice', 'is_correct': True},
                                {'id': 'b', 'text': 'slice', 'is_correct': False},
                                {'id': 'c', 'text': 'push', 'is_correct': True},
                                {'id': 'd', 'text': 'concat', 'is_correct': False},
                            ],
                            'explain': 'splice/push mutate; slice/concat return copies — the pair the interview loves.',
                        },
                        {
                            'slug': 'find-vs-indexof',
                            'title': 'By test',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'First student with mark >= 90, needing the student object itself:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'students.find(s => s.mark >= 90)', 'is_correct': True},
                                {'id': 'b', 'text': 'students.findIndex(s => s.mark >= 90)', 'is_correct': False},
                                {'id': 'c', 'text': 'students.includes(s => s.mark >= 90)', 'is_correct': False},
                                {'id': 'd', 'text': 'students.filter(s => s.mark >= 90)', 'is_correct': False},
                            ],
                            'explain': 'find returns the element; findIndex the position; filter an array of ALL matches.',
                        },
                        {
                            'slug': 'out-of-range-read',
                            'title': 'Past the end',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const a = [1, 2]; console.log(a[5]);  What prints? (one lower-case word)',
                            'xp_reward': 40,
                            'expected_output': 'undefined',
                            'choices': [],
                            'explain': 'Reading out of range gives undefined silently (writing it would create a hole).',
                        },
                        {
                            'slug': 'isarray-test',
                            'title': 'Correct check',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The reliable way to test "is this an array?"',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Array.isArray(x)', 'is_correct': True},
                                {'id': 'b', 'text': 'typeof x === "array"', 'is_correct': False},
                                {'id': 'c', 'text': 'x.length !== undefined', 'is_correct': False},
                                {'id': 'd', 'text': 'x instanceof Array only — always', 'is_correct': False},
                            ],
                            'explain': 'typeof says object; length checks pass for arguments-like things; isArray is the tool.',
                        },
                    ],
                },
                {
                    'title': 'Objects: Properties, this, and Passing Them Around',
                    'slug': 'object-basics',
                    'objective': 'Create and manipulate objects, choose bracket vs dot access, explain this.',
                    'duration': 15,
                    'body': r"""# Key-value everything

```js
const student = {
  name: "Amina",          // identifier keys need no quotes
  "roll no": 12,          // spaces require quotes
  gpa: 3.6,
  enrolled: true,
  introduce() {           // method shorthand
    return `I am ${this.name}, GPA ${this.gpa}`;
  },
};

student.name;             // "Amina"  — dot when you KNOW the key
student["roll no"];       // 12       — bracket when the key is dynamic/expression
const k = "gpa";
student[k];               // 3.6      — the whole point of bracket access
student.city = "Karachi"; // create OR update with one assignment
delete student.enrolled;  // remove a property
Object.keys(student);     // ["name", "roll no", "gpa", "city"]
Object.values(student);   // the values, same order (insertion order for strings)
Object.entries(student);  // [[key, value], ...] — pairs for maps/loops
```

## Reference semantics — the Java contrast clarified

Objects (and arrays/functions) are handled by REFERENCE:

```js
const a = { score: 1 };
const b = a;              // SAME object, two names
b.score = 99;
a.score;                  // 99 (!)
a === b;                  // true — identity, not equality of contents
const c = { score: 99 };
c === a;                  // false — identical contents, different object
```

Assigning an object never copies it; to copy, spread it shallowly:
`const copy = { ...a }` (one level deep — nested objects still share
references; the "deep copy" question is chapter 7 territory).
This is why React insists you replace state objects instead of
mutating them, and why `sort()` on a state array broke things.

## this: the call-site rule

Inside a normal (non-arrow) function, `this` is decided by HOW the
function is CALLED, not where it is written:

```js
const obj = { name: "X", get() { return this.name; } };
obj.get();                // "X" — called as obj.something -> this = obj
const f = obj.get;
f();                    // undefined — bare call -> this is undefined (strict)
setTimeout(obj.get, 100); // BROKEN for the same reason
setTimeout(() => obj.get(), 100);  // fine — arrow borrows the outer scope
```

Rules of thumb that survive real code:

- `obj.method()` → `this` is `obj`. Everything else → unreliable.
- Arrows have NO own `this`; they use the surrounding one — which is
  why callbacks and React handlers prefer them.
- Legacy patterns (`bind`, `const self = this`) exist; recognise them
  but write arrows.

## Optional chaining and friends (ES2020)

```js
const city = order?.customer?.address?.city;   // undefined instead of TypeError
order.customer ?? { guest: true };             // fallback when null/undefined
customer.name ||= "anonymous";                 // assign-if-nullish (logical assignment)
```

`?.` replaced the `a && a.b && a.b.c` chains — same short-circuit,
fewer typographical gymnastics. You will see it constantly reading real
React code.

## Common mistakes
- `student[name]` when you wanted the KEY named name (dot) — bracket
  evaluates its inside as an expression.
- Passing an "unchanged" object into a function and trusting the
  function not to mutate it — reference means shared power.
- Method extracted from object losing `this` (the setTimeout trap).
- Deep-equality confusion: `===` on objects is identity; compare with
  JSON.stringify only for toy cases, real code compares chosen fields.

## Lesson summary
Dot vs bracket is "known vs computed", creation/update is plain
assignment, the Object.* trio turns objects into arrays for looping,
references are shared not copied, and this follows the call site —
with arrows opting out entirely.""",
                    'exercises': [
                        {
                            'slug': 'reference-shared',
                            'title': 'Two names',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const p = {x:1}; const q = p; q.x = 5; console.log(p.x);  Output?',
                            'xp_reward': 40,
                            'expected_output': '5',
                            'choices': [],
                            'explain': 'q and p are name tags on ONE object; q.x wrote through to p.',
                        },
                        {
                            'slug': 'bracket-when',
                            'title': 'Dynamic key',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Given let field = "gpa", read student.gpa:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'student[field]', 'is_correct': True},
                                {'id': 'b', 'text': 'student.field', 'is_correct': False},
                                {'id': 'c', 'text': 'student.(field)', 'is_correct': False},
                                {'id': 'd', 'text': 'student{field}', 'is_correct': False},
                            ],
                            'explain': 'Dot looks up the LITERAL name; bracket evaluates the expression.',
                        },
                        {
                            'slug': 'this-lost',
                            'title': 'Call site',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'const f = obj.get; f();  Inside get(), this is (strict mode):',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'undefined — the obj. prefix was lost', 'is_correct': True},
                                {'id': 'b', 'text': 'obj — methods remember their owner', 'is_correct': False},
                                {'id': 'c', 'text': 'the global window always', 'is_correct': False},
                                {'id': 'd', 'text': 'null', 'is_correct': False},
                            ],
                            'explain': 'this is the CALL prefix, not the definition site. Fix: arrow wrapper or bind.',
                        },
                        {
                            'slug': 'optional-chain',
                            'title': '?. safety',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const o = {a: {}}; console.log(o.a?.b?.c);  What prints? (one lower-case word)',
                            'xp_reward': 40,
                            'expected_output': 'undefined',
                            'choices': [],
                            'explain': 'Short-circuit: any missing link yields undefined without throwing.',
                        },
                        {
                            'slug': 'spread-shallow',
                            'title': 'Copy depth',
                            'exercise_type': 'multiple_select',
                            'instructions': 'const copy = { ...orig };  Select ALL true statements.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Top-level values are copied into a new object', 'is_correct': True},
                                {'id': 'b', 'text': 'Nested objects still share references with orig', 'is_correct': True},
                                {'id': 'c', 'text': 'It is a full deep clone', 'is_correct': False},
                                {'id': 'd', 'text': 'Mutating a nested object via copy affects orig too', 'is_correct': True},
                            ],
                            'explain': 'Shallow is the operative word — one layer new, everything below shared.',
                        },
                    ],
                },
                {
                    'title': 'JSON and Destructuring',
                    'slug': 'json-destructuring',
                    'objective': 'Convert objects to JSON text and unpack arrays/objects with destructuring.',
                    'duration': 12,
                    'body': r"""# JSON: objects on a wire

**JSON** (JavaScript Object Notation) is a text format — the lingua
franca every backend and frontend speak. JavaScript can convert
between objects and JSON strings:

```js
const student = { name: "Aya", marks: [90, 85], active: true };

const text = JSON.stringify(student);      // object -> string
// '{"name":"Aya","marks":[90,85],"active":true}'

const back = JSON.parse(text);             // string -> object
back.marks.length;                          // 2 — a REAL object again

localStorage.setItem("profile", text);      // storage only takes strings
const saved = JSON.parse(localStorage.getItem("profile"));
```

What survives the round trip: objects, arrays, strings, numbers,
booleans, null. What does NOT: functions (dropped), `undefined`
properties (dropped), `Date` objects (become strings), Maps/Sets
(lose everything), and cycles (TypeError — use a replacer or a
library). JSON keys are always double-quoted — hand-writing it with
single quotes is the classic `JSON.parse` SyntaxError.

`JSON.stringify(value, null, 2)` adds 2-space indentation — the debug
printer you will actually use.

## Destructuring: naming the parts

```js
// array pattern — POSITION matters
const [first, second] = [10, 20, 30];        // first=10, second=20
const [head, ...tail] = [1, 2, 3, 4];        // head=1, tail=[2,3,4]
const [, , third] = [1, 2, 3];               // skip slots with empties

// object pattern — NAME matters (order does not)
const { name, marks } = student;             // same names, done
const { name: fullName, gpa = 3.0 } = student;  // rename + default

function greet({ name, gpa }) { ... }        // parameter destructuring

// swap without temp:
[a, b] = [b, a];
```

Destructuring is bookkeeping made free: React's `const { title,
children } = props` and `const [count, setCount] = useState(0)` are
both this one idea. `...` in a pattern is REST (gather); `...` at a
use site is SPREAD (scatter) — same three dots, opposite verbs:

```js
const merged = { ...defaults, ...overrides };   // later key wins
const all = [...arr1, ...arr2];
```

That spread-merge is how React updates state immutably:
`setUser({ ...user, name: typed })` — new object, one field changed.

## Common mistakes
- `JSON.parse(object)` — parse takes a STRING; stringify makes one.
- Expecting a Date or Map to come back intact from JSON. It will not;
  revive it explicitly (`new Date(text.createdAt)`).
- Single quotes or trailing commas in hand-written JSON.
- Destructuring null/undefined throws ("Cannot destructure 'x' of
  undefined") — guard or default the whole source: `const { a } = obj
  || {}`.

## Lesson summary
stringify/parse bridge objects and text (with known losses), array
patterns unpack by position, object patterns by name, rest/spread are
two directions of the same dots, and rename+default syntax covers the
awkward cases — the exact grammar React code is written in.""",
                    'exercises': [
                        {
                            'slug': 'json-dropped',
                            'title': 'What survives',
                            'exercise_type': 'multiple_select',
                            'instructions': 'JSON.stringify omits (does NOT throw on) which of these?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Function-valued properties', 'is_correct': True},
                                {'id': 'b', 'text': 'undefined-valued properties', 'is_correct': True},
                                {'id': 'c', 'text': 'Number values like NaN (become null)', 'is_correct': True},
                                {'id': 'd', 'text': 'Nested arrays', 'is_correct': False},
                            ],
                            'explain': 'Arrays serialize fine; functions/undefined vanish quietly and NaN turns into null.',
                        },
                        {
                            'slug': 'destructure-rename',
                            'title': 'Rename syntax',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Take student.gpa into a variable named score with default 0:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'const { gpa: score = 0 } = student', 'is_correct': True},
                                {'id': 'b', 'text': 'const { score: gpa = 0 } = student', 'is_correct': False},
                                {'id': 'c', 'text': 'const { gpa = 0 as score } = student', 'is_correct': False},
                                {'id': 'd', 'text': 'const [gpa: score = 0] = student', 'is_correct': False},
                            ],
                            'explain': 'key: newName = default — read it left to right as a mapping.',
                        },
                        {
                            'slug': 'rest-vs-spread',
                            'title': 'Same dots, opposite jobs',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'const [a, ...rest] = nums;  — here ...rest is:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'REST: gathering the remaining items into a new array', 'is_correct': True},
                                {'id': 'b', 'text': 'SPREAD: expanding nums into the array', 'is_correct': False},
                                {'id': 'c', 'text': 'A slice reference — changes to a change rest', 'is_correct': False},
                                {'id': 'd', 'text': 'A shorthand for the last element', 'is_correct': False},
                            ],
                            'explain': 'Inside a PATTERN dots gather (rest); at use sites they scatter (spread).',
                        },
                        {
                            'slug': 'merge-order',
                            'title': 'Later wins',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const o = { ...{a:1, b:2}, ...{b:9} }; console.log(o.b);  Output?',
                            'xp_reward': 40,
                            'expected_output': '9',
                            'choices': [],
                            'explain': 'Spread applies left to right; the second b overwrites the first.',
                        },
                        {
                            'slug': 'parse-vs-stringify',
                            'title': 'Direction check',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Reading a JSON string FROM a server into a usable object requires:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'JSON.parse', 'is_correct': True},
                                {'id': 'b', 'text': 'JSON.stringify', 'is_correct': False},
                                {'id': 'c', 'text': 'eval(text) — same thing', 'is_correct': False},
                                {'id': 'd', 'text': 'Number(text)', 'is_correct': False},
                            ],
                            'explain': 'parse = text in, object out. (And never eval untrusted text — parse validates instead.)',
                        },
                    ],
                },
                {
                    'title': 'Chapter 5 Quiz',
                    'slug': 'js-arrays-objects-quiz',
                    'objective': 'Check mastery of arrays, objects, JSON and destructuring.',
                    'duration': 8,
                    'body': """# Chapter 5 quiz

Five questions on the two data structures and the text bridge between
them.""",
                    'exercises': [
                        {
                            'slug': 'q5-length-prop',
                            'title': 'After the ends',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const a = [1,2,3]; a.push(4); a.pop(); a.shift(); console.log(a.length);  Output?',
                            'xp_reward': 50,
                            'expected_output': '2',
                            'choices': [],
                            'explain': '+1, -1, then removed the front: [2,3] left, length 2.',
                        },
                        {
                            'slug': 'q5-map-shape',
                            'title': 'What map returns',
                            'exercise_type': 'multiple_choice',
                            'instructions': '[1,2,3].map(n => n * 2) produces:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'A NEW array [2,4,6]; the original unchanged', 'is_correct': True},
                                {'id': 'b', 'text': 'The original mutated to [2,4,6]', 'is_correct': False},
                                {'id': 'c', 'text': 'The single value 12', 'is_correct': False},
                                {'id': 'd', 'text': 'undefined', 'is_correct': False},
                            ],
                            'explain': 'map: same length, transformed items, no mutation. reduce would fold to one value.',
                        },
                        {
                            'slug': 'q5-json-type',
                            'title': 'Stringify result',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log(typeof JSON.stringify({a: 1})[0]);  What prints? (the typeof of the FIRST CHARACTER)',
                            'xp_reward': 50,
                            'expected_output': 'string',
                            'choices': [],
                            'explain': 'stringify returns a string; indexing gives its first char "{" — still a string.',
                        },
                        {
                            'slug': 'q5-swap',
                            'title': 'Destructuring swap',
                            'exercise_type': 'output_prediction',
                            'instructions': 'let x = 1, y = 2; [x, y] = [y, x]; console.log(`${x}${y}`);  Output?',
                            'xp_reward': 50,
                            'expected_output': '21',
                            'choices': [],
                            'explain': 'The array literal evaluates fully first (2,1), then unpacks: x=2, y=1.',
                        },
                        {
                            'slug': 'q5-object-keys',
                            'title': 'Keys order',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Object.keys({b: 1, a: 2, 3: "x"}) returns the keys in:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Integer-like keys first ("3"), then insertion order: ["3", "b", "a"]', 'is_correct': True},
                                {'id': 'b', 'text': 'Strict insertion order always', 'is_correct': False},
                                {'id': 'c', 'text': 'Sorted alphabetically', 'is_correct': False},
                                {'id': 'd', 'text': 'Random each call', 'is_correct': False},
                            ],
                            'explain': 'JS objects order integer-like keys ascending first — an old engine quirk now in the spec.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 6 ════════════════════
        {
            'title': 'Array Methods at Depth',
            'slug': 'js-array-methods',
            'description': 'The higher-order trio and their supporting cast, chained into real data pipelines.',
            'lessons': [
                {
                    'title': 'forEach, map and filter',
                    'slug': 'map-filter',
                    'objective': 'Replace index loops with the three iteration methods and know their contracts.',
                    'duration': 14,
                    'body': r"""# Three jobs, three tools

```js
const nums = [1, 2, 3, 4, 5, 6];

nums.forEach(n => console.log(n * n));     // side effects; returns UNDEFINED
const squares = nums.map(n => n * n);      // 1:1 transform; NEW array same size
const evens = nums.filter(n => n % 2 === 0);  // subset; NEW array, any size
```

The contract table interviewers probe:

| Method | Callback answers | Returns | Mutates? |
|---|---|---|---|
| `forEach` | "do this" | undefined | no |
| `map` | "what value for this item?" | new array, SAME length | no |
| `filter` | "keep or drop?" (truthy = keep) | new array, subset | no |

All three pass `(item, index, array)` to the callback — you usually
name only the first. `map` is NOT a loop that "sometimes returns
undefined"; if your callback has no return, every slot becomes
undefined — a linter error (`array-callback-return`) precisely because
it is a bug in disguise.

## Worked examples (the shapes you will meet)

```js
const students = [
  { name: "Amina", gpa: 3.8 },
  { name: "Bilal", gpa: 2.9 },
  { name: "Sara",  gpa: 3.6 },
];

const names = students.map(s => s.name);        // ["Amina","Bilal","Sara"]
const honor = students.filter(s => s.gpa >= 3.5);  // 2 students
const cards = students.map(s => `<li>${s.name}</li>`).join("");
// template-per-item + join = the classic "render a list" pattern —
// React does the same thing with JSX (chapter 10).
```

## Chaining: pipelines read left to right

```js
const report = students
  .filter(s => s.gpa >= 3.5)
  .map(s => s.name.toUpperCase())
  .sort();
// each link gets the PREVIOUS link's array — no temp variables
```

Chain order can matter for speed (filter before map avoids
transforming items you will drop) and for correctness (sort before
slice). Each link allocates a new array — fine at web scale; if it
bothers you, that is what loop loyalists defend, and they are not
wrong, just reading different trade-offs.

## forEach vs the others — the honest advice

`forEach` is fine when you truly want side effects (logging, pushing
into an external array). But half of real `forEach` usage is a
`map`/`filter` in disguise — and the disguised ones are harder to
read. "Prefer map/filter" is the modern style rule for a reason:
declared transformation beats imperative accretion.

## Common mistakes
- `const x = nums.map(n => { n * 2 })` — braces + no return = array of
  undefined. Arrow bodies: braces mean statements.
- Using `filter` to CHANGE items (it only selects) or `map` to remove
  (it cannot; `flatMap(n => cond ? [n] : [])` can).
- Expecting `forEach` to return something useful. It never does.
- Mutating the source array inside the callback — iteration counts
  change mid-flight (see the splice trap below).

## Lesson summary
forEach acts, map converts, filter selects — all copy-free, all
take (item, index, array), and chaining them turns noun data into
verb pipelines.""",
                    'exercises': [
                        {
                            'slug': 'map-brace-trap',
                            'title': 'Braces are statements',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log([1,2].map(x => { x * 2 }).join(","));  Output? (two words, comma between)',
                            'xp_reward': 40,
                            'expected_output': 'undefined,undefined',
                            'choices': [],
                            'explain': 'The braced body never returns — every slot is undefined.',
                        },
                        {
                            'slug': 'filter-contract',
                            'title': 'Keep rule',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'filter keeps an item when the callback returns:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'anything truthy', 'is_correct': True},
                                {'id': 'b', 'text': 'exactly true', 'is_correct': False},
                                {'id': 'c', 'text': 'the item itself', 'is_correct': False},
                                {'id': 'd', 'text': 'a number > 0', 'is_correct': False},
                            ],
                            'explain': 'filter is if() in method form — truthiness rules apply.',
                        },
                        {
                            'slug': 'chain-result',
                            'title': 'Pipeline trace',
                            'exercise_type': 'output_prediction',
                            'instructions': '[5,1,9].filter(n => n > 2).map(n => n * 2).join("-");  Result string?',
                            'xp_reward': 40,
                            'expected_output': '10-18',
                            'choices': [],
                            'explain': 'filter keeps 5,9 -> map doubles -> join hyphenates: "10-18".',
                        },
                        {
                            'slug': 'removing-while-looping',
                            'title': 'Splice during iteration',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'array.splice(...) inside a forEach over that SAME array typically:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Skips elements — indices shift mid-iteration', 'is_correct': True},
                                {'id': 'b', 'text': 'Works perfectly, that is the idiom', 'is_correct': False},
                                {'id': 'c', 'text': 'Throws immediately', 'is_correct': False},
                                {'id': 'd', 'text': 'Auto-copies the array first', 'is_correct': False},
                            ],
                            'explain': 'Use filter into a new array (or reverse loops) — mutating while iterating drops neighbours.',
                        },
                    ],
                },
                {
                    'title': 'reduce, some, every and the Rest',
                    'slug': 'reduce-search',
                    'objective': 'Fold arrays to one value and answer yes/no questions about them.',
                    'duration': 14,
                    'body': r"""# reduce: many into one

`reduce(callback, initial)` walks the array carrying one value
forward. The callback is `(accumulator, item) => nextAccumulator`:

```js
const nums = [3, 1, 4, 1, 5];

nums.reduce((acc, n) => acc + n, 0);        // 14  — sum
nums.reduce((acc, n) => Math.max(acc, n), -Infinity);   // 5 — max
nums.reduce((acc, n) => acc * n, 1);        // 60  — product

// the flagship example: count by key
const marks = ["A", "B", "A", "C", "A", "B"];
const tally = marks.reduce((acc, m) => {
  acc[m] = (acc[m] || 0) + 1;
  return acc;
}, {});                        // {A:3, B:2, C:1}
```

Trace `sum` on [3,1,4]: acc=0 -> 3 -> 4 -> 8. Always think "what is
the ONE thing I am building, and how does each item change it?"

Reduce rules that keep you safe:
- **Always pass the initial value.** `nums.reduce((a,n)=>a+n)` with no
  0 uses the first ELEMENT as initial — works for sum, but explodes on
  empty arrays (`TypeError: Reduce of empty array`) and does weird
  things on mixed types.
- You can return ANY accumulator shape: number, string, object, even
  an array (reduce can emulate map/filter — but do not, that is
  chaining's job).

## some / every: questions, not transformations

```js
nums.some(n => n > 100);     // false — "does ANY match?" (short-circuits)
nums.every(n => n > 0);      // true  — "do ALL match?" (short-circuits)
```

Both return booleans and stop early — they are `find`'s yes/no
siblings. `includes`/`indexOf` for values; `some`/`every`/`find` for
tests.

## The supporting cast worth memorising

```js
nums.flat(1);                       // flatten one level ([[1,2],[3]] -> [1,2,3])
[1,2].flatMap(n => [n, n * 10]);    // map + flatten in one pass: [1,10,2,20]
nums.at(-1);                        // 5 — negative indexing, modern slice-of-last
Array.from("Code");                 // ["C","o","d","e"] — iterable -> array
Array.from({length: 3}, (_, i) => i * i);  // [0,1,4] — the range trick
[...new Set([1,1,2])];              // [1,2] — the one-line dedupe (Set: chapter 7)
nums.fill(0, 1, 3);                 // mutate indices 1..2 to 0
```

`flatMap` quietly replaces two older idioms: `.map(...).flat()` and
the filter-out-undefined hack for one-to-zero mappings.

## Choosing: the decision list

| I want… | use |
|---|---|
| side effects per item | forEach |
| a same-size new array | map |
| a subset | filter |
| one total/combined value | reduce |
| the first match | find |
| yes/no any/all | some / every |
| a joined string | join |
| one-to-many expansion | flatMap |

## Common mistakes
- reduce without initial value on data that may be empty.
- Forgetting `return acc` in the braced reduce callback — accumulator
  becomes undefined on round two (the #1 reduce bug by a distance).
- `every`/`some` on an empty array: every is TRUE, some is FALSE —
  vacuous truth surprises people at code review.

## Lesson summary
reduce is a trace-table in method form (carry one value, always seed
it), some/every ask questions, flatMap maps one item into many — and
the decision list turns "which method?" from a debate into a lookup.""",
                    'exercises': [
                        {
                            'slug': 'reduce-trace',
                            'title': 'Accumulator walk',
                            'exercise_type': 'output_prediction',
                            'instructions': '[2,3,4].reduce((acc, n) => acc + n, 10)  What is the result?',
                            'xp_reward': 40,
                            'expected_output': '19',
                            'choices': [],
                            'explain': 'Start 10, add 2,3,4: 19. The initial value is included in the sum.',
                        },
                        {
                            'slug': 'reduce-missing-return',
                            'title': 'The silent killer',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'reduce((acc, n) => { acc += n; }, 0) returns:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'NaN — acc became undefined after round one', 'is_correct': True},
                                {'id': 'b', 'text': 'The correct sum, style nit only', 'is_correct': False},
                                {'id': 'c', 'text': '0', 'is_correct': False},
                                {'id': 'd', 'text': 'TypeError immediately', 'is_correct': False},
                            ],
                            'explain': 'No return statement => undefined accumulator; 0+1+undefined chain poisons to NaN.',
                        },
                        {
                            'slug': 'empty-vacuous',
                            'title': 'Empty arrays',
                            'exercise_type': 'multiple_select',
                            'instructions': 'For  const x = [];  which results are correct?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'x.every(n => n > 5) is true', 'is_correct': True},
                                {'id': 'b', 'text': 'x.some(n => n > 5) is false', 'is_correct': True},
                                {'id': 'c', 'text': 'x.every(...) is false (nothing to check)', 'is_correct': False},
                                {'id': 'd', 'text': 'x.reduce((a,n)=>a+n) without initial throws', 'is_correct': True},
                            ],
                            'explain': 'Vacuous truth: all-zero items satisfy every; some needs at least one. Reduce on empty needs a seed.',
                        },
                        {
                            'slug': 'flatmap-output',
                            'title': 'One-to-many',
                            'exercise_type': 'output_prediction',
                            'instructions': '[1,2].flatMap(n => [n, -n]).join(",")  Result? (comma-separated, no spaces)',
                            'xp_reward': 40,
                            'expected_output': '1,-1,2,-2',
                            'choices': [],
                            'explain': 'Each item maps to a pair; flatMap flattens the pairs one level.',
                        },
                        {
                            'slug': 'dedupe-line',
                            'title': 'One-line dedupe',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the idiom:  const unique = [...new ____(items)];  '
                                'Answer with the exact built-in constructor name, capitalised.'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'Set',
                            'explain': 'Set rejects duplicates; spread turns it back into an Array.',
                        },
                    ],
                },
                {
                    'title': 'Sorting, Searching and Copying in Practice',
                    'slug': 'sort-search-practice',
                    'objective': 'Write comparators, sort objects safely, and search without mutation.',
                    'duration': 12,
                    'body': r"""# Comparators, demystified

`sort(cmp)` asks one question of every pair it compares:

> "should `a` come before `b`?" — return **negative** yes, **0** tie,
> **positive** no.

```js
nums.slice().sort((a, b) => a - b);     // numeric ascending
nums.slice().sort((b, a) => b - a);     // descending (swap the params!)
students.slice().sort((x, y) => x.name.localeCompare(y.name));  // strings, accent-aware
const byGpa = (x, y) => y.gpa - x.gpa;  // reusable named comparator
ranked.sort(byGpa);                      // highest first
```

The subtraction trick works because numbers' difference IS the sign
the engine wants. For strings use `localeCompare` — raw `<` sort
breaks on accents and case ("Z" < "a" in code-unit order — uppercase
first, surprising every beginner).

Multi-key sorting is compare-A-then-B: `(x, y) => x.grade - y.grade ||
x.name.localeCompare(y.name)` — the `||` chains to the tiebreaker only
when the first comparison returned 0.

## Sort safely (three laws)

1. **Copy first when the original must survive**: `items.slice().sort()`
   or `[...items].sort()`. In React this is mandatory — sorting state
   in place changes nothing's reference and may corrupt render
   assumptions.
2. **The sort is stable** (ES2019 guarantee): equal-key items keep
   their original relative order — the reason multi-key results via
   one comparator beat repeated single-key passes.
3. **Unsortable is sortable-ish**: undefined/NaN sort to the end and
   comparisons with NaN silently misbehave — sanitise input first.

## Searching without helpers

```js
const sorted = ages.slice().sort((a, b) => a - b);
const found = sorted.find(a => a >= 18);          // linear, first match
const idx = sorted.findIndex(a => a >= 18);       // its position
// for big repeated lookups: binary search (DSA course ch 6) — sorted + O(log n)
```

`find` on an unsorted list is a scan (O(n), first truthy wins); if you
find yourself calling it in a loop over the same array (join-style
lookups), build an index Map once — `Object.groupBy` (ES2024) or
reduce-to-Map turns O(n²) nested matching into O(n):

```js
const byTeacher = Object.groupBy(courses, c => c.teacher);
// byTeacher["Ms. Raza"] -> [that teacher's courses] instantly
```

## Sorting real data: the full worked pattern

```js
const report = students
  .filter(s => s.enrolled)
  .map(s => ({ ...s, name: s.name.trim() }))   // clean while copying
  .sort((a, b) => b.gpa - a.gpa || a.name.localeCompare(b.name));
// top performers, name-alphabetical among ties — original array intact
```

## Common mistakes
- `.sort()` on numbers without comparator (chapter 5's trap, again —
  it mutates too).
- Comparator returning booleans: `(a,b) => a > b` is WRONG (true→1,
  false→0 — only half-informs the engine, results are shuffled).
- Sorting a live React state array in place, then "no re-render."
- Case-sensitive name sorts surprising everyone: localeCompare or
  normalise with toLowerCase in the comparator.

## Lesson summary
Comparator = signed opinion about a pair; copy-then-sort as a reflex;
stable sort unlocks clean multi-key chains; and when find-in-a-loop
shows up in your profile, index with a Map or groupBy instead.""",
                    'exercises': [
                        {
                            'slug': 'bool-comparator',
                            'title': 'Boolean comparator',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'arr.sort((a, b) => a > b) on numbers is wrong because:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'true/false coerce to 1/0 — never negative, so "a before b" is never said', 'is_correct': True},
                                {'id': 'b', 'text': 'comparators must return strings', 'is_correct': False},
                                {'id': 'c', 'text': 'it throws a TypeError', 'is_correct': False},
                                {'id': 'd', 'text': 'it only works on arrays of objects', 'is_correct': False},
                            ],
                            'explain': 'The engine needs a SIGN: negative/0/positive. Booleans collapse to 0/1 — half the contract.',
                        },
                        {
                            'slug': 'stable-order',
                            'title': 'Stability',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A stable sort guarantees:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Equal-key items keep their original relative order', 'is_correct': True},
                                {'id': 'b', 'text': 'The array is never mutated', 'is_correct': False},
                                {'id': 'c', 'text': 'Sorting twice gives different results', 'is_correct': False},
                                {'id': 'd', 'text': 'Comparators run in parallel', 'is_correct': False},
                            ],
                            'explain': 'Stability (ES2019) is what makes tie-breaker chains behave.',
                        },
                        {
                            'slug': 'multi-key-pick',
                            'title': 'Tiebreaker chain',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Sort by gpa descending, then name ascending on ties:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '(a, b) => b.gpa - a.gpa || a.name.localeCompare(b.name)', 'is_correct': True},
                                {'id': 'b', 'text': '(a, b) => a.gpa - b.gpa && a.name.localeCompare(b.name)', 'is_correct': False},
                                {'id': 'c', 'text': '(a, b) => b.gpa - a.gpa && b.name.localeCompare(a.name)', 'is_correct': False},
                                {'id': 'd', 'text': '(a, b) => a.name.localeCompare(b.name) || b.gpa - a.gpa', 'is_correct': False},
                            ],
                            'explain': '|| falls through ONLY on 0 (tie); the first link orders gpa, second breaks with name.',
                        },
                        {
                            'slug': 'groupBy-purpose',
                            'title': 'Index instead of scan',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about Object.groupBy(data, keyFn).',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'It builds one object whose keys are the computed groups', 'is_correct': True},
                                {'id': 'b', 'text': 'Values are arrays of the matching items', 'is_correct': True},
                                {'id': 'c', 'text': 'It returns items sorted within each group', 'is_correct': False},
                                {'id': 'd', 'text': 'Missing groups simply have no key', 'is_correct': True},
                            ],
                            'explain': 'Grouping preserves encounter order (no sorting); absent keys are omitted entirely.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 6 Quiz',
                    'slug': 'js-array-methods-quiz',
                    'objective': 'Check mastery of the method contracts and pipeline reading.',
                    'duration': 8,
                    'body': """# Chapter 6 quiz

Five questions on the array-method toolkit — trace each pipeline one
link at a time.""",
                    'exercises': [
                        {
                            'slug': 'q6-foreach-return',
                            'title': 'Return of forEach',
                            'exercise_type': 'output_prediction',
                            'instructions': 'console.log([1,2].forEach(n => n));  What prints? (one lower-case word)',
                            'xp_reward': 50,
                            'expected_output': 'undefined',
                            'choices': [],
                            'explain': 'forEach always returns undefined — its job is the side effect.',
                        },
                        {
                            'slug': 'q6-chain-length',
                            'title': 'Pipeline result',
                            'exercise_type': 'output_prediction',
                            'instructions': '[1,2,3,4].filter(n => n % 2).map(n => n ** 2).length  Value? (one digit)',
                            'xp_reward': 50,
                            'expected_output': '2',
                            'choices': [],
                            'explain': 'Odds are 1,3 -> squares [1,9] -> length 2.',
                        },
                        {
                            'slug': 'q6-reduce-shape',
                            'title': 'Accumulator types',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'reduce can produce which accumulator types?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Any: number, string, object, array — whatever you return each round', 'is_correct': True},
                                {'id': 'b', 'text': 'Only numbers', 'is_correct': False},
                                {'id': 'c', 'text': 'Only the same type as the items', 'is_correct': False},
                                {'id': 'd', 'text': 'Exactly one object', 'is_correct': False},
                            ],
                            'explain': 'The accumulator is YOUR variable; its type is your choice every round.',
                        },
                        {
                            'slug': 'q6-some-vs-find',
                            'title': 'Answer type',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL correct pairings.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'some -> boolean', 'is_correct': True},
                                {'id': 'b', 'text': 'find -> the element or undefined', 'is_correct': True},
                                {'id': 'c', 'text': 'findIndex -> boolean', 'is_correct': False},
                                {'id': 'd', 'text': 'every -> boolean', 'is_correct': True},
                            ],
                            'explain': 'findIndex returns a number (-1 when absent) — the swapped pairing is a quiz classic.',
                        },
                        {
                            'slug': 'q6-safe-sort',
                            'title': 'Non-mutating sort',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the copy-then-sort idiom:  const top = [...items].__(cmp);  '
                                'Answer with the method name only, lower-case.'
                            ),
                            'xp_reward': 50,
                            'solution_code': 'sort',
                            'explain': 'The spread copies; sort mutates only the copy.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 7 ════════════════════
        {
            'title': 'Modern JavaScript and ES6+',
            'slug': 'js-es6',
            'description': 'Classes, modules, Maps/Sets and the syntax upgrades real codebases run on.',
            'lessons': [
                {
                    'title': 'Classes: Syntax, Not a New Model',
                    'slug': 'classes',
                    'objective': 'Write a class with constructor, methods, inheritance, and explain what it compiles to conceptually.',
                    'duration': 15,
                    'body': r"""# The sugar, honestly

`class` (ES6) is the clearest way to write prototype-based code — but
the prototype model underneath did NOT change. A class declares a
constructor function plus methods that live on its prototype:

```js
class Student {
  school = "Code Yaar";          // PUBLIC FIELD (per instance)
  #gpa;                          // PRIVATE field (# syntax, modern)

  constructor(name, gpa) {
    this.name = name;
    this.#gpa = gpa;             // enforced privacy, not a naming hint
  }

  introduce() {                  // method -> prototype (shared)
    return `${this.name} (${this.#gpa.toFixed(1)})`;
  }

  get isHonor() {                // getter: property SYNTAX, method cost
    return this.#gpa >= 3.5;
  }

  static compare(a, b) {         // static: on the CLASS, not instances
    return b.#gpa - a.#gpa;
  }
}

const s = new Student("Amina", 3.8);
s.introduce();      // "Amina (3.8)"
s.isHonor;          // true — getter called without ()
s.#gpa;             // SyntaxError — private is REAL
Student.compare(a, b);   // static usage; s.compare would fail
```

## Inheritance: extends + super

```js
class GradStudent extends Student {
  #thesis;
  constructor(name, gpa, thesis) {
    super(name, gpa);        // MUST call before using this (before it, no object)
    this.#thesis = thesis;
  }
  introduce() {              // override, then augment
    return super.introduce() + ` — researching ${this.#thesis}`;
  }
}
```

- `super(...)` in a constructor calls the parent's; in a method it
  reaches the parent's version of that method.
- Single inheritance only (like Java) — shared BEHAVIOUR beyond the
  chain is composed with mixins or plain objects, not multiple extends.
- `instanceof` walks the chain: `new GradStudent(...) instanceof
  Student` is true.

## What "prototype" still means (interview floor)

`new Student()` creates an object whose hidden prototype link points
at `Student.prototype`; method lookups that miss on the instance
follow that link. Class syntax is a readable wrapper on exactly this —
which explains real oddities: methods are shared (one copy, not per
instance), `obj.hasOwnProperty` sees only own fields, and older code
you will read (`Object.create`, `function` constructors, `.prototype.x
= ...`) is the same machine without the sugar.

## this, one more time — because classes hit it hardest

```js
class Panel {
  message = "ready";
  show = () => console.log(this.message);   // FIELD arrow: this locked to instance
  showLate() { console.log(this.message); } // prototype method: this depends on call site
}
const p = new Panel();
setTimeout(p.show, 100);      // safe — arrow field
setTimeout(p.showLate, 100);  // this is gone (undefined) — the trap
```

Arrow-field methods are the React-callback idiom precisely because
they survive being passed around; chapter 10 leans on it.

## Common mistakes
- Using `this` before `super()` in a derived constructor — ReferenceError.
- Forgetting `new`: `Student("x")` throws ("Class constructor cannot
  be invoked without new") — old function-constructors silently
  created globals instead; that was worse.
- Expecting private `#field` to be security — it is language-level
  encapsulation, not encryption; everything client-side is readable.

## Lesson summary
class is the clearest voice for the old prototype model: fields per
instance, methods on the prototype, extends + super for chains, # for
enforced privacy — and this still follows the call-site rule unless
you pin it with an arrow field.""",
                    'exercises': [
                        {
                            'slug': 'super-before-this',
                            'title': 'Constructor order',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In a derived class constructor, using this before super():',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'ReferenceError — the instance does not exist until super runs', 'is_correct': True},
                                {'id': 'b', 'text': 'Works but is discouraged style', 'is_correct': False},
                                {'id': 'c', 'text': 'Silently binds to the parent instance', 'is_correct': False},
                                {'id': 'd', 'text': 'TypeError only in strict mode', 'is_correct': False},
                            ],
                            'explain': 'super() CREATES this; before it there is nothing to bind.',
                        },
                        {
                            'slug': 'method-location',
                            'title': 'Where methods live',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Class methods (non-field) are stored:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'On the prototype, shared by all instances', 'is_correct': True},
                                {'id': 'b', 'text': 'Copied into every instance', 'is_correct': False},
                                {'id': 'c', 'text': 'On the global object', 'is_correct': False},
                                {'id': 'd', 'text': 'Inside the constructor closure', 'is_correct': False},
                            ],
                            'explain': 'Prototype chain, unchanged since before class existed — fields per instance, methods shared.',
                        },
                        {
                            'slug': 'private-enforced',
                            'title': '# semantics',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about  #gpa  in a class.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Accessing it outside the class is a SyntaxError', 'is_correct': True},
                                {'id': 'b', 'text': 'It does not appear in Object.keys or JSON output', 'is_correct': True},
                                {'id': 'c', 'text': 'It is encrypted against a curious user', 'is_correct': False},
                                {'id': 'd', 'text': 'Subclasses can still read their OWN #fields the same way', 'is_correct': True},
                            ],
                            'explain': 'Language-enforced encapsulation, but client-side data is never secret.',
                        },
                        {
                            'slug': 'instanceof-chain',
                            'title': 'Chain test',
                            'exercise_type': 'output_prediction',
                            'instructions': 'new GradStudent("A",3,"T") instanceof Student  — value? (True or False, capital first letter)',
                            'xp_reward': 40,
                            'expected_output': 'True',
                            'choices': [],
                            'explain': 'instanceof walks the prototype chain, and GradStudent extends Student. (console prints booleans capitalised.)',
                        },
                    ],
                },
                {
                    'title': 'Modules: export and import',
                    'slug': 'modules',
                    'objective': 'Split code with ES modules and explain why modules replaced globals.',
                    'duration': 12,
                    'body': r"""# Files that are scopes

A **module** is a file whose top-level variables are private to it by
default. No more accidental global collisions — you export what is
public and import what you need:

```js
// utils/grades.js
export const PASS = 50;                       // named export
export function grade(score) {                // named
  return score >= 90 ? "A" : score >= PASS ? "B" : "F";
}
export default class Report { ... }           // ONE default per file

// app.js
import Report, { grade, PASS as PASS_MARK } from "./utils/grades.js";
import * as grades from "./utils/grades.js";  // namespace object
import "./setup-logging.js";                  // side-effect only
```

Facts that bite beginners:

- **Named exports match by NAME** (`{ grade }` must exist); the
  default export matches by whatever you call it locally.
- `import { x }` is a LIVE BINDING: if the module later reassigns x
  (rare, but true for module singletons), your import sees the new
  value. `import * as ns` gives you an object snapshot of names.
- You cannot `import` a default that was never `export default`ed —
  the error text ("does not provide an export named 'default'") is
  the #1 module question on forums.
- Extensions matter: with plain Node ESM you write `"./grades.js"`
  exactly; bundlers (Vite, Next.js — the project you are in) resolve
  shorter specifiers for you.

## Why this exists

Before ES6 modules (2015, shipped ~2019 in browsers) the ecosystem
hand-rolled it: CommonJS (`require`/`module.exports` — still every
Node backend), AMD, then bundler magic. ES modules unified the story:
top-level `await` is only legal in modules, tree-shaking (dropping
unused exports at build time) only works because imports are static
and analyserable.

You will meet BOTH systems in the wild; recognising CommonJS is
half the battle:

```js
const { grade } = require("./grades");   // CommonJS — dynamic-ish
```

## Modules + everything so far

`export function makeCounter() { ... }` — chapter 4's factories,
`export const students = [...]` — module data, `import Report from` —
chapter 7's classes. React is modules all the way down: every `.jsx`
file imports its dependencies and exports its component (chapter 10).

## Common mistakes
- Mixing default and named confusion: `import grades` when the file
  exported `export const grade` (no default) — grades is undefined.
- Circular imports (A imports B imports A): partially initialised
  modules, mysterious undefined at top level. Restructure instead of
  outsmarting.
- Mutating an imported binding (`PASS = 60`) — TypeError; imports are
  read-only views.

## Lesson summary
One file = one scope; named exports are the default-default, one
default per file gets to be named anything at import; live bindings,
namespace imports, and side-effect imports round out the grammar —
and everything you have learned now simply lives inside these files.""",
                    'exercises': [
                        {
                            'slug': 'default-import-name',
                            'title': 'Default freedom',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A file has  export default function grade() {...} . Which import works?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'import myOwnName from "./grades.js"', 'is_correct': True},
                                {'id': 'b', 'text': 'import { grade } from "./grades.js"', 'is_correct': False},
                                {'id': 'c', 'text': 'import default grade from "./grades.js"', 'is_correct': False},
                                {'id': 'd', 'text': 'require.default(grade)', 'is_correct': False},
                            ],
                            'explain': 'The default is chosen by ABSENCE of braces and named locally at will.',
                        },
                        {
                            'slug': 'namespace-import',
                            'title': 'Star import',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'import * as utils from "./u.js"  then calling its grade export:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'utils.grade(x)', 'is_correct': True},
                                {'id': 'b', 'text': 'utils.default.grade(x)', 'is_correct': False},
                                {'id': 'c', 'text': 'grade(x) directly', 'is_correct': False},
                                {'id': 'd', 'text': 'utils["default"]["grade"](x)', 'is_correct': False},
                            ],
                            'explain': 'The namespace object holds every export by its export name.',
                        },
                        {
                            'slug': 'readonly-binding',
                            'title': 'Reassigning an import',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'import { PASS } from ...;  PASS = 60;  results in:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'TypeError — import bindings are read-only', 'is_correct': True},
                                {'id': 'b', 'text': 'Silent local override', 'is_correct': False},
                                {'id': 'c', 'text': 'The source module changes too', 'is_correct': False},
                                {'id': 'd', 'text': 'Works in dev, fails in prod', 'is_correct': False},
                            ],
                            'explain': 'You can import and READ; writing to the binding itself is forbidden.',
                        },
                        {
                            'slug': 'commonjs-recognise',
                            'title': 'Old system',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about CommonJS (require/module.exports).',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Still the default inside many Node backends', 'is_correct': True},
                                {'id': 'b', 'text': 'module.exports is its export mechanism', 'is_correct': True},
                                {'id': 'c', 'text': 'require() can take computed/dynamic paths', 'is_correct': True},
                                {'id': 'd', 'text': 'It supports top-level await', 'is_correct': False},
                            ],
                            'explain': 'Top-level await is ESM-only; dynamic require was CommonJS\u2019 own superpower.',
                        },
                    ],
                },
                {
                    'title': 'Maps, Sets and Iterables',
                    'slug': 'maps-sets',
                    'objective': 'Choose Map/Set over plain objects and arrays where the contract fits better.',
                    'duration': 12,
                    'body': r"""# The two collections objects/arrays never were

```js
const scores = new Map();
scores.set("Amina", 92);          // KEYS CAN BE ANYTHING: objects, even functions
scores.get("Amina");              // 92
scores.has("Bilal");              // false
scores.size;                       // 1 — a real number, not length tricks
for (const [name, mark] of scores) { ... }   // ITERABLE — direct, insertion order
[...scores.keys()];               // ["Amina"]

const seen = new Set([1, 2, 2, 3]);   // dedupe constructor: Set from array
seen.add(4); seen.add(4);             // second add ignored
seen.has(2);                           // true
seen.size;                             // 4
[...new Set(items)];                   // the one-line array dedupe, again
```

**Why not a plain object as a dictionary?** Object keys are
string-or-Symbol only, `for...in` walks the prototype chain too
(buggy iteration), insertion order has integer-key exceptions (chapter
5), and `obj.size` does not exist. Map fixes exactly that list; Set
fixes "array but membership is O(1) and values unique" (the DSA
hashing chapter, in library form).

Rule of thumb (the one linters encode):
- Record-shaped data with known fields → **object**
- Key → value lookups with dynamic keys → **Map**
- Unique membership / dedupe → **Set**
- Ordered list → **array**

## WeakMap and WeakSet (recognition level)

Keys that are OBJECTS ONLY and can be garbage-collected when nothing
else references them — that is the whole design: caches and private
state attached to DOM nodes/instances without leaking them. No
iteration, no size. You will not write one this year; you will read
them in library code (React internals use WeakMap for exactly the
"metadata about a fiber without keeping it alive" job).

## Iterables: the protocol under everything

Anything usable in `for...of` implements a tiny contract: a method
named `Symbol.iterator` returning `{ next() }`. Arrays, strings, Maps,
Sets, and querySelectorAll results do; plain objects do not (chapter
3's TypeError, explained). You can make your own:

```js
const range = {
  from: 1, to: 3,
  *[Symbol.iterator]() {              // generator method (the * matters)
    for (let i = this.from; i <= this.to; i++) yield i;
  },
};
[...range];                    // [1, 2, 3]
for (const n of range) { ... } // works
```

`function*` + `yield` is the shorthand factory for iterators: each
`yield` pauses the function, `next()` resumes it — lazy sequences,
the same generator idea the ML course meets in Python. Enough to
recognise; production code rarely hand-rolls them.

## Spread is iteration too

`[...iterable]`, `Math.max(...arr)` (careful: huge arrays blow the
argument stack — reduce instead), `{...obj}` — all speak the iterable
protocol (objects via their own enumerable entries; the spread of a
plain object is the special non-iterable case).

## Common mistakes
- `map["key"]` — Map is method-access (`get/set`), not property
  access; brackets create a plain JS property ON the Map object.
- Expecting object-keyed Maps (`map.set(obj, v)`) to survive JSON —
  Maps do not serialize; decide the wire format explicitly.
- `Math.max(...millionItems)` — RangeError stack boom.
- Iterating a Map with for...in — gives nothing (Maps have no
  enumerable properties); use for...of.

## Lesson summary
Map = any-keys ordered dictionary with size and iteration; Set =
uniqueness with O(1) membership; both are iterable because of
Symbol.iterator, generators can make more iterables, and
spread/for...of/Array.from all consume that one protocol.""",
                    'exercises': [
                        {
                            'slug': 'map-access',
                            'title': 'Method access',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const m = new Map([["a", 1]]); console.log(m.get("a"), m["a"]);  Output? (two values, space, comma between)',
                            'xp_reward': 40,
                            'expected_output': '1 undefined',
                            'choices': [],
                            'explain': 'get() reads the Map; bracket syntax reads a JS property — which was never set.',
                        },
                        {
                            'slug': 'set-dedupe-size',
                            'title': 'Set arithmetic',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const s = new Set([1, "1", 1, true]); console.log(s.size);  Output? (one digit)',
                            'xp_reward': 40,
                            'expected_output': '3',
                            'choices': [],
                            'explain': 'Set uses SameValueZero: 1 === 1 collapses, but "1" and true are distinct from 1.',
                        },
                        {
                            'slug': 'weakmap-rule',
                            'title': 'Weak keys',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about WeakMap.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Keys must be objects', 'is_correct': True},
                                {'id': 'b', 'text': 'Key entries can be garbage-collected away', 'is_correct': True},
                                {'id': 'c', 'text': 'It is iterable with for...of', 'is_correct': False},
                                {'id': 'd', 'text': 'It is used for caches/private metadata', 'is_correct': True},
                            ],
                            'explain': 'No iteration, no size — weakness is the feature and the limit.',
                        },
                        {
                            'slug': 'generator-next',
                            'title': 'Pause semantics',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In a function* generator, each yield:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Pauses the function and returns a value to next()\u2019s caller', 'is_correct': True},
                                {'id': 'b', 'text': 'Terminates the function permanently', 'is_correct': False},
                                {'id': 'c', 'text': 'Runs the whole loop eagerly', 'is_correct': False},
                                {'id': 'd', 'text': 'Is just return with extra steps', 'is_correct': False},
                            ],
                            'explain': 'Lazy, resumable execution — the defining behaviour of generators.',
                        },
                        {
                            'slug': 'which-collection',
                            'title': 'Tool pick',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Counting occurrences of arbitrary words from user text, with fast lookup by word:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Map<string, number>', 'is_correct': True},
                                {'id': 'b', 'text': 'Array of [word, count] pairs', 'is_correct': False},
                                {'id': 'c', 'text': 'Set of words only', 'is_correct': False},
                                {'id': 'd', 'text': 'One big string', 'is_correct': False},
                            ],
                            'explain': 'Dynamic string keys + O(1) lookup + a count value per key = Map exactly.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 7 Quiz',
                    'slug': 'js-es6-quiz',
                    'objective': 'Check mastery of classes, modules and the new collections.',
                    'duration': 8,
                    'body': """# Chapter 7 quiz

Five questions on the ES6+ toolkit — classes, modules, Map/Set and
iteration.""",
                    'exercises': [
                        {
                            'slug': 'q7-extends-super',
                            'title': 'Inheritance call',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Inside a child method, super.method() invokes:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The parent class\u2019s version of method', 'is_correct': True},
                                {'id': 'b', 'text': 'The grandparent\u2019s version always', 'is_correct': False},
                                {'id': 'c', 'text': 'A copy of the child method', 'is_correct': False},
                                {'id': 'd', 'text': 'The static method of that name', 'is_correct': False},
                            ],
                            'explain': 'super in methods walks up one prototype level — the same idea as Java.',
                        },
                        {
                            'slug': 'q7-static-this',
                            'title': 'Static scope',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A static method can directly use:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'other statics via this.Other (this = the class)', 'is_correct': True},
                                {'id': 'b', 'text': 'instance fields like this.name', 'is_correct': False},
                                {'id': 'c', 'text': 'anything a normal method can', 'is_correct': False},
                                {'id': 'd', 'text': 'only constructor logic', 'is_correct': False},
                            ],
                            'explain': 'In static context this is the class itself; instances may not even exist.',
                        },
                        {
                            'slug': 'q7-map-object-key',
                            'title': 'Any-key advantage',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const k = {}; const m = new Map([[k, "hit"]]); console.log(m.get({}) || m.get(k));  Output?',
                            'xp_reward': 50,
                            'expected_output': 'hit',
                            'choices': [],
                            'explain': 'Map keys compare by IDENTITY — the fresh {} is not k, but k itself retrieves the value.',
                        },
                        {
                            'slug': 'q7-set-size',
                            'title': 'Size after ops',
                            'exercise_type': 'output_prediction',
                            'instructions': 'const s = new Set(); s.add(5); s.add(5); s.delete(5); s.add("five"); console.log(s.size);  Output?',
                            'xp_reward': 50,
                            'expected_output': '1',
                            'choices': [],
                            'explain': 'Duplicate add ignored, delete removed 5, the string stays: size 1.',
                        },
                        {
                            'slug': 'q7-tree-shake',
                            'title': 'Why static imports',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Bundlers can tree-shake (drop unused code) because ES import/export are:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Static — names known at parse time, analysable', 'is_correct': True},
                                {'id': 'b', 'text': 'Faster at runtime than require', 'is_correct': False},
                                {'id': 'c', 'text': 'Encrypted', 'is_correct': False},
                                {'id': 'd', 'text': 'Loaded in parallel threads', 'is_correct': False},
                            ],
                            'explain': 'Top-level, string-literal import specifiers are what makes the dependency graph computable.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 8 ════════════════════
        {
            'title': 'The DOM: Manipulation and Events',
            'slug': 'js-dom-events',
            'description': 'Select and change page elements, build them from data, and respond to users.',
            'lessons': [
                {
                    'title': 'The DOM Tree and Selection',
                    'slug': 'dom-selection',
                    'objective': 'Navigate and select elements; explain the DOM as JavaScript\u2019s view of the page.',
                    'duration': 14,
                    'body': r"""# The page as a live object tree

When the browser parses HTML it builds the **DOM** (Document Object
Model): a tree of Node objects mirroring your markup. JavaScript
mutates that tree and the screen follows — the DOM is the bridge:

```
document (Node)
 \- <html>
    +- <head> ...
    +- <body>
        +- <div id="app" class="card">
            +- <h1>Title</h1>
            +- <ul> -> <li>...</li>
```

Everything is a node: elements, text runs, even comments.
`document` is the entry point the browser gives you.

## Selecting

```js
const box = document.getElementById("app");        // one, by id (oldest API)
const li  = document.querySelector("#app li");     // FIRST match, ANY CSS selector
const all = document.querySelectorAll(".card li");  // ALL matches — a STATIC NodeList

all.length;                    // count, array-like
all[0];                          // indexed access works
all.forEach(render);             // forEach exists on NodeList
const arr = [...all];            // a REAL array when you need map/filter/reduce
```

`querySelector` is the modern default because CSS selectors are the
language you already know: `"nav > a"`, `".list-item:not(.done)"`,
`"input[name=email]"`. The distinction the exams love:
`querySelectorAll` returns a **static** NodeList (a snapshot — later
DOM changes do NOT appear in it) while `document.getElementsByTagName`
returns a **live** HTMLCollection (updates itself — surprising mid-loop
behaviour). Spread into an array and you side-step both.

## The navigation properties

```js
box.parentElement          // the <div>'s parent element
box.children                // element children (live, HTMLCollection)
box.firstElementChild, .lastElementChild, .nextElementSibling
box.closest(".card")        // UP the tree to first matching ancestor — gold for events
```

(`childNodes`, `parentNode` etc. also see text and comment nodes;
the `...Element...` variants are the sane defaults for app code.)

## Reading and writing content

```js
const title = document.querySelector("h1");

title.textContent;            // "Title" — all text, tags stripped (SAFE)
title.textContent = "New";    // replace text

title.innerHTML;              // "<em>Markup</em>" as a STRING
title.innerHTML = "<em>Hi</em>";   // PARSES HTML — powerful, dangerous

box.classList.add("active");  // class API — never assign className strings blindly
box.classList.toggle("open");
box.classList.remove("hidden");
box.dataset.id;               // reads data-id="7" -> "7"  (custom data)
box.getAttribute("role");
box.style.color = "tomato";    // inline styles (CSS custom props: chapter 6 of Web course)
box.hidden = true;             // many attributes mirror as plain properties
```

The security headline of the chapter: **`innerHTML` parses and
executes** — injecting user text through it (`` `<p>${comment}</p>`
``) is the classic XSS hole (the Cybersecurity course makes it
official). If you mean text, use `textContent`; if you must build
markup, build nodes (next lesson).

## When is the DOM ready?

Chapter 1's `defer` is the clean answer. The alternative you will see
in the wild:

```js
document.addEventListener("DOMContentLoaded", init);  // tree parsed, images may still load
```

Without either, a head script selecting `#app` gets `null` — the
element is not in the tree yet (that IS a DOM fact, not a scoping bug).

## Common mistakes
- `querySelector("#app li")[1]` — first-match API returns ONE node;
  use All for collections.
- Re-reading `document.getElementById` inside a loop — cache the node
  reference; lookups are cheap but not free, and the code says what
  you mean.
- `element.class = "x"` — the property is `className` (class is a
  reserved word legacy); or better, `classList`.
- Treating NodeList like a full Array (`map` is missing until you
  spread).

## Lesson summary
The DOM mirrors your HTML as a node tree reached from `document`;
selectors are CSS, `querySelectorAll` snapshots statically, the
textContent-vs-innerHTML line is a security boundary, and nodes are
cheap to hold but expensive to re-find.""",
                    'exercises': [
                        {
                            'slug': 'qs-qa-difference',
                            'title': 'One vs all',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'To style every  .score  element, select the right call:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'document.querySelectorAll(".score")', 'is_correct': True},
                                {'id': 'b', 'text': 'document.querySelector(".score")', 'is_correct': False},
                                {'id': 'c', 'text': 'document.getElementById(".score")', 'is_correct': False},
                                {'id': 'd', 'text': 'document.selectAll(".score")', 'is_correct': False},
                            ],
                            'explain': 'querySelector returns only the FIRST match; getElementById takes ids without a dot.',
                        },
                        {
                            'slug': 'innerhtml-risk',
                            'title': 'Safe insertion',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Displaying user-typed comment text under a post should use:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'el.textContent = comment', 'is_correct': True},
                                {'id': 'b', 'text': 'el.innerHTML = comment', 'is_correct': False},
                                {'id': 'c', 'text': 'el.outerHTML += comment', 'is_correct': False},
                                {'id': 'd', 'text': 'document.write(comment)', 'is_correct': False},
                            ],
                            'explain': 'textContent treats input as TEXT; innerHTML parses markup — script tags and all.',
                        },
                        {
                            'slug': 'closest-purpose',
                            'title': 'closest direction',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'button.closest(".card") returns:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The nearest ANCESTOR of button matching .card', 'is_correct': True},
                                {'id': 'b', 'text': 'The first .card child inside button', 'is_correct': False},
                                {'id': 'c', 'text': 'The next .card sibling', 'is_correct': False},
                                {'id': 'd', 'text': 'All matching cards on the page', 'is_correct': False},
                            ],
                            'explain': 'closest walks UPWARD — the standard "which row/card was clicked" tool.',
                        },
                        {
                            'slug': 'static-vs-live',
                            'title': 'Snapshot semantics',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true about querySelectorAll results.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'It is a static NodeList — later DOM additions are absent', 'is_correct': True},
                                {'id': 'b', 'text': 'It supports forEach', 'is_correct': True},
                                {'id': 'c', 'text': 'It has map/filter built in', 'is_correct': False},
                                {'id': 'd', 'text': '[...nodes] turns it into a real array', 'is_correct': True},
                            ],
                            'explain': 'Static + iterable but NOT an Array; the spread is the documented escape hatch.',
                        },
                        {
                            'slug': 'classlist-flag',
                            'title': 'Class API',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'The element property offering add/remove/toggle of classes (without clobbering '
                                'the whole class string) is ______. Answer with the exact camelCase property name.'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'classList',
                            'explain': 'classList.toggle etc. — className is the raw string, class is illegal.',
                        },
                    ],
                },
                {
                    'title': 'Creating Nodes and Rendering Lists',
                    'slug': 'dom-creation',
                    'objective': 'Build elements from data with createElement and DocumentFragment.',
                    'duration': 13,
                    'body': r"""# From data to nodes, the honest way

The pattern that powers every "render a list" screen before React:

```js
const courses = [
  { id: 1, name: "Python", level: "beginner" },
  { id: 2, name: "DSA",    level: "intermediate" },
];

function renderCourse(c) {
  const li = document.createElement("li");      // NEW node, detached
  li.className = "course";
  li.dataset.id = c.id;

  const strong = document.createElement("strong");
  strong.textContent = c.name;                   // data via textContent: safe
  const span = document.createElement("span");
  span.textContent = ` — ${c.level}`;

  li.append(strong, span);                        // append takes nodes AND strings
  return li;
}

const list = document.querySelector("#courses");
const frag = document.createDocumentFragment();   // batch, then attach ONCE
for (const c of courses) frag.append(renderCourse(c));
list.append(frag);                                // one reflow, not three
```

Why each detail earns its place:

- **createElement then append** keeps data and structure separate —
  values go through textContent (no injection), markup goes through
  the API (no parse surprises). The innerHTML-string-template style is
  shorter but you must then escape every value yourself.
- **DocumentFragment** is a invisible container: appending nodes to it
  does NOT touch the live tree, so the browser restyles/reflows ONCE
  when the fragment lands. Without it, every append repaints.
- **`append` vs the old `appendChild`**: append takes multiple nodes
  and strings, has no return value; appendChild returns the child and
  takes one node. Prefer append in new code.

## Updating instead of rebuilding

Rendering twice means either destroy-and-rebuild or patch:

```js
// rebuild (simple, fine for small lists):
list.replaceChildren(...courses.map(renderCourse));   // atomic swap, modern

// patch (targeted, no flicker, state preserved inside rows):
const existing = list.querySelector(`[data-id="${c.id}"]`);
if (existing) existing.querySelector("span").textContent = ` — ${c.level}`;
else list.append(renderCourse(c));
```

That if-patch-or-create loop, written generically with key matching,
is literally what React's reconciler does for you (chapter 10) —
realise the list twice by hand once here and React\'s `key` prop
suddenly makes total sense.

## Removing and clearing

```js
row.remove();                       // detach self (modern; old: parent.removeChild(row))
list.replaceChildren();             // clear ALL children, fast
node.replaceWith(newNode);          // swap in place
node.before(x); node.after(y);      // positional inserts around a node
```

An element can only be in ONE place — appending a node you already
attached MOVES it (the classic "it vanished from the old list" bug).

## The React preview (why this chapter still matters)

You have now seen: state (the array), render (create/patch nodes),
and update (rebuild vs patch). React = those three ideas with an
automatic diff, a declarative template (JSX) and a batching
scheduler. This chapter is the "how it works inside" that makes React
feel obvious instead of magical — and remains the toolset for
widgets, emails, and anything without a framework.

## Common mistakes
- Rebuilding the whole list inside a scroll handler (jank) — patch or
  throttle; chapter 9 for the handler cost.
- Forgetting nodes are single-place objects (the moved-row surprise).
- innerHTML += inside loops — re-parses everything each round and
  destroys event listeners on surviving elements.

## Lesson summary
createElement + textContent is the safe construction set,
DocumentFragment batches DOM writes, replaceChildren is the modern
clear/swap, and the patch-by-key loop is React's job you just did
manually.""",
                    'exercises': [
                        {
                            'slug': 'frag-why',
                            'title': 'Fragment payoff',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Building 50 rows in a DocumentFragment before one append helps because:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The live tree changes once, so layout/reflow runs once', 'is_correct': True},
                                {'id': 'b', 'text': 'Fragments execute JavaScript faster', 'is_correct': False},
                                {'id': 'c', 'text': 'Fragments keep event listeners alive better', 'is_correct': False},
                                {'id': 'd', 'text': 'The browser caches fragment HTML', 'is_correct': False},
                            ],
                            'explain': 'The fragment is inert until attached — batch writes, single reflow.',
                        },
                        {
                            'slug': 'replacechildren-call',
                            'title': 'Atomic swap',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Clear #list and insert freshly rendered rows in ONE DOM operation:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'list.replaceChildren(...rows)', 'is_correct': True},
                                {'id': 'b', 'text': 'list.innerHTML = rows', 'is_correct': False},
                                {'id': 'c', 'text': 'rows.forEach(r => list.append(r))', 'is_correct': False},
                                {'id': 'd', 'text': 'list.swap(rows)', 'is_correct': False},
                            ],
                            'explain': 'replaceChildren takes a node list, replaces everything atomically; no-args clears.',
                        },
                        {
                            'slug': 'single-parent',
                            'title': 'The moving bug',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'node already in list A;  listB.append(node)  results in:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'node MOVED to listB — it left A', 'is_correct': True},
                                {'id': 'b', 'text': 'node now appears in both lists', 'is_correct': False},
                                {'id': 'c', 'text': 'Error: already has a parent', 'is_correct': False},
                                {'id': 'd', 'text': 'A clone lands in listB', 'is_correct': False},
                            ],
                            'explain': 'A node has one parent; appending elsewhere detaches first. Clone via node.cloneNode(true).',
                        },
                        {
                            'slug': 'construction-safety',
                            'title': 'Why createElement',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true advantages of createElement+textContent over innerHTML templates.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'User data is never parsed as markup — no injection path', 'is_correct': True},
                                {'id': 'b', 'text': 'You attach listeners to real node references, not after re-parsing', 'is_correct': True},
                                {'id': 'c', 'text': 'It is always fewer lines of code', 'is_correct': False},
                                {'id': 'd', 'text': 'No HTML parse cost per string interpolation', 'is_correct': True},
                            ],
                            'explain': 'It is usually MORE lines — the safety and reference control are the price worth paying.',
                        },
                    ],
                },
                {
                    'title': 'Events: Listeners, Delegation and Forms',
                    'slug': 'events-forms',
                    'objective': 'Attach listeners correctly, read the event object, delegate, and handle form input.',
                    'duration': 15,
                    'body': r"""# Reacting to the user

```js
const btn = document.querySelector("#join");

btn.addEventListener("click", () => {
  console.log("clicked");
});
```

`addEventListener(type, fn)` is the ONLY professional way: multiple
handlers coexist (unlike `btn.onclick =`, which overwrites), and
`removeEventListener` can undo them. The listener receives the
**Event object** — the textbook example of data you must actually use:

```js
list.addEventListener("click", (event) => {
  event.type;            // "click"
  event.target;          // the DEEPEST element actually clicked
  event.currentTarget;   // the element the listener is attached to
  event.clientX, event.key, event.detail ...   // per-type payload
});
```

## Bubbling and delegation — the important pair

A click on `<li>` fires listeners on the li, then its ul, then body,
then document — events **bubble upward** by default. That is not a
quirk, it is a feature:

```js
// ONE listener for a thousand rows:
list.addEventListener("click", (event) => {
  const row = event.target.closest("[data-id]");   // which row?
  if (!row) return;                                  // clicked padding — ignore
  openEditor(row.dataset.id);                        // row.dataset — chapter: DOM lesson
});
```

**Delegation** = listen on the container, dispatch by target. Wins:
rows created later work with zero re-registration (the killer
argument for dynamic lists), and one listener is cheaper than many.
The guard (`if (!row) return`) is not optional — clicks between rows
exist.

(There is a **capturing** phase that runs top-down before bubbling:
`addEventListener(type, fn, { capture: true })`. Rarely needed; know
the word exists.)

## The keyboard and the mouse you actually handle

```js
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitSearch(input.value);
  if (e.key === "Escape") closeOverlay();
});
// e.key: "a", "Enter", "ArrowUp"  |  e.code: physical "KeyA", "Digit1"
// modifiers: e.ctrlKey / e.metaKey / e.shiftKey / e.altKey
```

## Forms: reading, preventing, responding

```js
const form = document.querySelector("#login");

form.addEventListener("submit", (event) => {
  event.preventDefault();              // STOP the browser's GET/POST reload
  const email = form.email.value;      // named access via name attribute
  const pass  = form.elements.password.value;
  if (!email.includes("@")) {
    form.email.setCustomValidity("Needs an @");   // native bubble
    form.email.reportValidity();                    // show it
    return;
  }
  login(email, pass);                  // your own path (fetch, chapter 9)
});

// per-keystroke input (the React onChange equivalent):
input.addEventListener("input", () => updatePreview(input.value));
select.addEventListener("change", () => applyTheme(select.value));
checkbox.addEventListener("change", () => enableSubmit(checkbox.checked));
```

`submit` vs `click`: handle SUBMIT (covers Enter-key submits and
programmatic ones); the submit button's own click is a different,
incomplete event. `input` fires per keystroke, `change` on commit
(blur/select/checkbox) — pair them like keystroke vs "final answer".

## Timers alongside events

```js
const id = setInterval(tick, 1000);      // repeating — MUST clear eventually
clearInterval(id);
setTimeout(later, 300);                   // once (chapter 4's first-class demo)
requestAnimationFrame(draw);              // once per screen paint — smooth UI work
```

Forgetting `clearInterval` on cleanup (navigating away, component
unmount — React's useEffect return, chapter 11) is how zombie timers
pile up.

## removeEventListener reality

Removing requires the SAME function reference — which means anonymous
inline arrows can never be removed, and `bind` creates a new function
(the double-bind bug). The fix is the arrow FIELD from chapter 7, or a
named function reference.

## Common mistakes
- `addEventListener("onclick", fn)` — the type is "click"; the "on"
  version is the property-style `onclick=`.
- Delegation without the `closest`/guard: handlers fire on container
  clicks and crash reading `dataset` of undefined.
- Not calling `preventDefault` on submit, then "my JS reloads the
  page" (the GET query string in the URL bar is the fingerprint).
- Expensive work in `input`/`scroll`/`keydown` handlers without
  thinking — they fire at human-speed maximum; debounce/throttle
  (small closure from chapter 4: store a timer id, reset on call).

## Lesson summary
addEventListener is the door; the Event object is the visitor's
briefcase (target = deepest node, currentTarget = listener host);
bubbling makes container-level delegation the pattern for dynamic
lists; forms answer submit with preventDefault and stream via
input/change — and every timer needs its cleanup partner.""",
                    'exercises': [
                        {
                            'slug': 'target-vs-current',
                            'title': 'The two hosts',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Listener on #list; user clicks a nested <span> inside an <li>. event.target is:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the span', 'is_correct': True},
                                {'id': 'b', 'text': 'the li', 'is_correct': False},
                                {'id': 'c', 'text': '#list', 'is_correct': False},
                                {'id': 'b2', 'text': 'document', 'is_correct': False},
                            ],
                            'explain': 'target = deepest actual hit; currentTarget = #list, the listener host.',
                        },
                        {
                            'slug': 'delegation-benefit',
                            'title': 'Why delegate',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true benefits of container-level delegation.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Later-added children are handled with no new listeners', 'is_correct': True},
                                {'id': 'b', 'text': 'Fewer listener objects on the page', 'is_correct': True},
                                {'id': 'c', 'text': 'It stops bubbling to save time', 'is_correct': False},
                                {'id': 'd', 'text': 'One handler centralises the row logic', 'is_correct': True},
                            ],
                            'explain': 'Delegation rides bubbling, it does not stop it; the guard against stray clicks is the cost.',
                        },
                        {
                            'slug': 'prevent-default',
                            'title': 'What it stops',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'event.preventDefault() inside a submit handler:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Cancels the browser\u2019s default form send/reload', 'is_correct': True},
                                {'id': 'b', 'text': 'Stops bubbling too', 'is_correct': False},
                                {'id': 'c', 'text': 'Disables the button', 'is_correct': False},
                                {'id': 'd', 'text': 'Removes the listener', 'is_correct': False},
                            ],
                            'explain': 'stopPropagation() is the bubbling switch — different method, different job.',
                        },
                        {
                            'slug': 'input-vs-change',
                            'title': 'Firing moments',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Live character-count as the user types uses:',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the input event', 'is_correct': True},
                                {'id': 'b', 'text': 'the change event', 'is_correct': False},
                                {'id': 'c', 'text': 'the submit event', 'is_correct': False},
                                {'id': 'd', 'text': 'keyup exclusively', 'is_correct': False},
                            ],
                            'explain': 'change commits on blur/selection; input is the per-keystroke stream.',
                        },
                        {
                            'slug': 'timer-cleanup',
                            'title': 'Hygiene',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'A running setInterval(id) must eventually be cancelled. Answer with the '
                                'FULL cancel call including the id argument, exactly as written in lessons.'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'clearInterval(id)',
                            'explain': 'clearInterval/clearTimeout — every start deserves a matching cleanup.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 8 Quiz',
                    'slug': 'js-dom-events-quiz',
                    'objective': 'Check mastery of selection, node building and events.',
                    'duration': 8,
                    'body': """# Chapter 8 quiz

Five questions on the DOM and events — the browser half of
JavaScript.""",
                    'exercises': [
                        {
                            'slug': 'q8-defer-null',
                            'title': 'Missing defer',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A head script (no defer) calls document.querySelector("#app"); #app is later in body. Result:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'null — the element is not parsed yet', 'is_correct': True},
                                {'id': 'b', 'text': 'The element, deferred automatically', 'is_correct': False},
                                {'id': 'c', 'text': 'TypeError from querySelector', 'is_correct': False},
                                {'id': 'd', 'text': 'undefined variable', 'is_correct': False},
                            ],
                            'explain': 'Selectors return null for "no match YET" — hence defer / DOMContentLoaded.',
                        },
                        {
                            'slug': 'q8-dataset',
                            'title': 'data attributes',
                            'exercise_type': 'output_prediction',
                            'instructions': 'HTML: <tr data-id="42"></tr>.  JS reads row.dataset.id.  Value and type? (answer like: 42 string)',
                            'xp_reward': 50,
                            'expected_output': '42 string',
                            'choices': [],
                            'explain': 'Dataset values are always STRINGS — Number(row.dataset.id) if you need math.',
                        },
                        {
                            'slug': 'q8-remove-api',
                            'title': 'Modern detach',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The MODERN one-call way to remove element el from its parent:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'el.remove()', 'is_correct': True},
                                {'id': 'b', 'text': 'el.parentElement.removeChild(el) — the legacy two-step', 'is_correct': False},
                                {'id': 'c', 'text': 'el.delete()', 'is_correct': False},
                                {'id': 'd', 'text': 'el.detach()', 'is_correct': False},
                            ],
                            'explain': 'b is the correct LEGACY form (still everywhere); a is the modern self-service.',
                        },
                        {
                            'slug': 'q8-enter-key',
                            'title': 'Keyboard payload',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'In a keydown handler, event.____ gives the semantic key name like '
                                '"Enter" or "ArrowUp". Answer with the property name, lower-case.'
                            ),
                            'xp_reward': 50,
                            'solution_code': 'key',
                            'explain': 'event.key === "Enter" — event.code would be the physical "NumpadEnter" etc.',
                        },
                        {
                            'slug': 'q8-capture-order',
                            'title': 'Phases',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Default addEventListener timing:',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Bubbling phase — after target, walking up', 'is_correct': True},
                                {'id': 'b', 'text': 'Capturing — before target, walking down', 'is_correct': False},
                                {'id': 'c', 'text': 'Target phase only', 'is_correct': False},
                                {'id': 'd', 'text': 'Randomly either', 'is_correct': False},
                            ],
                            'explain': 'Capture:true opts into the early walk; default is the bubble.',
                        },
                    ],
                },
            ],
        },
    ],
}
