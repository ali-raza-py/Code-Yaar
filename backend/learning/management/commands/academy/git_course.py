"""Course 4 — Git and GitHub Fundamentals.

Ten chapters that take a learner from "what is version control" to a
collaborative GitHub workflow with branches, pull requests and conflict
resolution. Every check is answer-graded server-side (multiple choice /
multiple select / output prediction / fill in the blank); nothing pretends
to execute git for the learner. Each chapter ends with a Chapter Quiz
lesson, and the course closes with a project chapter and a 24-question
final assessment that spans the whole syllabus.
"""

COURSE = {
    'slug': 'git-github-foundations',
    'title': 'Git & GitHub',
    'subtitle': 'Track changes, branch safely and collaborate on GitHub.',
    'description': (
        'Git records every change you make to a project so you can inspect '
        'history, undo mistakes and work with others without fear. This '
        'course starts with why version control exists, then builds the full '
        'daily workflow: repositories, staging, commits, branching, merging, '
        'remotes on GitHub, pull requests, and recovery tools like restore, '
        'revert, reset and stash. You finish by running a professional '
        'workflow on a real repository of your own.'
    ),
    'difficulty': 'beginner',
    'language': 'other',
    'prerequisites': (
        'Basic computer knowledge and familiarity with any programming '
        'language. Comfort with a terminal / command prompt helps but the '
        'early chapters introduce it slowly.'
    ),
    'track': {
        'slug': 'developer-tools',
        'title': 'Developer Tools',
        'category': 'other',
        'description': 'The professional tooling every developer is expected to know.',
    },
    'objectives': [
        'Explain why version control exists and how Git differs from GitHub.',
        'Initialise, clone and configure repositories confidently.',
        'Use the working directory / staging area / repository workflow.',
        'Create branches, merge them and resolve merge conflicts by hand.',
        'Push and pull with GitHub, and collaborate through forks and pull requests.',
        'Inspect history and undo mistakes with log, diff, restore, revert, reset and stash.',
        'Follow a professional GitHub workflow: commit messages, README, issues.',
        'Publish a documented repository with branches and a pull request.',
    ],
    'certification': {'passing_score': 70},
    'modules': [
        # ════════════════════ Chapter 1 ════════════════════
        {
            'title': 'Introduction to Version Control',
            'slug': 'vc-intro',
            'description': 'What version control is, why developers need it, and where Git fits.',
            'lessons': [
                {
                    'title': 'What Is Version Control?',
                    'slug': 'what-is-version-control',
                    'objective': 'Define version control and name the problems it solves.',
                    'duration': 10,
                    'body': """# What is version control?

Imagine writing a final assignment by saving a new copy every day:
`assignment_v1.doc`, `assignment_v2.doc`, `assignment_FINAL.doc`,
`assignment_FINAL_really_final.doc`. A week later you cannot answer simple
questions: *Which version is correct? What did I change on Tuesday? Can I
get back yesterday's paragraph without losing today's work?*

**Version control** (also called *source control* or *revision control*) is
a system that records changes to files over time so that you can recall
specific versions later. A version control system keeps:

1. **Every version of every file** — nothing is lost just because you saved over it.
2. **Who made each change** — every edit is linked to an author.
3. **Why each change was made** — the author writes a message explaining the reason.
4. **The ability to go back** — any earlier version can be restored in seconds.

With that history you can ask and answer real questions:

- *What exactly changed between yesterday and today?*
- *Who broke the login page, and in which change?*
- *How do I return to the version that worked last week?*
- *Can two people edit the same project at the same time without destroying each other's work?*

Teams face these problems multiplied by hundreds of files and dozens of
people. Without version control, collaboration means emailing zip files and
stepping on each other's changes. With it, everyone works on their own
copy and the system merges the work safely.

> **Key term — commit (revision):** one saved snapshot of the project,
> recorded with an author, a message and a timestamp. Older tools say
> "revision"; Git says "commit". They mean the same idea.

## Why it matters
Every professional codebase you will ever join is under version control.
Interviewers expect you to know it; coursework teams survive deadlines
because of it; your future self thanks you when a laptop dies.

## Real-world application
Two students pair-build a project: one writes the interface, the other the
logic. Each commits their own work. When the interface breaks something the
logic relied on, they compare the two latest commits and restore only the
broken part — the rest of the work is untouched.

## Common mistakes
- Thinking "I keep backups on Google Drive, so I have version control."
  Drive stores a few snapshots without authors, messages, diffs or merge
  support. That is a backup, not version control.
- Committing huge binary files (videos, zips) that bloat history forever.
  Version control shines on text files where changes compare line by line.

## Lesson summary
Version control = history for your files, with attribution and the power to
rewind. It solves the `_FINAL_really_final.doc` problem for individuals and
makes safe teamwork possible.""",
                    'exercises': [
                        {
                            'slug': 'vc-problem-definition',
                            'title': 'What version control gives you',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which option best describes the core service a version control system provides?',
                            'context': 'Recall the four things a version control system keeps.',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'A record of every file saved over time, with author, message and the ability to restore any version', 'is_correct': True},
                                {'id': 'b', 'text': 'A cloud folder that always keeps the newest copy of each file', 'is_correct': False},
                                {'id': 'c', 'text': 'A tool that prevents all bugs by testing your code', 'is_correct': False},
                                {'id': 'd', 'text': 'A chat system for a development team', 'is_correct': False},
                            ],
                            'explain': (
                                'Version control is history for your files: snapshots with '
                                'authors and messages, restorable at any time. A backup keeps '
                                'only the newest copy; version control keeps all of them.'
                            ),
                        },
                        {
                            'slug': 'backup-vs-vcs',
                            'title': 'Backup or version control?',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL capabilities that a version control system provides but a plain file backup does not.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Seeing who changed a specific file and why', 'is_correct': True},
                                {'id': 'b', 'text': 'Comparing line-by-line differences between two versions', 'is_correct': True},
                                {'id': 'c', 'text': 'Storing a copy of the newest files', 'is_correct': False},
                                {'id': 'd', 'text': "Merging two people's changes to the same project safely", 'is_correct': True},
                            ],
                            'explain': (
                                'Backups store copies. Version control adds history with '
                                'authors and messages, line-level diffs, and safe merging — '
                                'the abilities that make team work possible. Storing the '
                                'newest copy is something plain backups do too.'
                            ),
                        },
                    ],
                },
                {
                    'title': 'Why Developers Need Version Control',
                    'slug': 'why-developers-need-it',
                    'objective': 'Explain concrete situations where version control saves a developer.',
                    'duration': 8,
                    'body': """# Why every developer needs version control

Programming means changing code constantly, and every change risks breaking
something that worked. Version control turns that risk into routine.

## Situations that make it essential

**"It worked yesterday."** You changed five files and now the app crashes.
Without history you inspect files one by one, guessing. With Git you compare
yesterday's commit with your current work and see every changed line.

**"Who broke this?"** In a team of eight, the checkout page fails at 2 a.m.
Because every commit stores an author and a message, you find the exact
change that caused the failure, contact its author, and undo just that
change — in minutes instead of a full investigation.

**"Let's try the other approach."** You want to experiment with a new
design but fear losing the working one. Version control keeps both versions
side by side so you can choose later — experiments cost nothing.

**"Send me the final project."** Clients and lecturers change requirements.
You can deliver version A today and keep building version B at the same
time, because both exist in the same repository.

**Disaster recovery.** Laptops die. A repository's complete history lives
on your machine *and* on a server, so one broken disk loses nothing.

## The habit behind all of this
The professional habit is: *make a small change, check it works, commit it,
write why.* History is only useful when it is honest and frequent. Ten
small commits tell a story; one commit called "updates" tells nothing.

## Important terminology
- **Commit:** a saved snapshot with a message and author.
- **History:** the timeline of all commits.
- **Diff:** the list of line-level differences between two versions.
- **Checkpoint:** a commit made specifically so you can return later.

## Common mistakes
- Working for days without committing "because it isn't finished."
  Commits are checkpoints, not presentations. Commit broken states with an
  honest message like `wip: cart not working yet`.
- Writing messages like `fix`, `update`, `asdf`. Six months later they
  answer nothing. Write the *why*: `fix: prevent double charge on retry`.

## Lesson summary
Version control removes the fear from change: diagnose with diffs, locate
faults by author, experiment safely, deliver any old version on request,
and survive hardware failure. The habit that makes it work is frequent,
honest, small commits.""",
                    'exercises': [
                        {
                            'slug': 'commit-frequency',
                            'title': 'When should you commit?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A feature will take two days to build. Which is the best commit habit?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'One commit at the end, when everything works perfectly', 'is_correct': False},
                                {'id': 'b', 'text': 'Small commits after each checkpoint that works, with honest messages — even while unfinished', 'is_correct': True},
                                {'id': 'c', 'text': 'Never commit until a teammate reviews the code', 'is_correct': False},
                                {'id': 'd', 'text': 'Commit only when the client asks for a delivery', 'is_correct': False},
                            ],
                            'explain': (
                                'Frequent small commits create a safety net: you can rewind '
                                'to any checkpoint. One giant commit at the end throws away '
                                'all the intermediate history that makes Git useful.'
                            ),
                        },
                        {
                            'slug': 'who-broke-it',
                            'title': 'Finding the culprit fast',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A team of 10 finds a bug introduced last week. Why can version control locate it quickly?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Every commit stores author, message and timestamp, so changes can be inspected one by one', 'is_correct': True},
                                {'id': 'b', 'text': 'Git automatically rewrites buggy code correctly', 'is_correct': False},
                                {'id': 'c', 'text': 'Team members email each other before every edit', 'is_correct': False},
                                {'id': 'd', 'text': 'The newest file is always the correct file', 'is_correct': False},
                            ],
                            'explain': (
                                'History with attribution is the point: you walk commit by '
                                'commit and find the change that introduced the bug. Git '
                                'never rewrites code by itself.'
                            ),
                        },
                    ],
                },
                {
                    'title': 'Centralized vs Distributed, and What Git Is',
                    'slug': 'centralized-vs-distributed',
                    'objective': 'Contrast centralized and distributed version control; describe how Git stores history.',
                    'duration': 10,
                    'body': """# Centralized vs distributed version control

## Centralized (CVCS) — e.g. SVN
Older systems keep **one server that holds all history**. Everyone checks
out files from it and commits back to it.

- Simple to understand: one "truth" on the server.
- Painful consequences: **no server, no commits** — lost internet on a
  train means a lost workday. The server is a single point of failure; if
  it dies without a backup, all history dies with it.

## Distributed (DVCS) — Git, Mercurial
Every developer's machine holds a **complete copy of the entire history**,
not just the latest files.

- You commit offline — a server is only needed when you *share* work.
- If any server dies, every clone still contains the full history and can
  restore it.
- Because everyone works on private copies, merging is normal daily work,
  so distributed tools made merging powerful (you meet it in chapter 5).

## How Git stores history
Git stores a **snapshot** of the whole project at each commit (not a list
of changes), then compresses identical content internally so storage
stays small.

- Each commit points to its **parent** — the commit before it — forming a
  chain. That chain *is* the history.
- Each commit has a **SHA-1 hash**: a 40-character fingerprint like
  `a3f2b81...` computed from the commit's content, author, message and
  time. Nobody can quietly alter a commit without changing its fingerprint,
  so history is tamper-evident.

## Git vs GitHub — a crucial distinction
- **Git** is the version control *program* installed on your computer.
  It works completely offline.
- **GitHub** is a *website/service* that hosts Git repositories so teams
  can share them, review code (pull requests) and publish open source.
  Alternatives exist: GitLab, Bitbucket, Azure DevOps.

You can use Git without GitHub. You cannot use GitHub without Git.

## Common mistakes
- Saying "I pushed my code to Git." You push to a **remote**, commonly
  hosted on GitHub. Git itself is just the tool on your laptop.
- Believing GitHub *is* your backup. If you only ever work on the GitHub
  web editor with no local clone, you actually have a centralized setup —
  the weakness of CVCS, by accident.

## Lesson summary
Centralized systems depend on one server; distributed systems like Git give
everyone the full history. Git records snapshots chained by parents, names
each commit with a hash, and is often paired with (but distinct from) the
GitHub hosting service.""",
                    'exercises': [
                        {
                            'slug': 'distributed-meaning',
                            'title': 'Distributed history',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What does it mean that Git is a *distributed* system?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': "History lives only on GitHub's servers", 'is_correct': False},
                                {'id': 'b', 'text': 'Every clone contains the complete project history', 'is_correct': True},
                                {'id': 'c', 'text': 'Files are split across many machines', 'is_correct': False},
                                {'id': 'd', 'text': 'Commits run in parallel on many CPUs', 'is_correct': False},
                            ],
                            'explain': (
                                'Distributed means every developer keeps a full copy of '
                                'history locally — that is why you can commit offline and why '
                                'a dead server is recoverable.'
                            ),
                        },
                        {
                            'slug': 'git-vs-github',
                            'title': 'Git vs GitHub',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which statement is correct about Git and GitHub?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'GitHub is the program on your computer; Git is the website', 'is_correct': False},
                                {'id': 'b', 'text': 'Git and GitHub are two names for the same product', 'is_correct': False},
                                {'id': 'c', 'text': 'Git is the tool you install; GitHub is one service that hosts Git repositories', 'is_correct': True},
                                {'id': 'd', 'text': 'You must pay GitHub to use Git', 'is_correct': False},
                            ],
                            'explain': (
                                'Git is the local version control program. GitHub hosts Git '
                                'repositories — GitLab and Bitbucket can do the same job.'
                            ),
                        },
                        {
                            'slug': 'commit-hash-fill',
                            'title': 'The commit fingerprint',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the sentence. Git names each commit with a '
                                '40-character ____________ computed from its content, '
                                'author and message. (One word, lowercase.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'hash',
                            'explain': (
                                'Each commit has a SHA-1 hash — a fingerprint that changes if '
                                'anything in the commit changes, making history tamper-evident.'
                            ),
                        },
                    ],
                },
                {
                    'title': 'Chapter 1 Quiz',
                    'slug': 'vc-intro-quiz',
                    'objective': 'Check understanding of version control fundamentals.',
                    'duration': 5,
                    'body': """# Chapter 1 quiz

Six questions on what version control is, why developers need it, and the
difference between Git and GitHub. Answer after reading all three lessons —
every question is graded instantly.""",
                    'exercises': [
                        {
                            'slug': 'q1-snapshot-parent',
                            'title': 'How commits form history',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In Git, the history of a project is formed by…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Each commit pointing to its parent, forming a chain', 'is_correct': True},
                                {'id': 'b', 'text': 'A list of diffs stored on the GitHub server', 'is_correct': False},
                                {'id': 'c', 'text': 'Copies of files named with dates', 'is_correct': False},
                                {'id': 'd', 'text': 'The staging area remembering every edit', 'is_correct': False},
                            ],
                            'explain': 'Commits are snapshots that reference their parent commit; the chain of parents is the history.',
                        },
                        {
                            'slug': 'q1-cvs-vs-dvs',
                            'title': 'The server problem',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What is the main weakness of a centralized version control system?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'It cannot store text files', 'is_correct': False},
                                {'id': 'b', 'text': 'If the single server fails without backup, all history is lost and nobody can commit', 'is_correct': True},
                                {'id': 'c', 'text': 'It requires every developer to work offline', 'is_correct': False},
                                {'id': 'd', 'text': 'It only supports two users at a time', 'is_correct': False},
                            ],
                            'explain': 'CVCS keeps one copy of history on one server — a single point of failure. DVCS like Git avoids this by replicating history into every clone.',
                        },
                        {
                            'slug': 'q1-not-a-vcs',
                            'title': 'Which is not version control?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which of these is NOT a version control system?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Git', 'is_correct': False},
                                {'id': 'b', 'text': 'SVN', 'is_correct': False},
                                {'id': 'c', 'text': 'Mercurial', 'is_correct': False},
                                {'id': 'd', 'text': 'WinRAR', 'is_correct': True},
                            ],
                            'explain': 'WinRAR compresses archives. Git, SVN and Mercurial all record file history with authors and messages.',
                        },
                        {
                            'slug': 'q1-commit-message',
                            'title': 'Good commit messages',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which commit message is most useful six months later?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'update', 'is_correct': False},
                                {'id': 'b', 'text': 'fixed the login crash caused by the empty password check', 'is_correct': True},
                                {'id': 'c', 'text': 'final final v2', 'is_correct': False},
                                {'id': 'd', 'text': 'asdf', 'is_correct': False},
                            ],
                            'explain': 'A good message explains *why* the change exists. One-word or joke messages answer nothing when read later.',
                        },
                        {
                            'slug': 'q1-offline-commits',
                            'title': 'Committing on a train',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You are on a plane with no internet. Can a properly cloned Git repository record new commits?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'No — commits require the GitHub server', 'is_correct': False},
                                {'id': 'b', 'text': 'Yes — Git commits into your local repository and pushing comes later', 'is_correct': True},
                                {'id': 'c', 'text': 'Only if the files are smaller than 10 MB', 'is_correct': False},
                                {'id': 'd', 'text': 'Only for the first commit of a repository', 'is_correct': False},
                            ],
                            'explain': 'This is the core benefit of distributed version control: commits are local; sharing (pushing) is a separate step.',
                        },
                        {
                            'slug': 'q1-github-role',
                            'title': 'What GitHub adds',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL services GitHub provides on top of plain Git.',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Hosting repositories so teams can share history', 'is_correct': True},
                                {'id': 'b', 'text': 'Pull requests and code review', 'is_correct': True},
                                {'id': 'c', 'text': 'Compiling your code into a faster program', 'is_correct': False},
                                {'id': 'd', 'text': 'Issue tracking for bugs and features', 'is_correct': True},
                            ],
                            'explain': 'GitHub = hosting + collaboration (PRs, issues, CI). It does not compile or optimise your code; Git itself works without any of this.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 2 ════════════════════
        {
            'title': 'Git Installation and Configuration',
            'slug': 'install-config',
            'description': 'Install Git, meet the terminal, and set your identity.',
            'lessons': [
                {
                    'title': 'Installing Git',
                    'slug': 'installing-git',
                    'objective': 'Install Git on your machine and verify the installation.',
                    'duration': 8,
                    'body': """# Installing Git

Git runs on Windows, macOS and Linux. Choose your platform:

## Windows
1. Download the installer from **git-scm.com/downloads** (it detects your
   system automatically).
2. Run the `.exe`. Accepting the defaults for every screen is fine for
   learners — the defaults include **Git Bash**, a terminal that understands
   Git commands and Unix-style paths.
3. Finish and open **Git Bash** from the Start menu.

## macOS
The fastest route is the same installer from git-scm.com. (Homebrew users
can run `brew install git`.) macOS ships an Apple Git that installs on
demand when you first type `git` — acceptable to start, though updating it
later is easier via the installer or Homebrew.

## Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install git
```
Fedora uses `sudo dnf install git`.

## Verify the installation
In any terminal (Git Bash on Windows):

```bash
git --version
```

Expected output — a version line, for example:

```
git version 2.45.2
```

If the terminal replies `command not found` / `'git' is not recognized`,
the installation did not add Git to your **PATH** — reinstall and keep the
default "Add Git to PATH" option selected.

## What got installed
- The `git` program itself.
- On Windows: **Git Bash** (a terminal emulating a Unix shell) and a
  right-click menu, *Git GUI* if you chose it, and helper tools like `git
  credential manager` that save your GitHub password safely.

## Common mistakes
- Downloading a "Git client" bundled with ads from unofficial sites.
  Always use git-scm.com.
- Using PowerShell or CMD on Windows and being surprised by path syntax.
  Everything in this course works in Git Bash, which understands both.
- Skipping the version check and then following tutorials on a 10-year-old
  Git that lacks commands like `git restore` (added in Git 2.23).

## Lesson summary
Install from git-scm.com (or your package manager), keep the defaults, and
prove it with `git --version`. On Windows, plan to work inside Git Bash.""",
                    'exercises': [
                        {
                            'slug': 'official-source',
                            'title': 'Where to download Git',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What is the recommended source for installing Git on Windows?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'git-scm.com', 'is_correct': True},
                                {'id': 'b', 'text': 'Any software-download site with the highest ranking', 'is_correct': False},
                                {'id': 'c', 'text': 'github.com/downloads', 'is_correct': False},
                                {'id': 'd', 'text': 'The Windows Control Panel', 'is_correct': False},
                            ],
                            'explain': 'git-scm.com is the official Git site maintained by the Git project; the installer bundles Git Bash.',
                        },
                        {
                            'slug': 'version-check',
                            'title': 'Verifying Git',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Type the exact command that prints the installed Git version. (Two words, including the double dash.)',
                            'constraints': 'Lowercase, one space.',
                            'xp_reward': 40,
                            'solution_code': 'git --version',
                            'explain': '`git --version` prints e.g. `git version 2.45.2` and proves Git is installed and on the PATH.',
                        },
                    ],
                },
                {
                    'title': 'The Terminal and Git Bash',
                    'slug': 'terminal-git-bash',
                    'objective': 'Open a terminal, run Git commands, and read the prompt.',
                    'duration': 8,
                    'body': """# The terminal and Git Bash

A **terminal** (also *command line*, *shell*, *console*) is a window where
you type commands instead of clicking. Git's interface *is* a command-line
tool, so every workflow in this course happens here.

## Which terminal?
| Operating system | Use | Notes |
|---|---|---|
| Windows | **Git Bash** (installed with Git) | Understands Git commands and Unix paths like `/c/Users/you` |
| macOS | Terminal.app or iTerm2 | Git commands available once Git is installed |
| Linux | Any terminal (GNOME Terminal…) | Same commands everywhere |

Windows PowerShell or CMD also work for `git` commands, but Git Bash feels
closer to what tutorials and this course show.

## Reading the prompt
```bash
hp@DESKTOP ~/project (main)
$ git status
```
- The line ending with `$` is where you type. Everything after `$` is the
  **command**; Git runs it and prints the result.
- In Git Bash, a prompt showing `(main)` means: you are inside a repository
  whose current branch is `main`. Outside a repository, no branch appears.

## Essential navigation (30 seconds of survival skills)
```bash
pwd             # print working directory — where am I?
ls              # list files here
cd project      # move into the project folder
cd ..           # move up one folder
clear           # clean the screen
```
You will use `cd` constantly: Git commands act on *the folder you are in*.

## How commands are written in this course
- Lines starting with `$` are what you **type**; lines without it are
  Git's **output**.
- `#` marks a comment — never type it expecting Git to obey what follows.

## Common mistakes
- Running Git commands from a folder that is *not* a repository. Git replies
  `fatal: not a git repository`. Fix: `cd` into your project first — or
  create one (chapter 3).
- Typing the `$` that tutorials show as part of the prompt. `git status` is
  the command; `$ git status` including the `$` will fail.

## Lesson summary
Work in a terminal — Git Bash on Windows. `pwd`, `ls` and `cd` move you
around; the prompt shows your repository and branch; typed commands follow
`$`, output does not.""",
                    'exercises': [
                        {
                            'slug': 'which-terminal-windows',
                            'title': 'Terminal choice on Windows',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which terminal does this course recommend for Git on Windows?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Git Bash, installed with Git', 'is_correct': True},
                                {'id': 'b', 'text': 'The Command Prompt in safe mode', 'is_correct': False},
                                {'id': 'c', 'text': 'Any terminal is impossible on Windows', 'is_correct': False},
                                {'id': 'd', 'text': 'The GitHub desktop app console', 'is_correct': False},
                            ],
                            'explain': 'Git Bash understands Unix-style paths and matches the commands shown in tutorials and this course.',
                        },
                        {
                            'slug': 'meaning-of-prompt-branch',
                            'title': 'The branch in the prompt',
                            'exercise_type': 'multiple_choice',
                            'instructions': (
                                'In Git Bash you see this prompt line:\n'
                                '`hp@DESKTOP ~/shop (main)`\n'
                                'What does `(main)` tell you?'
                            ),
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The folder is a Git repository and the branch you are on is named main', 'is_correct': True},
                                {'id': 'b', 'text': 'The repository has exactly one commit', 'is_correct': False},
                                {'id': 'c', 'text': 'Your username on GitHub', 'is_correct': False},
                                {'id': 'd', 'text': 'The number of files staged for commit', 'is_correct': False},
                            ],
                            'explain': (
                                'Git Bash shows the current branch of the repository you are '
                                'in, in parentheses. No parentheses at all means the current '
                                'folder is not a repository.'
                            ),
                        },
                        {
                            'slug': 'cd-up-folder',
                            'title': 'Moving up',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command moves you from ~/project/src to ~/project?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'cd ..', 'is_correct': True},
                                {'id': 'b', 'text': 'cd up', 'is_correct': False},
                                {'id': 'c', 'text': 'pwd', 'is_correct': False},
                                {'id': 'd', 'text': 'cd ~', 'is_correct': False},
                            ],
                            'explain': '`..` means the parent folder. `cd ..` goes up one level; `cd ~` jumps to your home folder.',
                        },
                    ],
                },
                {
                    'title': 'Configuring Your Identity',
                    'slug': 'configuring-identity',
                    'objective': 'Set your Git username and email globally, and inspect configuration.',
                    'duration': 10,
                    'body': """# Configuring your identity

Every commit records **who made it**. Before your first commit, Git wants
two pieces of information:

```bash
git config --global user.name "Ayesha Khan"
git config --global user.email "ayesha@example.com"
```

Use the email you will add to GitHub — GitHub links commits to accounts by
email address.

## Why Git insists
Commits are snapshots with an author stamp. In a team, when a bug appears,
`git log` shows whose commit introduced it; on GitHub, the right profile
photo and name appear beside it. Wrong or missing identity means invisible
work.

## The `--global` flag
Git reads configuration at three levels, from widest to most specific:

1. **System** — every user of the machine.
2. **Global** — your user account (`~/.gitconfig`). Set once, applies to
   all repositories.
3. **Local** — one repository (`.git/config`). Wins over global. Use it for
   a work email on a work project: run the same `git config` without
   `--global`, inside that repo.

## Check your work
```bash
git config --list          # everything Git will apply, level by level
git config user.name       # ask for one value
```

Expected output of `git config user.name`:

```
Ayesha Khan
```

## Where these values live
`~/.gitconfig` is a plain text file you can open:

```ini
[user]
    name = Ayesha Khan
    email = ayesha@example.com
```

## Other settings worth knowing
```bash
git config --global core.editor "nano"     # editor for commit messages
git config --global init.defaultBranch main  # new repos start on main
git config --global alias.st status          # type git st instead of git status
```

## Common mistakes
- Using your university email on one machine and personal email on
  another — history then shows two strangers did the same project.
- Typing the name without quotes when it contains spaces
  (`user.name Ayesha Khan`) — Git takes only the first word.
- Setting identity *per repository* by forgetting `--global`, then
  wondering why the next repo "forgot" it.

## Lesson summary
`git config --global user.name / user.email` once per machine. Local
config overrides global; `git config --list` shows what is active. Match
your GitHub email so commits appear on your profile.""",
                    'exercises': [
                        {
                            'slug': 'set-name-command',
                            'title': 'Setting the user name',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that sets your Git name for ALL '
                                'repositories on your account:\n'
                                '`git config ____________ user.name "Ali Raza"`\n'
                                '(One flag, with its dashes.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': '--global',
                            'explain': '--global writes to ~/.gitconfig and applies to every repository your account works with.',
                        },
                        {
                            'slug': 'config-precedence',
                            'title': 'Which value wins?',
                            'exercise_type': 'multiple_choice',
                            'instructions': (
                                'Globally, user.name is "Ayesha Khan". Inside repo X, '
                                'the local config sets user.name to "Ayesha (Work)". '
                                'Commits made inside repo X are stamped with…'
                            ),
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Ayesha Khan — global always wins', 'is_correct': False},
                                {'id': 'b', 'text': 'Ayesha (Work) — local config overrides global', 'is_correct': True},
                                {'id': 'c', 'text': 'Both names, merged', 'is_correct': False},
                                {'id': 'd', 'text': 'No name — Git refuses to commit', 'is_correct': False},
                            ],
                            'explain': 'Git layers config: system < global < local. The most specific value present is used.',
                        },
                        {
                            'slug': 'list-config',
                            'title': 'Inspecting configuration',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command shows every configuration value Git will apply in the current repository?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'git config --list', 'is_correct': True},
                                {'id': 'b', 'text': 'git status --config', 'is_correct': False},
                                {'id': 'c', 'text': 'git show settings', 'is_correct': False},
                                {'id': 'd', 'text': 'git --config-all', 'is_correct': False},
                            ],
                            'explain': 'git config --list prints the effective merged configuration. The other options do not exist.',
                        },
                    ],
                },
                {
                    'title': 'Setup Exercise and First Checks',
                    'slug': 'initial-setup-exercise',
                    'objective': 'Run a guided setup check: version, identity and config in one pass.',
                    'duration': 7,
                    'body': """# Guided setup exercise

Do this once, in order, in Git Bash. It takes two minutes and becomes your
troubleshooting routine whenever Git "behaves strangely".

```bash
# 1. Is Git installed and recent?
git --version

# 2. Who am I to Git?
git config user.name
git config user.email

# 3. What else is configured?
git config --list

# 4. Make sure a default branch name is set (modern practice)
git config --global init.defaultBranch main
```

A healthy run looks like:

```
git version 2.45.2
Ayesha Khan
ayesha@example.com
user.name=Ayesha Khan
user.email=ayesha@example.com
init.defaultbranch=main
```

## Expected output decoded
- `git --version` → a single version line.
- `git config user.name` → your name, or **nothing** if unset (silence
  means the value is missing — that is how you spot an unconfigured
  machine).
- `git config --list` → one `key=value` line per effective setting.

## If something is wrong
| Symptom | Cause | Fix |
|---|---|---|
| `git: command not found` | Git not on PATH | Reinstall from git-scm.com, keep defaults |
| Empty `user.name` | Never configured | Run the two `git config` commands above |
| Weird editor opens on commit | `core.editor` unset + odd terminal | `git config --global core.editor "nano"` |

## Common mistakes
- Configuring identity *after* making commits — old commits keep whatever
  stamp existed at the time. Fix them or start clean in chapter 4.
- Copying a command from a forum without testing what it changes. `git
  config --list` before and after any setup command is cheap insurance.

## Lesson summary
A four-command routine — `--version`, `config user.name`,
`config user.email`, `config --list` — confirms a machine is ready for
real repository work in chapter 3.""",
                    'exercises': [
                        {
                            'slug': 'empty-name-meaning',
                            'title': 'Silence has meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You run `git config user.name` and Git prints nothing. What does that mean?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Git is corrupted; reinstall', 'is_correct': False},
                                {'id': 'b', 'text': 'No user.name value is set at any effective level', 'is_correct': True},
                                {'id': 'c', 'text': 'Your name is set but hidden for privacy', 'is_correct': False},
                                {'id': 'd', 'text': 'The command needs sudo', 'is_correct': False},
                            ],
                            'explain': 'git config prints the value it finds; an empty result means the key is unset. Set it with git config --global user.name "Your Name".',
                        },
                        {
                            'slug': 'default-branch-flag',
                            'title': 'Naming new repositories’ first branch',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that makes every NEW repository '
                                'start on a branch called main:\n'
                                '`git config --global init.default________ main`\n'
                                '(Write just the missing word, starting with a capital B.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': 'Branch',
                            'explain': 'The key is init.defaultBranch. Older Git versions (<2.28) do not have it and default to master.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 2 Quiz',
                    'slug': 'install-config-quiz',
                    'objective': 'Check understanding of installation, terminal and configuration.',
                    'duration': 5,
                    'body': """# Chapter 2 quiz

Six questions on installing Git, working in the terminal, and configuring
your identity.""",
                    'exercises': [
                        {
                            'slug': 'q2-windows-bundle',
                            'title': 'What Windows Git installs',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL components the official Windows Git installer provides.',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The git command-line program', 'is_correct': True},
                                {'id': 'b', 'text': 'Git Bash terminal', 'is_correct': True},
                                {'id': 'c', 'text': 'A Python interpreter', 'is_correct': False},
                                {'id': 'd', 'text': 'Git Credential Manager (safe GitHub sign-in helper)', 'is_correct': True},
                            ],
                            'explain': 'The installer bundles Git itself, Git Bash and helpers like the credential manager. It never installs Python.',
                        },
                        {
                            'slug': 'q2-apt-command',
                            'title': 'Installing on Ubuntu',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command installs Git on Ubuntu/Debian?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'sudo apt install git', 'is_correct': True},
                                {'id': 'b', 'text': 'npm install git', 'is_correct': False},
                                {'id': 'c', 'text': 'git --self-install', 'is_correct': False},
                                {'id': 'd', 'text': 'control panel > add git', 'is_correct': False},
                            ],
                            'explain': 'apt is Ubuntu/Debian’s package manager; Fedora uses dnf. npm installs JavaScript packages.',
                        },
                        {
                            'slug': 'q2-not-a-repo',
                            'title': 'Outside a repository',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You type `git status` in a plain folder. Git replies `fatal: not a git repository`. Why?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Git commands act on the folder you are in; this folder has no .git repository', 'is_correct': True},
                                {'id': 'b', 'text': 'status must be run with admin rights', 'is_correct': False},
                                {'id': 'c', 'text': 'You must be online for any Git command', 'is_correct': False},
                                {'id': 'd', 'text': 'The folder name has no capital letters', 'is_correct': False},
                            ],
                            'explain': 'Git works relative to your current directory. Either cd into a repo or create one with git init (chapter 3).',
                        },
                        {
                            'slug': 'q2-email-matching',
                            'title': 'Matching GitHub',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why should your Git user.email match the email on your GitHub account?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'GitHub links commits to accounts by email so your work shows on your profile', 'is_correct': True},
                                {'id': 'b', 'text': 'Git refuses to push otherwise', 'is_correct': False},
                                {'id': 'c', 'text': 'It makes commits faster', 'is_correct': False},
                                {'id': 'd', 'text': 'There is no reason; it is a myth', 'is_correct': False},
                            ],
                            'explain': 'Git will happily commit with any email — but GitHub credits contributions by matching the commit email to an account email (or a verified secondary one).',
                        },
                        {
                            'slug': 'q2-global-meaning',
                            'title': 'Scope of --global',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Setting a value with `git config --global` applies it to…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'The one repository where you ran it', 'is_correct': False},
                                {'id': 'b', 'text': 'All repositories of the current user account', 'is_correct': True},
                                {'id': 'c', 'text': 'All users of the computer', 'is_correct': False},
                                {'id': 'd', 'text': 'Everyone who clones your repositories', 'is_correct': False},
                            ],
                            'explain': '--global writes ~/.gitconfig for your account. System-wide needs --system; a single repo needs no flag.',
                        },
                        {
                            'slug': 'q2-config-file',
                            'title': 'Where global config lives',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which file stores your global Git configuration?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': '~/.gitconfig', 'is_correct': True},
                                {'id': 'b', 'text': '.git/settings.json inside each repo', 'is_correct': False},
                                {'id': 'c', 'text': 'The GitHub account page', 'is_correct': False},
                                {'id': 'd', 'text': 'C:/Windows/git.ini', 'is_correct': False},
                            ],
                            'explain': 'Global config is a plain text file in your home directory (~/.gitconfig). A repository keeps its own settings in .git/config.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 3 ════════════════════
        {
            'title': 'Creating and Managing Repositories',
            'slug': 'repositories',
            'description': 'git init, git clone, and the anatomy of a repository.',
            'lessons': [
                {
                    'title': 'What Is a Repository? Creating One with git init',
                    'slug': 'git-init',
                    'objective': 'Create a new repository and explain the .git folder.',
                    'duration': 10,
                    'body': """# Repositories and `git init`

A **repository** ("repo") is a project folder plus the hidden history
Git keeps about it. The history lives in a subfolder named `.git`.

```
my-project/
├── .git/          ← all of Git's brain: history, config, staging area
├── index.html     ← your actual files (the "working directory")
└── style.css
```

**Working directory** = the visible files you edit.
**Repository** = the whole thing, `.git` included.

## Creating a repo from scratch
```bash
mkdir lecture-notes
cd lecture-notes
git init
```

Expected output:

```
Initialized empty Git repository in /home/hp/lecture-notes/.git/
```

That is all — no server, no GitHub, no approval. You now own a version
history that updates with every commit.

## What `git init` actually writes
Inside `.git/`:

- `HEAD` — a pointer to the branch you are currently on.
- `config` — this repository's local settings.
- `objects/` — the snapshots themselves, compressed and hashed.
- `refs/` — pointers naming commits (one per branch and tag).

You never edit these by hand. (Deleting `.git` deletes all history —
double-check before removing folders!)

## Inspecting a fresh repo
```bash
git status
```

Expected output on a brand-new, empty repository:

```
On branch main

No commits yet

nothing to commit (create/copy files and use "git add")
```

Three facts in four lines: your branch is `main`; zero commits exist;
there is nothing staged.

## A repository per project
Keep one repo per independent project. Nesting unrelated things in one
giant repo makes history noisy; splitting a project into many repos makes
cross-file changes painful. A school assignment, a website, a notes
collection — each earns its own `git init`.

## Common mistakes
- Running `git init` twice in the same folder. Harmless — Git says the
  repository already exists. The real danger is running it in your *home*
  folder by accident, turning everything into one repo.
- Expecting `git init` to upload anything. It creates a purely local,
  empty history. Sharing comes in chapter 6.
- Committing with sensitive files inside. Everything committed lives in
  history forever — we cover removing files and `.gitignore` in chapter 8.

## Lesson summary
`git init` turns a folder into a repository by adding `.git/`, where
commits, config and staging live. `git status` reads the current state of
working directory, staging and branch.""",
                    'exercises': [
                        {
                            'slug': 'init-output-folder',
                            'title': 'Where does history live?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'After `git init` in ~/shop, where does Git store the project history?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': '~/shop/.git/', 'is_correct': True},
                                {'id': 'b', 'text': 'A system folder like C:/ProgramData/Git', 'is_correct': False},
                                {'id': 'c', 'text': 'Your GitHub account immediately', 'is_correct': False},
                                {'id': 'd', 'text': 'memory only, until the first commit', 'is_correct': False},
                            ],
                            'explain': 'Each repository keeps its own history in a .git folder inside that project directory.',
                        },
                        {
                            'slug': 'init-command',
                            'title': 'Starting a repository',
                            'exercise_type': 'fill_blank',
                            'instructions': 'Type the exact command that converts the current folder into a new Git repository. (Two words.)',
                            'xp_reward': 40,
                            'solution_code': 'git init',
                            'explain': 'git init creates the .git folder and an empty history in the current directory.',
                        },
                        {
                            'slug': 'git-status-facts',
                            'title': 'Reading git status',
                            'exercise_type': 'multiple_select',
                            'instructions': 'A fresh repo prints "On branch main / No commits yet / nothing to commit". Select ALL facts shown by these lines.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The branch you are currently on', 'is_correct': True},
                                {'id': 'b', 'text': 'That zero commits exist so far', 'is_correct': True},
                                {'id': 'c', 'text': 'The date of the last commit', 'is_correct': False},
                                {'id': 'd', 'text': 'That nothing is staged yet', 'is_correct': True},
                            ],
                            'explain': 'With no commits yet, there is no last-commit date to show. The other three lines state branch, commit count and staging emptiness.',
                        },
                    ],
                },
                {
                    'title': 'Cloning Existing Repositories',
                    'slug': 'git-clone',
                    'objective': 'Copy a complete existing repository (history included) with git clone.',
                    'duration': 9,
                    'body': """# `git clone` — joining an existing history

`git init` starts a *new* history. `git clone` copies an *existing* one —
from a server or any folder on your machine:

```bash
git clone https://github.com/octocat/Hello-World.git
```

Expected output:

```
Cloning into 'Hello-World'...
remote: Enumerating objects: 13, done.
remote: Total 13 (delta 0), reused 0 (delta 0)
Receiving objects: 100% (13/13), done.
```

You now have a folder `Hello-World/` containing:

- every file at its latest state,
- the **entire commit history**,
- configuration that remembers the original server as **origin** (chapter 6).

## Why cloning is more than downloading
A ZIP of a project gives you files only. A clone gives you files *and* the
full timeline: `git log` works immediately, and you can check out any
older version without contacting the server.

## Variations you will actually use
```bash
git clone <url> my-folder          # choose the local folder name
git clone <url> -b dev             # start on a specific branch
git clone --depth 1 <url>          # latest snapshot only — no history (fast)
git clone /c/Users/hp/lecture-notes backup   # clone from a local folder
```

## Clone-to-run routine
Cloning does **not** install anything. After cloning a real project you
usually still follow its README: install dependencies (`npm install`,
`pip install -r requirements.txt`) before it runs.

## Common mistakes
- Cloning into a folder that already contains a repo — Git refuses, or
  you end up nested. Pick an empty location.
- Recloning every day to "get updates". Do not make new copies; run
  `git pull` inside the existing clone (chapter 6).
- Forgetting private repositories need authentication. GitHub rejects
  clones of private repos until you sign in (the credential manager
  from chapter 2 handles this).

## Lesson summary
`git clone <url>` creates a local repository containing the project's
files, full history and a link back to the source as `origin`. It is how
you join existing work.""",
                    'exercises': [
                        {
                            'slug': 'clone-vs-download',
                            'title': 'What a clone includes',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Compared to downloading a ZIP of the same project, `git clone` also gives you… (select all that apply)',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The complete commit history', 'is_correct': True},
                                {'id': 'b', 'text': 'A configuration remembering the source server (origin)', 'is_correct': True},
                                {'id': 'c', 'text': 'Automatic installation of project dependencies', 'is_correct': False},
                                {'id': 'd', 'text': 'All branches of the project', 'is_correct': True},
                            ],
                            'explain': 'A clone is a full replica: history, branches, and the origin link. Running the project is still your job — read the README.',
                        },
                        {
                            'slug': 'clone-command-syntax',
                            'title': 'The clone command',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that copies the repository '
                                'https://github.com/ali/shop.git into a folder named shop:\n'
                                '`git ____________ https://github.com/ali/shop.git`\n'
                                '(One word.)'
                            ),
                            'xp_reward': 30,
                            'solution_code': 'clone',
                            'explain': 'git clone <url> copies a full repository; the folder name defaults to the repo name.',
                        },
                        {
                            'slug': 'shallow-clone-flag',
                            'title': 'Fast history-free copy',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You need only the latest files of a huge repository, not its history. Which flag helps?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git clone --depth 1 <url>', 'is_correct': True},
                                {'id': 'b', 'text': 'git clone --no-history-everything <url>', 'is_correct': False},
                                {'id': 'c', 'text': 'git clone --fast <url>', 'is_correct': False},
                                {'id': 'd', 'text': 'git init <url>', 'is_correct': False},
                            ],
                            'explain': '--depth 1 fetches a single recent snapshot (a "shallow clone"). It saves time and space but limits history-based commands like git log.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 3 Quiz',
                    'slug': 'repositories-quiz',
                    'objective': 'Check understanding of repository creation and cloning.',
                    'duration': 4,
                    'body': """# Chapter 3 quiz

Five questions on repositories, `git init` and `git clone`.""",
                    'exercises': [
                        {
                            'slug': 'q3-git-folder',
                            'title': 'Contents of .git',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which of these is stored inside the .git folder?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Your edited source files like index.html', 'is_correct': False},
                                {'id': 'b', 'text': 'The history objects, refs and repository config', 'is_correct': True},
                                {'id': 'c', 'text': 'A copy of your GitHub password', 'is_correct': False},
                                {'id': 'd', 'text': 'The compiled program', 'is_correct': False},
                            ],
                            'explain': '.git holds Git’s database (objects, refs, HEAD, config). Your visible files stay in the working directory outside it.',
                        },
                        {
                            'slug': 'q3-init-location',
                            'title': 'Where init acts',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You are in ~/Documents and run `git init` without arguments. Which folder becomes the repository?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': '~/Documents itself', 'is_correct': True},
                                {'id': 'b', 'text': 'A new folder ~/Documents/new-repo', 'is_correct': False},
                                {'id': 'c', 'text': 'The home folder ~', 'is_correct': False},
                                {'id': 'd', 'text': 'All subfolders each become repos', 'is_correct': False},
                            ],
                            'explain': 'git init creates .git in the current working directory — so cd into the project first.',
                        },
                        {
                            'slug': 'q3-clone-existing',
                            'title': 'Cloning over an existing clone',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You already cloned repo X yesterday. Today it was updated upstream. The correct move is…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Delete your folder and clone again', 'is_correct': False},
                                {'id': 'b', 'text': 'Run git pull inside your existing clone', 'is_correct': True},
                                {'id': 'c', 'text': 'Clone into a second folder and compare manually', 'is_correct': False},
                                {'id': 'd', 'text': 'Rename the files to force a refresh', 'is_correct': False},
                            ],
                            'explain': 'git pull brings the existing clone up to date without losing your local history. Recloning wastes bandwidth and discards any local work.',
                        },
                        {
                            'slug': 'q3-expected-log',
                            'title': 'Reading clone output',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A clone prints "Cloning into …", "remote: Enumerating objects", "Receiving objects: 100%". If you now run git log inside that folder, what do you see?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Only the single most recent commit', 'is_correct': False},
                                {'id': 'b', 'text': 'The full commit history of the remote repository', 'is_correct': True},
                                {'id': 'c', 'text': 'Nothing until you push', 'is_correct': False},
                                {'id': 'd', 'text': 'An error — log needs the server', 'is_correct': False},
                            ],
                            'explain': 'A normal (non-shallow) clone copies all history, so git log works offline immediately.',
                        },
                        {
                            'slug': 'q3-repo-definition',
                            'title': 'Defining a repository',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In Git terms, a "repository" is…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Any folder with source files', 'is_correct': False},
                                {'id': 'b', 'text': 'The project folder together with its .git history database', 'is_correct': True},
                                {'id': 'c', 'text': 'A GitHub account only', 'is_correct': False},
                                {'id': 'd', 'text': 'The staging area alone', 'is_correct': False},
                            ],
                            'explain': 'Repo = working files + the .git folder that stores everything Git knows about them.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 4 ════════════════════
        {
            'title': 'Understanding the Git Workflow',
            'slug': 'workflow',
            'description': 'Working directory, staging area and repository: status, add and commit in detail.',
            'lessons': [
                {
                    'title': 'The Three Areas',
                    'slug': 'three-areas',
                    'objective': 'Describe the working directory, staging area and repository, and how content flows between them.',
                    'duration': 10,
                    'body': """# Working directory → staging area → repository

Git's workflow has three places your files move through:

```
 Working directory        Staging area            Repository
 (you edit files)   →    (you choose what     →   (you record a
                          becomes next)            permanent snapshot)
```

1. **Working directory** — the visible folder where you create and edit
   files. Nothing here is remembered by Git yet.
2. **Staging area** (aka *index*) — the list of changes you have told Git
   to include in the *next* commit. `git add` puts changes here.
3. **Repository** — the `.git` folder holding every commit ever made.
   `git commit` copies the staging area into it as a permanent snapshot.

## Why a staging area at all?
It looks like an extra step — "why not commit my changes directly?"
Because it gives you **control over what belongs together**. You finish a
bug fix *and* start a risky experiment in the same folder. Staging lets you
commit only the bug fix now, and keep experimenting afterwards. One commit
should be one complete idea; staging is how you build it.

## The file's four possible states
Running `git status` classifies every file as:

- **Untracked** — Git sees the file but has never stored it.
- **Tracked, unmodified** — committed and unchanged since.
- **Tracked, modified** — changed in the working directory, not staged.
- **Staged** — changes added, waiting inside the next commit.

(There is a fifth, hidden state — *conflicted* — met in chapter 5.)

## Reading `git status` like a professional
```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   login.py

Changes not staged for commit:
        modified:   settings.py

Untracked files:
        notes.txt
```

Decoded: `login.py`'s changes ARE in the next commit; `settings.py`'s are
NOT; `notes.txt` is unknown to Git entirely. This screen answers "what
happens if I commit right now?" — the answer is: only the top section.

## Common mistakes
- The panic of "I edited settings.py but my commit only stored login.py"
  — that is the system working *correctly*. Only staged changes commit.
- Blindly running `git add .` before every commit. It stages everything,
  including the debug print you meant to delete. Stage deliberately, then
  read `git status` once before committing.

## Lesson summary
Content flows one way: edit (working directory) → `git add` (staging) →
`git commit` (repository). `git status` names each file's state so you
always know what the next commit will contain.""",
                    'exercises': [
                        {
                            'slug': 'flow-order',
                            'title': 'The correct flow',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which sequence describes how a change becomes part of Git history?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'edit → git commit → git add', 'is_correct': False},
                                {'id': 'b', 'text': 'edit → git add → git commit', 'is_correct': True},
                                {'id': 'c', 'text': 'git add → edit → git push', 'is_correct': False},
                                {'id': 'd', 'text': 'edit → git push → git commit', 'is_correct': False},
                            ],
                            'explain': 'You edit in the working directory, stage with git add, then record with git commit. Pushing (chapter 6) comes after, and only shares what is already committed.',
                        },
                        {
                            'slug': 'staging-purpose',
                            'title': 'Why staging exists',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What problem does the staging area solve?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'It lets you choose exactly which changes belong in the next commit', 'is_correct': True},
                                {'id': 'b', 'text': 'It makes commits faster to create', 'is_correct': False},
                                {'id': 'c', 'text': 'It backs up files to the cloud', 'is_correct': False},
                                {'id': 'd', 'text': 'It prevents you from editing the same file twice', 'is_correct': False},
                            ],
                            'explain': 'Staging is the "build your snapshot deliberately" step: two unrelated working changes can become two clean commits.',
                        },
                        {
                            'slug': 'status-decode',
                            'title': 'Reading a status screen',
                            'exercise_type': 'multiple_choice',
                            'instructions': (
                                'git status shows login.py under "Changes to be committed", '
                                'settings.py under "Changes not staged", notes.txt under '
                                '"Untracked". If you run git commit now, the new commit '
                                'will contain…'
                            ),
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'login.py, settings.py and notes.txt', 'is_correct': False},
                                {'id': 'b', 'text': 'only login.py', 'is_correct': True},
                                {'id': 'c', 'text': 'login.py and settings.py, because both are modified', 'is_correct': False},
                                {'id': 'd', 'text': 'nothing — Git refuses because files are untracked', 'is_correct': False},
                            ],
                            'explain': '"Changes to be committed" is the staging area — exactly what the next commit stores. Unstaged and untracked files stay outside it.',
                        },
                    ],
                },
                {
                    'title': 'git add — Staging Changes',
                    'slug': 'git-add',
                    'objective': 'Stage files deliberately and unstage when needed.',
                    'duration': 8,
                    'body': """# `git add` — telling Git what's next

```bash
git add login.py            # stage one file
git add templates/          # stage a whole folder
git add .                   # stage every change in this repo (use with care)
```

`git add` does two jobs with one word:

1. For **untracked** files: introduce them to Git (they join future snapshots).
2. For **modified** files: copy their current content into the staging area.

## Unstaging without losing work
You staged `settings.py` by accident. Take it out of the next commit while
keeping every edit:

```bash
git restore --staged settings.py
```

The file on disk is untouched; only the staging area forgets it.

## The mental model, once more
`git add file` means *"the version of `file` I see right now is what I want
in the next snapshot."* Edits made **after** the `git add` are not included
until you add again. This surprises everyone once; the fix is simply to
re-run `git add` on the file, or check with `git status` before committing.

## Important note on the name
"add" is a historical word. "stage" would be clearer — some newer Git
docs even suggest `git stage` as an alias. Nothing about `git add` merges
or uploads anything.

## Common mistakes
- `git add .` in your home folder after realising `git init` ran there by
  accident: thousands of files staged. (Recovery: chapter 8's reset.)
- Expecting `git add` to commit. Staging is a proposal; `git commit` is
  the decision.
- Editing a file right after `git add` and wondering why the newest edits
  are missing from the commit. Add again — staging copies a moment, not a
  live link.

## Lesson summary
`git add` stages exact current content; `git restore --staged` unstages.
Read `git status` after adding to confirm the proposal matches your intent.""",
                    'exercises': [
                        {
                            'slug': 'unstage-command',
                            'title': 'Removing from staging safely',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that takes app.js OUT of the staging '
                                'area while keeping your edits on disk:\n'
                                '`git restore ____________ app.js`\n'
                                '(The flag, with its dashes.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': '--staged',
                            'explain': 'git restore --staged <file> resets the staging area entry; the working file keeps all your changes.',
                        },
                        {
                            'slug': 'add-then-edit',
                            'title': 'The live-copy trap',
                            'exercise_type': 'multiple_choice',
                            'instructions': (
                                'You run `git add notes.txt`, then type more edits into '
                                'notes.txt, then `git commit`. The committed version of '
                                'notes.txt is…'
                            ),
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'The newest content, including edits after git add', 'is_correct': False},
                                {'id': 'b', 'text': 'The content as it was when you ran git add — later edits are not staged', 'is_correct': True},
                                {'id': 'c', 'text': 'Empty, because edits after add are discarded', 'is_correct': False},
                                {'id': 'd', 'text': 'Whatever GitHub decides', 'is_correct': False},
                            ],
                            'explain': 'Staging copies a moment in time. Edits after the add live only in the working directory until you add again.',
                        },
                    ],
                },
                {
                    'title': 'git commit and git status Deep Dive',
                    'slug': 'git-commit',
                    'objective': 'Create commits with good messages and interpret the commit summary.',
                    'duration': 10,
                    'body': """# `git commit` — recording the snapshot

```bash
git commit -m "Add user login form"
```

Expected output:

```
[main 3f2a9c1] Add user login form
 2 files changed, 14 insertions(+), 2 deletions(-)
 create mode 100644 login.py
```

Decoded line by line:

- `[main 3f2a9c1]` — the commit landed on branch `main` with hash `3f2a9c1`
  (short form of the 40-character fingerprint).
- `2 files changed, 14 insertions(+), 2 deletions(-)` — the size of the delta.
- `create mode …` — a file that did not exist before joined the history.

## Message craft (revisited, because it matters)
`-m` takes the message on the command line. Without `-m`, Git opens your
editor (nano, Vim, Notepad…) for a longer message. Rules that keep history
readable:

1. **Summarise in ≤ 50 characters**, imperative mood: "Fix typo" not
   "Fixed typo" or "Fixes typo". Read it as *"If applied, this commit will
   ___"* — "…Fix typo" works; "…Fixed typo" does not.
2. **Explain why, not what.** The diff already shows what. "Split the
   payment retry so a timeout cannot double-charge" explains why.
3. One commit = one idea. Staging (previous lesson) is how you build it.

## Skipping the editor habit
For a quick change you can stage and commit together:

```bash
git commit -am "Update copy on landing page"
```

`-a` stages every *tracked-and-modified* file first. (It never picks up
new, untracked files.) Convenient, but only after you have trained
yourself to read `git status` — otherwise it commits debug leftovers.

## Amending the last commit
Made a typo in the message, or forgot a file? The very last commit can be
replaced:

```bash
git add forgotten.py
git commit --amend -m "Add login form and validation"
```

This creates a *new* commit and hides the old one. Rule: **never amend a
commit you have already pushed** where others may have copied it (chapter 8
explains why rewriting shared history hurts teammates).

## Common mistakes
- Committing with `"update"`, `"wip"`, `"fix"` as the whole message.
- Amending pushed commits on a shared branch — causes the painful
  force-push warnings in chapter 6.
- `git commit` says *"no changes added to commit"*: nothing was staged.
  Run `git add` first, or use `-a` deliberately.

## Lesson summary
`git commit -m` freezes the staging area as history, printing branch, hash
and a delta summary. Imperative *why* messages make the log worth reading;
`--amend` safely fixes only unpushed, final commits.""",
                    'exercises': [
                        {
                            'slug': 'commit-output-decode',
                            'title': 'What the hash line means',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The line `[main 3f2a9c1] Add user login form` tells you…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The commit landed on branch main and starts with hash 3f2a9c1', 'is_correct': True},
                                {'id': 'b', 'text': 'The commit was pushed to GitHub branch main', 'is_correct': False},
                                {'id': 'c', 'text': '3 files were changed on branch main', 'is_correct': False},
                                {'id': 'd', 'text': 'The branch was renamed to 3f2a9c1', 'is_correct': False},
                            ],
                            'explain': 'The square brackets show branch + short hash of the brand-new local commit. Nothing has been pushed yet.',
                        },
                        {
                            'slug': 'imperative-message',
                            'title': 'Imperative mood check',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which message follows the "If applied, this commit will …" convention?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Updated the header', 'is_correct': False},
                                {'id': 'b', 'text': 'updates header', 'is_correct': False},
                                {'id': 'c', 'text': 'Update header logo for dark background', 'is_correct': True},
                                {'id': 'd', 'text': 'header', 'is_correct': False},
                            ],
                            'explain': '"If applied, this commit will Update header logo…" reads correctly, and the tail explains why. Past tense and one-word messages fail the test.',
                        },
                        {
                            'slug': 'amend-rule',
                            'title': 'When --amend is safe',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'git commit --amend should be used on…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Any commit, at any time', 'is_correct': False},
                                {'id': 'b', 'text': 'Only your most recent commit, before pushing it', 'is_correct': True},
                                {'id': 'c', 'text': 'Only merge commits', 'is_correct': False},
                                {'id': 'd', 'text': 'Only commits older than a week', 'is_correct': False},
                            ],
                            'explain': 'Amending replaces the last commit with a new hash. If teammates already pulled the old one, rewriting it breaks their history.',
                        },
                        {
                            'slug': 'flag-a-meaning',
                            'title': 'The -a flag',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What does `git commit -am "msg"` do differently from `git commit -m "msg"`?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'It first stages all tracked, modified files automatically', 'is_correct': True},
                                {'id': 'b', 'text': 'It commits every file including new untracked ones', 'is_correct': False},
                                {'id': 'c', 'text': 'It also pushes to the remote', 'is_correct': False},
                                {'id': 'd', 'text': 'It asks GitHub for approval first', 'is_correct': False},
                            ],
                            'explain': '-a = auto-stage tracked modifications. New untracked files still need git add — and it still does not push.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 4 Quiz',
                    'slug': 'workflow-quiz',
                    'objective': 'Check understanding of the three-area workflow, add, status and commit.',
                    'duration': 5,
                    'body': """# Chapter 4 quiz

Six questions on staging, status output and committing.""",
                    'exercises': [
                        {
                            'slug': 'q4-index-name',
                            'title': 'Another name for the staging area',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In Git documentation the staging area is also called the…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'index', 'is_correct': True},
                                {'id': 'b', 'text': 'cache', 'is_correct': False},
                                {'id': 'c', 'text': 'buffer', 'is_correct': False},
                                {'id': 'd', 'text': 'vault', 'is_correct': False},
                            ],
                            'explain': 'The staging area is formally the index — .git/index stores it.',
                        },
                        {
                            'slug': 'q4-no-staged-changes',
                            'title': 'Empty commit refusal',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You run `git commit -m "done"` but nothing is staged. Git replies…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Creates an empty commit anyway', 'is_correct': False},
                                {'id': 'b', 'text': 'no changes added to commit — and records nothing', 'is_correct': True},
                                {'id': 'c', 'text': 'Commits your last push instead', 'is_correct': False},
                                {'id': 'd', 'text': 'Deletes the staging area', 'is_correct': False},
                            ],
                            'explain': 'Without staged changes (and without --allow-empty) Git declines. Stage with git add first.',
                        },
                        {
                            'slug': 'q4-untracked-state',
                            'title': 'What untracked means',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A file listed under "Untracked files" has never been…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'opened in an editor', 'is_correct': False},
                                {'id': 'b', 'text': 'added to Git — it is not in any snapshot or the staging area', 'is_correct': True},
                                {'id': 'c', 'text': 'pushed to GitHub', 'is_correct': False},
                                {'id': 'd', 'text': 'saved to disk', 'is_correct': False},
                            ],
                            'explain': 'Untracked = Git does not follow this file yet. git add starts tracking it.',
                        },
                        {
                            'slug': 'q4-status-sections',
                            'title': 'Status ordering',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Which sections can appear in normal `git status` output? (select all)',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Changes to be committed', 'is_correct': True},
                                {'id': 'b', 'text': 'Changes not staged for commit', 'is_correct': True},
                                {'id': 'c', 'text': 'Untracked files', 'is_correct': True},
                                {'id': 'd', 'text': 'Changes rejected by GitHub', 'is_correct': False},
                            ],
                            'explain': 'Those three sections mirror the three areas. GitHub rejection is a network event shown by push, never by status.',
                        },
                        {
                            'slug': 'q4-what-commits',
                            'title': 'The commit source of truth',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'git commit builds the new snapshot from…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the working directory, always', 'is_correct': False},
                                {'id': 'b', 'text': 'the staging area', 'is_correct': True},
                                {'id': 'c', 'text': 'the previous commit plus the last push', 'is_correct': False},
                                {'id': 'd', 'text': 'GitHub\u0027s server copy', 'is_correct': False},
                            ],
                            'explain': 'Commit freezes what is staged. That is exactly why unstaged edits survive a commit untouched.',
                        },
                        {
                            'slug': 'q4-restore-staged',
                            'title': 'Undo staging, keep work',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You want app.js out of the next commit but every edit kept on disk. Which command?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git restore --staged app.js', 'is_correct': True},
                                {'id': 'b', 'text': 'git restore app.js', 'is_correct': False},
                                {'id': 'c', 'text': 'git commit --no app.js', 'is_correct': False},
                                {'id': 'd', 'text': 'git delete app.js', 'is_correct': False},
                            ],
                            'explain': '--staged touches only the staging area. Plain git restore (option b) would DISCARD your working edits — the dangerous twin.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 5 ════════════════════
        {
            'title': 'Branching and Merging',
            'slug': 'branching',
            'description': 'What branches really are, creating and switching, merging, and resolving conflicts.',
            'lessons': [
                {
                    'title': 'What Branches Really Are',
                    'slug': 'what-branches-are',
                    'objective': 'Explain a branch as a movable pointer and HEAD as the current-branch marker.',
                    'duration': 10,
                    'body': """# Branches are cheap pointers — not copies

A common fear: "creating a branch must duplicate my whole project."
It does not. Remember chapter 1 — commits already store snapshots and
point to their parents. A **branch** is simply a small file that names one
commit as a landmark:

```
commit A ─ commit B ─ commit C   ← branch main points here
```

Creating branch `feature-cart` at the same commit costs ~40 bytes: one
pointer. Branches are **cheap and disposable**, so use many of them.

**HEAD** is a second pointer that says *which branch you are standing on*.
When you switch branches, Git rewrites your working directory files to
match the commit HEAD's branch points at. Your uncommitted changes usually
carry across the switch — chapter 8's stash is for when they clash.

## Why branch at all?
- **Isolate work-in-progress.** The half-built cart feature cannot disturb
  the stable main line while you keep editing.
- **Safe experiments.** Delete a failed branch and main never knew it
  existed.
- **Parallel work in teams.** Each person (or each ticket) gets a branch;
  history shows the features as separate rivers that merge together.

## The daily rhythm professionals use
1. On `main`, up to date.
2. Create branch `feature-x`.
3. Commit all the feature work there.
4. Merge `feature-x` back into `main` when complete.
5. Delete the branch; repeat.

## Terminology
- **Trunk / main line:** the primary branch (historically `master`,
  modernly `main`).
- **Feature branch:** a temporary branch for one piece of work.
- **Checkout / switch:** moving HEAD to another branch.

## Common mistakes
- Doing days of work directly on main "to avoid merge hassle". Merging
  two-hour-old changes is trivial; merging two-week-old parallel edits on
  main is the painful one. Branch early.
- Leaving dozens of stale branches after merges. Deleted branches lose
  nothing — their commits live in main's history once merged.

## Lesson summary
A branch = a pointer to a commit; HEAD = pointer to your current branch.
Switching rewrites the working directory. Branch cheaply, merge early.""",
                    'exercises': [
                        {
                            'slug': 'branch-cost',
                            'title': 'What a branch stores',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Creating a new branch in Git copies the project files. True or false?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'True — every branch has its own full copy of all files', 'is_correct': False},
                                {'id': 'b', 'text': 'False — a branch is just a small pointer to a commit', 'is_correct': True},
                                {'id': 'c', 'text': 'True, but only on GitHub', 'is_correct': False},
                                {'id': 'd', 'text': 'False — branches store only deleted files', 'is_correct': False},
                            ],
                            'explain': 'Snapshots already exist in the commit chain; the branch adds one reference, which is why branching is instant and cheap.',
                        },
                        {
                            'slug': 'head-definition',
                            'title': 'What HEAD does',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'HEAD is best described as…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'The first commit of the repository', 'is_correct': False},
                                {'id': 'b', 'text': 'A pointer indicating which branch you are currently on', 'is_correct': True},
                                {'id': 'c', 'text': 'The main branch by another name', 'is_correct': False},
                                {'id': 'd', 'text': 'The staging area\u2019s alias', 'is_correct': False},
                            ],
                            'explain': 'HEAD points at the current branch; new commits advance that branch, and switching branches moves HEAD.',
                        },
                    ],
                },
                {
                    'title': 'Creating, Switching and Merging Branches',
                    'slug': 'create-switch-merge',
                    'objective': 'Create and switch branches and merge a finished branch into main.',
                    'duration': 12,
                    'body': """# The branch commands

```bash
git branch                # list branches; * marks the current one
git branch login-form     # create branch login-form at the current commit
git switch login-form     # move HEAD (and your files) onto it
git switch -c dark-mode   # create AND switch in one step (modern shortcut)
git switch main           # jump back
git merge login-form      # while ON main, fold login-form's work in
```

## What a merge actually does
Git finds the **merge base** (the last commit the two branches shared).
If changes touch different lines or different files, Git combines them
automatically — the clean merge:

```
      .--- B --- C   (login-form)
A --- B
      `--- D         (main)
      v
   merge → A-B-C-D combined, plus a merge commit
```

Output you will see on the simple case:

```
Merge made by the 'ort' strategy.
 login.py | 12 ++++++++++++
 1 file changed, 12 insertions(+)
```

When main had no new commits since the branch, Git just slides the main
pointer forward — the **fast-forward** case, with no merge commit at all.

## Delete when finished
```bash
git branch -d login-form   # -d: delete (only if already merged)
git branch -D login-form   # -D: force (thinks it unmerged — be careful)
```

## A practical scenario, start to finish
You must add a profile page without disturbing the working site:

```bash
git switch -c profile-page
git add .
git commit -m "Add profile page template"
git commit -m "Wire profile URL and view"
git switch main
git merge profile-page
git branch -d profile-page
```

Main gains both commits as one merged result; the branch pointer is gone.

## Important notes
- Older tutorials use `git checkout` for both switching and creating
  (`git checkout -b`). `git switch` and `git restore` split that overloaded
  command — learn the modern ones; recognise the old ones.
- `git merge X` merges **into wherever you currently are**. Read your
  prompt: if you are on `experiment`, you just merged X into `experiment`.

## Common mistakes
- Forgetting to `git switch main` before merging and pulling feature work
  into the wrong branch.
- Using `-D` reflexively when `-d` refuses — that refusal is Git warning
  you that unmerged commits would be lost.

## Lesson summary
`switch -c` to branch, commit on the branch, `switch main`, `merge`,
`branch -d`. Merging combines histories from their common base; different
line edits are combined automatically.""",
                    'exercises': [
                        {
                            'slug': 'create-switch-shortcut',
                            'title': 'One-step branch and switch',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that creates branch `tests` and '
                                'immediately switches to it:\n'
                                '`git switch ____ tests`\n'
                                '(The short flag, dash and letter.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': '-c',
                            'explain': 'git switch -c <name> = create + checkout, the modern equivalent of git checkout -b.',
                        },
                        {
                            'slug': 'merge-direction',
                            'title': 'Who merges into whom',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You are on branch `main` and run `git merge feature`. What happens?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'main\u2019s commits are copied into feature', 'is_correct': False},
                                {'id': 'b', 'text': 'feature\u2019s commits are incorporated into main', 'is_correct': True},
                                {'id': 'c', 'text': 'Both branches are deleted and replaced', 'is_correct': False},
                                {'id': 'd', 'text': 'feature is renamed to main', 'is_correct': False},
                            ],
                            'explain': 'merge always brings the named branch INTO your current branch. The current branch advances; the named one stays where it was.',
                        },
                        {
                            'slug': 'safe-delete-flag',
                            'title': 'Deleting a merged branch',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command deletes branch `old-idea` but refuses if it has unmerged commits?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git branch -d old-idea', 'is_correct': True},
                                {'id': 'b', 'text': 'git branch -D old-idea', 'is_correct': False},
                                {'id': 'c', 'text': 'git branch --remove --force old-idea', 'is_correct': False},
                                {'id': 'd', 'text': 'git delete branch old-idea', 'is_correct': False},
                            ],
                            'explain': 'Lowercase -d is safety-first: it checks for unmerged work first. Uppercase -D overrides that check.',
                        },
                        {
                            'slug': 'sequence-order',
                            'title': 'Ordering the workflow',
                            'exercise_type': 'multiple_select',
                            'instructions': 'You finished a feature branch and want it in main and the branch gone. Select ALL steps the workflow needs.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'git switch main', 'is_correct': True},
                                {'id': 'b', 'text': 'git merge <feature>', 'is_correct': True},
                                {'id': 'c', 'text': 'git branch -d <feature>', 'is_correct': True},
                                {'id': 'd', 'text': 'git clone <feature>', 'is_correct': False},
                            ],
                            'explain': 'Switch to the target, merge the feature, delete the (now merged) branch. Cloning has nothing to do with branch integration.',
                        },
                    ],
                },
                {
                    'title': 'Merge Conflicts and How to Resolve Them',
                    'slug': 'merge-conflicts',
                    'objective': 'Recognise conflict markers and resolve a conflict deliberately.',
                    'duration': 12,
                    'body': """# When Git cannot decide: conflicts

Automatic merging works while branches touched **different lines**. If two
branches changed the *same lines of the same file* differently, Git
refuses to guess. That is a **merge conflict** — not an error, a request:
*"pick which version, or combine them yourself."*

## What the file looks like mid-conflict
```python
def greet(name):
<<<<<<< HEAD
    return f"Hi {name}!"          # your current branch's version
=======
    return f"Hello, {name}."      # the merged branch's version
>>>>>>> feature-greeting
```

- `<<<<<<< HEAD` … `=======` → the version on the branch you are ON.
- `=======` … `>>>>>>> feature-greeting` → the version coming IN.

`git status` meanwhile says `Unmerged paths` and names the file, and the
prompt may show `(main|MERGING)`.

## The resolution routine
1. Open every conflicted file. Decide: keep yours, keep theirs, or hand
   combine. Delete all three marker lines and the version(s) you reject.
2. `git add greeting.py` — staging the edited file means "conflict
   resolved for this file".
3. `git commit` — Git creates the **merge commit** that records both
   parents and the decision.

## Useful helpers
```bash
git diff                    # shows the remaining conflict hunks
git checkout --theirs file  # crude: take the incoming side entirely
git merge --abort           # give up: return to the pre-merge state
```

## Conflict vs merge — mind the vocabulary
A **merge** is normal and often silent. A **conflict** is the sub-case
where human choice is required. Many beginners fear the word; the actual
task is almost always: open file, read the two candidates, keep the right
one, add, commit.

## Common mistakes
- Committing WITH the markers still in the file — the `<<<<<<<` lines ship
  into your codebase. Search the file for `<<<<<<<` before `git add`.
- Panicking and running `git merge --abort` every time. Abort is a fine
  escape hatch, but resolving one small conflict takes two minutes.
- Deleting both sides by accident and losing each candidate. Note the
  other branch name; its commits still contain the original text.

## Lesson summary
Conflicts happen when the same line diverged. Read the markers, edit to the
final desired text, `git add`, `git commit`. `--abort` rewinds the whole
attempt.""",
                    'exercises': [
                        {
                            'slug': 'conflict-marker-meaning',
                            'title': 'Reading the markers',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In a conflicted file, the text between `<<<<<<< HEAD` and `=======` is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'The version from the branch being merged in', 'is_correct': False},
                                {'id': 'b', 'text': 'The version from the branch you are currently on', 'is_correct': True},
                                {'id': 'c', 'text': 'The original common-base version', 'is_correct': False},
                                {'id': 'd', 'text': 'Git\u2019s suggestion of the final code', 'is_correct': False},
                            ],
                            'explain': 'HEAD is your side; the section after ======= belongs to the incoming branch. Git does not pick for you.',
                        },
                        {
                            'slug': 'resolve-steps',
                            'title': 'Finishing a conflict resolution',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'After editing the conflicted file and deleting the markers, the correct way to complete the merge is…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'git add the file, then git commit', 'is_correct': True},
                                {'id': 'b', 'text': 'git push immediately', 'is_correct': False},
                                {'id': 'c', 'text': 'git merge --abort and start over', 'is_correct': False},
                                {'id': 'd', 'text': 'Nothing — saving the file finishes the merge', 'is_correct': False},
                            ],
                            'explain': 'Staging marks the file resolved; the commit writes the merge commit. Saving alone leaves the merge half-finished.',
                        },
                        {
                            'slug': 'abort-flag',
                            'title': 'Backing out cleanly',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that cancels an in-progress merge '
                                'and returns to the state before you started:\n'
                                '`git merge ____________`\n'
                                '(One word, with its two dashes.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': '--abort',
                            'explain': 'git merge --abort rewinds to the pre-merge snapshot; you can retry later after discussing versions.',
                        },
                        {
                            'slug': 'when-conflicts-happen',
                            'title': 'Root cause of conflicts',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A merge conflict occurs specifically when…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'two branches modified the same lines of the same file differently', 'is_correct': True},
                                {'id': 'b', 'text': 'the branches have any different files at all', 'is_correct': False},
                                {'id': 'c', 'text': 'GitHub is offline', 'is_correct': False},
                                {'id': 'd', 'text': 'you created more than three branches', 'is_correct': False},
                            ],
                            'explain': 'Different files, or different lines of the same file, merge automatically. Same-line divergence needs a human.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 5 Quiz',
                    'slug': 'branching-quiz',
                    'objective': 'Check understanding of branches, merging and conflicts.',
                    'duration': 5,
                    'body': """# Chapter 5 quiz

Six questions on branches, switching, merging and conflict resolution.""",
                    'exercises': [
                        {
                            'slug': 'q5-branch-list',
                            'title': 'Listing branches',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command lists all local branches, marking the current one with *?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'git branch', 'is_correct': True},
                                {'id': 'b', 'text': 'git list branches', 'is_correct': False},
                                {'id': 'c', 'text': 'git status --branches', 'is_correct': False},
                                {'id': 'd', 'text': 'git log --all', 'is_correct': False},
                            ],
                            'explain': 'Plain git branch prints the local branch list; git branch -a adds remote-tracking branches too.',
                        },
                        {
                            'slug': 'q5-merge-base',
                            'title': 'Where merging starts looking',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Git computes an automatic merge by comparing both branches against…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'their last common ancestor (merge base)', 'is_correct': True},
                                {'id': 'b', 'text': 'the GitHub server copy', 'is_correct': False},
                                {'id': 'c', 'text': 'the newest file on disk', 'is_correct': False},
                                {'id': 'd', 'text': 'the .gitignore rules', 'is_correct': False},
                            ],
                            'explain': 'Git walks back to the shared ancestor commit and applies each side\u2019s changes since that point.',
                        },
                        {
                            'slug': 'q5-switch-vs-restore',
                            'title': 'Modern command split',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The old overloaded `git checkout` was split into which two modern commands?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git switch (branches) and git restore (undo files)', 'is_correct': True},
                                {'id': 'b', 'text': 'git merge and git rebase', 'is_correct': False},
                                {'id': 'c', 'text': 'git add and git commit', 'is_correct': False},
                                {'id': 'd', 'text': 'git pull and git fetch', 'is_correct': False},
                            ],
                            'explain': 'git switch handles branch movement; git restore undoes file changes. Recognise checkout when you see older guides.',
                        },
                        {
                            'slug': 'q5-conflict-file-add',
                            'title': 'Staging means resolving',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'During a conflict, running `git add conflicted.txt` tells Git that…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the file is deleted', 'is_correct': False},
                                {'id': 'b', 'text': 'you have resolved that file and its content is the final result', 'is_correct': True},
                                {'id': 'c', 'text': 'the merge is aborted', 'is_correct': False},
                                {'id': 'd', 'text': 'the other branch wins', 'is_correct': False},
                            ],
                            'explain': 'In the merge state, staging = \u201cresolved\u201d. When no unmerged files remain, git commit completes the merge.',
                        },
                        {
                            'slug': 'q5-branch-early',
                            'title': 'Why branch early helps',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Merging two branches that diverged two hours ago is usually easier than two weeks ago mainly because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'less time means fewer same-line divergences to adjudicate', 'is_correct': True},
                                {'id': 'b', 'text': 'Git forgets old conflicts after seven days', 'is_correct': False},
                                {'id': 'c', 'text': 'branches shrink over time', 'is_correct': False},
                                {'id': 'd', 'text': 'the merge base moves forward by itself', 'is_correct': False},
                            ],
                            'explain': 'Overlap grows with time. Merge often and conflicts stay small and obvious.',
                        },
                        {
                            'slug': 'q5-fast-forward',
                            'title': 'Fast-forward meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A \u201cfast-forward\u201d merge happens when…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'the current branch has no new commits since the branch was created, so its pointer just slides forward', 'is_correct': True},
                                {'id': 'b', 'text': 'the merge skips conflict checking entirely', 'is_correct': False},
                                {'id': 'c', 'text': 'GitHub merges on the server instead', 'is_correct': False},
                                {'id': 'd', 'text': 'both branches are deleted', 'is_correct': False},
                            ],
                            'explain': 'Fast-forward = no true divergence; main simply moves to the feature tip and no merge commit is created.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 6 ════════════════════
        {
            'title': 'Working with GitHub',
            'slug': 'github-remotes',
            'description': 'Create a GitHub repository, connect it as origin, and exchange work with push, pull and fetch.',
            'lessons': [
                {
                    'title': 'Creating a Repository on GitHub and Connecting origin',
                    'slug': 'create-remote',
                    'objective': 'Create a GitHub repo and link it to a local repository as origin.',
                    'duration': 10,
                    'body': """# From local repo to GitHub

Your repository lives on your machine. GitHub hosting makes it shareable,
backed up and visible. The bridge is a **remote**: a named shortcut to a
repository URL.

## 1. Create the empty repo on GitHub
1. Sign in to github.com → **New repository**.
2. Name it (match your local folder, e.g. `lecture-notes`).
3. Choose **Private** for coursework, **Public** for portfolio work.
4. **Do NOT tick "Add a README"** for an existing local project — a
   README makes the remote non-empty and complicates the first push.
   (GitHub's own guide offers the exact commands for a fresh repo —
   ignore them; you will type them yourself.)

## 2. Link the local repository
```bash
git remote add origin https://github.com/yourname/lecture-notes.git
git remote -v
```

Expected output of `git remote -v`:

```
origin  https://github.com/yourname/lecture-notes.git (fetch)
origin  https://github.com/yourname/lecture-notes.git (push)
```

`origin` is just a **convention name** for "the main remote" — like
calling your home Wi-Fi "Home". It could be called anything; every tool
assumes the name, so keep it.

## 3. First push
```bash
git push -u origin main
```

- `push` uploads your commits.
- `-u` (upstream) records "my local `main` tracks `origin/main`", so
  later you can type just `git push` and `git pull`.

GitHub's empty repo now mirrors your entire local history. The next
section covers the day-to-day exchange: push, pull, fetch.

## SSH or HTTPS?
The URL above is HTTPS; the credential manager you installed in chapter 2
signs you in with a browser popup / personal access token. SSH URLs
(`git@github.com:...`) need an SSH key added to your account once, then
never sign in again. Either works; pick one and stick to it.

## Common mistakes
- Ticking "Add README/.gitignore/license" then pushing and seeing
  "Updates were rejected because the remote contains work". Fix (chapter
  routine): `git pull --rebase origin main`, then push.
- Pushing to `master` when GitHub shows `main` (or vice versa): your
  default branch name comes from your `init.defaultBranch` setting.
- Sharing the HTTPS URL of a **private** repo expecting others to see it —
  they will get a login prompt and a 404 until you add them as collaborator.

## Lesson summary
Create the (empty) repo on GitHub, `git remote add origin <url>`, then
`git push -u origin main`. From now on, plain `git push` / `git pull`
sync this branch.""",
                    'exercises': [
                        {
                            'slug': 'origin-is-what',
                            'title': 'Naming the remote',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In `git remote add origin <url>`, what is \u201corigin\u201d?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'A required magic word Git searches for on GitHub', 'is_correct': False},
                                {'id': 'b', 'text': 'A conventional local nickname for the main remote URL', 'is_correct': True},
                                {'id': 'c', 'text': 'The name of your first branch', 'is_correct': False},
                                {'id': 'd', 'text': 'Your GitHub username', 'is_correct': False},
                            ],
                            'explain': 'origin is just the agreed nickname for the primary remote; the URL it stores is what matters.',
                        },
                        {
                            'slug': 'upstream-flag',
                            'title': 'The -u flag',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What does `git push -u origin main` remember for the future?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'That local main should sync with origin/main, so later bare git push/pull work', 'is_correct': True},
                                {'id': 'b', 'text': 'That main is now write-protected', 'is_correct': False},
                                {'id': 'c', 'text': 'That every branch must be pushed twice', 'is_correct': False},
                                {'id': 'd', 'text': 'Nothing — -u only affects that single push', 'is_correct': False},
                            ],
                            'explain': '-u sets the \u201cupstream\u201d tracking relationship between the local branch and the remote branch.',
                        },
                        {
                            'slug': 'remote-list-command',
                            'title': 'Checking remotes',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that lists the remotes your '
                                'repository knows, with their URLs:\n'
                                '`git remote ____`\n'
                                '(Short flag, dash and letter.)'
                            ),
                            'xp_reward': 30,
                            'solution_code': '-v',
                            'explain': 'git remote -v (verbose) shows each remote name with its fetch and push URLs.',
                        },
                    ],
                },
                {
                    'title': 'Push, Fetch and Pull',
                    'slug': 'push-fetch-pull',
                    'objective': 'Distinguish push, fetch and pull, and use each correctly.',
                    'duration': 10,
                    'body': """# The three sync commands

```bash
git push            # send YOUR commits TO the remote
git fetch           # bring THEIR commits INTO your local copy of the remote…
git pull            # …and also merge them into your current branch (= fetch + merge)
```

## Push — sharing your work
```bash
git push
```
Works because of the `-u` you set earlier. Rejected pushes usually mean
*the remote has new commits you do not*: pull first, then push. Never
make it work with `--force` on a shared branch (chapter 8 explains the
proper tools).

## Fetch — look before you touch
`git fetch origin` downloads new remote commits into a **remote-tracking
branch** named `origin/main` — a local read-only memory of \u201cwhat GitHub
had at fetch time\u201d. It changes *nothing* you are working on:

```bash
git fetch
git log main..origin/main   # commits GitHub has that I don\u2019t
```

Safe to run constantly — that is why professionals fetch to *review*
teamwork before merging it.

## Pull — fetch + merge in one step
```bash
git pull
```
Short for fetch, then merge `origin/main` into your current branch. If
both sides changed the same lines, you get a normal conflict to resolve
(chapter 5 skills apply).

## The daily team loop
```bash
git pull            # start work on the newest state
git switch -c task-42
… commit …
git switch main
git pull            # in case teammates moved ahead
git merge task-42
git push
```

## Important notes
- `origin/main` (with slash) is a local snapshot; `origin main` (space)
  is \u201cremote named origin, branch main\u201d. Slashes in names confuse
  beginners — read them as \u201cthe remembered copy of\u201d.
- Pull never uploads anything. Push never modifies your branch. They are
  one-way streets.

## Common mistakes
- Editing locally, pulling, resolving nothing, and assuming your newest
  commits went away — they didn\u2019t; the merge commit just joins both
  lines.
- Running `git pull` on top of a conflicted, unstaged mess — always get
  your own work committed (or stashed, chapter 8) before pulling.

## Lesson summary
Push sends; fetch previews; pull sends-you-the-updates-and-merges. Start
each work session with a pull and finish it with a push.""",
                    'exercises': [
                        {
                            'slug': 'pull-equals',
                            'title': 'Pull decomposed',
                            'exercise_type': 'multiple_choice',
                            'instructions': '`git pull` is equivalent to…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git fetch + git merge of the fetched branch', 'is_correct': True},
                                {'id': 'b', 'text': 'git push + git fetch', 'is_correct': False},
                                {'id': 'c', 'text': 'downloading the latest ZIP', 'is_correct': False},
                                {'id': 'd', 'text': 'git clone into a new folder', 'is_correct': False},
                            ],
                            'explain': 'Pull = fetch (download remote commits) then merge (integrate into your branch).',
                        },
                        {
                            'slug': 'fetch-safety',
                            'title': 'What fetch changes',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Running `git fetch origin` modifies…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'your working directory files', 'is_correct': False},
                                {'id': 'b', 'text': 'only the remote-tracking branches like origin/main', 'is_correct': True},
                                {'id': 'c', 'text': 'the GitHub server copy', 'is_correct': False},
                                {'id': 'd', 'text': 'your uncommitted changes', 'is_correct': False},
                            ],
                            'explain': 'Fetch is read-only for you: it updates the remembered snapshots so you can inspect them risk-free.',
                        },
                        {
                            'slug': 'push-rejected-cause',
                            'title': 'Why pushes get rejected',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Your push fails with \u201crejected \u2026 remote contains work you do not have\u201d. The correct first move is…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'git push --force to overwrite their work', 'is_correct': False},
                                {'id': 'b', 'text': 'git pull (or fetch+merge), integrate the new commits, resolve any conflict, then push again', 'is_correct': True},
                                {'id': 'c', 'text': 'delete the remote and re-create it', 'is_correct': False},
                                {'id': 'd', 'text': 're-clone into a second folder', 'is_correct': False},
                            ],
                            'explain': 'The remote moved ahead (a teammate pushed). You must incorporate their commits before adding yours on top. Forcing destroys their work.',
                        },
                        {
                            'slug': 'origin-slash-meaning',
                            'title': 'origin/main decoded',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The branch named `origin/main` on your machine is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'a live connection to GitHub', 'is_correct': False},
                                {'id': 'b', 'text': 'a local snapshot of GitHub\u2019s main branch as of your last fetch/push', 'is_correct': True},
                                {'id': 'c', 'text': 'a backup copy of your own commits', 'is_correct': False},
                                {'id': 'd', 'text': 'another name for your HEAD', 'is_correct': False},
                            ],
                            'explain': 'Remote-tracking branches are remembered copies, updated only when you fetch/push/pull.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 6 Quiz',
                    'slug': 'github-remotes-quiz',
                    'objective': 'Check understanding of remotes, push, fetch and pull.',
                    'duration': 4,
                    'body': """# Chapter 6 quiz

Five questions on GitHub repositories and remote synchronisation.""",
                    'exercises': [
                        {
                            'slug': 'q6-empty-repo-advice',
                            'title': 'First push friction',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why should you skip "Add a README" when creating a GitHub repo for an EXISTING local project?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'READMEs are not supported on Git', 'is_correct': False},
                                {'id': 'b', 'text': 'The new remote commit would not be in your local history, making the first push rejected', 'is_correct': True},
                                {'id': 'c', 'text': 'It slows GitHub down', 'is_correct': False},
                                {'id': 'd', 'text': 'It converts the repo to SVN', 'is_correct': False},
                            ],
                            'explain': 'An initialised remote has one commit your history does not contain; Git refuses to push over it until you pull/merge it first.',
                        },
                        {
                            'slug': 'q6-push-target',
                            'title': 'Where push goes',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that uploads the current branch '
                                'to the main remote:\n'
                                '`git ____`\n(One word.)'
                            ),
                            'xp_reward': 30,
                            'solution_code': 'push',
                            'explain': 'With an upstream set, bare \u201cgit push\u201d uploads the current branch to origin.',
                        },
                        {
                            'slug': 'q6-see-remote-work',
                            'title': 'Reviewing teammates\u2019 commits first',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You want to see what teammates pushed WITHOUT touching your files. Which pair of commands does exactly that?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'git fetch, then git log main..origin/main', 'is_correct': True},
                                {'id': 'b', 'text': 'git pull, then git status', 'is_correct': False},
                                {'id': 'c', 'text': 'git push, then git diff', 'is_correct': False},
                                {'id': 'd', 'text': 'git clone elsewhere', 'is_correct': False},
                            ],
                            'explain': 'fetch updates the snapshot; the log range lists their new commits. pull would merge immediately instead of previewing.',
                        },
                        {
                            'slug': 'q6-https-vs-ssh',
                            'title': 'Clone URL types',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about HTTPS vs SSH remote URLs.',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'HTTPS URLs prompt via credential manager / personal access token', 'is_correct': True},
                                {'id': 'b', 'text': 'SSH URLs (git@github.com:…) authenticate with a key pair added to your account', 'is_correct': True},
                                {'id': 'c', 'text': 'A repository can only ever have one of the two types', 'is_correct': False},
                                {'id': 'd', 'text': 'git remote set-url lets you switch a clone between them', 'is_correct': True},
                            ],
                            'explain': 'Both access the same repository; you can switch anytime with git remote set-url origin <new-url>.',
                        },
                        {
                            'slug': 'q6-trailing-history',
                            'title': 'Does push upload history?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'When you push, GitHub receives…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'only your newest file changes', 'is_correct': False},
                                {'id': 'b', 'text': 'the commits (with their history) that the remote branch lacks', 'is_correct': True},
                                {'id': 'c', 'text': 'your whole hard drive', 'is_correct': False},
                                {'id': 'd', 'text': 'a ZIP of the working directory', 'is_correct': False},
                            ],
                            'explain': 'Push transfers commit objects and their parent links — history travels with the tip.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 7 ════════════════════
        {
            'title': 'Collaboration and Pull Requests',
            'slug': 'collaboration',
            'description': 'Forking, feature-branch teamwork, opening pull requests and reviewing code.',
            'lessons': [
                {
                    'title': 'Two Team Models: Shared Repo vs Fork and PR',
                    'slug': 'team-models',
                    'objective': 'Choose between the shared-repository model and the fork-and-pull-request model.',
                    'duration': 10,
                    'body': """# How teams actually work on GitHub

## Model A — shared repository with branches (small teams, classmates)
Everyone is a **collaborator** on one repo. Each person clones it, works
on a feature branch, merges and pushes. This is chapters 4–6 exactly.

- Add teammates: repo → **Settings → Collaborators**.
- Best for: 2–8 trusted people, coursework, startup teams.

## Model B — fork and pull request (open source, strangers)
You cannot push to someone else's repository. GitHub's answer:

1. **Fork**: click *Fork* on `original-project` — GitHub creates
   `yourname/original-project`, a full copy under YOUR account.
2. **Clone your fork**, work, push to your fork.
3. **Pull request (PR)**: propose your commits to the original owners.
   The PR is a request: "please merge my branch `fix-typo` into your
   `main`".
4. Owners **review**, comment, request changes, then **merge** — or close.

The remote setup in Model B reflects the two repos:

```bash
git remote -v
origin    https://github.com/yourname/project.git   (your fork)
upstream  https://github.com/original/project.git   (the source)
```

Keeping fresh: `git fetch upstream && git merge upstream/main` before new
work, so your fork tracks the original.

## Why "pull" in "pull request"?
The owner *pulls* your changes in — you are announcing something is ready
to be pulled. (GitHub's squash/rebase/merge button options: chapter 9.)

## Real-world application
Your first open-source contribution is usually tiny: fix a README typo.
The workflow still teaches the full loop — fork, branch, commit, PR,
review, merge — and maintainers of huge projects began exactly that way.

## Common mistakes
- Pushing feature work to `main` of a shared repo "because PRs are slow".
  PRs exist so broken work stays invisible until reviewed.
- Opening a PR from your fork's `main` after many unrelated local
  commits — the PR contains everything. Always branch per change.
- Forking, then forgetting `upstream` and falling months behind; your
  one-line fix then carries a giant conflict.

## Lesson summary
Trusted teams share one repo with branches; public contribution uses
fork → branch → PR. `origin` is your copy, `upstream` is the source.""",
                    'exercises': [
                        {
                            'slug': 'fork-what',
                            'title': 'What forking does',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Clicking \u201cFork\u201d on GitHub creates…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'a branch inside the original repository', 'is_correct': False},
                                {'id': 'b', 'text': 'a full copy of the repository under your own account', 'is_correct': True},
                                {'id': 'c', 'text': 'download access without a repository', 'is_correct': False},
                                {'id': 'd', 'text': 'an invitation to become an owner', 'is_correct': False},
                            ],
                            'explain': 'A fork is your own server-side copy with its own URL; PRs later connect the two.',
                        },
                        {
                            'slug': 'pr-definition',
                            'title': 'The pull request in one line',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A pull request is best defined as…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'a demand that maintainers download your ZIP', 'is_correct': False},
                                {'id': 'b', 'text': 'a proposed set of commits, opened for review before merging into the target branch', 'is_correct': True},
                                {'id': 'c', 'text': 'a GitHub bug report', 'is_correct': False},
                                {'id': 'd', 'text': 'an automatic backup of your repository', 'is_correct': False},
                            ],
                            'explain': 'The PR page is the review conversation; merging applies your commits; closing discards them.',
                        },
                        {
                            'slug': 'upstream-remote',
                            'title': 'Naming the source',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In the fork workflow, the remote called `upstream` normally points to…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'your fork on your account', 'is_correct': False},
                                {'id': 'b', 'text': 'the original repository you forked', 'is_correct': True},
                                {'id': 'c', 'text': 'a teammate\u2019s laptop', 'is_correct': False},
                                {'id': 'd', 'text': 'the GitHub issues page', 'is_correct': False},
                            ],
                            'explain': 'origin = your copy; upstream = the source you follow and propose changes to.',
                        },
                    ],
                },
                {
                    'title': 'Opening and Surviving a Code Review',
                    'slug': 'code-review',
                    'objective': 'Write a useful PR description and respond to review comments.',
                    'duration': 10,
                    'body': """# The PR as a conversation

A reviewer decides in minutes whether to trust your work. Help them:

## A PR description that earns fast merges
```markdown
## What
Fixes crash when cart quantity exceeds stock (#142).

## Why
The checkout loop trusted cached stock; on retry it double-charged.

## How
Re-read stock inside the transaction; added regression test.

## Testing
Ran pytest; manual retry of the failing scenario twice.
```

Small, single-purpose PRs get reviewed. 800-line \u201ceverything\u201d PRs get
procrastinated.

## The review loop
1. Reviewer leaves inline comments on specific lines.
2. You push **new commits to the same branch** — the PR updates
   automatically. (This is the beauty of branches: a PR is just a live
   view of a branch.)
3. Approved → merged. Requested changes → repeat step 2.

## Responding like a professional
- Treat critique of code as separate from critique of person. \u201cGood
  catch — pushed a fix\u201d beats defending a wrong choice.
- Answer every comment, even disagreement: \u201cKept as-is because X —
  happy to change if the team prefers Y.\u201d
- Never merge your own PR when others are available to review; team
  norms and GitHub branch protection often forbid it.

## What reviewers look for
Correctness, readable naming, tests, no leftovers (debug prints, secrets,
commented-out code), and a description matching the diff.

## Common mistakes
- Force-pushing over reviewed commits mid-review — reviewers' comments
  detach from the code they discuss. Push follow-up commits instead.
- Leaving PRs open for weeks; they rot as the target branch moves.
  Update (merge/rebase from main) or close.

## Lesson summary
PR = branch under discussion. Tiny purposeful diffs, honest testing notes,
push fixes to the same branch, answer every comment, merge last.""",
                    'exercises': [
                        {
                            'slug': 'pr-update-mechanics',
                            'title': 'How a PR updates',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A reviewer asks for changes. To update the open PR you…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'close it and open a new PR', 'is_correct': False},
                                {'id': 'b', 'text': 'push new commits to the same branch — the PR reflects them automatically', 'is_correct': True},
                                {'id': 'c', 'text': 'email the reviewer a patch file', 'is_correct': False},
                                {'id': 'd', 'text': 'edit the PR description only', 'is_correct': False},
                            ],
                            'explain': 'A PR tracks its source branch live. New commits appear in the same thread; comments stay attached.',
                        },
                        {
                            'slug': 'pr-description-parts',
                            'title': 'Useful PR descriptions',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL elements a strong PR description contains.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'What the change does, in one or two lines', 'is_correct': True},
                                {'id': 'b', 'text': 'Why it exists (linked issue)', 'is_correct': True},
                                {'id': 'c', 'text': 'How it was tested', 'is_correct': True},
                                {'id': 'd', 'text': 'A apology for the change', 'is_correct': False},
                            ],
                            'explain': 'What / why / how-tested is the professional standard. Confidence, not apology — the diff speaks, you explain.',
                        },
                        {
                            'slug': 'review-push-anti-pattern',
                            'title': 'The mid-review rewrite',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Why is `git push --force` to a branch under active review discouraged?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'It rewrites commits so inline comments detach from the code they reference', 'is_correct': True},
                                {'id': 'b', 'text': 'GitHub charges for rewritten commits', 'is_correct': False},
                                {'id': 'c', 'text': 'Force push is always impossible after review starts', 'is_correct': False},
                                {'id': 'd', 'text': 'It closes the PR automatically', 'is_correct': False},
                            ],
                            'explain': 'Forcing replaces history; the reviewer sees \u201ccomment on outdated diff\u201d and trust drops. Add commits instead — squash after approval if the team prefers.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 7 Quiz',
                    'slug': 'collaboration-quiz',
                    'objective': 'Check understanding of forks, PRs and review etiquette.',
                    'duration': 4,
                    'body': """# Chapter 7 quiz

Five questions on team models, pull requests and code review.""",
                    'exercises': [
                        {
                            'slug': 'q7-model-choice',
                            'title': 'Pick the model',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You contribute to a famous open-source project you do not own. Which workflow applies?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Shared repository: ask maintainers for collaborator access', 'is_correct': False},
                                {'id': 'b', 'text': 'Fork, branch on your fork, open a pull request', 'is_correct': True},
                                {'id': 'c', 'text': 'Clone, commit locally, email the patch', 'is_correct': False},
                                {'id': 'd', 'text': 'Edit directly on github.com', 'is_correct': False},
                            ],
                            'explain': 'Without write access, the fork-and-PR path is the standard contribution route.',
                        },
                        {
                            'slug': 'q7-pr-is-branch-view',
                            'title': 'PR mechanics revisited',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Technically, an open GitHub pull request shows…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'a frozen snapshot taken when the PR was created', 'is_correct': False},
                                {'id': 'b', 'text': 'the live difference between a head branch and the base branch', 'is_correct': True},
                                {'id': 'c', 'text': 'only the last commit of a branch', 'is_correct': False},
                                {'id': 'd', 'text': 'a duplicate of the whole repository', 'is_correct': False},
                            ],
                            'explain': 'PR = compare of head (your branch) against base (target branch); push more commits, it grows.',
                        },
                        {
                            'slug': 'q7-branch-per-change',
                            'title': 'Why one branch per change',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Opening a PR from your fork\u2019s main after many unrelated local commits is bad because…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'GitHub blocks main-branch PRs', 'is_correct': False},
                                {'id': 'b', 'text': 'the PR must include every extra commit, making review impossible', 'is_correct': True},
                                {'id': 'c', 'text': 'merge conflicts become guaranteed', 'is_correct': False},
                                {'id': 'd', 'text': 'the fork\u2019s main cannot be pushed to', 'is_correct': False},
                            ],
                            'explain': 'Branch-per-change isolates the proposal. Keep your fork\u2019s main mirror-clean by resetting it to upstream.',
                        },
                        {
                            'slug': 'q7-review-reply',
                            'title': 'Review response',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A reviewer is wrong about your code. The professional reply is…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Silently ignore the comment', 'is_correct': False},
                                {'id': 'b', 'text': 'Explain your reasoning with evidence; offer to change if the team prefers otherwise', 'is_correct': True},
                                {'id': 'c', 'text': 'Delete the comment thread', 'is_correct': False},
                                {'id': 'd', 'text': 'Close the PR out of pride', 'is_correct': False},
                            ],
                            'explain': 'Every comment gets an answer. PRs are discussions; disappearing or arguing with facts missing is how contributions get rejected.',
                        },
                        {
                            'slug': 'q7-fetch-upstream-fill',
                            'title': 'Staying fresh',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that downloads the original '
                                'project\u2019s latest commits into your fork-tracking copy, '
                                'changing no files of your own:\n'
                                '`git ________ upstream`\n(One word.)'
                            ),
                            'xp_reward': 30,
                            'solution_code': 'fetch',
                            'explain': 'git fetch upstream previews; merge the updates into your branch when ready.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 8 ════════════════════
        {
            'title': 'Advanced Git Fundamentals',
            'slug': 'advanced',
            'description': '.gitignore, log and diff for insight; restore, revert, reset and stash for recovery.',
            'lessons': [
                {
                    'title': '.gitignore, git log and git diff',
                    'slug': 'ignore-log-diff',
                    'objective': 'Ignore noise files and inspect history and differences.',
                    'duration': 12,
                    'body': """# Keeping the repo clean and reading its story

## .gitignore — files Git should never see
Compile output, virtual environments, `.env` secrets, `node_modules/` —
noise that must not enter history. Create a file named `.gitignore` in
the repo root:

```gitignore
# build output
build/
dist/
__pycache__/

# secrets and local settings
.env
*.local

# editor noise
.vscode/settings.json
```

Rules: one pattern per line, `#` comments, `/` ends a folder, `*` is a
wildcard. Ignoring stops **new** tracking; an already-committed file stays
committed until you `git rm --cached <file>` (removes from Git, keeps on
disk).

## git log — the history reader
```bash
git log                       # full history, press q to quit
git log --oneline             # one line per commit
git log --oneline --graph --all   # the branch tree — extremely useful
git log -3                    # only the last 3
git log --author="Ayesha"
git log -- login.py           # history of one file
```

Typical `--oneline` output:

```
a1c9f2e (HEAD -> main) Merge branch 'profile-page'
9b3d1aa Wire profile URL and view
7f0aa21 Add profile page template
3f2a9c1 Add user login form
```

Newest first; the hash lets you reference any commit anywhere else.

## git diff — the question you will ask a thousand times
```bash
git diff                 # working directory vs staging (unseen next commit)
git diff --staged        # staging vs last commit (what WOULD commit)
git diff main login-fix  # two branches/commits compared
git diff 3f2a9c1 HEAD    # a specific commit vs now
```

Output format: lines with `-` are removed, `+` added, context lines
unchanged, grouped per file. This is the same shape you saw on GitHub's
"Files changed" tab — GitHub runs diffs of pushed commits.

## Common mistakes
- Adding secrets AFTER committing them. History keeps secrets forever;
  rotation and history rewriting (chapter 9 note) is the painful fix.
- `git log` appearing frozen: it is a pager. Press `q`; `space` pages.
- Reading only file names in a diff — check line numbers and the
  `@@ … @@` hunk headers before judging.

## Lesson summary
.gitignore prevents noise entering; `git rm --cached` extracts what
slipped in. log reads the story, diff answers "what exactly changed?"
at every comparison level.""",
                    'exercises': [
                        {
                            'slug': 'ignore-vs-rm-cached',
                            'title': 'The already-trapped file',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You committed `.env` last week and now added it to .gitignore. Git still tracks it. Why?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': '.gitignore only affects untracked files; the committed .env must be removed with git rm --cached', 'is_correct': True},
                                {'id': 'b', 'text': '.env is a protected system name', 'is_correct': False},
                                {'id': 'c', 'text': 'gitignore needs a restart of Git Bash', 'is_correct': False},
                                {'id': 'd', 'text': 'Only GitHub applies .gitignore, not Git', 'is_correct': False},
                            ],
                            'explain': 'Ignoring applies to files Git does not yet track. git rm --cached stops tracking it; a follow-up commit records the removal (and rotate the secret!).',
                        },
                        {
                            'slug': 'diff-staged-flag',
                            'title': 'Preview the next commit',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that shows the difference between '
                                'the staging area and the last commit:\n'
                                '`git diff ____________`\n(One word flag with dashes.)'
                            ),
                            'xp_reward': 40,
                            'solution_code': '--staged',
                            'explain': 'git diff --staged (older docs: --cached) previews exactly what git commit would record.',
                        },
                        {
                            'slug': 'log-graph-selection',
                            'title': 'See the branch tree',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command shows a compact commit-per-line history WITH the branching structure?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git log --oneline --graph --all', 'is_correct': True},
                                {'id': 'b', 'text': 'git status --tree', 'is_correct': False},
                                {'id': 'c', 'text': 'git diff --history', 'is_correct': False},
                                {'id': 'd', 'text': 'git branch -v', 'is_correct': False},
                            ],
                            'explain': 'The trio --oneline --graph --all renders the whole branch topology compactly — the single best history view.',
                        },
                        {
                            'slug': 'diff-minus-plus',
                            'title': 'Diff direction',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'In `git diff` output, lines marked `-` are…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'present in the older version, absent in the newer', 'is_correct': True},
                                {'id': 'b', 'text': 'newly added lines', 'is_correct': False},
                                {'id': 'c', 'text': 'lines with conflicts', 'is_correct': False},
                                {'id': 'd', 'text': 'commented-out code', 'is_correct': False},
                            ],
                            'explain': '`-` = removed relative to the compared-from version; `+` = added. Read old → new top to bottom.',
                        },
                    ],
                },
                {
                    'title': 'Undoing: restore, revert and reset',
                    'slug': 'undo-tools',
                    'objective': 'Pick the right undo tool for each mistake level.',
                    'duration': 14,
                    'body': """# Three levels of undo — match the tool to the damage

Mistakes happen at three stages; each has its own tool.

## 1. Uncommitted edits → `git restore`
"This file's edits are garbage, give me the committed version back:"

```bash
git restore login.py           # DISCARDS working changes (careful!)
git restore --staged app.js    # unstage only; edits stay (chapter 4)
```

`git restore` erases uncommitted work irrecoverably. When in doubt, stash
instead (below).

## 2. A commit that should not exist → `git revert`
"Yesterday's merge broke production; history already went public."

```bash
git revert 9b3d1aa
```

Revert creates a **new commit that undoes** the old one's changes.
History is not rewritten — the bad commit stays visible, its damage
cancelled. This is the safe undo on shared branches, full stop.

## 3. Your own branch is mislabelled → `git reset`
"I made three commits on the wrong branch" / "I want main to forget the
last commit (and keep/lose the changes)" — reset moves the branch pointer
backward (or forward). Three flavours:

```bash
git reset --soft HEAD~1   # move pointer; changes STAY staged
git reset --mixed HEAD~1  # default; changes stay in working dir, unstaged
git reset --hard HEAD~1   # ⚠ changes DISAPPEAR from the working dir
```

Rules for reset:
- `HEAD~1` means "one commit back"; `HEAD~3` three back.
- Use reset only on commits **nobody has pulled**. Resetting shared
  history makes your branch disagree with teammates and forces the
  destructive `--force` push.
- A lost commit is often still recoverable for days via `git reflog` —
  Git rarely deletes objects immediately.

## revert vs reset, decided in one line
Already shared or public → **revert** (forward-fix). Private and local →
**reset** (rewrite freely). Never certain → revert; it is reversible too.

## Common mistakes
- `--hard` reflex. Type `git status` first; if it says uncommitted work
  exists, `--hard` deletes it.
- Resetting pushed main "to undo" — teammates now have divergent
  history. Use revert.
- Forgetting `git restore` (no `--staged`) is the file-level undo that
  surprises people with how completely it wipes.

## Lesson summary
restore = forget uncommitted edits; revert = commit that cancels a
commit (safe in public); reset = move a private branch pointer, with
--hard being the sharpest tool in Git.""",
                    'exercises': [
                        {
                            'slug': 'undo-wrong-branch',
                            'title': 'Shared history safety',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A pushed commit on the team\u2019s main must be undone. Which command, and why?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'git reset --hard — cleanest', 'is_correct': False},
                                {'id': 'b', 'text': 'git revert — it undoes by adding a new commit, without rewriting shared history', 'is_correct': True},
                                {'id': 'c', 'text': 'git restore — file-level undo fits best', 'is_correct': False},
                                {'id': 'd', 'text': 'Delete the branch and start over', 'is_correct': False},
                            ],
                            'explain': 'Rewriting commits others have pulled breaks their copies. Revert is the forward-fix designed for exactly this.',
                        },
                        {
                            'slug': 'reset-soft-meaning',
                            'title': 'reset --soft effect',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'After `git reset --soft HEAD~1`, the undone commit\u2019s changes are…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'gone from disk', 'is_correct': False},
                                {'id': 'b', 'text': 'kept in the working directory AND still staged', 'is_correct': True},
                                {'id': 'c', 'text': 'kept but unstaged', 'is_correct': False},
                                {'id': 'd', 'text': 'pushed to origin', 'is_correct': False},
                            ],
                            'explain': 'soft moves only the pointer; mixed also unstages; hard discards. The ladder from gentle to destructive is worth memorising.',
                        },
                        {
                            'slug': 'reflog-rescue',
                            'title': 'The safety net',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'You destroyed work with `reset --hard` minutes ago. Best first recovery step?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Reinstall Git', 'is_correct': False},
                                {'id': 'b', 'text': 'git reflog to find the lost commit hash, then reset/branch to it', 'is_correct': True},
                                {'id': 'c', 'text': 'Everything is gone forever', 'is_correct': False},
                                {'id': 'd', 'text': 'Ask GitHub by email', 'is_correct': False},
                            ],
                            'explain': 'reflog lists every position HEAD has held — including commits no branch points to. Act within its expiry window and work returns.',
                        },
                        {
                            'slug': 'restore-vs-restore-staged',
                            'title': 'Same command, opposite blast radius',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about git restore.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'git restore <file> discards uncommitted working changes for that file', 'is_correct': True},
                                {'id': 'b', 'text': 'git restore --staged <file> keeps working changes and only unstages', 'is_correct': True},
                                {'id': 'c', 'text': 'git restore can undo a commit', 'is_correct': False},
                                {'id': 'd', 'text': 'Plain restore\u2019s discarded edits are not recoverable through Git', 'is_correct': True},
                            ],
                            'explain': 'restore is for the working area (and staging with the flag). Commits need revert/reset. Uncommitted discards are truly gone.',
                        },
                        {
                            'slug': 'revert-command-fill',
                            'title': 'The forward-fix command',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that creates a new commit undoing '
                                'commit 9b3d1aa:\n`git ________ 9b3d1aa`\n(One word.)'
                            ),
                            'xp_reward': 30,
                            'solution_code': 'revert',
                            'explain': 'git revert <commit> opens/requires a message and records the inverse change as a fresh commit.',
                        },
                    ],
                },
                {
                    'title': 'Stashing: pause your work',
                    'slug': 'stashing',
                    'objective': 'Park uncommitted changes and bring them back.',
                    'duration': 8,
                    'body': """# `git stash` — the clipboard for your working directory

Scenario: halfway through styling, you must hot-fix a typo on main
NOW — but switching branches with half-edited files risks carrying the
mess or blocking the switch. Stash tucks every uncommitted change into a
small stack, leaving your working directory pristine:

```bash
git stash                 # shelve modified TRACKED files
git stash -u              # include untracked (-u) too — usually what you want
git switch main
… fix, commit, push …
git switch feature
# OR from anywhere:
git stash pop             # restore newest stash and remove it from the list
git stash list            # see shelved entries: stash@{0}, stash@{1} …
git stash apply stash@{1} # restore an older one without deleting it
git stash drop            # discard the newest
```

## pop vs apply
`pop` = restore + delete. `apply` = restore, keep the stash. If applying
hits conflicts, the stash survives — retry after resolving, then drop.

## Good taste in stashes
Stash to **branch**, not to hoard. A week-old stash nobody remembers is
a forgotten drawer of unfinished code — either finish it, or drop it.
For pausing real features, prefer committing a `wip:` on your branch.

## Common mistakes
- Piling several stashes then popping the wrong one. Check
  `git stash list` first; pop applies the newest, which after two stashes
  is not the one you mean.
- Expecting stashes to be pushed/shared. They are purely local, and lost
  if the repo is deleted.

## Lesson summary
stash parks uncommitted work so you can switch context cleanly;
pop/apply returns it; keep the stack tiny and remembered.""",
                    'exercises': [
                        {
                            'slug': 'stash-purpose',
                            'title': 'When to stash',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Best description of git stash\u2019s role:',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'A permanent backup of unfinished features', 'is_correct': False},
                                {'id': 'b', 'text': 'A short-term parking lot for uncommitted changes so you can change context', 'is_correct': True},
                                {'id': 'c', 'text': 'A way to share WIP with teammates', 'is_correct': False},
                                {'id': 'd', 'text': 'A replacement for committing', 'is_correct': False},
                            ],
                            'explain': 'Stash is a temporary clipboard, local-only. For real WIP sharing, commit to a branch and push.',
                        },
                        {
                            'slug': 'pop-vs-apply',
                            'title': 'pop versus apply',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'After `git stash apply stash@{0}`, that stash entry…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'is deleted like pop would', 'is_correct': False},
                                {'id': 'b', 'text': 'remains in the list until you git stash drop it', 'is_correct': True},
                                {'id': 'c', 'text': 'is pushed to origin', 'is_correct': False},
                                {'id': 'd', 'text': 'converts into a branch', 'is_correct': False},
                            ],
                            'explain': 'apply is restore-copy; pop is restore-move. Conflicted applies also keep the stash as insurance.',
                        },
                        {
                            'slug': 'stash-untracked-flag',
                            'title': 'The missed new file',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'You stashed but your brand-new untracked helper.py was '
                                'left behind. Which flag should you have used to include '
                                'untracked files? Write just the flag, dash and letter.\n'
                                '`git stash ____`'
                            ),
                            'xp_reward': 40,
                            'solution_code': '-u',
                            'explain': '-u (\u201cinclude untracked\u201d) stashes new files too; without it only tracked modifications are shelved.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 8 Quiz',
                    'slug': 'advanced-quiz',
                    'objective': 'Check understanding of history inspection and recovery tools.',
                    'duration': 5,
                    'body': """# Chapter 8 quiz

Six questions on ignore rules, log/diff, undo tools and stash.""",
                    'exercises': [
                        {
                            'slug': 'q8-ignored-already',
                            'title': 'Pattern scope',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Adding `*.log` to .gitignore causes…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'all .log files anywhere in the repo to stop being tracked or shown as untracked', 'is_correct': True},
                                {'id': 'b', 'text': 'existing committed .log files to be deleted', 'is_correct': False},
                                {'id': 'c', 'text': '.log files to be deleted from disk', 'is_correct': False},
                                {'id': 'd', 'text': 'only the root folder’s .log files to hide', 'is_correct': False},
                            ],
                            'explain': 'Ignore patterns only affect Git\u2019s attention, never your disk. Already-committed files are the exception — they need git rm --cached.',
                        },
                        {
                            'slug': 'q8-history-of-file',
                            'title': 'One file\u2019s story',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command lists every commit that touched pricing.py?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'git log -- pricing.py', 'is_correct': True},
                                {'id': 'b', 'text': 'git diff pricing.py', 'is_correct': False},
                                {'id': 'c', 'text': 'git show --file pricing.py', 'is_correct': False},
                                {'id': 'd', 'text': 'git status pricing.py', 'is_correct': False},
                            ],
                            'explain': 'The -- separator takes path filters: git log -- <path> limits history to those files.',
                        },
                        {
                            'slug': 'q8-hard-reset-damage',
                            'title': 'The destructive combo',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which action loses uncommitted working-directory edits immediately?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git stash push', 'is_correct': False},
                                {'id': 'b', 'text': 'git reset --hard HEAD~1 with uncommitted changes present', 'is_correct': True},
                                {'id': 'c', 'text': 'git revert HEAD', 'is_correct': False},
                                {'id': 'd', 'text': 'git restore --staged file', 'is_correct': False},
                            ],
                            'explain': 'reset --hard overwrites the working tree to match the target commit; unstashed edits vanish. Always git status before --hard.',
                        },
                        {
                            'slug': 'q8-shared-undo',
                            'title': 'Public mistake policy',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The rule for undoing commits already pushed to a shared branch is…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Never undo public commits', 'is_correct': False},
                                {'id': 'b', 'text': 'Revert forward; reserve reset/rewrite for private branches', 'is_correct': True},
                                {'id': 'c', 'text': 'Force-push the reset version quietly', 'is_correct': False},
                                {'id': 'd', 'text': 'Ask GitHub support to delete commits', 'is_correct': False},
                            ],
                            'explain': 'History rewriting on shared branches destroys teammates\u2019 bases. Forward-fixing with revert is the professional norm.',
                        },
                        {
                            'slug': 'q8-reflog',
                            'title': 'reflog truth',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What does git reflog record?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Every position HEAD has occupied, including commits branches later abandoned', 'is_correct': True},
                                {'id': 'b', 'text': 'Only merge events', 'is_correct': False},
                                {'id': 'c', 'text': 'File edit history inside the editor', 'is_correct': False},
                                {'id': 'd', 'text': 'GitHub access logs', 'is_correct': False},
                            ],
                            'explain': 'reflog is your local safety net for resets, rebases and \u201clost\u201d commits — its entries expire, so act quickly.',
                        },
                        {
                            'slug': 'q8-stash-switch',
                            'title': 'Mid-stash branch switch',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'With a stash saved, you switch branches and pop. The changes land…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'back on the original branch automatically', 'is_correct': False},
                                {'id': 'b', 'text': 'on whatever branch is currently checked out', 'is_correct': True},
                                {'id': 'c', 'text': 'nowhere until you merge', 'is_correct': False},
                                {'id': 'd', 'text': 'onto a new branch git creates', 'is_correct': False},
                            ],
                            'explain': 'Stashes are not branch-bound. pop/apply writes into the current working tree — choose the branch yourself first.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 9 ════════════════════
        {
            'title': 'Professional GitHub Workflow',
            'slug': 'professional',
            'description': 'Commit message standards, README craft, issues, project boards and the open-source contribution path.',
            'lessons': [
                {
                    'title': 'Commit Messages, READMEs and Repository Hygiene',
                    'slug': 'repo-hygiene',
                    'objective': 'Write conventional commits and a README that makes a repo readable by strangers.',
                    'duration': 12,
                    'body': """# The repository as your public professional document

Recruiters and collaborators judge process from three artefacts: commit
messages, README, and issue discipline.

## Conventional Commits (the industry standard)
Format: `type(scope): subject`

```
feat(cart): add quantity limit per item
fix(checkout): re-read stock inside transaction (#142)
docs(readme): describe setup steps for MySQL
test(api): add timeout retry case
refactor(utils): extract currency formatter
chore: bump dependencies
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`,
`style`. Scope optional; subject imperative (chapter 4). Tools read this
format to generate changelogs automatically — writing it is learning it.

## README — the six blocks that matter
1. **What** — one-paragraph project description and why it exists.
2. **Screenshots / demo link** if it is visual.
3. **Setup** — exact commands to install and run (`pip install -r
   requirements.txt`, `python manage.py runserver`).
4. **Usage** — one worked example a reader can copy.
5. **Tech stack** — languages, frameworks, databases.
6. **Credits / license / contact.**

A README a stranger can follow to a running program is worth ten
portfolios' worth of screenshots.

## Hygiene settings worth five minutes
- **LICENSE file** — no license means "all rights reserved" by default.
  Pick MIT for permissive sharing.
- **`.gitignore` from the start** (GitHub offers templates per language).
- **Description + topics** on the repo page — how search finds you.
- **Branch protection on main** (team repos): require PRs + passing
  checks before merge. GitHub: Settings → Branches.

## Common mistakes
- `git commit -m "final v3"` as the public face of your work.
- README written once, stale forever. Update it in the same commit that
  changes setup — make it part of the definition of done.
- Forcing pushes to main "to fix CI quickly" — protection exists exactly
  for this temptation; use a revert + fresh PR.

## Lesson summary
Conventional commits tell machine-readable stories; READMEs turn repos
into invitations; licences and protection settings make the project
legally and technically safe.""",
                    'exercises': [
                        {
                            'slug': 'conventional-type',
                            'title': 'Choosing the type',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which conventional-commit prefix fits: correcting a crash when the cart is empty?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'feat(cart): handle empty cart', 'is_correct': False},
                                {'id': 'b', 'text': 'fix(cart): prevent crash on empty cart', 'is_correct': True},
                                {'id': 'c', 'text': 'chore: empty cart crash', 'is_correct': False},
                                {'id': 'd', 'text': 'docs(cart): crash note', 'is_correct': False},
                            ],
                            'explain': 'A crash correction is fix; the scope names the area; the subject says what and where.',
                        },
                        {
                            'slug': 'readme-essential-blocks',
                            'title': 'README completeness',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL blocks a portfolio-quality README should include.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Setup commands to install and run', 'is_correct': True},
                                {'id': 'b', 'text': 'A one-paragraph description of what and why', 'is_correct': True},
                                {'id': 'c', 'text': 'Full source code pasted into the README', 'is_correct': False},
                                {'id': 'd', 'text': 'Tech stack and a usage example', 'is_correct': True},
                            ],
                            'explain': 'The code already lives in the files; the README guides a human to run and understand it.',
                        },
                        {
                            'slug': 'no-license-default',
                            'title': 'The silent licence',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A public repository with no LICENSE file legally means…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Anyone may use it freely', 'is_correct': False},
                                {'id': 'b', 'text': 'All rights reserved by you — others have no permission to use it', 'is_correct': True},
                                {'id': 'c', 'text': 'GitHub applies MIT automatically', 'is_correct': False},
                                {'id': 'd', 'text': 'It becomes public domain after a year', 'is_correct': False},
                            ],
                            'explain': 'Absence of a licence means absence of granted rights. Add one deliberately (MIT is a common permissive default).',
                        },
                        {
                            'slug': 'branch-protection-where',
                            'title': 'Enforcing the PR gate',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'On GitHub, requiring pull requests before changes land on main is configured in…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'Repository Settings → Branches (branch protection rules)', 'is_correct': True},
                                {'id': 'b', 'text': 'the .gitignore file', 'is_correct': False},
                                {'id': 'c', 'text': 'git config --global protect true', 'is_correct': False},
                                {'id': 'd', 'text': 'it is impossible on GitHub', 'is_correct': False},
                            ],
                            'explain': 'Protection rules block direct pushes and can require reviews and passing checks.',
                        },
                    ],
                },
                {
                    'title': 'Issues, Boards and the Open-Source Path',
                    'slug': 'issues-boards-oss',
                    'objective': 'Use issues and project boards to plan work, and follow the open-source contribution workflow.',
                    'duration': 11,
                    'body': """# Planning in public: issues and boards

## Issues are the task database
Every bug, feature and task becomes an issue with a title, description,
**labels** (bug / enhancement / good-first-issue), an **assignee** and a
milestone. Linking language closes the loop:

- Commit message: `fix(cart): empty-cart crash (#142)` — GitHub links it.
- PR description: `Closes #142` — merging auto-closes the issue.

## Project boards
GitHub Projects is a kanban: **Todo → In progress → Done** (custom
columns allowed; automation can move cards on PR merge). Teams run
sprints entirely on one; a solo student can still track "3 of 8 tasks
done" honestly.

## Milestones and releases
Bundle issues into a milestone ("v1.0"); tag a commit
(`git tag -a v1.0 -m "first public release"`), push tags
(`git push origin v1.0`), and open a GitHub **Release** against it —
release notes auto-generate from merged PRs.

## The open-source contribution etiquette
1. Read `CONTRIBUTING.md` — projects state their exact rules.
2. Search existing issues; comment your intent before coding big changes.
3. Fork → branch named for the issue → small focused commits → PR.
4. Be patient; maintainers are often unpaid. Respond to every review
   comment with pushed fixes (chapter 7).
5. First contribution success → repeat with something larger.

## Real-world application
Class project, 4 people: instructor issues = graded deliverables; each
student picks tasks off the board; every deliverable is a merged PR
linked to a closed issue; the milestone shows the class exactly how far
the team is.

## Common mistakes
- Holding tasks "in your head" — invisible work cannot be tracked,
  reviewed or credited.
- One mega-issue covering the whole app; issues work when they are small
  and closable.
- Sending unrequested large PRs to OSS projects — they are usually
  closed unread. Discuss via an issue first.

## Lesson summary
Issues name the work, boards visualise flow, tags/releases mark time,
and the OSS path is conversation → fork → small PR → responsive review.""",
                    'exercises': [
                        {
                            'slug': 'closes-keyword',
                            'title': 'Auto-close magic',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A PR body containing “Closes #142”, once merged, will…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'delete issue 142', 'is_correct': False},
                                {'id': 'b', 'text': 'automatically close issue #142 and link the PR to it', 'is_correct': True},
                                {'id': 'c', 'text': 'rename the branch', 'is_correct': False},
                                {'id': 'd', 'text': 'approve the PR without review', 'is_correct': False},
                            ],
                            'explain': 'GitHub parses closes/fixes/resolves + issue references and closes them on merge.',
                        },
                        {
                            'slug': 'oss-first-step',
                            'title': 'Before the code',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Planning a significant change to an open-source project, the FIRST correct step is…',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Fork and immediately open a large PR to show effort', 'is_correct': False},
                                {'id': 'b', 'text': 'Read CONTRIBUTING.md, search/open an issue and discuss the approach', 'is_correct': True},
                                {'id': 'c', 'text': 'Email every maintainer asking permission', 'is_correct': False},
                                {'id': 'd', 'text': 'Clone and silently rewrite the module', 'is_correct': False},
                            ],
                            'explain': 'Agreement before work prevents rejected effort — the social step precedes the technical one.',
                        },
                        {
                            'slug': 'tag-push-fill',
                            'title': 'Publishing a version',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that uploads your new local tag '
                                'v1.0 to GitHub:\n`git ________ origin v1.0`\n(One word.)'
                            ),
                            'xp_reward': 30,
                            'solution_code': 'push',
                            'explain': 'Tags are not included in ordinary git push; name them (or use --tags) explicitly.',
                        },
                        {
                            'slug': 'board-columns',
                            'title': 'Kanban reality',
                            'exercise_type': 'multiple_select',
                            'instructions': 'Select ALL true statements about GitHub Issues / Projects.',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Labels like “bug” or “good-first-issue” classify and surface issues', 'is_correct': True},
                                {'id': 'b', 'text': 'Milestones group issues toward a dated release', 'is_correct': True},
                                {'id': 'c', 'text': 'Only repository owners may comment on issues', 'is_correct': False},
                                {'id': 'd', 'text': 'Boards can automate card movement when PRs merge', 'is_correct': True},
                            ],
                            'explain': 'Anyone with access can comment (that is the point of public planning); the other three describe standard features.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 9 Quiz',
                    'slug': 'professional-quiz',
                    'objective': 'Check understanding of professional repository practices.',
                    'duration': 4,
                    'body': """# Chapter 9 quiz

Five questions on conventions, issues, boards and contribution.""",
                    'exercises': [
                        {
                            'slug': 'q9-chore-meaning',
                            'title': 'chore: meaning',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A commit titled `chore: bump dependencies` changes…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'user-facing behaviour', 'is_correct': False},
                                {'id': 'b', 'text': 'maintenance plumbing — no feature or fix', 'is_correct': True},
                                {'id': 'c', 'text': 'documentation only', 'is_correct': False},
                                {'id': 'd', 'text': 'nothing; chore is invalid', 'is_correct': False},
                            ],
                            'explain': 'chore = routine work outside feat/fix/docs/test/refactor. docs alone would be a docs: prefix.',
                        },
                        {
                            'slug': 'q9-readme-purpose',
                            'title': 'README test',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The practical test of a good README is…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'a stranger can reach a running program following only its setup steps', 'is_correct': True},
                                {'id': 'b', 'text': 'it lists every file in the project', 'is_correct': False},
                                {'id': 'c', 'text': 'it is at least 1000 words', 'is_correct': False},
                                {'id': 'd', 'text': 'it contains the whole source', 'is_correct': False},
                            ],
                            'explain': 'READMEs exist to convert visitors into users. Length or file lists do not matter.',
                        },
                        {
                            'slug': 'q9-milestone-vs-release',
                            'title': 'Milestones and releases',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which pairing is correct?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Milestone = planning grouping of issues; Release = published tagged version with notes', 'is_correct': True},
                                {'id': 'b', 'text': 'Milestone = finished code; Release = planning tool', 'is_correct': False},
                                {'id': 'c', 'text': 'Both mean the same thing', 'is_correct': False},
                                {'id': 'd', 'text': 'Releases delete milestones', 'is_correct': False},
                            ],
                            'explain': 'You plan toward a milestone and publish from a tag as a release.',
                        },
                        {
                            'slug': 'q9-issue-comment-intent',
                            'title': 'Why announce intent',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Commenting “I’d like to work on this issue” before coding helps because…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'GitHub locks the issue for you', 'is_correct': False},
                                {'id': 'b', 'text': 'maintainers can steer or reserve, avoiding two duplicated efforts and rejected work', 'is_correct': True},
                                {'id': 'c', 'text': 'it automatically forks the repo', 'is_correct': False},
                                {'id': 'd', 'text': 'it merges previous PRs', 'is_correct': False},
                            ],
                            'explain': 'Coordination is social: early feedback saves everyone time and doubles of the same fix.',
                        },
                        {
                            'slug': 'q9-good-first-issue',
                            'title': 'Label meanings',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'The `good-first-issue` label marks tasks that are…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'newest in the tracker', 'is_correct': False},
                                {'id': 'b', 'text': 'beginner-friendly, scoped for contributors unfamiliar with the codebase', 'is_correct': True},
                                {'id': 'c', 'text': 'already solved', 'is_correct': False},
                                {'id': 'd', 'text': 'reserved for maintainers', 'is_correct': False},
                            ],
                            'explain': 'It is an on-ramp label: small, well-described tasks where newcomers can succeed.',
                        },
                    ],
                },
            ],
        },
        # ════════════════════ Chapter 10 ════════════════════
        {
            'title': 'Final Practical Project',
            'slug': 'project',
            'description': 'Put it all together: a documented repository with branches, a PR and a resolved conflict.',
            'lessons': [
                {
                    'title': 'Project Brief: The Study Notes Repository',
                    'slug': 'project-brief',
                    'objective': 'Understand the deliverables and evaluation rubric for the course project.',
                    'duration': 10,
                    'body': """# Project: publish a real, well-managed repository

You will build a small **study notes repository** — three Markdown files
of your own course notes — and manage it with everything this course
taught. The product is not the notes; the product is the **workflow**.

## Requirements (the rubric, in order)
1. **Local repository** created with `git init`, identity configured,
   `.gitignore` ignoring at least one pattern (e.g. `*.tmp` or `drafts/`).
2. **README.md** with the six blocks from chapter 9 (what, setup, usage,
   stack, licence, contact).
3. **≥ 8 commits total** following the message conventions (imperative
   or `type(scope): subject`), each a single idea.
4. **Two feature branches**, merged into main with real merges
   (`notes-chemistry`, `notes-math` — or your subjects).
5. **A simulated conflict, resolved**: edit the same line of `README.md`
   differently on main and on a branch, merge, resolve deliberately,
   commit the resolution.
6. **A GitHub repository**: create empty, `git remote add origin`,
   `git push -u origin main`; history visible online.
7. **One pull request opened and merged** — even solo, you can open a PR
   from a branch to main on GitHub and merge it (this is how you
   rehearse the collaboration flow).
8. **Submit** the repository URL and a 3–5 sentence description of your
   workflow decisions.

## Suggested architecture (file layout)
```
study-notes/
├── .gitignore
├── README.md
├── LICENSE          (MIT text from choosealicense.com)
└── notes/
    ├── 01-git.md
    ├── 02-branching.md
    └── 03-github.md
```

## Milestones
- **M1 (local):** init, ignore, first commit, README present.
- **M2 (branches):** two branches merged with at least one conflict
  resolution commit (its message says so).
- **M3 (published):** pushed to GitHub, one PR merged, URL submitted.

## Evaluation rubric (100 points)
| Area | Points | What full marks look like |
|---|---|---|
| History quality | 30 | ≥8 small commits, imperative/c conventional messages, no "update" |
| Branch & merge | 25 | two branches, clean merges, one deliberate conflict resolution |
| README & hygiene | 20 | runnable-by-stranger README, .gitignore active, LICENSE |
| GitHub presence | 15 | pushed with origin, history renders, one merged PR |
| Reflection | 10 | description explains two decisions you made and why |

## Extension challenges (optional)
- Add a tagged **release** v1.0 and a GitHub Release page.
- Protect `main` with a branch protection rule and observe a direct push
  being refused.
- Contribute one real fix (typo or broken link) to someone else's open
  source project via fork + PR, and link the merged PR in your README.

## Honest note on submission
Where the platform supports repository submission, paste the URL in the
project field; otherwise include it in your final-assignment reflection.
Graders inspect **your repository's history**, not the notes' content —
keep the commits themselves the exhibit.""",
                    'exercises': [
                        {
                            'slug': 'rubric-history-evidence',
                            'title': 'What the grader inspects',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which repository view proves requirement 3 (history quality)?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git log --oneline --graph --all (or the GitHub commits page)', 'is_correct': True},
                                {'id': 'b', 'text': 'git status on main', 'is_correct': False},
                                {'id': 'c', 'text': 'the number of files in the folder', 'is_correct': False},
                                {'id': 'd', 'text': 'git remote -v', 'is_correct': False},
                            ],
                            'explain': 'Commit count, messages and merge structure all appear in the graph log — the project\u2019s evidence sheet.',
                        },
                        {
                            'slug': 'deliberate-conflict-setup',
                            'title': 'Engineering the required conflict',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'To create the required simulated conflict, you should…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'edit DIFFERENT files on the two branches, then merge', 'is_correct': False},
                                {'id': 'b', 'text': 'edit the SAME line of README.md differently on main and the branch, then merge', 'is_correct': True},
                                {'id': 'c', 'text': 'delete README on one branch', 'is_correct': False},
                                {'id': 'd', 'text': 'push before committing', 'is_correct': False},
                            ],
                            'explain': 'Conflicts need same-line divergence (chapter 5). Different files or deleted-file cases merge without markers here.',
                        },
                        {
                            'slug': 'pr-solo-justification',
                            'title': 'PR without teammates',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Opening and merging your own PR on a solo project is worthwhile because…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'it doubles your XP on GitHub', 'is_correct': False},
                                {'id': 'b', 'text': 'it rehearses the exact collaboration surface teams use — diff review, description, merge gate', 'is_correct': True},
                                {'id': 'c', 'text': 'main branches cannot be merged locally', 'is_correct': False},
                                {'id': 'd', 'text': 'it is required by Git itself', 'is_correct': False},
                            ],
                            'explain': 'The PR is the interface of teamwork; practising it solo builds the muscle memory teams expect.',
                        },
                    ],
                },
                {
                    'title': 'Chapter 10 Quiz',
                    'slug': 'project-quiz',
                    'objective': 'Confirm the project workflow decisions.',
                    'duration': 3,
                    'body': """# Chapter 10 quiz

Three scenario checks before you build.""",
                    'exercises': [
                        {
                            'slug': 'q10-push-before-pr',
                            'title': 'PR preconditions',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'GitHub can only open a PR from your branch after you have…',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'pushed that branch to the repository hosting it', 'is_correct': True},
                                {'id': 'b', 'text': 'deleted main', 'is_correct': False},
                                {'id': 'c', 'text': 'tagged a release', 'is_correct': False},
                                {'id': 'd', 'text': 'closed every issue', 'is_correct': False},
                            ],
                            'explain': 'A PR compares two branches that must exist on GitHub; local-only branches are invisible there.',
                        },
                        {
                            'slug': 'q10-reflection-quality',
                            'title': 'Reflection that scores',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which reflection sentence earns the "explain two decisions" credit?',
                            'xp_reward': 30,
                            'choices': [
                                {'id': 'a', 'text': 'I used Git and GitHub for the project.', 'is_correct': False},
                                {'id': 'b', 'text': 'I kept branches short because merges were easier, and added a licence since I want others to reuse the notes.', 'is_correct': True},
                                {'id': 'c', 'text': 'The project was difficult but I finished it.', 'is_correct': False},
                                {'id': 'd', 'text': 'git push uploads commits.', 'is_correct': False},
                            ],
                            'explain': 'Decision + reason, twice. Generic statements or dictionary definitions show no reflection.',
                        },
                        {
                            'slug': 'q10-extension-release',
                            'title': 'Extension: tag then release',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'For the release extension, first create the marker:\n'
                                '`git ____ -a v1.0 -m "first public release"`\n(One word.)'
                            ),
                            'xp_reward': 30,
                            'solution_code': 'tag',
                            'explain': 'git tag -a creates an annotated tag; push it, then build the GitHub Release on top.',
                        },
                    ],
                },
            ],
        },
    ],
    'assessment': [
        # 24 questions spanning all ten chapters; graded for certification.
        {'slug': 'fa-01-vcs-purpose', 'title': 'Purpose of version control', 'exercise_type': 'multiple_choice',
         'instructions': 'A version control system exists primarily to…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'record file history with authors and messages so any version can be restored', 'is_correct': True},
             {'id': 'b', 'text': 'compile programs faster', 'is_correct': False},
             {'id': 'c', 'text': 'replace the need for backups entirely', 'is_correct': False},
             {'id': 'd', 'text': 'encrypt source files', 'is_correct': False},
         ],
         'explain': 'History + attribution + restore is the definition; security/compilation are unrelated services.'},
        {'slug': 'fa-02-git-not-github', 'title': 'Git vs GitHub', 'exercise_type': 'multiple_choice',
         'instructions': 'Which is true?', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'Git needs GitHub to commit', 'is_correct': False},
             {'id': 'b', 'text': 'GitHub is required before git init', 'is_correct': False},
             {'id': 'c', 'text': 'Git works fully offline; GitHub is an optional host for sharing', 'is_correct': True},
             {'id': 'd', 'text': 'Git and GitHub are the same product', 'is_correct': False},
         ],
         'explain': 'Commits are local operations; GitHub only participates when pushing/fetching.'},
        {'slug': 'fa-03-config-global', 'title': 'Global configuration', 'exercise_type': 'fill_blank',
         'instructions': 'Complete: set your commit name for all repos — `git config ________ user.name "Your Name``. Write only the missing flag.', 'xp_reward': 10, 'is_final_assessment': True,
         'solution_code': '--global',
         'explain': '--global writes ~/.gitconfig; per-repo config omits the flag.'},
        {'slug': 'fa-04-clone-includes', 'title': 'What cloning copies', 'exercise_type': 'multiple_select',
         'instructions': 'Select ALL things a full `git clone` brings to your machine.', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'the latest files', 'is_correct': True},
             {'id': 'b', 'text': 'the entire commit history', 'is_correct': True},
             {'id': 'c', 'text': 'the origin remote configuration', 'is_correct': True},
             {'id': 'd', 'text': 'installed program dependencies', 'is_correct': False},
         ],
         'explain': 'Cloning is copying the repository, not running setup scripts.'},
        {'slug': 'fa-05-three-areas', 'title': 'Name the middle area', 'exercise_type': 'fill_blank',
         'instructions': 'Files flow: working directory → ____________ → repository. Write the missing area\u2019s common name (one word).', 'xp_reward': 10, 'is_final_assessment': True,
         'solution_code': 'staging',
         'explain': 'Also called the index; git add places changes there.'},
        {'slug': 'fa-06-add-effect', 'title': 'Effect of git add', 'exercise_type': 'multiple_choice',
         'instructions': 'Running `git add file.txt`…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'creates a commit', 'is_correct': False},
             {'id': 'b', 'text': 'copies the file\u2019s current content into the staging area', 'is_correct': True},
             {'id': 'c', 'text': 'uploads the file to GitHub', 'is_correct': False},
             {'id': 'd', 'text': 'locks the file from further edits', 'is_correct': False},
         ],
         'explain': 'add proposes; commit records; push shares. Three different verbs.'},
        {'slug': 'fa-07-commit-scope', 'title': 'What commits capture', 'exercise_type': 'multiple_choice',
         'instructions': 'git commit records…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'everything in the working directory', 'is_correct': False},
             {'id': 'b', 'text': 'exactly the staged snapshot', 'is_correct': True},
             {'id': 'c', 'text': 'only the newest file', 'is_correct': False},
             {'id': 'd', 'text': 'whatever GitHub requests', 'is_correct': False},
         ],
         'explain': 'Commit freezes the staging area — unstaged edits wait for the next one.'},
        {'slug': 'fa-08-imperative', 'title': 'Message style', 'exercise_type': 'multiple_choice',
         'instructions': 'Which subject line is in correct imperative style?', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'Adding the search bar', 'is_correct': False},
             {'id': 'b', 'text': 'Added search bar', 'is_correct': False},
             {'id': 'c', 'text': 'Add search bar to header', 'is_correct': True},
             {'id': 'd', 'text': 'Search bar updates', 'is_correct': False},
         ],
         'explain': '"If applied, this commit will Add search bar…" — the standard test.'},
        {'slug': 'fa-09-branch-pointer', 'title': 'Branch essence', 'exercise_type': 'multiple_choice',
         'instructions': 'A Git branch is…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'a copy of all project files', 'is_correct': False},
             {'id': 'b', 'text': 'a movable pointer to a commit', 'is_correct': True},
             {'id': 'c', 'text': 'a server-side account', 'is_correct': False},
             {'id': 'd', 'text': 'a type of merge', 'is_correct': False},
         ],
         'explain': 'That is why branches are cheap, instant and numerous in real work.'},
        {'slug': 'fa-10-switch-c', 'title': 'Create + switch', 'exercise_type': 'fill_blank',
         'instructions': '`git switch __ experiment` creates branch experiment and moves you onto it. Write the flag only.', 'xp_reward': 10, 'is_final_assessment': True,
         'solution_code': '-c',
         'explain': 'git switch -c = create and checkout.'},
        {'slug': 'fa-11-merge-direction', 'title': 'Merge target', 'exercise_type': 'multiple_choice',
         'instructions': 'On main, `git merge feature`…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'copies main into feature', 'is_correct': False},
             {'id': 'b', 'text': 'integrates feature into main', 'is_correct': True},
             {'id': 'c', 'text': 'renames feature to main', 'is_correct': False},
             {'id': 'd', 'text': 'only works after pushing', 'is_correct': False},
         ],
         'explain': 'merge pulls the named branch into the branch you stand on.'},
        {'slug': 'fa-12-conflict-rule', 'title': 'Conflict condition', 'exercise_type': 'multiple_choice',
         'instructions': 'Git asks for conflict resolution when…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'branches touched different files', 'is_correct': False},
             {'id': 'b', 'text': 'the same lines diverged on both sides', 'is_correct': True},
             {'id': 'c', 'text': 'the network dropped', 'is_correct': False},
             {'id': 'd', 'text': 'more than two branches exist', 'is_correct': False},
         ],
         'explain': 'Line-level overlap forces a human choice.'},
        {'slug': 'fa-13-marker-split', 'title': 'HEAD side of markers', 'exercise_type': 'multiple_choice',
         'instructions': 'Between `<<<<<<< HEAD` and `=======` you find…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'your current branch\u2019s version', 'is_correct': True},
             {'id': 'b', 'text': 'the incoming branch\u2019s version', 'is_correct': False},
             {'id': 'c', 'text': 'the merge-base original', 'is_correct': False},
             {'id': 'd', 'text': 'auto-generated tests', 'is_correct': False},
         ],
         'explain': 'HEAD = where you are; >>>>>>> side = what is coming in.'},
        {'slug': 'fa-14-finish-merge', 'title': 'Completing resolution', 'exercise_type': 'multiple_choice',
         'instructions': 'After editing a conflicted file to the final text you…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'git add then git commit', 'is_correct': True},
             {'id': 'b', 'text': 'git push only', 'is_correct': False},
             {'id': 'c', 'text': 'delete .git', 'is_correct': False},
             {'id': 'd', 'text': 'git merge --abort', 'is_correct': False},
         ],
         'explain': 'Staging = resolved flag; the commit writes the merge result.'},
        {'slug': 'fa-15-fetch-effect', 'title': 'fetch versus pull', 'exercise_type': 'multiple_choice',
         'instructions': 'Unlike git pull, git fetch…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'uploads nothing and merges nothing — it only updates remote-tracking snapshots', 'is_correct': True},
             {'id': 'b', 'text': 'deletes local commits', 'is_correct': False},
             {'id': 'c', 'text': 'requires admin rights', 'is_correct': False},
             {'id': 'd', 'text': 'only works with SSH URLs', 'is_correct': False},
         ],
         'explain': 'fetch = preview; pull = preview + merge.'},
        {'slug': 'fa-16-rejected-push', 'title': 'Push rejected', 'exercise_type': 'multiple_choice',
         'instructions': 'Push rejected: "remote contains work you do not have". Correct response…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'git push --force', 'is_correct': False},
             {'id': 'b', 'text': 'pull/merge the remote work, resolve, then push', 'is_correct': True},
             {'id': 'c', 'text': 're-clone', 'is_correct': False},
             {'id': 'd', 'text': 'rename the branch', 'is_correct': False},
         ],
         'explain': 'Integrate before you share; forcing destroys the teammate\u2019s commits on the remote.'},
        {'slug': 'fa-17-fork-workflow', 'title': 'Fork and PR order', 'exercise_type': 'multiple_select',
         'instructions': 'Select ALL steps in the correct fork-and-PR contribution flow.', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'Fork the project on GitHub', 'is_correct': True},
             {'id': 'b', 'text': 'Clone your fork, branch, commit, push to your fork', 'is_correct': True},
             {'id': 'c', 'text': 'Open a PR from your fork branch to the original repo', 'is_correct': True},
             {'id': 'd', 'text': 'Push directly to the original main branch', 'is_correct': False},
         ],
         'explain': 'Without write access, direct pushes to the original are impossible — that is why forks exist.'},
        {'slug': 'fa-18-gitignore-scope', 'title': 'gitignore limits', 'exercise_type': 'multiple_choice',
         'instructions': 'A file already committed, later added to .gitignore, will…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'automatically vanish from history', 'is_correct': False},
             {'id': 'b', 'text': 'remain tracked until git rm --cached removes it', 'is_correct': True},
             {'id': 'c', 'text': 'be deleted from disk', 'is_correct': False},
             {'id': 'd', 'text': 'cause every later commit to fail', 'is_correct': False},
         ],
         'explain': 'Ignore rules only cover untracked files.'},
        {'slug': 'fa-19-log-graph-fill', 'title': 'Tree view command', 'exercise_type': 'fill_blank',
         'instructions': 'Complete: `git log --oneline --______ --all` draws the branch graph. Write the flag word only.', 'xp_reward': 10, 'is_final_assessment': True,
         'solution_code': 'graph',
         'explain': 'git log --oneline --graph --all is the topology view.'},
        {'slug': 'fa-20-restore-danger', 'title': 'restore without flags', 'exercise_type': 'multiple_choice',
         'instructions': '`git restore app.py` with uncommitted edits present…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'discards those edits permanently (working tree returns to HEAD)', 'is_correct': True},
             {'id': 'b', 'text': 'unsets the upstream', 'is_correct': False},
             {'id': 'c', 'text': 'deletes the file from disk entirely', 'is_correct': False},
             {'id': 'd', 'text': 'moves the edits to staging', 'is_correct': False},
         ],
         'explain': 'Plain restore = file-level discard. When unsure, stash first.'},
        {'slug': 'fa-21-revert-versus-reset', 'title': 'Undo tool choice', 'exercise_type': 'multiple_choice',
         'instructions': 'A pushed, shared commit must be undone. Choose the tool and reason.', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'reset --hard, because it is thorough', 'is_correct': False},
             {'id': 'b', 'text': 'revert, because forward-fixing avoids rewriting history others have pulled', 'is_correct': True},
             {'id': 'c', 'text': 'restore, because the commit is one file', 'is_correct': False},
             {'id': 'd', 'text': 'stash, because it parks work', 'is_correct': False},
         ],
         'explain': 'Public history: add a cancelling commit. Private history: reset is fine.'},
        {'slug': 'fa-22-reflog', 'title': 'Recovery after hard reset', 'exercise_type': 'multiple_choice',
         'instructions': 'Where do you look first to recover a commit destroyed minutes ago by reset --hard?', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'git reflog', 'is_correct': True},
             {'id': 'b', 'text': 'git status', 'is_correct': False},
             {'id': 'c', 'text': '.gitignore', 'is_correct': False},
             {'id': 'd', 'text': 'GitHub notifications', 'is_correct': False},
         ],
         'explain': 'reflog keeps HEAD\u2019s recent positions, including now-unreferenced commits.'},
        {'slug': 'fa-23-stash-pop', 'title': 'pop versus apply', 'exercise_type': 'multiple_choice',
         'instructions': 'After `git stash pop`, the stash entry is…', 'xp_reward': 10, 'is_final_assessment': True,
         'choices': [
             {'id': 'a', 'text': 'kept forever', 'is_correct': False},
             {'id': 'b', 'text': 'removed from the stash list (applied changes stay)', 'is_correct': True},
             {'id': 'c', 'text': 'pushed to origin', 'is_correct': False},
             {'id': 'd', 'text': 'converted to a branch', 'is_correct': False},
         ],
         'explain': 'pop = apply + drop. (On conflict, pop keeps the stash — but normally it drops.)'},
        {'slug': 'fa-24-conventional-prefix', 'title': 'Conventional commit', 'exercise_type': 'fill_blank',
         'instructions': 'Complete the conventional prefix for a commit that adds a new user feature: `____(auth): add password reset` — write the type word only.', 'xp_reward': 10, 'is_final_assessment': True,
         'solution_code': 'feat',
         'explain': 'feat = new user-facing capability; fix = correcting behaviour; chore = maintenance.'},
    ],
}
