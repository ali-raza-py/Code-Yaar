# Code-Yaar Product Requirements Document

## 1. Document Information

| Field | Value |
|---|---|
| Product name | Code-Yaar |
| Document title | Product Requirements Document |
| Version | 0.1 |
| Status | Draft |
| Last updated | 2026-09-10 |
| Owner | TBD |
| Contributors | TBD |
| Related documents | [ARCHITECTURE.md](ARCHITECTURE.md), [MVP-ROADMAP.md](MVP-ROADMAP.md), [CURRENT-PROGRESS.md](CURRENT-PROGRESS.md), [AI-CODING-RULES.md](AI-CODING-RULES.md) |

Status definitions used throughout this document are defined in [CURRENT-PROGRESS.md](CURRENT-PROGRESS.md).

## 2. Product Overview

Code-Yaar is being developed as a student-focused technology and software engineering platform/community intended to help learners move beyond passive tutorial consumption toward practical technical skills, real projects, and demonstrable outcomes.

The product vision is to help aspiring developers **Learn, Build, and Prove**. The intended audience is students and beginner-to-intermediate technology learners interested in programming, software engineering, computer science, AI/ML, web development, problem solving, projects, and career-oriented learning.

This document describes product direction and proposed requirements. The repository currently contains no application implementation, so these capabilities are not presented as available today.

## 3. Problem

Many learners can consume programming content without developing strong practical ability. The intended problem space includes tutorial dependence, limited project practice, weak problem-solving confidence, unclear next steps, fragmented resources, and difficulty creating credible evidence of technical ability.

These are product hypotheses and problem areas supplied for exploration, not validated market findings.

## 4. Target Users

The following personas are **Proposed** and require validation:

- **Beginner programmer:** needs a clear first path, guided practice, and a manageable first project.
- **Student developer:** wants structured progression and evidence of practical work alongside formal study.
- **Intermediate learner:** needs increasingly difficult projects, feedback, and help identifying skill gaps.
- **Project-focused learner:** wants to turn learning into finished, explainable work.

Final age range, geography, accessibility needs, purchasing authority, and other segmentation are TBD.

## 5. User Needs

Proposed user needs include:

- Clear direction about what to learn next.
- Practical exercises and projects.
- Feedback that improves technical reasoning.
- Visibility into progress and capability.
- A way to create evidence of work.
- High-quality technical guidance without removing independent problem solving.
- A coherent path from learning to building.

## 6. Value Proposition

**Code-Yaar helps aspiring developers learn practical software skills, build real projects, and prove what they can actually do.**

The central product loop is:

**Learn → Build → Prove**

The statement is a working positioning statement, not evidence that each capability is currently implemented.

## 7. Product Goals

### MVP goals

The MVP should, once defined and built:

- Give a learner a coherent starting path.
- Connect learning content or guidance to practical practice.
- Support at least one meaningful build activity.
- Make progress or work visible to the learner.
- Produce evidence that can be reviewed or revisited.
- Allow the core Learn → Build → Prove loop to be evaluated with real users.

Exact MVP scope, content model, platform scope, and validation method are TBD.

### Long-term goals

Proposed long-term goals are to support progressive technical development through projects, challenges, feedback, community, collaboration, portfolios, and carefully scoped AI assistance.

## 8. Non-Goals

The MVP is not intended to be, unless later approved:

- A complete university replacement.
- A general-purpose social network.
- A massive course marketplace.
- A recruitment platform.
- A full IDE.
- An everything-in-one AI platform.

## 9. Core User Journey

| Journey step | Intended direction | Current status |
|---|---|---|
| Discover | Find Code-Yaar and understand its purpose | Not Implemented |
| Understand what to learn | Select a useful next step | Proposed |
| Learn | Study a relevant concept | Proposed |
| Practice | Apply the concept in exercises or challenges | Proposed |
| Build | Complete a meaningful project | Proposed |
| Receive feedback | Review work and identify improvements | Proposed |
| Improve | Iterate and increase difficulty | Proposed |
| Prove progress | Preserve evidence of capability | Proposed |

## 10. Functional Requirements

Priorities: P0 = essential, P1 = important, P2 = later. Requirements below are proposed product requirements; none are implemented in the current repository.

### FR-001: Learner entry point

- **Requirement:** Provide a clear entry point for the intended learner.
- **Description:** A learner can understand Code-Yaar's purpose and begin an appropriate journey.
- **Priority:** P0
- **Status:** Proposed
- **Acceptance criteria:** A first-time learner can identify the product purpose and a next action through a validated interface.

### FR-002: Learning direction

- **Requirement:** Help a learner identify what to learn next.
- **Description:** Present a coherent, appropriately scoped learning direction.
- **Priority:** P0
- **Status:** Proposed
- **Acceptance criteria:** A learner can select or receive a next learning step and understand why it is relevant.

