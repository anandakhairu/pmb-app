# Web Push & Background Worker Architecture — PMB-APP

**Version:** 1.0 (Phase 5 Approved)  
**Authority:** Chief Engineering Lead & Solution Architect  
**Protocol:** W3C Push API, W3C Notifications API, RFC 8291 (Message Encryption), RFC 8292 (VAPID)  
**Queue Engine:** BullMQ (^6.x) + Redis / IORedis (^6.x)  
**Worker Runtime:** Standalone Node.js process (`src/workers/notification-worker.js`)

---

## 1. System Architecture Overview

```
                           [ CLIENT BROWSER ]
                           │                │
            1. User Action │                │ 6. Decrypt & Show
            (Subscribe)    ▼                ▼    (public/sw.js)
            ┌─────────────────┐          ┌───────────────────────┐
            │ PushManager     │          │ Service Worker        │
            │ Registration    │          │ showNotification()    │
            └────────┬────────┘          └───────────▲───────────┘
                     │                               │
        2. Endpoint  │                               │ 5. Outbound Push
        & P256 Keys  ▼                               │    (Encrypted RFC 8291)
┌──────────────────────────────────────────────┐     │
│ NEXT.JS WEB RUNTIME                          │     │
│                                              │     │
│ ┌──────────────────────────────────────────┐ │     │
│ │ Server Action: daftarkanPerangkatAction  │ │     │
│ └────────────────────┬─────────────────────┘ │     │
│                      │ 3. Atomic Upsert      │     │
│                      ▼                       │     │
│          ┌───────────────────────┐           │     │
│          │ PostgreSQL (Supabase) │           │     │
│          │ perangkat_notifikasi  │           │     │
│          └───────────────────────┘           │     │
│                                              │     │
│ ┌──────────────────────────────────────────┐ │     │
│ │ Business Mutation Trigger:               │ │     │
│ │ - simpanVerifikasiBerkasAction           │ │     │
│ │ - finalisasiPendaftaranAction            │ │     │
│ └────────────────────┬─────────────────────┘ │     │
│                      │ 4. Enqueue Job        │     │
│                      ▼ (Fail-safe)           │     │
│          ┌───────────────────────┐           │     │
│          │ BullMQ Queue Producer │           │     │
│          │ 'pmb-notifications'   │           │     │
│          └───────────┬───────────┘           │     │
└──────────────────────┼───────────────────────┘     │
                       │                             │
                       ▼                             │
            ┌─────────────────────┐                  │
            │ REDIS (Port 6379)   │                  │
            │ Persistent Queue    │                  │
            └──────────┬──────────┘                  │
                       │                             │
                       │ 5. Consume Job (FIFO)       │
                       ▼                             │
┌──────────────────────────────────────────────┐     │
│ STANDALONE WORKER PROCESS                    │     │
│ (src/workers/notification-worker.js)         │     │
│                                              │     │
│ 1. Load active subscriptions from PostgreSQL │     │
│ 2. VAPID Signing (VAPID_PRIVATE_KEY)         │     │
│ 3. webpush.sendNotification() ───────────────┼─────┘
│ 4. Handle 404/410 $\rightarrow$ deactive in DB           │
└──────────────────────────────────────────────┘
```

---

## 2. Queue & Job Data Contract

### Queue Name
`"pmb-notifications"`

### Job Payload Structure
```typescript
interface NotificationJobPayload {
  targetId: string;           // UUID of CalonMahasiswa or Admin
  targetType: "MAHASISWA" | "ADMIN";
  title: string;              // Short, formal title (e.g., "Berkas Terverifikasi")
  body: string;               // Concise message body (Zero PII: no NIK, grades, or secrets)
  url: string;                // Deep link internal path (e.g., "/dashboard/berkas")
  tag: string;                // Grouping tag (e.g., "pmb-verifikasi-UUID")
  timestamp: string;          // ISO 8601 string
}
```

### Idempotency & Deduplication
To comply with BullMQ at-least-once delivery semantics:
* Jobs are submitted with a deterministic `jobId`: `notif-${targetId}-${deduplicationId}`.
* Subsequent attempts with identical IDs within the deduplication window are discarded by BullMQ, preventing double notifications.

---

## 3. Database Subscription Model (`perangkat_notifikasi`)

* **Table Structure:**
  - `id`: UUID (PK)
  - `mahasiswa_id`: UUID (FK to `calon_mahasiswa`, `ON DELETE CASCADE`)
  - `admin_id`: UUID (FK to `admin`, `ON DELETE CASCADE`)
  - `endpoint`: TEXT (Unique)
  - `p256dh`: TEXT (Client public key)
  - `auth_key`: TEXT (Client auth secret)
  - `aktif`: BOOLEAN (Default `true`)
  - `terakhir_dipakai`: TIMESTAMPTZ
  - `created_at`: TIMESTAMPTZ
* **Layer 3 Integrity Constraint:**
  Enforced by PostgreSQL constraint `chk_perangkat_pemilik`:
  `CHECK ((mahasiswa_id IS NOT NULL)::int + (admin_id IS NOT NULL)::int = 1)`

---

## 4. Service Worker Specification (`public/sw.js`)

* **Event Listeners:**
  1. `push`: Intercepts push event, decrypts JSON payload with fallback to raw text, displays native OS notification via `self.registration.showNotification`.
  2. `notificationclick`: Closes notification banner, validates that the destination URL starts with `/` (anti-open-redirect security protection), checks for an existing open browser tab on the origin to focus, or opens a new tab.
