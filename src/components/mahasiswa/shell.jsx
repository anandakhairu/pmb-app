"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Dialog } from "radix-ui";
import {
  FolderUp,
  GraduationCap,
  House,
  LogOut,
  Menu,
  UserRound,
  X,
} from "lucide-react";
import { Logo } from "@/components/logo";
import { cn } from "@/lib/utils";

const MENU = [
  { href: "/dashboard", label: "Beranda", ikon: House, tepat: true },
  { href: "/dashboard/biodata", label: "Biodata", ikon: UserRound },
  { href: "/dashboard/berkas", label: "Unggah Berkas", ikon: FolderUp, kunciPerhatian: "berkas" },
  { href: "/dashboard/kelulusan", label: "Hasil Seleksi", ikon: GraduationCap },
];

function inisial(nama) {
  return nama
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((k) => k[0])
    .join("")
    .toUpperCase();
}

function NavMenu({ perhatian, onNavigate }) {
  const pathname = usePathname();

  return (
    <nav aria-label="Menu pendaftar" className="flex flex-col gap-1">
      {MENU.map(({ href, label, ikon: Ikon, tepat, kunciPerhatian }) => {
        const aktif = tepat ? pathname === href : pathname.startsWith(href);
        const butuhPerhatian = kunciPerhatian && perhatian?.[kunciPerhatian];
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            aria-current={aktif ? "page" : undefined}
            className={cn(
              "flex h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4B6E5A]",
              aktif
                ? "bg-[#4B6E5A]/10 font-bold text-[#2F4A3B]"
                : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900",
            )}
          >
            <Ikon className={cn("size-[18px]", aktif && "text-[#4B6E5A]")} aria-hidden />
            <span className="flex-1">{label}</span>
            {butuhPerhatian && (
              <>
                <span aria-hidden className="size-2 rounded-full bg-[#D97706]" />
                <span className="sr-only">Perlu tindakan</span>
              </>
            )}
          </Link>
        );
      })}
    </nav>
  );
}

function ProfilPengguna({ nama, nomor }) {
  return (
    <div className="border-t border-neutral-200 pt-4">
      <div className="flex items-center gap-3 px-1">
        <span
          aria-hidden
          className="flex size-9 shrink-0 items-center justify-center rounded-full bg-[#4B6E5A] text-xs font-bold text-white"
        >
          {inisial(nama)}
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-bold text-neutral-900">{nama}</p>
          <p className="truncate text-xs text-neutral-500">{nomor ?? "Nomor pendaftaran belum terbit"}</p>
        </div>
      </div>
      {/* TODO (Supabase Auth): ganti dengan aksi keluar, mis. supabase.auth.signOut() lalu redirect. */}
      <Link
        href="/login"
        className="mt-3 flex h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium text-neutral-600 transition-colors hover:bg-neutral-100 hover:text-neutral-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4B6E5A]"
      >
        <LogOut className="size-[18px]" aria-hidden />
        Keluar
      </Link>
    </div>
  );
}

/**
 * Kerangka halaman pendaftar.
 * Desktop: sidebar tetap di kiri. Mobile: topbar dengan drawer.
 * Semua bagian navigasi disembunyikan saat dicetak (halaman bukti kelulusan).
 */
export function MahasiswaShell({ nama, nomor, perhatian, children }) {
  const [terbuka, setTerbuka] = useState(false);

  return (
    <div className="min-h-screen bg-[#F5F6F5]">
      {/* Sidebar desktop */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col justify-between border-r border-neutral-200 bg-white p-5 lg:flex print:hidden">
        <div>
          <Logo className="px-1 pb-8 pt-1" />
          <NavMenu perhatian={perhatian} />
        </div>
        <ProfilPengguna nama={nama} nomor={nomor} />
      </aside>

      {/* Topbar mobile */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-neutral-200 bg-white/90 px-5 py-3 backdrop-blur lg:hidden print:hidden">
        <Logo />
        <Dialog.Root open={terbuka} onOpenChange={setTerbuka}>
          <Dialog.Trigger
            aria-label="Buka menu"
            className="flex size-10 items-center justify-center rounded-lg text-neutral-700 hover:bg-neutral-100 focus-visible:outline-2 focus-visible:outline-[#4B6E5A]"
          >
            <Menu className="size-5" aria-hidden />
          </Dialog.Trigger>
          <Dialog.Portal>
            <Dialog.Overlay className="fixed inset-0 z-40 bg-[#2F4A3B]/40 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=closed]:animate-out data-[state=closed]:fade-out-0" />
            <Dialog.Content
              aria-describedby={undefined}
              className="fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col justify-between bg-white p-5 outline-none data-[state=open]:animate-in data-[state=open]:slide-in-from-left data-[state=closed]:animate-out data-[state=closed]:slide-out-to-left"
            >
              <div>
                <div className="flex items-center justify-between pb-8">
                  <Dialog.Title className="sr-only">Menu pendaftar</Dialog.Title>
                  <Logo className="px-1" />
                  <Dialog.Close
                    aria-label="Tutup menu"
                    className="flex size-10 items-center justify-center rounded-lg text-neutral-600 hover:bg-neutral-100 focus-visible:outline-2 focus-visible:outline-[#4B6E5A]"
                  >
                    <X className="size-5" aria-hidden />
                  </Dialog.Close>
                </div>
                <NavMenu perhatian={perhatian} onNavigate={() => setTerbuka(false)} />
              </div>
              <ProfilPengguna nama={nama} nomor={nomor} />
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>
      </header>

      <main className="lg:pl-64 print:pl-0">
        <div className="mx-auto max-w-4xl px-5 py-8 sm:px-8 sm:py-12 print:max-w-none print:p-0">
          {children}
        </div>
      </main>
    </div>
  );
}
