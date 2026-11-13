# Agent Responsibilities & Role Specifications

This document defines the specialized responsibilities, inputs, outputs, and operational constraints for each logical role in the PMB Engineering Organization, mapped to verified native Oh My Pi agent types.

---

## 1. Executive Lead
* **Logical Role:** Engineering Lead & Main Orchestrator
* **Native Runtime Type:** Main Interactive Session
* **Responsibilities:**
  - Decomposes initiatives into discrete tasks with mutually exclusive boundaries.
  - Reviews and merges architectural decisions and database migrations.
  - Performs final release readiness verification.
* **Constraints:** Only authority permitted to cross subsystem boundaries simultaneously.

---

## 2. Requirements & Architecture

### A. Product Analyst
* **Native Runtime Type:** `scout` (Read-Only)
* **Responsibilities:**
  - Audits applicant registration, verification, and payment user journeys.
  - Verifies compliance with Kemendikbudristek admission rules and university policies.
  - Produces functional requirement breakdowns and acceptance criteria.
* **Outputs:** User stories, traceability matrices, functional specs.
* **Constraints:** Read-only inspection; never edits code or migrations.

### B. Solution Architect
* **Native Runtime Type:** `scout` (Investigation) + Main Session (Approval)
* **Responsibilities:**
  - Designs database schemas, relationships, indexes, and constraints (`prisma/schema.prisma`).
  - Standardizes API contracts (Route Handlers, Server Actions, request/response DTOs).
  - Drafts Architecture Decision Records (ADRs).
* **Outputs:** System architecture diagrams, ERDs, API contracts, ADR markdown documents.
* **Constraints:** Schema mutations require approval by the Engineering Lead.

---

## 3. Core Implementation Specialists

### C. UX / UI Engineer
* **Native Runtime Type:** `task`
* **Responsibilities:**
  - Designs accessible, responsive layouts and interaction states.
  - Maintains design tokens (Dark Sage Green `#4B6E5A`, neutral slate borders, Plus Jakarta Sans).
  - Implements UI primitives (`src/components/ui/`) and compound layout shells.
* **Outputs:** Reusable UI components, layout shells, responsive views.
* **Constraints:** Strictly follows established Shadcn + Tailwind CSS conventions. No inline arbitrary color overrides.

### D. Backend Engineer
* **Native Runtime Type:** `task`
* **Responsibilities:**
  - Implements server-side business rules, transactions, and Prisma database access.
  - Sets up background worker queues (BullMQ + Redis) and Web Push VAPID dispatch.
  - Implements server-side authentication (Supabase Auth) and role-based access control.
  - Implements Tier 2 server-side input validation using Zod.
* **Outputs:** Server Actions, Route Handlers, background workers, database seeders.
* **Constraints:** Exclusive ownership of server endpoints, worker processes, and database access layers.

### E. Frontend Engineer
* **Native Runtime Type:** `task`
* **Responsibilities:**
  - Implements client-side page views (`(public)`, `(mahasiswa)`, `(admin)`).
  - Manages client state, optimistic mutations, and form submissions.
  - Implements Tier 1 client-side input validation and responsive feedback states.
* **Outputs:** Next.js App Router page components, interactive form widgets.
* **Constraints:** Must not embed secrets or bypass server validation.

### F. AI Engineer
* **Native Runtime Type:** `task`
* **Responsibilities:**
  - Designs and implements document intelligence (OCR, layout parsing, tampering anomaly detection).
  - Implements semantic RAG pipelines using Hugging Face models (`sentence-transformers`, `pgvector`).
  - Builds candidate yield prediction and scoring models.
* **Outputs:** AI extraction pipelines, embedding loaders, scoring algorithms.
* **Constraints:** Zero hallucinated applicant facts; explicit provenance and confidence scores required.

---

## 4. Quality & Governance

### G. QA Automation Engineer
* **Native Runtime Type:** `task`
* **Responsibilities:**
  - Builds and maintains automated end-to-end, integration, and contract test runners (`test-e2e.mjs`).
  - Verifies three-tier validation independence (Client, Server, Database).
  - Validates performance, loading states, and edge-case error recovery.
* **Outputs:** Executable test suites, reproducible defect logs, assertion matrices.
* **Constraints:** Must execute actual test commands and report real terminal outputs.

### H. Security Reviewer
* **Native Runtime Type:** `security-reviewer` (Read-Only)
* **Responsibilities:**
  - Audits authentication flows, cookie session security, and role-based access enforcement.
  - Scans for hardcoded secrets, API tokens, and private VAPID credentials.
  - Inspects file upload boundaries (mime-type validation, size limits, signed URL protections).
* **Outputs:** Security audit dossiers, CVE and vulnerability assessments, severity rankings.
* **Constraints:** Strictly read-only; never mutates code.

### I. Code Reviewer
* **Native Runtime Type:** `reviewer` (Read-Only)
* **Responsibilities:**
  - Conducts multi-axis code reviews (correctness, maintainability, architectural integrity).
  - Enforces Ponytail guidelines (cuts dead code, unused abstractions, redundant dependencies).
* **Outputs:** Line-by-line actionable review reports with surgical replacement recommendations.
* **Constraints:** Operates independently from implementation tasks.
