import { Suspense } from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Pemberitahuan, Stepper, StatusBadge } from "@/components/mahasiswa/status";
import {
  formatTanggal,
  gabungkanBerkas,
  getDataMahasiswa,
  hitungTahap,
} from "@/lib/data-mahasiswa";

export const metadata = { title: "Beranda" };

/** Pesan dinamis berdasarkan status_berkas dan status_kelulusan di formulir. */
function susunPemberitahuan(formulir) {
  const { statusBerkas, statusKelulusan, langkahTerakhir, catatanRevisi, jalur } = formulir;

  if (statusKelulusan === "LULUS") {
    return { nada: "sukses", judul: "Selamat, kamu dinyatakan lulus", isi: "Hasil seleksi sudah tersedia. Lihat program studi yang kamu terima dan cetak bukti kelulusannya.", aksi: { href: "/dashboard/kelulusan", label: "Lihat hasil seleksi" } };
  }
  if (statusKelulusan === "CADANGAN") {
    return { nada: "info", judul: "Kamu masuk daftar cadangan", isi: "Panitia akan menghubungi bila ada kursi kosong di program studi pilihanmu.", aksi: { href: "/dashboard/kelulusan", label: "Lihat rincian hasil" } };
  }
  if (statusKelulusan === "TIDAK_LULUS") {
    return { nada: "info", judul: "Hasil seleksi sudah diumumkan", isi: "Kamu belum lolos pada seleksi kali ini. Rincian dan catatan panitia ada di halaman hasil.", aksi: { href: "/dashboard/kelulusan", label: "Lihat rincian hasil" } };
  }

  switch (statusBerkas) {
    case "DRAFT":
      return langkahTerakhir < 4
        ? { nada: "info", judul: "Formulir belum lengkap", isi: "Lengkapi biodata dan data sekolah dulu sebelum mengunggah berkas.", aksi: { href: "/dashboard/biodata", label: "Lanjutkan pengisian" } }
        : { nada: "info", judul: "Berkas belum lengkap", isi: "Unggah semua dokumen wajib, lalu kirim untuk diverifikasi panitia.", aksi: { href: "/dashboard/berkas", label: "Unggah berkas" } };
    case "DIKIRIM":
      return { nada: "tunggu", judul: "Berkas menunggu giliran diperiksa", isi: "Panitia sudah menerima berkasmu. Kamu akan mendapat notifikasi saat pemeriksaan selesai." };
    case "DALAM_REVIEW":
      return { nada: "tunggu", judul: "Berkas sedang diperiksa panitia", isi: "Tidak ada yang perlu kamu lakukan sekarang. Hasil pemeriksaan akan muncul di halaman ini." };
    case "REVISI":
      return { nada: "peringatan", judul: "Ada berkas yang perlu diperbaiki", isi: catatanRevisi, aksi: { href: "/dashboard/berkas", label: "Perbaiki berkas" } };
    case "TERVERIFIKASI":
      return { nada: "sukses", judul: "Berkas sudah terverifikasi", isi: `Semua berkasmu dinyatakan valid. Hasil seleksi diumumkan pada ${formatTanggal(jalur.tanggalPengumumanHasil)}.` };
    default:
      return { nada: "info", judul: "Status belum tersedia", isi: "Muat ulang halaman ini beberapa saat lagi." };
  }
}

export default function BerandaPage() {
  return (
    <Suspense fallback={<div className="py-12 text-center text-sm text-neutral-500">Memuat beranda pendaftar...</div>}>
      <KontenBeranda />
    </Suspense>
  );
}

async function KontenBeranda() {
  const { mahasiswa, formulir, berkas } = await getDataMahasiswa();
  const tahap = hitungTahap(formulir);
  const notif = susunPemberitahuan(formulir);

  const wajib = gabungkanBerkas(berkas, formulir.jalur.kode).filter((d) => d.wajib);
  const terunggah = wajib.filter((d) => d.berkas).length;

  const rincian = [
    ["Program studi", `${formulir.prodi.nama} (${formulir.prodi.jenjang})`],
    ["Fakultas", formulir.prodi.fakultas],
    ["Jalur", formulir.jalur.nama],
    ["Tahun akademik", formulir.tahunAkademik],
    ["Nomor pendaftaran", formulir.nomorPendaftaran ?? "Terbit setelah berkas dikirim"],
    ["Berkas dikirim", formatTanggal(formulir.finalisasiAt)],
  ];

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-3xl font-extrabold tracking-tight text-[#2F4A3B]">
          Halo, {mahasiswa.namaLengkap.split(" ")[0]}
        </h1>
        <p className="mt-2 text-[15px] text-neutral-600">
          Pantau tahapan pendaftaranmu di sini. Tahun akademik {formulir.tahunAkademik}.
        </p>
      </header>

      <Pemberitahuan {...notif} />

      <section aria-labelledby="judul-tahap" className="rounded-xl border border-neutral-200 bg-white px-5 py-8 sm:px-10">
        <h2 id="judul-tahap" className="sr-only">Tahapan pendaftaran</h2>
        <Stepper indeks={tahap.indeks} peringatan={tahap.peringatan} />
      </section>

      <div className="grid gap-10 lg:grid-cols-5">
        <section aria-labelledby="judul-rincian" className="lg:col-span-3">
          <h2 id="judul-rincian" className="text-lg font-extrabold text-neutral-900">Pendaftaran kamu</h2>
          <dl className="mt-4 divide-y divide-neutral-200 border-y border-neutral-200">
            {rincian.map(([label, nilai]) => (
              <div key={label} className="grid gap-1 py-3.5 sm:grid-cols-[10rem_1fr] sm:gap-6">
                <dt className="text-sm text-neutral-500">{label}</dt>
                <dd className="text-sm font-semibold text-neutral-900">{nilai}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section aria-labelledby="judul-berkas" className="lg:col-span-2">
          <div className="flex items-baseline justify-between gap-3">
            <h2 id="judul-berkas" className="text-lg font-extrabold text-neutral-900">Kelengkapan berkas</h2>
            <p className="text-sm font-semibold text-neutral-500">{terunggah} dari {wajib.length} diunggah</p>
          </div>
          <div
            role="progressbar"
            aria-label="Berkas wajib yang sudah diunggah"
            aria-valuemin={0}
            aria-valuemax={wajib.length}
            aria-valuenow={terunggah}
            className="mt-4 h-1.5 overflow-hidden rounded-full bg-neutral-200"
          >
            <div className="h-full rounded-full bg-[#4B6E5A]" style={{ width: `${(terunggah / wajib.length) * 100}%` }} />
          </div>
          <ul className="mt-4 divide-y divide-neutral-200 border-y border-neutral-200">
            {wajib.map((d) => (
              <li key={d.jenis} className="flex items-center justify-between gap-3 py-3">
                <span className="text-sm text-neutral-700">{d.nama}</span>
                <StatusBadge status={d.status} />
              </li>
            ))}
          </ul>
          <Link
            href="/dashboard/berkas"
            className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-[#4B6E5A] underline-offset-4 hover:text-[#2F4A3B] hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4B6E5A]"
          >
            Kelola berkas
            <ArrowRight className="size-4" aria-hidden />
          </Link>
        </section>
      </div>
    </div>
  );
}
