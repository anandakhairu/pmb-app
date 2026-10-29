# Technical Requirements — Full-Stack Web Development

**Stack utama:** Next.js + JavaScript + PostgreSQL

Dokumen ini berlaku untuk seluruh tema proyek. Fitur dan alur bisnis mengikuti requirement masing-masing tema, sedangkan standar teknis berikut wajib dipenuhi.

## 1. Teknologi Wajib

- **Frontend & Backend:** Next.js, React, dan JavaScript.
- **Database:** PostgreSQL.
- **Backend API:** Next.js Route Handlers atau Server Actions sesuai kebutuhan.
- **Database Access:** Prisma, Drizzle, atau `pg`.
- **Validasi:** Zod atau library setara.
- **Version Control:** Git.
- **Web Push:** Service Worker, VAPID, dan library `web-push`.
- **Background Worker:** Proses worker terpisah dengan antrean pekerjaan yang persisten, misalnya BullMQ + Redis atau solusi setara.

**Larangan:** Dilarang menggunakan PostgREST atau layanan lain sebagai pengganti implementasi backend. Mahasiswa wajib membuat backend sendiri menggunakan JavaScript dan Next.js.

## 2. Validation — Wajib 3 Lapisan

Setiap operasi yang relevan wajib menerapkan validasi pada ketiga lapisan berikut.

