# Engineering Team Charter — PMB Application (ADMITRA)

## 1. Mission & Vision
The PMB Application (ADMITRA) Engineering Organization delivers a modern, high-integrity, secure, and accessible admissions platform for prospective university students and administrative staff. Our core engineering priorities are **correctness**, **data integrity**, and **maintainability**, guided by the Ponytail philosophy (YAGNI, minimal complexity, zero AI slop).

---

## 2. Organization Structure & Governance

```
                    ┌─────────────────────────────────┐
                    │        ENGINEERING LEAD         │
                    │        (Main Session)           │
                    │  Architecture, Direction, Gates │
                    └────────────────┬────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
┌────────┴────────┐         ┌────────┴────────┐         ┌────────┴────────┐
│ PRODUCT ANALYST │         │    SOLUTIONS    │         │  AI SPECIALIST  │
│     (scout)     │         │ ARCHITECT(scout)│         │     (task)      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
┌────────┴────────┐         ┌────────┴────────┐         ┌────────┴────────┐
│ UI/UX ENGINEER  │         │FRONTEND ENGINEER│         │BACKEND ENGINEER │
│     (task)      │         │     (task)      │         │     (task)      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
┌────────┴────────┐         ┌────────┴────────┐         ┌────────┴────────┐
│   QA ENGINEER   │         │  CODE REVIEWER  │         │SECURITY REVIEWER│
│     (task)      │         │   (reviewer)    │         │(security-review)│
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

The **Engineering Lead** (main session) is the sole executive authority over:
- Task decomposition, dependency sequencing, and specialist delegation.
- Architectural boundary approvals, database migrations, and schema changes.
- Integration conflict resolution and release readiness gating.

---

## 3. Core Engineering Principles
1. **The Necessity Ladder (Ponytail / YAGNI):**
   * Does it need to exist? Skip speculative abstractions.
   * Is it already in the codebase? Reuse existing helpers (`formatTanggal`, `cn`, `Button`, `Badge`).
   * Does the standard library/native platform do it? Prefer native HTML/CSS/DB constraints before third-party packages.
   * Can it be one line? Keep it minimal.
2. **Three-Tier Validation Contract (Mandatory):**
   * *Tier 1 (Client):* HTML forms + Zod schemas for immediate user feedback.
   * *Tier 2 (Server):* Route Handlers / Server Actions re-verifying every request independently.
   * *Tier 3 (Database):* Relational PostgreSQL constraints (`NOT NULL`, `CHECK`, `UNIQUE`, `FOREIGN KEY`).
3. **Evidence-First Verification:**
   * No completion claim without actual execution output.
   * Automated end-to-end regression testing before merges.
