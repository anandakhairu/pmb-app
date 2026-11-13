# Phase 4 — Database Integration & Persistent Data Cutover Report

**System:** PMB-APP (Sistem Penerimaan Mahasiswa Baru / ADMITRA)  
**Database:** PostgreSQL 15+ hosted on Supabase (`foxotwfiqtiicduiqtuq.supabase.co`)  
**ORM:** Prisma 6.19.3  
**Framework:** Next.js 16.4.3 (React 19, Turbopack, Partial Prerendering)  
**Status:** **PHASE 4 COMPLETE — PASSED ALL QUALITY GATES**

---

## 1. Executive Summary

Phase 4 successfully connected the application to the live cloud PostgreSQL database hosted on Supabase, replacing client-side mock simulations with persistent, transactional Prisma database operations while retaining clean fallback paths.

All 11 relational models, 8 PostgreSQL enums, and 17 Layer 3 database constraints were verified active in Supabase. Server Actions with Tier 2 Zod input validation were created for applicant biodata updates, registration finalization, and admin split-view verifications. Both the database-level test suite (`scripts/test-phase4-database.mjs`: 10/10 tests) and the full-stack web E2E test suite (`test-e2e.mjs`: 60/60 assertions) passed with a **100% green verdict**.

---

## 2. Database Discovery & Schema Verification

### Active PostgreSQL Models (11 Tables Verified in Supabase)
1. `calon_mahasiswa` (14 cols): Core applicant profile linked to Supabase Auth via `auth_user_id`.
2. `data_asal_sekolah` (11 cols): Applicant secondary education record (1:1 with `calon_mahasiswa`, `ON DELETE CASCADE`).
3. `program_studi` (12 cols): Study program catalog, quota, and UKT fee tiers (JSONB).
4. `jalur_pendaftaran` (13 cols): Admission channels (SNBP, SNBT, Mandiri) with fees, dates, and requirements.
5. `formulir_pendaftaran` (19 cols): Core application transaction, tracking status cycle (`DRAFT` $\rightarrow$ `DIKIRIM` $\rightarrow$ `DALAM_REVIEW` $\rightarrow$ `REVISI` $\rightarrow$ `TERVERIFIKASI`).
6. `berkas_dokumen` (11 cols): Supporting file upload metadata (storage path, MIME type, byte size, verification status).
7. `jadwal_ujian_cbt` (12 cols): CBT exam session slots for testing pathways.
8. `tagihan_pembayaran` (12 cols): Invoicing and payment status tracking.
9. `admin` (8 cols): Panitia accounts linked to Supabase Auth.
10. `perangkat_notifikasi` (10 cols): Web Push VAPID subscriptions for background worker notifications.
11. `pengumuman` (10 cols): Public news and announcements managed by panitia.

### Connection Architecture
* **Runtime (`DATABASE_URL`):** Connected to Supabase PgBouncer transaction pooler on port `6543` (`?pgbouncer=true`). Prepared statements disabled to prevent connection errors across serverless invocations.
* **Migrations (`DIRECT_URL`):** Connected directly to PostgreSQL session pooler on port `5432` for DDL operations and schema migrations.

---

## 3. Data Flow & Model Mapping

| Layer Function | Previous Mock Implementation | Live Persistent Implementation |
| :--- | :--- | :--- |
| `getDataMahasiswa(idOrEmail)` | Static fixture `SKENARIO_AKTIF = "revisi"` | Queries `prisma.calonMahasiswa.findFirst` with full relational tree (`asalSekolah`, `formulir`, `prodi`, `jalur`, `berkas`). |
| `getStatistikAdmin()` | Summed length of hardcoded array | Queries `prisma.formulirPendaftaran.count()` concurrently across statuses (`DIKIRIM`, `REVISI`, `LULUS`, `TERVERIFIKASI`). |
| `getDaftarPendaftarAdmin(filter)` | In-memory JS array `.filter()` | Queries `prisma.formulirPendaftaran.findMany` with SQL `WHERE` clauses (status, jalur, prodi, case-insensitive ILIKE search). |
| `getDetailPendaftarAdmin(id)` | In-memory array `.find(id)` | Queries `prisma.formulirPendaftaran.findUnique({ where: { id } })` with deep relation hydration. |
| `simpanVerifikasiBerkasAction` | Client-side `setTimeout` simulation | Executes `prisma.$transaction`: row-locks formulir, updates application status, updates per-file verification statuses, and logs Web Push job. |
| `simpanBiodataAction` | Client-side `setTimeout` simulation | Executes `prisma.$transaction`: updates `calon_mahasiswa` and upserts `data_asal_sekolah`. |
| `finalisasiPendaftaranAction` | Client-side `setTimeout` simulation | Executes `prisma.$transaction`: generates official registration number (`PMB-YYYY-NNNNNN`), sets status `DIKIRIM`, locks form. |

