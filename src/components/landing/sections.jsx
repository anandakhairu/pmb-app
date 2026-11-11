import Link from "next/link";
import { CalendarDays, Check, Megaphone } from "lucide-react";
import { GAMBAR, JADWAL, JALUR, PENGUMUMAN, PROFIL } from "@/lib/data-publik";
import { Foto } from "@/components/landing/foto";

const rupiah = new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 });
const judul = "text-3xl font-extrabold leading-tight tracking-tight text-[#2F4A3B] sm:text-4xl";

/* Profil institusi + galeri kehidupan kampus */
export function Profil() {
  return (
    <section id="profil" className="scroll-mt-16 bg-[#F5F6F5] py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-12 lg:gap-16">
          <Foto src={GAMBAR.kampus} alt="Foto kampus" className="aspect-[4/3] rounded-2xl lg:col-span-5" />
          <div className="lg:col-span-7">
            <h2 className={judul}>{PROFIL.judul}</h2>
            <div className="mt-6 space-y-4 text-base leading-relaxed text-neutral-600">
              {PROFIL.deskripsi.map((p) => <p key={p}>{p}</p>)}
            </div>
            <dl className="mt-10 grid gap-6 sm:grid-cols-3">
              {PROFIL.nilai.map((n) => (
                <div key={n.judul} className="border-t-2 border-[#4B6E5A] pt-4">
                  <dt className="text-[15px] font-bold text-neutral-900">{n.judul}</dt>
                  <dd className="mt-1.5 text-sm leading-relaxed text-neutral-600">{n.isi}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>

        <div className="mt-16 grid gap-4 md:h-[520px] md:grid-cols-12 md:grid-rows-2">
          <Foto src={GAMBAR.galeri[0]} alt="Kegiatan belajar di kampus" className="aspect-[4/3] rounded-2xl md:col-span-7 md:row-span-2 md:aspect-auto" />
          <Foto src={GAMBAR.galeri[1]} alt="Fasilitas kampus" className="aspect-[4/3] rounded-2xl md:col-span-5 md:aspect-auto" />
          <Foto src={GAMBAR.galeri[2]} alt="Kegiatan mahasiswa" className="aspect-[4/3] rounded-2xl md:col-span-5 md:aspect-auto" />
        </div>
      </div>
    </section>
  );
}

/* Jalur penerimaan: persyaratan, periode, dan biaya dalam satu baris per jalur */
export function Jalur() {
  return (
    <section id="jalur" className="scroll-mt-16 bg-[#F5F6F5] py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <h2 className={`${judul} max-w-md`}>Pilihan Jalur Penerimaan</h2>
          <p className="max-w-md text-base leading-relaxed text-neutral-600">
            Pilih jalur yang paling sesuai dengan kemampuan dan kesiapanmu. Persyaratan, periode, dan biaya tertera di tiap jalur.
          </p>
        </div>

        <div className="mt-12 border-b border-neutral-300">
          {JALUR.map((j) => (
            <article key={j.id} id={`jalur-${j.id}`} className="grid gap-6 border-t border-neutral-300 py-10 md:grid-cols-12 md:gap-10">
              <div className="md:col-span-3">
                <h3 className="text-2xl font-extrabold tracking-tight text-[#2F4A3B]">{j.nama}</h3>
                <p className="mt-1 text-sm font-medium text-[#5C836A]">{j.subjudul}</p>
                <p className="mt-4 flex items-start gap-2 text-sm text-neutral-500">
                  <CalendarDays className="mt-0.5 size-4 shrink-0" />
                  {j.periode}
                </p>
              </div>
              <div className="md:col-span-6">
                <p className="text-[15px] leading-relaxed text-neutral-600">{j.deskripsi}</p>
                <ul className="mt-5 space-y-2.5">
                  {j.persyaratan.map((s) => (
                    <li key={s} className="flex gap-3 text-sm leading-relaxed text-neutral-700">
                      <Check className="mt-0.5 size-4 shrink-0 text-[#4B6E5A]" />
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="md:col-span-3 md:text-right">
                <p className="text-sm text-neutral-500">Biaya pendaftaran</p>
                <p className="text-2xl font-extrabold tracking-tight text-neutral-900">{j.biaya === 0 ? "Gratis" : rupiah.format(j.biaya)}</p>
                <Link href="/register" className="mt-5 inline-block text-sm font-semibold text-[#4B6E5A] underline underline-offset-4 hover:text-[#2F4A3B]">
                  Daftar melalui {j.nama}
                </Link>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

/* Jadwal penerimaan */
export function Jadwal() {
  return (
      <section id="jadwal" className="scroll-mt-16 bg-[#F5F6F5] py-20 sm:py-28">
        <div className="mx-auto grid max-w-6xl gap-12 px-6 lg:grid-cols-12 lg:gap-16">
          <div className="lg:col-span-4">
            <h2 className={judul}>Jadwal Penerimaan</h2>
            <p className="mt-5 text-base leading-relaxed text-neutral-600">
              Catat tanggal pentingnya. Pendaftaran hanya dapat dikirim selama periode jalur dibuka.
            </p>
          </div>
          <ol className="divide-y divide-neutral-200 border-y border-neutral-200 lg:col-span-8">
            {JADWAL.map((j) => (
              <li key={j.tahap} className="grid gap-1 py-5 sm:grid-cols-[11rem_1fr] sm:gap-6">
                <p className="text-sm font-bold text-[#4B6E5A]">{j.tanggal}</p>
                <div>
                  <p className="text-[15px] font-bold text-neutral-900">{j.tahap}</p>
                  <p className="mt-0.5 text-sm text-neutral-500">{j.ket}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>
  );
}

/* Pengumuman terbaru */
export function Pengumuman() {
  return (
      <section id="pengumuman" className="scroll-mt-16 bg-white py-20 sm:py-28">
        <div className="mx-auto max-w-6xl px-6">
          <div className="flex items-end justify-between gap-4">
            <h2 className={judul}>Pengumuman Terbaru</h2>
            <Link href="/pengumuman" className="hidden text-sm font-semibold text-[#4B6E5A] underline-offset-4 hover:underline sm:block">
              Semua pengumuman
            </Link>
          </div>
          <ul className="mt-10 grid gap-4 md:grid-cols-3">
            {PENGUMUMAN.map((a) => (
              <li key={a.slug}>
                <Link href={`/pengumuman/${a.slug}`} className="flex h-full flex-col rounded-xl border border-neutral-200 bg-white p-6 transition-colors hover:border-[#4B6E5A]">
                  <span className="flex items-center gap-2 text-[13px] text-neutral-500">
                    <Megaphone className="size-4 text-[#D97706]" />
                    {a.tanggal}
                  </span>
                  <span className="mt-4 text-[15px] font-bold leading-snug text-neutral-900">{a.judul}</span>
                  <span className="mt-2 text-sm leading-relaxed text-neutral-600">{a.ringkasan}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>
  );
}