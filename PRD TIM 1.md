# **📘 BUKU SAKU & PEDOMAN CLAUDE: PROYEK PMB-APP (TIM 1\)**

**Halo Tim\!** Fondasi proyek (Database Prisma, Setup Tailwind+Shadcn, Auth Shell, dan Landing Page) sudah di-push ke cabang main di GitHub.

Sebelum mulai mengerjakan bagian masing-masing, **WAJIB lakukan ini di terminal VS Code kalian:**

1. git checkout main  
2. git pull origin main (Untuk mengambil UI Landing Page & setup terbaru)  
3. npm install (Untuk memastikan semua package terinstal)  
4. Buat branch baru untuk tugasmu: git checkout \-b feat/nama-tugasmu

## **🧬 MASTER SYSTEM DIRECTIVE (Aturan Wajib UI/UX)**

*Aturan ini adalah "DNA" sistem kita. Jangan biarkan AI membuat desain yang norak/berbeda.*

* **Tema UI:** Portal Kampus SaaS Premium (Modern, Bersih, Profesional).  
* **Warna Utama:** Dark Sage Green (\#4B6E5A), Accent (\#5C836A).  
* **Font:** Plus Jakarta Sans.  
* **Komponen:** Eksklusif menggunakan Tailwind CSS & shadcn/ui.  
* **Aturan Anti-AI:** Dilarang keras menggunakan gambar vektor clipart AI, efek 3D murahan, atau shadow yang terlalu tebal. Gunakan *whitespace* yang lapang dan border abu-abu lembut (border-slate-200).

## **🧑‍💻 PROMPT UNTUK TEMAN 1 (Tugas: Dashboard Mahasiswa & Upload Berkas)**

**Cara Pakai:** Buka chat baru di Claude. *Copy-paste* teks di bawah ini ke Claude agar dia membuatkan Dashboard Pendaftar dengan gaya yang sama persis dengan Landing Page.

> **PROMPT UNTUK CLAUDE:** "Anda adalah Senior Front-End Developer. Saya sedang melanjutkan proyek Sistem PMB (Next.js App Router, Tailwind, Shadcn UI). Teman saya sudah membuat Skema Prisma (10 tabel) dan Landing Page dengan warna utama Dark Sage Green (\#4B6E5A) dan font Plus Jakarta Sans.

> TUGAS ANDA: Buatkan UI untuk area app/(mahasiswa)/.... JANGAN mengubah file landing page atau prisma schema. Desain harus ultra-clean, minimalis, dan bergaya SaaS dashboard modern (Sidebar kiri di desktop, Topbar drawer di mobile).

> Buatkan 4 file komponen berikut dengan kode utuh yang siap jalan:

> 1. app/(mahasiswa)/layout.tsx: Layout Sidebar (Menu: Beranda, Biodata, Unggah Berkas, Hasil Seleksi).  
> 2. app/(mahasiswa)/dashboard/page.tsx: Halaman Overview. Berisi 'Horizontal Stepper' status pendaftaran (Draft \-\> Berkas \-\> Verifikasi \-\> Lulus), dan Alert box yang dinamis.  
> 3. app/(mahasiswa)/dashboard/berkas/page.tsx: UI Form Upload Dokumen. Buat desain 'Dropzone' area yang modern (garis putus-putus, icon Lucide) untuk upload Ijazah, Rapor, dan KK. Tambahkan status badge (Belum Diunggah / Menunggu Verifikasi / Perlu Revisi).  
> 4. app/(mahasiswa)/dashboard/kelulusan/page.tsx: Halaman hasil akhir. Jika lulus, tampilkan Card perayaan elegan berwarna Sage Green dengan rincian prodi yang diterima dan tombol 'Cetak Bukti Kelulusan PDF'.

> Pastikan semua komponen menggunakan class utility Tailwind dengan rapi dan import dari lucide-react untuk icon."

## **👨‍💼 PROMPT UNTUK TEMAN 2 (Tugas: Dashboard Admin Back-Office)**

**Cara Pakai:** Buka chat baru di Claude. *Copy-paste* teks di bawah ini ke Claude. Ini akan menginstruksikan Claude membuat UI Admin yang canggih dan memenuhi syarat "Web Push Notification" dari dosen.

> **PROMPT UNTUK CLAUDE:** "Anda adalah Senior Front-End Developer. Saya melanjutkan proyek Sistem PMB (Next.js App Router, Tailwind, Shadcn UI). Desain sistem menggunakan warna utama Dark Sage Green (\#4B6E5A) dan font Plus Jakarta Sans yang sangat clean dan profesional ala enterprise SaaS.

> TUGAS ANDA: Buatkan UI untuk area app/(admin)/.... JANGAN mengubah landing page. Layout menggunakan Sidebar Admin. Buatkan kode UI yang responsif dan interaktif untuk 3 file ini:

> 1. app/(admin)/layout.tsx: Layout Sidebar Admin (Menu: Analytics, Antrean Verifikasi, Master Data, Pengaturan).  
> 2. app/(admin)/dashboard/page.tsx: Dashboard Analytics. Berikan 4 Card metrik (Total Pendaftar, Perlu Verifikasi, Revisi, Lulus). Di bawahnya ada layout tabel pendaftar terbaru menggunakan UI table modern (bukan tabel HTML biasa, gunakan desain rapi dengan border-b).  
> 3. app/(admin)/dashboard/verifikasi/page.tsx: Halaman inti Verifikasi Berkas. Buat desain 'Dual-Pane / Split View'. Sisi kiri: Placeholder PDF/Image Viewer untuk admin melihat berkas dokumen mahasiswa. Sisi Kanan: Form checklist verifikasi dokumen, Textarea untuk 'Catatan Revisi', dropdown Status (Terverifikasi/Revisi/Tolak), dan tombol Submit. Tambahkan desain 'Toggle' atau tombol untuk memicu pengiriman Web Push Notification ke mahasiswa saat statusnya diubah (sesuai requirement sistem).

> Pastikan kode utuh, siap render, dan bebas dari desain AI generik yang kaku."

### **Tips Tambahan untuk Teman-temanmu:**

1. Jika Claude memberikan komponen *shadcn* yang belum ter-install (misal: table, tabs, dialog), pastikan mereka menjalankannya di terminal (contoh: npx shadcn@latest add table).  
2. Minta mereka **konsisten melakukan commit dan push ke branch masing-masing**, lalu lakukan Pull Request (PR) ke main kalau sudah selesai agar kodemu tidak tertimpa\!

