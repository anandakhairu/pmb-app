# Web Push & Background Worker Security Specification

**Standard Reference:** OWASP Top 10 (2021), UU No. 27/2022 Pelindungan Data Pribadi (UU PDP), RFC 8292 (VAPID)

---

## 1. VAPID Key Management & Boundaries

1. **Public vs. Private Segregation:**
   * `NEXT_PUBLIC_VAPID_PUBLIC_KEY`: Safe for client exposure; consumed by browser `navigator.serviceWorker` / `PushManager.subscribe()`.
   * `VAPID_PRIVATE_KEY`: **Strictly server-side secret**. Never given the `NEXT_PUBLIC_` prefix; never imported by client components.
2. **Permanent Keypair Invariant:**
   * VAPID keys must be statically provisioned in `.env`.
   * Never dynamically re-generate VAPID keys on startup; regenerating keys invalidates all existing client subscriptions stored in the database.

---

## 2. Subscription Ownership & Authorization (Anti-BOLA/IDOR)

* **Threat:** Malicious user A submits device endpoint belonging to user B, or alters admin notification routes.
* **Mitigation:**
  1. The server action `daftarkanPerangkatAction` derives user identity directly from the authenticated server session or trusted context.
  2. Database constraint `chk_perangkat_pemilik` prevents a subscription from belonging to both a student and an admin simultaneously.
  3. Device registration uses an atomic `upsert` that resets the opposing foreign key.

---

## 3. Server-Side Request Forgery (SSRF) Defense

* **Threat:** Attacker registers an arbitrary internal network URL (e.g., `http://169.254.169.254/latest/meta-data` or `http://localhost:6379`) as a push endpoint, causing the background worker to execute internal HTTP requests.
* **Mitigation:**
  1. Input validation in `subscriptionSchema` requires `endpoint` to strictly use the `https://` protocol scheme.
  2. The worker only delivers via `webpush.sendNotification`, which formats payload according to RFC 8291/8292 using standard Web Push protocols.

---

## 4. Payload Privacy & Data Minimization (UU PDP Compliance)

Under Indonesian Personal Data Protection Law (UU No. 27/2022), personal and financial information must not be transmitted over unencrypted or third-party notification channels:

* **PROHIBITED in Push Body:**
  ❌ Nomor Induk Kependudukan (NIK)  
  ❌ Passwords / PINs  
  ❌ Detailed report card grades / GPAs  
  ❌ Exact household income / UKT payment invoice receipts  
* **PERMITTED in Push Body:**
  ✅ Generic, non-sensitive milestone alerts (e.g., *"Berkas pendaftaran Anda telah dinyatakan VALID oleh panitia."*)  
  ✅ Action prompts (e.g., *"Ada berkas yang memerlukan revisi. Silakan periksa catatan di portal."*)  
  ✅ Internal authenticated deep links (e.g., `/dashboard/berkas`).
