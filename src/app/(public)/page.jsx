import Link from "next/link";
import { Clock, Mail, MapPin, Phone, Star, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/logo";
import { Foto } from "@/components/landing/foto";
import { KalkulatorUkt } from "@/components/landing/kalkulator-ukt";
import { ProgramStudi } from "@/components/landing/program-studi";
import { Jadwal, Jalur, Pengumuman, Profil } from "@/components/landing/sections";
import { GAMBAR, KONTAK, STATISTIK } from "@/lib/data-publik";

const NAV = [
  { href: "#program-studi", label: "Program Studi" },
  { href: "#jalur", label: "Jalur" },
  { href: "#simulasi-ukt", label: "Simulasi UKT" },
  { href: "#jadwal", label: "Jadwal" },
  { href: "#pengumuman", label: "Pengumuman" },
];

const LINK_CEPAT = [
  ...NAV,
  { href: "/login", label: "Masuk" },
  { href: "/register", label: "Daftar akun" },
];

const IKON_KONTAK = [MapPin, Phone, Mail, Clock];

export default function LandingPage() {
  return (
    <div className="min-h-screen overflow-x-clip bg-[#F5F6F5]">
      {/* ----------------------------- HEADER ----------------------------- */}
      <header className="sticky top-0 z-40 border-b border-neutral-200/70 bg-[#F5F6F5]/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
          <Logo />
          <nav aria-label="Navigasi utama" className="hidden items-center gap-8 text-sm font-medium text-neutral-600 lg:flex">
            {NAV.map((n) => (
              <Link key={n.href} href={n.href} className="transition-colors hover:text-[#4B6E5A]">{n.label}</Link>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" className="h-10 rounded-lg px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-200/60">
              <Link href="/login">Masuk</Link>
            </Button>
            <Button asChild className="h-10 rounded-lg bg-[#4B6E5A] px-5 text-sm font-semibold text-white hover:bg-[#5C836A]">
              <Link href="/register">Daftar</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* ------------------------------ HERO ------------------------------ */}
      <section>
        <div className="mx-auto grid max-w-6xl items-center gap-16 px-6 py-16 sm:py-20 lg:grid-cols-12 lg:gap-10 lg:py-24">
          <div className="lg:col-span-7">
            <p className="text-sm font-semibold text-[#5C836A]">
              Penerimaan mahasiswa baru 2027/2028
            </p>
            <h1 className="mt-5 max-w-2xl text-5xl font-extrabold leading-[1.02] tracking-tight text-[#2F4A3B] sm:text-6xl lg:text-7xl">
              Mulai Perjalanan Akademikmu di Sini
            </h1>
            <p className="mt-7 max-w-xl text-lg leading-relaxed text-neutral-600">
              Daftar, unggah berkas, dan pantau hasil seleksi dari satu akun. Prosesnya jelas dari awal, dan estimasi biaya kuliah bisa kamu hitung sebelum memutuskan.
            </p>
            <div className="mt-10 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg" className="h-12 rounded-lg bg-[#4B6E5A] px-8 text-[15px] font-semibold text-white hover:bg-[#5C836A]">
                <Link href="/register">Daftar Sekarang</Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="h-12 rounded-lg border-[#4B6E5A]/30 bg-transparent px-8 text-[15px] font-semibold text-[#4B6E5A] hover:bg-[#4B6E5A]/5 hover:text-[#4B6E5A]">
                <Link href="#simulasi-ukt">Simulasi UKT</Link>
              </Button>
            </div>
          </div>

          <div className="relative mx-auto w-full max-w-md pb-10 lg:col-span-5 lg:max-w-none">
            <div aria-hidden className="absolute inset-0 bottom-10 translate-x-3 translate-y-3 rounded-2xl bg-[#4B6E5A]/10" />
            <Foto src={GAMBAR.hero} alt="Foto mahasiswa" priority sizes="(min-width: 1024px) 40vw, 90vw" className="aspect-[4/5] rounded-2xl" />
            <div className="absolute bottom-0 left-0 w-2/5 sm:-left-6">
              <Foto src={GAMBAR.heroKecil} alt="Suasana kampus" sizes="20vw" className="aspect-square rounded-2xl border-4 border-[#F5F6F5] shadow-lg" />
            </div>

            <div className="absolute left-3 top-6 flex items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-lg sm:-left-5">
              <span className="flex size-10 items-center justify-center rounded-full bg-[#D97706]/10 text-[#D97706]">
                <Star className="size-5 fill-current" />
              </span>
              <div>
                <p className="text-sm font-bold text-neutral-900">Akreditasi Unggul</p>
                <p className="text-xs text-neutral-500">BAN-PT</p>
              </div>
            </div>
            <div className="absolute bottom-16 right-3 flex items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-lg sm:-right-4">
              <span className="flex size-10 items-center justify-center rounded-full bg-[#4B6E5A]/10 text-[#4B6E5A]">
                <Users className="size-5" />
              </span>
              <div>
                <p className="text-sm font-bold text-neutral-900">10.000+</p>
                <p className="text-xs text-neutral-500">Mahasiswa aktif</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --------------------------- STATISTIK --------------------------- */}
      <section className="bg-[#4B6E5A] text-white">
        <dl className="mx-auto grid max-w-6xl grid-cols-2 gap-px bg-white/15 lg:grid-cols-4">
          {STATISTIK.map((s) => (
            <div key={s.label} className="bg-[#4B6E5A] px-6 py-9 sm:py-12 lg:px-8">
              <dd className="text-4xl font-extrabold tracking-tight sm:text-5xl">{s.nilai}</dd>
              <dt className="mt-2 text-sm text-white/70">{s.label}</dt>
            </div>
          ))}
        </dl>
      </section>

      <Profil />
      <ProgramStudi />
      <Jalur />
      <KalkulatorUkt />
      <Jadwal />
      <Pengumuman />

      {/* ----------------------------- FOOTER ----------------------------- */}
      <footer id="kontak" className="scroll-mt-16 bg-[#2F4A3B] text-white">
        <div className="mx-auto grid max-w-6xl gap-12 px-6 py-16 md:grid-cols-12">
          <div className="md:col-span-5">
            <Logo putih />
            <p className="mt-5 max-w-sm text-sm leading-relaxed text-white/65">
              Portal resmi penerimaan mahasiswa baru. Pendaftaran, verifikasi berkas, dan pengumuman hasil seleksi dilakukan secara daring.
            </p>
          </div>
          <div className="md:col-span-3">
            <p className="text-sm font-bold">Tautan cepat</p>
            <ul className="mt-5 space-y-3 text-sm text-white/65">
              {LINK_CEPAT.map((l) => (
                <li key={l.label}><Link href={l.href} className="transition-colors hover:text-white">{l.label}</Link></li>
              ))}
            </ul>
          </div>
          <div className="md:col-span-4">
            <p className="text-sm font-bold">Kontak panitia</p>
            <ul className="mt-5 space-y-4 text-sm text-white/65">
              {KONTAK.map((teks, i) => {
                const Icon = IKON_KONTAK[i];
                return (
                  <li key={teks} className="flex gap-3">
                    <Icon className="mt-0.5 size-4 shrink-0 text-white/50" />
                    <span>{teks}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
        <div className="border-t border-white/10">
          <p className="mx-auto max-w-6xl px-6 py-6 text-[13px] text-white/50">&copy; 2026 ADMITRA. Seluruh hak dilindungi.</p>
        </div>
      </footer>
    </div>
  );
}