# Code-Yaar AI Coding Rules

These rules apply to future AI coding agents working on Code-Yaar.

## General

- Read the documentation before modifying code.
- Inspect the existing architecture before creating architecture.
- Do not invent APIs, environment variables, database schemas, integrations, or implementation status.
- Do not duplicate existing functionality.
- Prefer simple solutions and minimize unnecessary dependencies.
- Keep product requirements separate from implementation details.
- Treat working code and successful verification as stronger evidence than names, comments, or README claims.

## Product

- Respect the PRD and the approved MVP scope.
- Do not expand scope without an explicit rationale and decision.
- Do not convert Proposed, Planned, Deferred, or TBD items into implemented behavior without approval.
- Preserve the Learn → Build → Prove philosophy.
- Keep current progress separate from future plans.
- Do not claim users, revenue, partnerships, analytics, security guarantees, scalability, performance numbers, or production readiness without evidence.

## Engineering

- Understand the existing code before editing it.
- Reuse existing utilities and components where they fit.
- Keep changes focused and consistent with local conventions.
- Handle errors explicitly.
- Avoid hardcoded secrets and never commit credentials.
- Keep public APIs stable unless a change is required and documented.
- Update architecture and progress documentation when implementation changes the system.
- Prefer a small working implementation over unnecessary abstraction.
- Do not rewrite large portions of the application without justification.

## Verification

After making changes:

1. Run relevant tests.
2. Run linting if configured.
3. Run type checking if applicable.
4. Run the production or build command when practical.
5. Inspect resulting errors and warnings.
6. Verify the behavior affected by the change.
7. Do not claim success without reporting the checks that actually ran.

When a check cannot be run, state why and label the result accurately.

## AI Behavior

AI coding agents must:

- State assumptions when requirements or repository evidence are incomplete.
- Flag uncertainty and use **TBD** only when the information or decision itself has not been determined.
- Use **Not Implemented** or **Planned** for known but unbuilt functionality.
- Ask for clarification when a decision materially affects architecture, privacy, security, or product scope.
- Never silently fabricate missing requirements.
- Prefer the smallest change that can be verified.
- Preserve unrelated user changes.
- Inspect the final diff and relevant errors before finishing.

## Status Definitions

Use these definitions consistently:

- **Implemented:** The functionality exists in the codebase.
- **Verified:** The functionality exists and has been meaningfully tested or confirmed.
- **In Progress:** Development has started but the feature is incomplete.
- **Planned:** The team has decided that it should be built.
- **Proposed:** An idea under consideration; not yet committed.
- **Deferred:** Previously considered or planned but intentionally postponed.
- **Not Implemented:** A known requirement exists, but no working implementation exists.
- **TBD:** The information or decision itself has not yet been determined.
