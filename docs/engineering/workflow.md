# Multi-Agent Engineering Workflow

This document specifies the operational lifecycle for feature development, bug fixes, and security hardening within the PMB Engineering Organization.

---

## 8-Phase Engineering Protocol

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   PHASE 1    │ ──> │   PHASE 2    │ ──> │   PHASE 3    │ ──> │   PHASE 4    │
│  Discovery   │     │ Requirements │     │ Architecture │     │Implementation│
│ (scout/sec)  │     │  (Analyst)   │     │  (Architect) │     │ (Dev Agents) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                       │
┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
│   PHASE 8    │ <── │   PHASE 7    │ <── │   PHASE 6    │ <───────────┘
│   Release    │     │ Review Gate  │     │   QA Suite   │
│  Readiness   │     │(Reviewer/Sec)│     │  (Automated) │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Phase 1: Discovery (Read-Only)
* **Agents:** `scout`, `security-reviewer`
* **Actions:** Inspect repository state, verify current database migrations, and map existing call graphs.
* **Gate:** No code modifications permitted. Findings delivered as structured reports.

### Phase 2: Requirements & Scope Definition
* **Agents:** Product Analyst (`scout`) + Engineering Lead
* **Actions:** Define explicit user stories, functional criteria, and out-of-scope non-goals. Trace every requirement to an observable outcome.
* **Gate:** Requirements signed off in the feature issue / task tracker.

### Phase 3: Architecture & Contract Definition
* **Agents:** Solution Architect (`scout`) + Engineering Lead
* **Actions:** Establish TypeScript/Zod API contracts, Prisma schema updates, and migration strategies before coding begins.
* **Gate:** Architectural Decision Record (ADR) approved.

### Phase 4: Parallel Implementation
* **Agents:** Frontend Engineer (`task`), Backend Engineer (`task`), AI Engineer (`task`)
* **Actions:**
  - Maximum 2 to 3 concurrent active write agents.
  - Strict disjoint file ownership enforced (zero overlapping write paths).
  - Continuous local checks via small, focused throwaway assertions.
* **Gate:** All assigned file modifications completed without regressions to shared files.

### Phase 5: Integration & Conflict Resolution
* **Agents:** Engineering Lead
* **Actions:** Merge feature streams, resolve import paths, and compile unified bundle (`npm run build`).
* **Gate:** Project builds cleanly with zero compiler or routing collision warnings.

### Phase 6: Automated QA Verification
* **Agents:** QA Automation Engineer (`task`)
* **Actions:** Execute automated end-to-end regression suites (`test-e2e.mjs`), API contract tests, and database constraints validation.
* **Gate:** 100% test pass rate across all active routes and endpoints.

### Phase 7: Independent Quality & Security Review
* **Agents:** Code Reviewer (`reviewer`), Security Reviewer (`security-reviewer`)
* **Actions:**
  - `reviewer` executes Ponytail review (flags dead code, unnecessary abstractions, redundant dependencies).
  - `security-reviewer` audits authentication boundaries, input sanitization, and secrets handling.
* **Gate:** All high/critical findings resolved; medium findings documented with explicit mitigation.

### Phase 8: Release Readiness & Documentation
* **Agents:** Engineering Lead
* **Actions:** Assemble operational changelog, verify documentation, tag Git commit, and push to target branch.
* **Gate:** Production deployment or pull request submitted.
