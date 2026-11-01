"""Course 4 — Git and GitHub Fundamentals.

Version control concepts practised with real command-line workflows. Every
check is answer-graded server-side (multiple choice / output prediction /
fill in the blank); nothing pretends to execute git for the learner.
"""

COURSE = {
    'slug': 'git-github-foundations',
    'title': 'Git and GitHub Fundamentals',
    'subtitle': 'Track changes, branch safely and collaborate on GitHub.',
    'description': (
        'Git records every change you make to a project so you can inspect '
        'history, undo mistakes and work with others. This course covers the '
        'working directory, staging and commits, branching and merging, '
        'remotes and GitHub, and collaboration through pull requests.'
    ),
    'difficulty': 'beginner',
    'language': 'other',
    'prerequisites': 'Basic comfort with a terminal / command prompt.',
    'track': {
        'slug': 'developer-tools',
        'title': 'Developer Tools',
        'category': 'other',
        'description': 'The professional tooling every developer is expected to know.',
    },
    'objectives': [
        'Explain the three areas: working directory, staging area, repository.',
        'Initialise a repo and record commits with git add / git commit.',
        'Inspect and rewrite history with log, diff and revert.',
        'Create branches, merge them and resolve simple conflicts.',
        'Connect to a remote and push/pull on GitHub.',
        'Collaborate with forks and pull requests.',
    ],
    'modules': [
        {
            'title': 'Version Control Basics',
            'slug': 'vc-basics',
            'description': 'Why Git exists and how it stores history.',
            'lessons': [
                {
                    'title': 'Snapshots, Not Diffs',
                    'slug': 'why-git',
                    'objective': 'Describe what a Git repository stores and why it helps.',
                    'duration': 8,
                    'body': (
                        '# Version control\n\n'
                        'Manually naming `project_v2_FINAL_reallyfinal.zip` collapses '
                        'past a week of work. A **version control system** stores every '
                        'version of every file, who changed it and why.\n\n'
                        'Git is **distributed**: each developer has the complete '
                        'history locally, so work continues offline and history is '
                        'survivable if a server dies.\n\n'
                        'Git stores a **snapshot** of the whole project per commit, not '
                        'a list of changes. Each commit points to its parent, forming a '
                        'chain of history.\n\n'
                        'The three areas:\n\n'
                        '1. **Working directory** — your files as you edit them.\n'
                        '2. **Staging area** — the snapshot you are preparing.\n'
                        '3. **Repository** (`.git/`) — committed history.\n\n'
                        '## Common mistakes\n'
                        'Thinking `git commit` saves everything you changed — it only '
                        'saves what you previously `git add`-ed to staging.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'distributed-meaning',
                            'title': 'Distributed history',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What does it mean that Git is a distributed system?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'History lives only on GitHub\'s servers', 'is_correct': False},
                                {'id': 'b', 'text': 'Every clone contains the complete project history', 'is_correct': True},
                                {'id': 'c', 'text': 'Files are split across many machines', 'is_correct': False},
                                {'id': 'd', 'text': 'Commits run in parallel on many CPUs', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'staging-purpose',
                            'title': 'The staging area',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What is the staging area for?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'Selecting which changes go into the next commit', 'is_correct': True},
                                {'id': 'b', 'text': 'Backing up files to the cloud', 'is_correct': False},
                                {'id': 'c', 'text': 'Running tests', 'is_correct': False},
                                {'id': 'd', 'text': 'Storing deleted files forever', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Everyday Git',
            'slug': 'everyday-git',
            'description': 'init, status, add, commit, log and undoing.',
            'lessons': [
                {
                    'title': 'First Commits',
                    'slug': 'init-add-commit',
                    'objective': 'Start a repo and record the first commit.',
                    'duration': 12,
                    'body': (
                        '# Starting and recording\n\n'
                        '```bash\ngit init              # create .git in this folder\n'
                        'git status             # what changed?\ngit add README.md      # stage one file\n'
                        'git add .                # stage all changes\ngit commit -m "Add project readme"\n'
                        '```\n\n'
                        '- `git status` shows modified / staged / untracked files.\n'
                        '- A commit **message** describes *why* the change exists; write '
                        'it in the imperative mood ("Add cart", not "Added cart").\n\n'
                        'Set your identity once:\n\n'
                        '```bash\ngit config --global user.name "Your Name"\ngit config --global user.email "you@example.com"\n```\n\n'
                        '## Common mistakes\n'
                        'Committing with no staged changes: the message is required, but '
                        'Git refuses to create an empty commit.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'stage-command',
                            'title': 'Stage everything',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that stages ALL current changes:\n\n'
                                '```bash\n______ .\n```'
                            ),
                            'starter_code': '',
                            'solution_code': 'git add',
                            'explain': 'git add . stages every modified and new file in the tree.',
                            'xp_reward': 50,
                        },
                        {
                            'slug': 'status-output',
                            'title': 'Which command answers "what changed?"',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command shows modified, staged and untracked files?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git log', 'is_correct': False},
                                {'id': 'b', 'text': 'git status', 'is_correct': True},
                                {'id': 'c', 'text': 'git diff --all', 'is_correct': False},
                                {'id': 'd', 'text': 'git watch', 'is_correct': False},
                            ],
                        },
                    ],
                },
                {
                    'title': 'History and Undo',
                    'slug': 'history-undo',
                    'objective': 'Read history and reverse mistakes safely.',
                    'duration': 12,
                    'body': (
                        '# Reading history\n\n'
                        '```bash\ngit log --oneline     # compact list of commits\n'
                        'git diff                 # unstaged changes vs last commit\n```\n\n'
                        '# Undoing\n\n'
                        '```bash\ngit restore file.txt          # discard working-dir changes\n'
                        'git restore --staged file.txt     # unstage, keep my edits\n'
                        'git revert <commit>               # NEW commit that undoes that one\n'
                        '```\n\n'
                        '`revert` is safe on shared branches because it adds a new '
                        'commit instead of rewriting history. Commands that rewrite '
                        'history (like `reset --hard`) can destroy work you have not '
                        'backed up elsewhere.\n\n'
                        '## Common mistakes\n'
                        'Running `git reset --hard` on a shared branch — collaborators\' '
                        'histories then diverge. Prefer `git revert`.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'safe-undo',
                            'title': 'Safe undo on a shared branch',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command undoes a commit by creating a new undo-commit?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'git reset --hard', 'is_correct': False},
                                {'id': 'b', 'text': 'git revert', 'is_correct': True},
                                {'id': 'c', 'text': 'git rm', 'is_correct': False},
                                {'id': 'd', 'text': 'git stash drop', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'oneline-flag',
                            'title': 'Compact log flag',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which flag makes git log print one line per commit?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': '--short', 'is_correct': False},
                                {'id': 'b', 'text': '--brief', 'is_correct': False},
                                {'id': 'c', 'text': '--oneline', 'is_correct': True},
                                {'id': 'd', 'text': '-1', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'Branching and Merging',
            'slug': 'branching',
            'description': 'Parallel work, merges and conflicts.',
            'lessons': [
                {
                    'title': 'Branches, Merges and Conflicts',
                    'slug': 'merge-conflicts',
                    'objective': 'Create a branch, merge it back and resolve a conflict.',
                    'duration': 14,
                    'body': (
                        '# Branches\n\n'
                        'A **branch** is an movable pointer to a commit. Work on a '
                        'feature without disturbing `main`:\n\n'
                        '```bash\ngit switch -c login-feature   # create + move to branch\n'
                        'git switch main                # go back\n'
                        'git merge login-feature        # fold the feature into main\n'
                        '```\n\n'
                        '# Conflicts\n\n'
                        'When two branches edit the same lines, Git cannot guess — it '
                        'marks the file:\n\n'
                        '```\n<<<<<<< HEAD\n    greet("world")\n=======\n    greet("yaar")\n>>>>>>> login-feature\n```\n\n'
                        'Edit the file to the version you want (removing the markers), '
                        '`git add` it, then `git commit` to finish the merge.\n\n'
                        '## Common mistakes\n'
                        'Committing while `<<<<<<<` markers are still in the file — '
                        'always search for them before finishing a conflict.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'create-branch-cmd',
                            'title': 'Create and switch',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that creates a new branch called '
                                '``dark-mode`` and moves you onto it:\n\n'
                                '```bash\ngit switch -c ______\n```'
                            ),
                            'starter_code': 'git switch -c ',
                            'solution_code': 'git switch -c dark-mode',
                            'explain': '-c is short for --create; the name follows.',
                            'xp_reward': 50,
                        },
                        {
                            'slug': 'conflict-marker',
                            'title': 'Meaning of <<<<<<<',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'What do lines like <<<<<<< HEAD ======= in a file indicate?',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'Corrupted repository', 'is_correct': False},
                                {'id': 'b', 'text': 'An unresolved merge conflict', 'is_correct': True},
                                {'id': 'c', 'text': 'A TODO comment style', 'is_correct': False},
                                {'id': 'd', 'text': 'The end of a commit message', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'title': 'GitHub and Collaboration',
            'slug': 'github',
            'description': 'Remotes, push/pull, forks and pull requests.',
            'lessons': [
                {
                    'title': 'Remotes: clone, push, pull',
                    'slug': 'remotes',
                    'objective': 'Sync a local repository with a GitHub remote.',
                    'duration': 12,
                    'body': (
                        '# Remotes\n\n'
                        'A **remote** is a version of your repo hosted elsewhere. GitHub '
                        'hosted repos speak the Git protocol.\n\n'
                        '```bash\ngit clone https://github.com/you/repo.git   # download + init\n'
                        'git remote add origin https://github.com/you/repo.git\n'
                        'git push -u origin main      # upload commits, set upstream\n'
                        'git pull                     # fetch + merge others\' commits\n'
                        '```\n\n'
                        '- `push` uploads YOUR commits.\n'
                        '- `pull` downloads and integrates OTHERS\' commits.\n'
                        '- `origin` is the conventional name for the main remote.\n\n'
                        'Push before you close your laptop; pull before you start.\n\n'
                        '## Common mistakes\n'
                        'A rejected push means the remote has commits you lack — '
                        '`git pull` (resolve anything), then push again.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'download-first-repo',
                            'title': 'Getting a hosted repo locally',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Which command creates a complete local copy of a GitHub repository?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'git pull', 'is_correct': False},
                                {'id': 'b', 'text': 'git fetch origin', 'is_correct': False},
                                {'id': 'c', 'text': 'git clone <url>', 'is_correct': True},
                                {'id': 'd', 'text': 'git remote add', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'push-vs-pull',
                            'title': 'Upload commits',
                            'exercise_type': 'fill_blank',
                            'instructions': (
                                'Complete the command that uploads your local commits on '
                                'the current branch to the remote:\n\n'
                                '```bash\ngit ______ origin main\n```'
                            ),
                            'starter_code': 'git ',
                            'solution_code': 'git push origin main',
                            'explain': 'git push uploads commits; pull downloads them.',
                            'xp_reward': 50,
                        },
                    ],
                },
                {
                    'title': 'Forks and Pull Requests',
                    'slug': 'pull-requests',
                    'objective': 'Propose changes to someone else\'s project.',
                    'duration': 10,
                    'body': (
                        '# The open-source workflow\n\n'
                        '1. **Fork** — a server-side copy of the project into your account.\n'
                        '2. **Clone** your fork, create a branch, commit fixes.\n'
                        '3. **Push** the branch to your fork.\n'
                        '4. Open a **pull request (PR)** — a request for the maintainers '
                        'to review and merge your branch into their project.\n\n'
                        'Review happens in the PR: comments, suggested edits, CI checks. '
                        'Pushing new commits to the same branch updates the PR '
                        'automatically.\n\n'
                        'Teams also use PRs internally — merge to `main` only through '
                        'review keeps quality high.\n\n'
                        '## Common mistakes\n'
                        'Making many unrelated changes in one PR. Branch per feature, one '
                        'PR per logical change.\n'
                    ),
                    'exercises': [
                        {
                            'slug': 'pr-definition',
                            'title': 'What is a pull request?',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'A pull request is best described as…',
                            'xp_reward': 50,
                            'choices': [
                                {'id': 'a', 'text': 'A demand to download a repository', 'is_correct': False},
                                {'id': 'b', 'text': 'A proposed change for review and merging into a branch', 'is_correct': True},
                                {'id': 'c', 'text': 'A bug report', 'is_correct': False},
                                {'id': 'd', 'text': 'An automatic deploy', 'is_correct': False},
                            ],
                        },
                        {
                            'slug': 'fork-meaning',
                            'title': 'Fork location',
                            'exercise_type': 'multiple_choice',
                            'instructions': 'Where does forking create a copy of a repository?',
                            'xp_reward': 40,
                            'choices': [
                                {'id': 'a', 'text': 'In your own GitHub account', 'is_correct': True},
                                {'id': 'b', 'text': 'On your local disk only', 'is_correct': False},
                                {'id': 'c', 'text': 'Inside the original repo\'s branch list', 'is_correct': False},
                                {'id': 'd', 'text': 'In the staging area', 'is_correct': False},
                            ],
                        },
                    ],
                },
            ],
        },
    ],
    'assessment': [
        {
            'slug': 'git-final-init',
            'title': 'Start a repository',
            'exercise_type': 'multiple_choice',
            'instructions': 'Which command begins Git tracking in the current folder?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'git start', 'is_correct': False},
                {'id': 'b', 'text': 'git init', 'is_correct': True},
                {'id': 'c', 'text': 'git create', 'is_correct': False},
                {'id': 'd', 'text': 'git clone .', 'is_correct': False},
            ],
        },
        {
            'slug': 'git-final-commit',
            'title': 'What a commit stores',
            'exercise_type': 'multiple_choice',
            'instructions': 'A Git commit contains…',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'Only the lines that changed', 'is_correct': False},
                {'id': 'b', 'text': 'A snapshot of staged files plus metadata and a parent pointer', 'is_correct': True},
                {'id': 'c', 'text': 'A zip of your whole working directory, unstaged included', 'is_correct': False},
                {'id': 'd', 'text': 'Just a message', 'is_correct': False},
            ],
        },
        {
            'slug': 'git-final-restore',
            'title': 'Discard a working-directory edit',
            'exercise_type': 'fill_blank',
            'instructions': (
                'Complete the command that overwrites ``notes.txt`` with its last '
                'committed version:\n\n```bash\ngit ______ notes.txt\n```'
            ),
            'starter_code': 'git ',
            'solution_code': 'git restore notes.txt',
            'xp_reward': 20,
        },
        {
            'slug': 'git-final-pull',
            'title': 'Rejected push',
            'exercise_type': 'multiple_choice',
            'instructions': 'Your push is rejected because the remote moved ahead. What is the standard fix?',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'git push --force', 'is_correct': False},
                {'id': 'b', 'text': 'git pull, resolve differences, then push', 'is_correct': True},
                {'id': 'c', 'text': 'Delete the repo and re-clone', 'is_correct': False},
                {'id': 'd', 'text': 'Nothing; the branch is broken', 'is_correct': False},
            ],
        },
        {
            'slug': 'git-final-conflict',
            'title': 'Finishing a conflict resolution',
            'exercise_type': 'multiple_choice',
            'instructions': 'After editing a conflicted file and removing the markers, you must…',
            'xp_reward': 20,
            'choices': [
                {'id': 'a', 'text': 'git add the file, then git commit', 'is_correct': True},
                {'id': 'b', 'text': 'git init again', 'is_correct': False},
                {'id': 'c', 'text': 'Delete the file', 'is_correct': False},
                {'id': 'd', 'text': 'Restart the computer', 'is_correct': False},
            ],
        },
    ],
}
