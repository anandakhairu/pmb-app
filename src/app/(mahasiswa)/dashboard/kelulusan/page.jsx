import { Suspense } from "react";
import Link from "next/link";
import { ArrowRight, Hourglass, Info, Lock } from "lucide-react";
import { Logo } from "@/components/logo";
import { TombolCetak } from "@/components/mahasiswa/tombol-cetak";
import { formatTanggal, getDataMahasiswa } from "@/lib/data-mahasiswa";
import { JADWAL } from "@/lib/data-publik";

export const metadata = { title: "Hasil Seleksi" };

const LANGKAH_LULUS = [
  "Simpan bukti kelulusan ini sebagai PDF atau cetak.",
  "Pantau pengumuman registrasi ulang di halaman utama portal.",
  "Siapkan pembayaran UKT sesuai golongan yang ditetapkan.",
];

function Judul({ children, deskripsi }) {
  return (
    <header className="mb-8 print:hidden">
      <h1 className="text-3xl font-extrabold tracking-tight text-[#2F4A3B]">{children}</h1>
      {deskripsi && <p className="mt-2 max-w-xl text-[15px] leading-relaxed text-neutral-600">{deskripsi}</p>}
    </header>
  );
}

function KotakInfo({ ikon: Ikon, judul, isi, aksi }) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-8 sm:p-10">
      <Ikon className="size-6 text-[#4B6E5A]" aria-hidden />
      <h2 className="mt-5 text-xl font-extrabold text-neutral-900">{judul}</h2>
      <p className="mt-2 max-w-lg text-[15px] leading-relaxed text-neutral-600">{isi}</p>
      {aksi && (
        <Link
          href={aksi.href}
          className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-[#4B6E5A] underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4B6E5A]"
        >
          {aksi.label}
          <ArrowRight className="size-4" aria-hidden />
        </Link>
      )}
    </div>
  );
}

export default function KelulusanPage() {
  return (
    <Suspense fallback={<div className="py-12 text-center text-sm text-neutral-500">Memuat hasil seleksi...</div>}>
      <KontenKelulusan />
    </Suspense>
  );
}

async function KontenKelulusan() {
  const { mahasiswa, formulir } = await getDataMahasiswa();
  const { statusBerkas, statusKelulusan, prodi, jalur } = formulir;
  const registrasi = JADWAL.find((j) => j.tahap.toLowerCase().includes("registrasi ulang"));

  /* 1. Berkas belum terverifikasi: hasil belum bisa ditetapkan */
  if (statusBerkas !== "TERVERIFIKASI") {
    return (
      <div>
        <Judul>Hasil seleksi</Judul>
        <KotakInfo
          ikon={Lock}
          judul="Hasil belum tersedia"
          isi="Hasil seleksi baru bisa ditetapkan setelah semua berkasmu terverifikasi panitia."
          aksi={{ href: "/dashboard/berkas", label: "Cek status berkas" }}
        />
      </div>
    );
  }

  /* 2. Berkas valid, hasil belum diumumkan */
  if (statusKelulusan === "BELUM_DITETAPKAN") {
    return (
      <div>
        <Judul>Hasil seleksi</Judul>
        <KotakInfo
          ikon={Hourglass}
          judul="Menunggu pengumuman"
          isi={`Berkasmu sudah terverifikasi. Hasil seleksi diumumkan pada ${formatTanggal(jalur.tanggalPengumumanHasil)} dan akan tampil di halaman ini.`}
        />
      </div>
    );
  }

  /* 3. Lulus */
  if (statusKelulusan === "LULUS") {
    const rincian = [
      ["Nama", mahasiswa.namaLengkap],
      ["Nomor pendaftaran", formulir.nomorPendaftaran],
      ["Jalur", jalur.nama],
      ["Tahun akademik", formulir.tahunAkademik],
      ["Ditetapkan", formatTanggal(formulir.ditetapkanAt)],
    ];

    return (
      <div>
        <Judul deskripsi="Simpan atau cetak bukti kelulusan ini untuk proses registrasi ulang.">Hasil seleksi</Judul>

        {/* Kop surat: hanya tampil saat dicetak */}
        <div className="mb-8 hidden items-center justify-between border-b border-neutral-300 pb-4 print:flex">
          <Logo />
          <p className="text-sm font-semibold text-neutral-700">Bukti Kelulusan Seleksi Mahasiswa Baru</p>
        </div>

        <article
          aria-labelledby="judul-lulus"
          className="overflow-hidden rounded-2xl bg-[#4B6E5A] text-white print:[print-color-adjust:exact]"
        >
          <div className="p-8 sm:p-12">
            <p className="text-sm font-semibold text-white/70">Selamat, {mahasiswa.namaLengkap}</p>
            <h2 id="judul-lulus" className="mt-3 text-sm font-semibold text-white/70">
              Kamu diterima di program studi
            </h2>
            <p className="mt-2 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">{prodi.nama}</p>
            <p className="mt-3 text-base text-white/80">
              {prodi.fakultas} &middot; Jenjang {prodi.jenjang} &middot; Akreditasi {prodi.akreditasi}
            </p>
          </div>

          <dl className="grid gap-px bg-white/15 sm:grid-cols-2">
            {rincian.map(([label, nilai]) => (
              <div key={label} className="bg-[#4B6E5A] px-8 py-5 sm:px-12 sm:[&:last-child:nth-child(odd)]:col-span-2 print:[print-color-adjust:exact]">
                <dt className="text-[13px] text-white/65">{label}</dt>
                <dd className="mt-1 text-[15px] font-bold">{nilai}</dd>
              </div>
            ))}
          </dl>

          <div className="flex flex-col gap-4 bg-[#2F4A3B] px-8 py-6 sm:flex-row sm:items-center sm:justify-between sm:px-12 print:hidden">
            <p className="text-sm text-white/75">
              Pilih &ldquo;Simpan sebagai PDF&rdquo; di dialog cetak untuk mendapatkan berkas PDF.
            </p>
            <TombolCetak />
          </div>
        </article>

        <section aria-labelledby="judul-langkah" className="mt-10 print:hidden">
          <h2 id="judul-langkah" className="text-lg font-extrabold text-neutral-900">Langkah berikutnya</h2>
          <ol className="mt-4 divide-y divide-neutral-200 border-y border-neutral-200">
            {LANGKAH_LULUS.map((l, i) => (
              <li key={l} className="flex gap-4 py-3.5 text-sm text-neutral-700">
                <span className="w-4 shrink-0 font-bold text-[#4B6E5A]">{i + 1}</span>
                {l}
              </li>
            ))}
          </ol>
          {registrasi && (
            <p className="mt-4 text-sm text-neutral-500">
              Registrasi ulang dibuka {registrasi.tanggal}.
            </p>
          )}
        </section>
      </div>
    );
  }

  /* 4. Cadangan atau tidak lulus */
  const cadangan = statusKelulusan === "CADANGAN";
  return (
    <div>
      <Judul>Hasil seleksi</Judul>
      <KotakInfo
        ikon={Info}
        judul={cadangan ? "Kamu masuk daftar cadangan" : "Kamu belum lolos seleksi kali ini"}
        isi={
          formulir.catatanKelulusan ??
          (cadangan
            ? "Panitia akan menghubungi bila ada kursi kosong."
            : "Terima kasih sudah mendaftar. Kamu bisa mengikuti jalur lain yang masih dibuka.")
        }
        aksi={cadangan ? undefined : { href: "/#jalur", label: "Lihat jalur yang masih dibuka" }}
      />
    </div>
  );
}
