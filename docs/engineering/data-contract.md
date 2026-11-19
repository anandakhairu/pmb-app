# Data Contract & Persistence Architecture — PMB-APP

**Version:** 1.0 (Approved for Phase 4 Implementation)  
**Authority:** Engineering Lead & Solutions Architect  
**ORM:** Prisma 6.19.3  
**Database:** PostgreSQL 15+ (Supabase Cloud, Project: `foxotwfiqtiicduiqtuq`)

---

## 1. Table-to-Domain Mapping

| PostgreSQL Table Name | Prisma Model Name | Domain Role / Aggregate Root | Ownership & Lifecycle |
| :--- | :--- | :--- | :--- |
| `calon_mahasiswa` | `CalonMahasiswa` | Applicant Profile | Owned by applicant via `auth_user_id` (Supabase Auth). Root of applicant aggregate. |
| `data_asal_sekolah` | `DataAsalSekolah` | School Education History | 1-to-1 dependent child of `CalonMahasiswa` (`ON DELETE CASCADE`). |
| `program_studi` | `ProgramStudi` | Academic Master Data | Master catalog. Read-only to applicants; maintained by Admin. |
| `jalur_pendaftaran` | `JalurPendaftaran` | Admission Channel Master | Master catalog with fee, dates, and requirements. |
| `formulir_pendaftaran`| `FormulirPendaftaran` | Admission Application Core | Core transactional aggregate root. 1 per student per academic year (`mahasiswa_id + tahun_akademik` UNIQUE). |
| `berkas_dokumen` | `BerkasDokumen` | Supporting Document Metadata | Metadata of uploaded files in private storage bucket. 1 per document type per application (`formulir_id + jenis` UNIQUE). |
| `jadwal_ujian_cbt` | `JadwalUjianCbt` | Exam Schedule Master | Session slots for channels requiring CBT exams (`butuh_ujian_cbt = true`). |
| `tagihan_pembayaran` | `TagihanPembayaran` | Invoicing & Payment Record | Financial ledger per application. Unique invoice number (`nomor_tagihan`). |
| `admin` | `Admin` | Panitia / Staff Profile | Back-office panitia linked via `auth_user_id` to Supabase Auth. Roles: `SUPER_ADMIN`, `VERIFIKATOR`, `PANITIA`. |
| `perangkat_notifikasi`| `PerangkatNotifikasi`| Push Subscription Registry | Web Push VAPID subscriptions for browser notifications (linked to student OR admin). |
| `pengumuman` | `Pengumuman` | Public Announcement System | Published updates and news authored by Admin. |

---

## 2. Relational Integrity & Key Constraints

```
  auth.users (Supabase Auth)
       │ (auth_user_id)
       ▼
┌─────────────────────────┐  1 : 1   ┌───────────────────────────┐
│     calon_mahasiswa     │─────────│     data_asal_sekolah     │
└────────────┬────────────┘          └───────────────────────────┘
             │ 1 : N
             ▼
┌─────────────────────────┐  N : 1   ┌───────────────────────────┐
│  formulir_pendaftaran   │─────────│       program_studi       │
└──────┬───────────┬──────┘          └───────────────────────────┘
       │           │ N : 1
       │           ▼
       │     ┌───────────────────────────┐
       │     │     jalur_pendaftaran     │
       │     └───────────────────────────┘
       │ 1 : N
       ├───────────────────────────┐
       ▼                           ▼
┌─────────────────────────┐ ┌───────────────────────────┐
│     berkas_dokumen      │ │    tagihan_pembayaran     │
└─────────────────────────┘ └───────────────────────────┘
```

### Key Foreign Key Policies:
1. `CalonMahasiswa` $\rightarrow$ `FormulirPendaftaran`: `ON DELETE CASCADE`. Deleting an applicant purges their forms, files, and tags.
2. `ProgramStudi` / `JalurPendaftaran` $\rightarrow$ `FormulirPendaftaran`: `ON DELETE RESTRICT`. Cannot delete a program or channel that has active applications.
3. `FormulirPendaftaran` $\rightarrow$ `Admin` (`verifikator_id`, `penetap_id`): `ON DELETE SET NULL`. If an admin account is deactivated, historical verification audit trails remain intact.

---

## 3. Layer 3 Database Integrity Constraints (PostgreSQL)

The database enforces business rules at the schema layer via `prisma/constraints.sql`:
1. `chk_maba_nik_16_digit`: `nik ~ '^[0-9]{16}$'`
2. `chk_maba_no_hp`: `no_hp ~ '^(\+62|62|0)8[0-9]{8,12}$'`
3. `chk_sekolah_npsn`: `npsn IS NULL OR npsn ~ '^[0-9]{8}$'`
4. `chk_sekolah_tahun_lulus`: `tahun_lulus BETWEEN 2000 AND 2100`
5. `chk_sekolah_nilai`: `nilai_rata_rata BETWEEN 0 AND 100`
6. `chk_berkas_ukuran`: `ukuran_byte > 0 AND ukuran_byte <= 10485760` (Max 10MB per file)
7. `chk_nomor_pendaftaran_format`: `nomor_pendaftaran IS NULL OR nomor_pendaftaran ~ '^PMB-[0-9]{4}-[0-9]{6}$'`
8. `chk_perangkat_notif_owner`: Exactly one owner: `(mahasiswa_id IS NOT NULL AND admin_id IS NULL) OR (mahasiswa_id IS NULL AND admin_id IS NOT NULL)`

---

## 4. Transaction Boundaries & Concurrency

### A. Finalisasi Pendaftaran (Student Submission)
* **Pre-conditions:** All mandatory documents for the channel have `storage_path` populated. Status must be `DRAFT` or `REVISI`.
* **Transaction Steps:**
  1. Acquire pessimistic row lock on `formulir_pendaftaran` row (`SELECT ... FOR UPDATE`).
  2. Generate official registration number from sequence `seq_nomor_pendaftaran` (Format: `PMB-YYYY-NNNNNN`).
  3. Set `status_berkas = 'DIKIRIM'`, `finalisasi_at = NOW()`, `langkah_terakhir = 4`.
  4. Generate initial `tagihan_pembayaran` if channel has fee (`biaya_pendaftaran > 0`).

### B. Admin Verification Decision
* **Pre-conditions:** Admin must possess `role_admin IN ('SUPER_ADMIN', 'VERIFIKATOR')`. Formulir status must be `DIKIRIM` or `DALAM_REVIEW`.
* **Transaction Steps:**
  1. Acquire row lock on `formulir_pendaftaran`.
  2. Batch update verification status for each `berkas_dokumen` (`VALID` or `REVISI` with mandatory note if revisi).
  3. If any document is `REVISI`, set formulir `status_berkas = 'REVISI'`, set `catatan_revisi`.
  4. If all mandatory documents are `VALID`, set formulir `status_berkas = 'TERVERIFIKASI'`.
  5. Record `verifikator_id = admin.id`, `diverifikasi_at = NOW()`.
  6. Enqueue asynchronous Web Push notification job to BullMQ queue.

---

## 5. Authorization & Server Boundary Contract

1. **Prisma Connection:** Prisma runs with database-owner permissions (`postgres` user) which bypasses PostgreSQL RLS.
2. **Mandatory Application Guard:**
   - Every applicant query/mutation must filter by `mahasiswa.authUserId = session.user.id`.
   - Every admin query/mutation must verify `admin.authUserId = session.user.id` AND `admin.aktif = true`.
3. **Encapsulation:** All Prisma calls reside strictly in Server Actions or server-only utilities (`src/lib/server/*`). No Prisma client code may ever be bundled to the browser.
