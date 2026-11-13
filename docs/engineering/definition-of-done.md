# Definition of Done (DoD) — PMB Application

A feature, bug fix, or refactoring task in the PMB Application is considered **DONE** only when all criteria in this checklist are verified with concrete evidence.

---

## 1. Traceability & Requirements
- [ ] Every user-facing change maps to an approved requirement in `PRD TIM 1.md` or an approved Architecture Decision Record (ADR).
- [ ] Non-goals and boundary constraints are explicitly respected (no speculative scope creep).

## 2. Code Quality & Ponytail Standard
- [ ] The solution follows the **Necessity Ladder**: simplest, most minimal working approach (YAGNI).
- [ ] Zero dead code, unused imports, or placeholder variables.
- [ ] Existing codebase helpers, design tokens, and components are reused rather than duplicated.
- [ ] Code is free of corporate AI slop, unnecessary abstractions, and speculative factories.

## 3. Three-Tier Validation Contract
- [ ] **Tier 1 (Client):** Input constraints (lengths, formats, required fields) validated in UI with clear error messaging.
- [ ] **Tier 2 (Server):** Independent validation in Server Action / Route Handler using Zod schemas (request rejected even if client bypassed).
- [ ] **Tier 3 (Database):** Underlying PostgreSQL constraints (`NOT NULL`, `CHECK`, `UNIQUE`, `FOREIGN KEY`) enforce schema integrity.

## 4. Verification & Testing Evidence
- [ ] `npm run build` completes successfully with zero compiler, syntax, or prerendering errors.
- [ ] Relevant automated tests in `test-e2e.mjs` execute and pass with 100% green status.
- [ ] Interactive UI components (forms, dialogs, viewers) render and behave as expected across desktop and mobile viewports.
- [ ] Background worker tasks (Web Push, email) handle error states gracefully without crashing the main application thread.

## 5. Security & Privacy
- [ ] No secrets, VAPID private keys, or database credentials exposed to client bundles or committed to Git.
- [ ] Access controls and role permissions (`ADMIN` vs `PENDAFTAR`) verified strictly on the server.
- [ ] File uploads validate MIME type, file size, and reject dangerous executable extensions.

## 6. Review & Release Gating
- [ ] Independent code review performed by `reviewer` or `ponytail-review` with all critical items addressed.
- [ ] Security audit completed by `security-reviewer` with clean verdict.
- [ ] All changes committed with clean Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`).
- [ ] Engineering Lead has approved the merged outcome.
