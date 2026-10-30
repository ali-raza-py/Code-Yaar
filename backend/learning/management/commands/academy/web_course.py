"""Course 3 — Web Development Foundations: HTML, CSS & JavaScript.

Learners build up to a small portfolio page. The live sandbox executes Python
only, so web exercises are graded honestly by the server through answer
comparison (multiple choice / output prediction / fill in the blank) — the
platform does NOT claim that student HTML/CSS/JS is rendered or executed.
"""

COURSE = {
    'slug': 'web-foundations',
    'title': 'Web Development Foundations: HTML, CSS & JavaScript',
    'subtitle': 'Structure, style and add behaviour to web pages — ending in a portfolio page.',
    'description': (
        'Understand how the web works, write semantic HTML, style pages with '
        'CSS (box model, flexbox), and make them interactive with JavaScript '
        'and the DOM. You finish by planning and assembling a personal '
        'portfolio page and passing a final assessment. Note: answers are '
        'checked by the server; page code is not executed by the current '
        'sandbox.'
    ),
    'difficulty': 'beginner',
    'language': 'javascript',
    'prerequisites': 'None — a first course in web development.',
    'track': {
        'slug': 'web',
        'title': 'Web Development',
        'description': 'Build modern websites from structure to interactivity.',
    },
    'objectives': [
        'Explain how a browser obtains and renders a page.',
        'Write valid semantic HTML documents.',
        'Style elements with CSS selectors, the box model and flexbox.',
        'Use JavaScript variables, functions and events.',
        'Read and modify the page with the DOM API.',
        'Assemble a multi-section portfolio page.',
    ],
    'modules': [
        {
            'title': 'How the Web Works',
            'slug': 'how-web-works',
            'description': 'Requests, responses and the three core web languages.',
            'lessons': [
                {
                    'title': 'Browsers, Servers and HTML/CSS/JS',
                    'slug': 'web-trio',
                    'objective': 'Describe the request/response cycle and the role of each language.',
                    'duration': 10,
                    'body': (
                        '# The request/response cycle\n\n'
                        'You type a URL, the browser sends an **HTTP request** to a '
                        'server, the server replies with an **HTTP response** that '
                        'usually contains an HTML document. The browser parses the '
                        'HTML, applies CSS for layout and colour, then runs JavaScript '
                        'to add behaviour.\n\n'
                        '## The trio\n'
                        '- **HTML** — structure and meaning (nouns of the page)\n'
                        '- **CSS** — presentation (how it looks)\n'
                        '- **JavaScript** — behaviour (what it does)\n\n'
                        'A minimal document:\n\n'
                        '```html\n<!DOCTYPE html>\n<html lang="en">\n  <head>\n'
                        '    <meta charset="utf-8">\n    <title>My Page</title>\n'
                        '  </head>\n  <body>\n    <h1>Hello</h1>\n  </body>\n</html>\n```\n\n'
                        '## Common mistakes\n'
                        'Putting page text inside `<head>` — visible content belongs '
                        'in `<body>`; `<head>` holds metadata only.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'role-of-css',
                            'title': 'Role of CSS',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What is CSS primarily responsible for?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Page structure and meaning', 'is_correct': False},
                                {'id': 'b', 'text': 'How the page looks and is laid out', 'is_correct': True},
                                {'id': 'c', 'text': 'Storing data on the server', 'is_correct': False},
                                {'id': 'd', 'text': 'Clicking links automatically', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'visible-content-tag',
                            'title': 'Where visible content goes',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the tag that wraps all visible page content:\n\n'
                                '```html\n<______>\n  <h1>Hello</h1>\n</______>\n```'
                            ),
                            'starter_code': '<',
                            'solution_code': '<body>',
                            'explain': 'Everything the user sees lives inside the <body> element.',
                            'xp_reward': 50,
                        },
                    ],
                },
            ],
        },
        {
            'title': 'HTML Structure',
            'slug': 'html-structure',
            'description': 'Headings, lists, links, images and semantic layout.',
            'lessons': [
                {
                    'title': 'Text, Links and Images',
                    'slug': 'text-links-images',
                    'objective': 'Mark up headings, paragraphs, links and images correctly.',
                    'duration': 12,
                    'body': (
                        '# Core elements\n\n'
                        '```html\n<h1>Main title</h1>\n<p>A paragraph of text with a '
                        '<a href="https://example.com">link</a>.</p>\n'
                        '<img src="photo.jpg" alt="A red bicycle">\n```\n\n'
                        '- Headings run `<h1>`–`<h6>`; use one `<h1>` per page and do '
                        'not skip levels.\n'
                        '- `<a href="...">` creates a hyperlink.\n'
                        '- `<img>` is self-closing; its `alt` text describes the image '
                        'for screen readers and for when loading fails.\n\n'
                        '## Lists\n\n'
                        '```html\n<ul>            <!-- unordered -->\n  <li>One</li>\n'
                        '  <li>Two</li>\n</ul>\n<ol>           <!-- ordered -->\n'
                        '  <li>First</li>\n</ol>\n```\n\n'
                        '## Common mistakes\n'
                        'Leaving `alt` empty on informative images — always describe '
                        'what the image conveys.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'alt-purpose',
                            'title': 'Why alt text?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What is the purpose of the alt attribute on an image?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'It shows a tooltip on hover', 'is_correct': False},
                                {'id': 'b', 'text': 'It describes the image for accessibility and failed loads', 'is_correct': True},
                                {'id': 'c', 'text': 'It sets the image width', 'is_correct': False},
                                {'id': 'd', 'text': 'It links the image to another page', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'list-tag',
                            'title': 'Bulleted list tag',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which element produces a bulleted (unordered) list?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '<ol>', 'is_correct': False},
                                {'id': 'b', 'text': '<ul>', 'is_correct': True},
                                {'id': 'c', 'text': '<li>', 'is_correct': False},
                                {'id': 'd', 'text': '<list>', 'is_correct': False},
                            ],
                        },
                    ],
                },
                {
                    'title': 'Semantic Layout Elements',
                    'slug': 'semantic-layout',
                    'objective': 'Lay out a page with header, nav, main, section, footer.',
                    'duration': 12,
                    'body': (
                        '# Semantic HTML\n\n'
                        'Semantic elements describe their **meaning**, not just their '
                        'appearance. Browsers, screen readers and search engines use '
                        'that meaning.\n\n'
                        '```html\n<body>\n  <header>Logo and site title</header>\n'
                        '  <nav> Links </nav>\n  <main>\n    <section>About</section>\n'
                        '    <section>Projects</section>\n  </main>\n  <footer>Copyright</footer>\n'
                        '</body>\n```\n\n'
                        '- `<main>` — unique primary content, exactly one per page.\n'
                        '- `<nav>` — major link groups.\n'
                        '- `<section>` — thematic grouping, usually with a heading.\n'
                        '- `<div>` — a generic box with no meaning; use it only when no '
                        'semantic element fits.\n\n'
                        '## Common mistakes\n'
                        'Nesting everything in `<div>` soup. If the box is the page '
                        'footer, use `<footer>`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'one-per-page',
                            'title': 'Exactly one per page',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which element should appear exactly once and holds the primary content?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '<section>', 'is_correct': False},
                                {'id': 'b', 'text': '<div>', 'is_correct': False},
                                {'id': 'c', 'text': '<main>', 'is_correct': True},
                                {'id': 'd', 'text': '<header>', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'CSS Styling',
            'slug': 'css-styling',
            'description': 'Selectors, the box model, colours, and flexbox layout.',
            'lessons': [
                {
                    'title': 'Selectors, Colours and the Box Model',
                    'slug': 'selectors-box-model',
                    'objective': 'Target elements and control spacing with the box model.',
                    'duration': 14,
                    'body': (
                        '# Attaching CSS\n\n'
                        '```html\n<link rel="stylesheet" href="styles.css">\n```\n\n'
                        '## Selectors\n\n'
                        '```css\nh1        { color: #2563eb; }        /* element */\n'
                        '.card     { padding: 16px; }           /* class */\n'
                        '#logo     { width: 120px; }            /* id */\n'
                        'nav a     { text-decoration: none; }   /* descendant */\n```\n\n'
                        '## The box model\n\n'
                        'From inside out: **content → padding → border → margin**. '
                        '`box-sizing: border-box` makes `width` include padding and '
                        'border, which most layouts rely on:\n\n'
                        '```css\n*, *::before, *::after {\n  box-sizing: border-box;\n}\n```\n\n'
                        '## Common mistakes\n'
                        'Adding margin *inside* a card and padding *outside* it — '
                        'padding is inner space, margin is outer space.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'class-selector',
                            'title': 'Class selector syntax',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which selector targets every element with class="card"?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '#card', 'is_correct': False},
                                {'id': 'b', 'text': '.card', 'is_correct': True},
                                {'id': 'c', 'text': 'card()', 'is_correct': False},
                                {'id': 'd', 'text': '*card', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'box-order',
                            'title': 'Box model order',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'From the content outward, what is the correct order?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'content, margin, padding, border', 'is_correct': False},
                                {'id': 'b', 'text': 'content, padding, border, margin', 'is_correct': True},
                                {'id': 'c', 'text': 'padding, content, border, margin', 'is_correct': False},
                                {'id': 'd', 'text': 'content, border, padding, margin', 'is_correct': False},
                            ],
                        },
                    ],
                },
                {
                    'title': 'Flexbox Layout',
                    'slug': 'flexbox',
                    'objective': 'Align and distribute space with flexbox.',
                    'duration': 12,
                    'body': (
                        '# Flexbox\n\n'
                        'Turn a container into a flex box and its children lay out in a '
                        'row (default) or column:\n\n'
                        '```css\n.toolbar {\n  display: flex;\n  justify-content: space-between;\n'
                        '  align-items: center;\n  gap: 12px;\n}\n```\n\n'
                        '- `justify-content` distributes items **along** the main axis.\n'
                        '- `align-items` positions them **across** the cross axis.\n'
                        '- `gap` adds space between items without margins.\n\n'
                        'A common nav bar: logo left, links right — `display: flex` plus '
                        '`justify-content: space-between`.\n\n'
                        '## Common mistakes\n'
                        'Applying `justify-content` to a block container that was never '
                        'given `display: flex` — nothing happens.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'space-between',
                            'title': 'Spread items to the edges',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In a flex row, which declaration pushes the first item to the left edge and the last to the right edge?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'justify-content: center', 'is_correct': False},
                                {'id': 'b', 'text': 'align-items: stretch', 'is_correct': False},
                                {'id': 'c', 'text': 'justify-content: space-between', 'is_correct': True},
                                {'id': 'd', 'text': 'text-align: right', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'enable-flex',
                            'title': 'Enabling flexbox',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the declaration that turns ``.toolbar`` into a flex container:\n\n'
                                '```css\n.toolbar {\n  ______: flex;\n}\n```'
                            ),
                            'starter_code': '',
                            'solution_code': 'display: flex',
                            'explain': 'display: flex activates flex layout on the container.',
                            'xp_reward': 50,
                        },
                    ],
                },
            ],
        },
        {
            'title': 'JavaScript and the DOM',
            'slug': 'js-dom',
            'description': 'Variables, functions, events and changing the page.',
            'lessons': [
                {
                    'title': 'Variables, Functions and console.log',
                    'slug': 'js-basics',
                    'objective': 'Declare values, call functions and predict console output.',
                    'duration': 14,
                    'body': (
                        '# JavaScript basics\n\n'
                        '```js\nconst name = "Yaar";   // cannot be reassigned\n'
                        'let count = 0;             // can change\ncount = count + 1;\n\n'
                        'function double(n) {\n  return n * 2;\n}\n\n'
                        'console.log(double(5));    // 10\n```\n\n'
                        '- `const` for values that never point elsewhere; `let` when '
                        'reassignment is needed.\n'
                        '- `function` declarations take parameters and `return` a value.\n'
                        '- `console.log` prints to the developer console.\n\n'
                        'JavaScript is **case-sensitive**: `myVar` and `myvar` are '
                        'different names.\n\n'
                        '## Common mistakes\n'
                        'Calling a `const` function before its declaration line — the '
                        'binding exists but is not initialised yet (temporal dead zone).\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'js-predict-double',
                            'title': 'Predict the output',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'What does this log?\n\n```js\nfunction double(n) {\n'
                                '  return n * 2;\n}\nconsole.log(double(7));\n```'
                            ),
                            'expected_output': '14',
                            'explain': 'double(7) returns 7 * 2 = 14, which console.log prints.',
                            'xp_reward': 60,
                        },
                        {
                            'slug': 'js-reassign-keyword',
                            'title': 'Which keyword allows reassignment?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which declaration can be reassigned later?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'const x = 1;', 'is_correct': False},
                                {'id': 'b', 'text': 'let x = 1;', 'is_correct': True},
                                {'id': 'c', 'text': 'fixed x = 1;', 'is_correct': False},
                                {'id': 'd', 'text': 'final x = 1;', 'is_correct': False},
                            ],
                        },
                    ],
                },
                {
                    'title': 'Events and Changing the Page',
                    'slug': 'events-dom',
                    'objective': 'Select elements, respond to clicks and change content.',
                    'duration': 14,
                    'body': (
                        '# The DOM\n\n'
                        'The browser turns HTML into a tree of objects — the Document '
                        'Object Model. JavaScript can query and change it:\n\n'
                        '```js\nconst button = document.querySelector("#buy");\n'
                        'const label = document.querySelector(".status");\n\n'
                        'button.addEventListener("click", function () {\n'
                        '  label.textContent = "Purchased!";\n});\n```\n\n'
                        '- `document.querySelector(cssSelector)` returns the first match.\n'
                        '- `addEventListener("click", fn)` runs `fn` when the user clicks.\n'
                        '- `textContent` gets/sets an element\'s text.\n\n'
                        '## Common mistakes\n'
                        'Running a script before the page exists — place the `<script>` '
                        'just before `</body>` or load it with `defer`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'querySelector-arg',
                            'title': 'What does querySelector take?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What argument does document.querySelector accept?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'A CSS selector string, e.g. "#buy"', 'is_correct': True},
                                {'id': 'b', 'text': 'An element ID without any prefix', 'is_correct': False},
                                {'id': 'c', 'text': 'A tag name only', 'is_correct': False},
                                {'id': 'd', 'text': 'A Boolean', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'js-predict-text',
                            'title': 'Predict the DOM result',
                            'exercise_type': 'output_prediction',
                            'instructions': (
                                'The page contains `<p class="msg">Hi</p>`. After this '
                                'script runs, what is `document.querySelector(".msg").textContent`?\n\n'
                                '```js\nconst p = document.querySelector(".msg");\n'
                                'p.textContent = "Hello";\n```'
                            ),
                            'expected_output': 'Hello',
                            'explain': 'Assigning textContent replaces the paragraph text with "Hello".',
                            'xp_reward': 60,
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Project: Portfolio Page',
            'slug': 'portfolio-project',
            'description': 'Combine everything into one deployable page.',
            'lessons': [
                {
                    'title': 'Planning the Portfolio Structure',
                    'slug': 'plan-portfolio',
                    'objective': 'Design the sections and markup of a personal portfolio page.',
                    'duration': 15,
                    'body': (
                        '# Build a portfolio page\n\n'
                        'A portfolio is your web developer résumé. Plan four sections:\n\n'
                        '1. **Header / hero** — name, one-line intro.\n'
                        '2. **About** — short bio with a photo (`alt` text!).\n'
                        '3. **Projects** — a flexbox grid of cards, each with title, '
                        'description and links.\n'
                        '4. **Contact footer** — email link and social links.\n\n'
                        'Skeleton:\n\n'
                        '```html\n<body>\n  <header class="hero">\n'
                        '    <h1>Amina Khan</h1>\n    <p>Front-end learner</p>\n  </header>\n'
                        '  <main>\n    <section id="about">…</section>\n'
                        '    <section id="projects">\n      <div class="grid">\n'
                        '        <article class="card">…</article>\n'
                        '      </div>\n    </section>\n  </main>\n'
                        '  <footer>…</footer>\n</body>\n```\n\n'
                        'Style with one external stylesheet, and add a small JS '
                        'interaction (for example a theme toggle button wired with '
                        '`addEventListener`).\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'portfolio-stylesheet',
                            'title': 'Link the stylesheet',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the `<head>` line that attaches an external '
                                ' stylesheet called ``styles.css``:\n\n'
                                '```html\n<link ______="styles.css" href="styles.css">\n```'
                            ),
                            'starter_code': '<link ',
                            'solution_code': '<link rel="stylesheet" href="styles.css">',
                            'explain': 'rel="stylesheet" tells the browser the linked file is CSS.',
                            'xp_reward': 60,
                        },
                        {
                            'slug': 'portfolio-section-choice',
                            'title': 'Semantic projects grid',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Each project entry has a title, description and links. Which element best expresses one self-contained project entry?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '<span>', 'is_correct': False},
                                {'id': 'b', 'text': '<article>', 'is_correct': True},
                                {'id': 'c', 'text': '<b>', 'is_correct': False},
                                {'id': 'd', 'text': '<table>', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
    ],
    'assessment': [
        {
            'slug': 'web-final-doctype',
            'title': 'Document declaration',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which line correctly starts a modern HTML5 document?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': '<!DOCTYPE html>', 'is_correct': True},
                {'id': 'b', 'text': '<html html5>', 'is_correct': False},
                {'id': 'c', 'text': '#HTML5', 'is_correct': False},
                {'id': 'd', 'text': '<head html5>', 'is_correct': False},
            ],
        },
        {
            'slug': 'web-final-id-selector',
            'title': 'ID selector',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which CSS selector targets the element with id="logo"?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': '.logo', 'is_correct': False},
                {'id': 'b', 'text': '#logo', 'is_correct': True},
                {'id': 'c', 'text': 'logo*', 'is_correct': False},
                {'id': 'd', 'text': 'a.logo', 'is_correct': False},
            ],
        },
        {
            'slug': 'web-final-boxmodel',
            'title': 'Outer spacing property',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which property creates space OUTSIDE an element\'s border?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'padding', 'is_correct': False},
                {'id': 'b', 'text': 'gap', 'is_correct': False},
                {'id': 'c', 'text': 'margin', 'is_correct': True},
                {'id': 'd', 'text': 'border-spacing', 'is_correct': False},
            ],
        },
        {
            'slug': 'web-final-js-log',
            'title': 'Predict the output',
            'exercise_type': 'output_prediction',
            'instructions': 'What does this log?\n\n```js\nlet x = 2;\nx += 3;\nconsole.log(x);\n```',
            'expected_output': '5',
            'xp_reward': 20,
        },
        {
            'slug': 'web-final-dom-method',
            'title': 'Responding to clicks',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which method attaches a click handler to a button element?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'button.addEventListener("click", fn)', 'is_correct': True},
                {'id': 'b', 'text': 'button.on("click", fn)', 'is_correct': False},
                {'id': 'c', 'text': 'document.listen(fn)', 'is_correct': False},
                {'id': 'd', 'text': 'button.attach(fn)', 'is_correct': False},
            ],
        },
    ],
}