### FR-003: Practical practice

- **Requirement:** Connect learning to hands-on practice.
- **Description:** Provide exercises, challenges, or equivalent practical activities.
- **Priority:** P0
- **Status:** Proposed
- **Acceptance criteria:** A learner can complete a practice activity and see what completion means.

### FR-004: Project building

- **Requirement:** Support meaningful project work.
- **Description:** Give learners a path from concepts to a project-sized outcome.
- **Priority:** P0
- **Status:** Proposed
- **Acceptance criteria:** A learner can start, work on, and finish a defined project outcome.

### FR-005: Progress evidence

- **Requirement:** Preserve evidence of progress or completed work.
- **Description:** Make work reviewable by the learner and, subject to product decisions, others.
- **Priority:** P0
- **Status:** Proposed
- **Acceptance criteria:** Completed work has an identifiable record and can be revisited.

### FR-006: Feedback

- **Requirement:** Help learners improve their work.
- **Description:** Provide useful feedback through an approved feedback mechanism.
- **Priority:** P1
- **Status:** Proposed
- **Acceptance criteria:** A learner can receive actionable feedback and identify a next improvement.

### FR-007: Progressive difficulty

- **Requirement:** Support progression from simpler to more challenging work.
- **Description:** Organize activities or projects into an understandable progression.
- **Priority:** P1
- **Status:** Proposed
- **Acceptance criteria:** The progression has explicit criteria or signals for moving forward.

### FR-008: AI learning assistance

- **Requirement:** Use AI, if included, to amplify learning.
- **Description:** AI should help learners reason, debug, and build without silently completing all work for them.
- **Priority:** P2
- **Status:** Proposed
- **Acceptance criteria:** AI behavior, boundaries, privacy model, and evaluation criteria are approved before implementation.

## 11. Non-Functional Requirements

No implementation-specific thresholds have been established. The following are requirements to define before release:

- **Performance:** TBD; journeys and acceptable response times need measurement targets.
- **Security:** TBD; threat model, secret handling, and security controls need definition.
- **Accessibility:** TBD; target standard and testing approach need definition.
- **Reliability:** TBD; availability and recovery expectations need definition.
- **Maintainability:** Proposed; preserve clear boundaries, focused changes, and documented decisions.
- **Scalability:** TBD; expected usage and scaling strategy are unknown.
- **Usability:** Proposed; validate that learners can progress without unnecessary confusion.
- **Privacy:** TBD; data collection, retention, sharing, and deletion rules are unknown.
- **Observability:** TBD; required logs, metrics, and tracing are unknown.

## 12. MVP Scope

### In MVP

Proposed only: a coherent learner entry point, a first learning direction, hands-on practice, one meaningful build workflow, and a basic way to preserve proof of work. The exact feature set is TBD.

### Post-MVP

Proposed: richer project catalogs, feedback workflows, progressive paths, collaboration, community, mentorship, and skill tracking.

### Explicitly excluded

A complete university replacement, general-purpose social network, large course marketplace, recruitment platform, full IDE, and broad AI platform are excluded from the initial scope unless explicitly reconsidered.

## 13. Future Scope

The following are **Proposed**, not commitments: personalized learning paths, project-based learning, challenges, skill tracking, portfolio and proof systems, community, mentorship, AI learning assistance, peer review, and carefully evaluated gamification.

## 14. Success Metrics

No product analytics or measurements exist in the repository. Candidate metrics are **Proposed** and require definitions, instrumentation, and privacy review:

- Learning completion.
- Project completion.
- Returning learners.
- Challenge completion.
- Proof-of-work creation.
- Progression between difficulty levels.
- Learner-reported usefulness.

No numerical targets are established.

## 15. Product Principles

These are confirmed product direction or proposed principles as indicated:

1. **Learn by doing** — Proposed.
2. **Build real things** — Proposed.
3. **Prove the skill** — Proposed.
4. **Avoid tutorial hell** — Proposed.
5. **Progressive difficulty** — Proposed.
6. **Practical over flashy** — Proposed.
7. **AI should amplify learning** — Proposed.
8. **Evidence over claims** — Proposed.

The central philosophy, **Learn → Build → Prove**, is confirmed product context; its implementation is not present in this repository.

## 16. Open Questions

| Question | Importance | Owner | Status |
|---|---|---|---|
| What is the exact MVP workflow? | High | TBD | TBD |
| Which target persona is primary? | High | TBD | TBD |
| What platform or platforms are in scope? | High | TBD | TBD |
| What is the content strategy? | High | TBD | TBD |
| What role should AI play? | High | TBD | TBD |
| What is the community scope? | Medium | TBD | TBD |
| What is the validation strategy? | High | TBD | TBD |
| Is monetization in scope, and which model? | Medium | TBD | TBD |
| What privacy, accessibility, and security standards apply? | High | TBD | TBD |