---

## 4. API & Server Actions Documentation

### `simpanVerifikasiBerkasAction(payload)`
* **File:** `src/lib/server/actions.js`
* **Input Schema (Zod):**
  ```typescript
  {
    formulirId: string (UUID),
    statusBerkas: "TERVERIFIKASI" | "REVISI" | "DALAM_REVIEW",
    catatanRevisi?: string | null,
    hasilPerBerkas?: Record<string, { status: "VALID" | "REVISI" | "MENUNGGU", catatan?: string }>,
    kirimNotifikasi?: boolean
  }
  ```
* **Transaction Behavior:** Atomically writes status and verification notes to `formulir_pendaftaran` and related `berkas_dokumen` rows. Revalidates Next.js cache paths (`/admin`, `/admin/verifikasi`, `/admin/verifikasi/[id]`, `/dashboard`).

### `simpanBiodataAction(formData)`
* **File:** `src/lib/server/actions.js`
* **Input Schema (Zod):** Validates 16-digit NIK, phone number regex, school year between 2000-2100, and average grade 0-100.
* **Transaction Behavior:** Updates applicant profile and upserts school record.

### `finalisasiPendaftaranAction(formulirId)`
* **File:** `src/lib/server/actions.js`
* **Behavior:** Locks application, issues next registration sequence number, transitions status from `DRAFT`/`REVISI` to `DIKIRIM`.

---

## 5. QA Verification Test Report

### A. Database Layer Tests (`scripts/test-phase4-database.mjs`)
* Total Test Cases: **10** | Passed: **10** | Failed: **0** | **Verdict: PASS (10/10)**
1. `Applicant Profile Retrieval from Supabase`: PASSED
2. `Admin Applicant List & Relations Retrieval`: PASSED
3. `Applicant Detail Retrieval by Form ID`: PASSED
4. `Admin Verification Mutation & Atomic Status Transition`: PASSED
5. `Database Layer 3 Constraint (Reject Invalid NIK)`: PASSED (PostgreSQL rejected malformed NIK)
6. `Database Constraint (RESTRICT on referenced MasterProdi)`: PASSED (Foreign key deletion blocked)
7. `Isolated Test Record (Insert & Cascade Cleanup)`: PASSED (Cascade deletion verified)
8. `Server-Side Validation (Reject Malformed Payload)`: PASSED (Zod rejected invalid inputs)
9. `Master Data Consistency (Prodi & Jalur)`: PASSED
10. `Database Connection Health via PgBouncer Pooler`: PASSED

### B. End-to-End Application Tests (`test-e2e.mjs`)
* Total Assertions: **60** | Passed: **60** | Failed: **0** | **Verdict: PASS (60/60)**
* All 12 routes tested live against the running application with real PostgreSQL streaming.

---

## 6. Security & Governance Review Summary

1. **Client Isolation:** Verified zero client components import Prisma Client. Server Actions are strictly isolated in `src/lib/server/actions.js`.
2. **PostgreSQL RLS Notice:** Prisma connects using the database owner role (`postgres`), which bypasses PostgreSQL RLS policies. Therefore, tenant authorization and IDOR protections are strictly enforced at the application layer.
3. **PII Masking:** NIK and contact numbers are encapsulated in authenticated routes (`(admin)` and `(mahasiswa)`) and never exposed on public landing pages.
4. **Credential Safety:** `.env` and `.env.local` containing Supabase passwords are confirmed in `.gitignore` and remain uncommitted.

---

## 7. Phase 4 Release Gate Matrix

| Verification Dimension | Required Criteria | Observed Result | Status |
| :--- | :--- | :--- | :---: |
| **Prisma Migrations** | 11 tables deployed without drift | 11 tables active in Supabase | **PASS** |
| **Data Persistence** | Real database queries in data layer | Prisma models wired in `data-admin` & `data-mahasiswa` | **PASS** |
| **Server Actions** | Atomic mutations for admin & applicant | 3 Server Actions implemented & verified | **PASS** |
| **Layer 3 Constraints** | PostgreSQL CHECK & FK constraints operational | Invalid NIK & FK deletions rejected by DB | **PASS** |
| **Full Build** | Static & Partial Prerendering builds cleanly | `npm run build` compiled 20 routes | **PASS** |
| **Automated QA** | 100% green test passes | 10/10 DB tests + 60/60 E2E assertions passed | **PASS** |
| **Data Preservation** | Zero user data loss or table truncation | Existing seeded applicant records intact | **PASS** |

**OVERALL PHASE 4 GATE VERDICT:** **PASSED — READY FOR PHASE 5 (WEB PUSH & BACKGROUND WORKER)**
