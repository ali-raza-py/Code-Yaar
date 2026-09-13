# Code-Yaar MVP Roadmap

This roadmap describes proposed work, not completed functionality. No dates are attached because none have been decided.

## Status Vocabulary

- **Implemented:** functionality exists in the codebase.
- **Verified:** functionality exists and has been meaningfully tested or confirmed.
- **In Progress:** development has started but is incomplete.
- **Planned:** the team has decided it should be built.
- **Proposed:** an idea under consideration and not committed.
- **Deferred:** previously considered or planned but intentionally postponed.
- **Not Implemented:** a known requirement exists, but no working implementation exists.
- **TBD:** the information or decision has not yet been determined.

## Phase 0 — Foundation

| Feature | Why it matters | Priority | Status | Dependencies | Completion criteria |
|---|---|---|---|---|---|
| Confirm MVP definition | Prevents scope drift and makes validation possible | P0 | Planned | Product-owner decision | Approved MVP scope and acceptance criteria are recorded |
| Establish repository foundation | Enables reproducible development | P0 | Not Implemented | Approved stack | Source layout, package setup, and basic checks exist |
| Define architecture decisions | Creates shared engineering direction | P0 | Planned | MVP definition and stack decision | Architecture records current choices and tradeoffs |
| Define design and content direction | Makes the first learner workflow coherent | P1 | Proposed | Primary persona and MVP scope | Approved content and interaction direction exists |
| Add automated verification | Makes future status claims evidence-based | P0 | Planned | Repository foundation | Relevant tests, linting, type checking, or build checks run |

## Phase 1 — MVP

| Feature | Why it matters | Priority | Status | Dependencies | Completion criteria |
|---|---|---|---|---|---|
| Learner entry point | Explains the product and starts the core loop | P0 | Proposed | MVP definition, frontend foundation | A learner can understand the purpose and begin |
| First learning direction | Addresses uncertainty about what to learn next | P0 | Proposed | Content strategy, primary persona | A learner can choose a relevant next step |
| Hands-on practice | Turns learning into action | P0 | Proposed | Learning direction and content | A learner can complete a practice activity |
| One meaningful build workflow | Tests the Build part of the product promise | P0 | Proposed | Practice model and project definition | A learner can complete a defined project outcome |
| Basic proof of work | Tests the Prove part of the product promise | P0 | Proposed | Build workflow and storage decision | Completed work is recorded and reviewable |
| MVP validation instrumentation | Enables evidence-based decisions | P1 | Proposed | Privacy decision and analytics requirements | Approved candidate metrics can be measured |

## Phase 2 — Validation

| Feature | Why it matters | Priority | Status | Dependencies | Completion criteria |
|---|---|---|---|---|---|
| Learner feedback workflow | Identifies whether guidance improves outcomes | P0 | Proposed | MVP usage and feedback design | Feedback is collected, reviewed, and translated into changes |
| Journey usability improvements | Removes obstacles found in real use | P0 | Proposed | Validation evidence | High-impact usability issues are addressed and retested |
| Content and difficulty iteration | Tests progression and relevance | P1 | Proposed | Learner feedback and completion data | Content changes are linked to observed evidence |
| Scope decision for community or mentorship | Avoids premature expansion | P1 | TBD | Validation results | Product owner records an explicit decision |

## Phase 3 — Expansion

| Feature | Why it matters | Priority | Status | Dependencies | Completion criteria |
|---|---|---|---|---|---|
| Additional project paths | Supports broader learner goals | P1 | Proposed | Validated MVP and content capacity | New paths solve demonstrated learner needs |
| Skill and progression tracking | Makes development visible over time | P1 | Proposed | Defined skill model and privacy rules | Progress signals are understandable and useful |
| Peer review or mentorship | Adds human feedback where it helps | P2 | Proposed | Community decision and moderation model | Feedback quality and safety can be evaluated |
| AI learning assistance | Can improve reasoning and debugging support | P2 | Proposed | AI role, privacy, and evaluation decisions | Assistance is bounded, tested, and learning-oriented |

## Phase 4 — Scale

Scale work is **Deferred** until adoption, reliability needs, data, and operational requirements justify it. Possible areas include deployment hardening, observability, performance work, moderation operations, and data lifecycle controls. No scale architecture or threshold is currently established.