1. **Frontend:** validasi field wajib, format, panjang, rentang nilai, serta pesan error yang jelas.
2. **Backend:** validasi request, business rules, relasi data, autentikasi, otorisasi, kepemilikan data, dan transisi status.
3. **Database:** gunakan constraint yang sesuai, seperti `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, dan `CHECK`.

Validasi frontend tidak menggantikan validasi backend. Validasi backend juga tidak menggantikan constraint database yang diperlukan untuk menjaga integritas data.

Mahasiswa wajib mampu mendemonstrasikan bahwa ketiga lapisan bekerja secara independen.

## 3. Database & Data Integrity

- Desain tabel, relasi, dan tipe data harus sesuai kebutuhan bisnis.
- Sediakan migration files agar database dapat dibuat ulang dari kondisi awal.
- Seed data diperbolehkan untuk inisialisasi, tetapi tidak boleh menggantikan fitur yang seharusnya menggunakan data persisten.
- Gunakan transaksi untuk operasi multi-langkah yang harus konsisten.
- Pertimbangkan race condition pada operasi seperti reservasi, kuota, saldo, dan transaksi.
- Gunakan query terparameterisasi, pagination untuk dataset besar, serta indeks berdasarkan kebutuhan query.
- Hindari N+1 query, pengambilan data berlebihan, dan duplikasi data yang tidak diperlukan.

## 4. Authentication & Security

Jika aplikasi memiliki akun pengguna, autentikasi dan otorisasi wajib diterapkan dengan benar.

- Pemeriksaan hak akses harus dilakukan di server.
- Jangan mempercayai role, harga, saldo, status, atau identitas pemilik yang dikirim oleh client.
- Password harus di-hash menggunakan algoritma yang sesuai jika dikelola sendiri.
- Secret, kredensial database, token, dan private key tidak boleh terekspos ke browser atau repository.
- Gunakan parameterized query atau ORM yang aman.
- Terapkan rate limiting pada endpoint yang rentan disalahgunakan.
- Operasi sensitif harus memeriksa kepemilikan data dan hak akses.
- Error response tidak boleh membocorkan informasi internal yang sensitif.

## 5. Web Push Notification & Background Worker — Wajib

Setiap proyek wajib mengimplementasikan **Web Push Notification nyata**, bukan sekadar toast atau alert.

### Browser

- Gunakan Service Worker untuk menangani event `push` dan `notificationclick`.
- Izin notifikasi diminta melalui interaksi pengguna.
- Notifikasi harus dapat mengarahkan pengguna ke halaman yang relevan.
- Tangani kondisi izin ditolak, browser tidak mendukung fitur, dan subscription tidak valid.

### Backend & Worker

- Gunakan VAPID dan library Web Push, misalnya `web-push`.
- Simpan push subscription pada PostgreSQL dan hubungkan dengan pengguna atau identitas yang sesuai.
- Private key VAPID hanya boleh tersedia di server.
- Sediakan background worker yang memproses pengiriman notifikasi secara asynchronous.
- Gunakan antrean persisten, misalnya BullMQ + Redis, atau solusi setara.
- Implementasikan retry terbatas, penanganan kegagalan, dan pencegahan pengiriman ganda.
- Worker harus dapat dijalankan secara terpisah dan dijelaskan cara menjalankannya.
- Kegagalan notifikasi tidak boleh membatalkan transaksi bisnis yang sudah berhasil disimpan.

Notifikasi wajib terhubung dengan setidaknya satu kejadian bisnis yang relevan dengan tema proyek.

**Alur minimum:** kejadian bisnis → database → antrean → background worker → Web Push → Service Worker → notifikasi pada browser.

## 6. File Upload & Object Storage

**Wajib jika tema memiliki fitur unggah berkas.**

Contoh teknologi: Cloudflare R2, Amazon S3, atau MinIO.

- Simpan berkas pada object storage atau layanan penyimpanan yang sesuai.
- PostgreSQL menyimpan metadata dan referensi berkas, bukan menggantikan object storage untuk file besar.
- Validasi ukuran, tipe, dan hak akses berkas di server.
- Lindungi berkas privat dari akses tanpa izin.
- Jangan mengekspos kredensial storage ke client.
- Presigned URL diperbolehkan jika dibuat secara aman oleh backend.

Jika tema tidak membutuhkan unggah berkas, object storage tidak wajib digunakan.

## 7. Error Handling & Observability

Aplikasi harus dapat ditelusuri ketika terjadi error, termasuk pada background worker.

Contoh teknologi:

- **Logging:** Pino atau Winston.
- **Error monitoring:** Sentry atau solusi setara.
- **Metrics/dashboard:** Prometheus + Grafana atau monitoring dari platform hosting.
- **Tracing:** OpenTelemetry sebagai best practice.

Ketentuan minimum:

- Catat error penting, durasi operasi, dan status pekerjaan worker.
- Gunakan log terstruktur dan konteks yang cukup untuk melakukan diagnosis.
- Jangan mencatat password, token, private key, atau data sensitif yang tidak diperlukan.
- Pastikan kegagalan worker tidak terjadi secara diam-diam.
- Mahasiswa harus dapat menunjukkan cara menemukan error dan memeriksa pekerjaan yang gagal.

Distributed tracing lengkap tidak wajib jika kompleksitas proyek belum membutuhkannya.

## 8. Performance & Code Quality

- Gunakan TypeScript dengan tipe yang sesuai dan hindari `any` tanpa alasan jelas.
- Hindari hardcode atau dummy data sebagai pengganti implementasi fitur.
- Terapkan pagination untuk dataset besar dan filtering sesuai kebutuhan.
- Hindari query berulang dan pengambilan data yang tidak diperlukan.
- Gunakan caching secara sadar dengan mempertimbangkan konsistensi data.
- Hindari abstraksi, library, dan arsitektur yang tidak memberikan manfaat nyata.
- Terapkan loading, empty, success, dan error state pada UI.
- Pastikan tampilan responsif dan alur utama dapat digunakan melalui keyboard.

**Best practice:** ESLint, pemeriksaan tipe TypeScript, serta CI/CD menggunakan GitHub Actions atau solusi setara.

## 9. Deployment & Documentation

Repository wajib menyediakan:

- Source code dan riwayat Git yang wajar.
- Petunjuk instalasi dan menjalankan aplikasi.
- `.env.example` tanpa secret asli.
- Migration files dan petunjuk inisialisasi database.
- ERD atau dokumentasi skema database.
- Dokumentasi arsitektur frontend, backend, database, dan worker.
- Petunjuk konfigurasi VAPID serta menjalankan worker.
- Daftar fitur yang selesai dan keterbatasan yang masih ada.

Aplikasi dan worker harus dapat dijalankan berdasarkan dokumentasi pada lingkungan baru. Deployment Web Push wajib menggunakan HTTPS, kecuali lingkungan lokal yang memenuhi ketentuan secure context browser.

## 10. Testing & Verification

Mahasiswa wajib menyediakan bukti verifikasi implementasi melalui demonstrasi dan pemeriksaan kode.

Cakupan minimum:

1. Validasi input di frontend.
2. Validasi backend melalui request langsung tanpa melewati frontend.
3. Constraint database terhadap data yang tidak valid.
4. Pemeriksaan autentikasi, otorisasi, dan kepemilikan data.
5. Operasi CRUD menggunakan data persisten.
6. Migrasi dan relasi database.
7. Pengiriman Web Push melalui background worker.
8. Penanganan kegagalan job dan subscription tidak valid.
9. Konsistensi data dan penanganan error.

Mahasiswa harus mampu menjelaskan implementasi dan keputusan teknis yang digunakan. Screenshot UI saja tidak cukup sebagai bukti bahwa fitur telah diimplementasikan.

## 11. Ketentuan Umum

- Teknologi tambahan diperbolehkan selama tidak menggantikan kompetensi inti yang diwajibkan.
- Contoh teknologi dalam dokumen ini merupakan rekomendasi, kecuali dinyatakan wajib.
- Alternatif teknologi diperbolehkan jika memenuhi fungsi, keamanan, dan kriteria teknis yang sama.
- Ketentuan kondisional hanya berlaku jika fitur terkait terdapat pada tema proyek.
- Penyimpangan dari ketentuan wajib harus mendapatkan persetujuan pengajar.
- Jika requirement fitur ambigu atau bertentangan, mintalah klarifikasi sebelum menentukan implementasi.

**Prinsip utama:** aplikasi harus benar-benar berfungsi, menggunakan data persisten, aman, dapat dijelaskan implementasinya, dan memenuhi standar full-stack development. Tampilan yang bagus saja tidak cukup.