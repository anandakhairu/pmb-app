# Code & File Ownership Matrix

To prevent merge conflicts, race conditions, and accidental overwrites in shared-workspace execution environments, this matrix defines strict, exclusive file write ownership across roles.

---

## 1. Exclusive Ownership Table

| Role / Subsystem | Dedicated Ownership Path | Primary File Types | Modifiable Shared Files? |
| :--- | :--- | :--- | :---: |
| **Engineering Lead** | Root configurations, release docs | `package.json`, `.gitignore`, `jsconfig.json`, `next.config.mjs` | **Sole Authority** |
| **Backend Engineer** | Server logic, database, workers | `src/app/api/**`, `src/lib/server/**`, `src/workers/**`, `prisma/**` | Only via Lead Approval |
| **Frontend Engineer**| Client UI pages & components | `src/app/(public)/**`, `src/app/(mahasiswa)/**`, `src/app/(admin)/**`, `src/components/**` | No |
| **AI Engineer** | Document AI, OCR, RAG pipelines | `src/lib/ai/**`, `src/services/ai/**`, `python/**` | No |
| **QA Automation** | Automated test suites & mocks | `test-e2e.mjs`, `tests/**`, `cypress/**` | No |
| **Reviewer / Security**| Read-only audit logs & dossiers | `docs/audits/**`, `docs/reviews/**` | No (Read-Only) |

---

## 2. Shared File Governance Rules

### A. Root Configuration (`package.json`, `package-lock.json`, `.env.example`)
* **Rule:** Implementation agents (`Frontend`, `Backend`, `AI`) must **never** run `npm install <package>` directly without Lead approval.
* **Protocol:** The agent submits a dependency request specifying package name, version, and rationale. The Engineering Lead verifies necessity against the Ponytail Ladder before installation.

### B. Database Schema & Migrations (`prisma/schema.prisma`, `prisma/migrations/**`)
* **Rule:** Only the **Backend Engineer** may draft schema changes; only the **Engineering Lead** may execute `npx prisma migrate dev` or `deploy`.
* **Protocol:** Schema modifications require an approved ERD update in `docs/ERD.md` before migration generation.

### C. Shared Primitives (`src/components/ui/**`, `src/lib/utils.js`)
* **Rule:** Primitives are treated as shared design system infrastructure.
* **Protocol:** Owned collaboratively by Frontend and UI/UX Engineers. New primitives must follow Shadcn conventions and must not contain domain-specific business logic.

---

## 3. Conflict Prevention in Shared Workspaces
1. **Zero Overlapping Write Spawns:** In any multi-agent batch call, no two agents may be assigned overlapping write paths.
2. **Sequential Handoffs:** If the Frontend Engineer requires a new API endpoint, the Backend Engineer finishes and verifies the endpoint first before the Frontend Engineer is dispatched.
3. **Pre-Push Validation:** Every agent must run verification checks on their owned path before yielding back to the Lead.
