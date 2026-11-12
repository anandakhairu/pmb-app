"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Dialog } from "radix-ui";
import {
  BarChart3,
  BookOpen,
  ClipboardCheck,
  FileCheck2,
  FolderSync,
  LogOut,
  Menu,
  ShieldCheck,
  Sliders,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import { Logo } from "@/components/logo";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const MENU_ADMIN = [
  {
    href: "/admin",
    label: "Analytics & Ringkasan",
    ikon: BarChart3,
    tepat: true,
  },
  {
    href: "/admin/verifikasi",
    label: "Antrean Verifikasi",
    ikon: FileCheck2,
    badge: "5 Antre",
  },
  {
    href: "/admin/master-data",
    label: "Master Data",
    ikon: BookOpen,
  },
  {
    href: "/admin/pengaturan",
    label: "Pengaturan & Web Push",
    ikon: Sliders,
  },
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

function NavMenu({ onNavigate }) {
  const pathname = usePathname();

  return (
    <nav aria-label="Menu admin" className="flex flex-col gap-1.5">
      {MENU_ADMIN.map(({ href, label, ikon: Ikon, tepat, badge }) => {
        const aktif = tepat ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            aria-current={aktif ? "page" : undefined}
            className={cn(
              "flex h-11 items-center gap-3 rounded-xl px-3.5 text-sm font-medium transition-all focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4B6E5A]",
              aktif
                ? "bg-[#4B6E5A] font-semibold text-white shadow-sm"
                : "text-neutral-600 hover:bg-neutral-100/90 hover:text-neutral-900"
            )}
          >
            <Ikon className={cn("size-4 shrink-0", aktif ? "text-white" : "text-neutral-500")} aria-hidden />
            <span className="flex-1 truncate">{label}</span>
            {badge && (
              <span
                className={cn(
                  "rounded-full px-2 py-0.5 text-[11px] font-bold tracking-tight",
                  aktif ? "bg-white/20 text-white" : "bg-[#D97706]/15 text-[#B45309]"
                )}
              >
                {badge}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}

function ProfilAdmin({ admin }) {
  return (
    <div className="rounded-xl border border-neutral-200/80 bg-neutral-50/70 p-3.5">
      <div className="flex items-center gap-3">
        <div
          aria-hidden
          className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[#4B6E5A]/15 text-sm font-bold text-[#2F4A3B]"
        >
          {inisial(admin.nama)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-bold text-neutral-900">{admin.nama}</p>
          <div className="mt-0.5 flex items-center gap-1.5">
            <span className="inline-block size-2 rounded-full bg-emerald-500" />
            <p className="truncate text-[11px] font-medium text-neutral-500">
              {admin.role} • PMB 2027
            </p>
          </div>
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-neutral-200/70 pt-2.5 text-xs text-neutral-500">
        <span>NIP: {admin.nip.slice(0, 10)}...</span>
        <Link
          href="/login"
          className="flex items-center gap-1 font-semibold text-neutral-600 hover:text-rose-600"
        >
          <LogOut className="size-3.5" /> Keluar
        </Link>
      </div>
    </div>
  );
}

export function AdminShell({ admin, children }) {
  const [mobileTerbuka, setMobileTerbuka] = useState(false);

  return (
    <div className="flex min-h-screen bg-[#F8F9F8] text-neutral-900">
      {/* ----------------------------- SIDEBAR DESKTOP ----------------------------- */}
      <aside className="sticky top-0 hidden h-screen w-72 shrink-0 flex-col border-r border-neutral-200/80 bg-white px-5 py-6 lg:flex">
        <div className="flex items-center justify-between px-1">
          <Logo />
          <Badge variant="outline" className="border-[#4B6E5A]/30 bg-[#4B6E5A]/10 text-[10px] font-extrabold text-[#2F4A3B]">
            BACK-OFFICE
          </Badge>
        </div>

        <div className="mt-8 flex-1 overflow-y-auto pr-1">
          <p className="mb-2.5 px-3 text-[11px] font-bold tracking-wider text-neutral-400 uppercase">
            Menu Utama
          </p>
          <NavMenu />

          <div className="mt-8 border-t border-neutral-100 pt-6">
            <p className="mb-2.5 px-3 text-[11px] font-bold tracking-wider text-neutral-400 uppercase">
              Tautan Cepat
            </p>
            <div className="flex flex-col gap-1 text-xs">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900"
              >
                <Users className="size-3.5 text-neutral-400" />
                Portal Calon Mahasiswa
              </Link>
              <Link
                href="/"
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900"
              >
                <Sparkles className="size-3.5 text-neutral-400" />
                Halaman Publik Portal
              </Link>
            </div>
          </div>
        </div>

        <div className="pt-4">
          <ProfilAdmin admin={admin} />
        </div>
      </aside>

      {/* ----------------------------- KONTEN & TOPBAR ----------------------------- */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* TOPBAR MOBILE */}
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-neutral-200/80 bg-white/95 px-4 backdrop-blur lg:hidden">
          <Logo />
          <button
            type="button"
            onClick={() => setMobileTerbuka(true)}
            aria-label="Buka menu admin"
            className="flex size-10 items-center justify-center rounded-lg border border-neutral-200 text-neutral-700 hover:bg-neutral-100"
          >
            <Menu className="size-5" />
          </button>
        </header>

        {/* DIALOG DRAWER MOBILE */}
        <Dialog.Root open={mobileTerbuka} onOpenChange={setMobileTerbuka}>
          <Dialog.Portal>
            <Dialog.Overlay className="fixed inset-0 z-40 bg-black/40 backdrop-blur-xs animate-in fade-in" />
            <Dialog.Content className="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-white p-5 shadow-2xl animate-in slide-in-from-left">
              <div className="flex items-center justify-between">
                <Logo />
                <Dialog.Close asChild>
                  <button
                    type="button"
                    aria-label="Tutup menu"
                    className="flex size-9 items-center justify-center rounded-lg border border-neutral-200 text-neutral-600 hover:bg-neutral-100"
                  >
                    <X className="size-4" />
                  </button>
                </Dialog.Close>
              </div>

              <div className="mt-6 flex-1 overflow-y-auto">
                <NavMenu onNavigate={() => setMobileTerbuka(false)} />
              </div>

              <div className="pt-4">
                <ProfilAdmin admin={admin} />
              </div>
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>

        {/* AREA UTAMA */}
        <main className="mx-auto w-full max-w-7xl flex-1 p-5 sm:p-8 lg:p-10">
          {children}
        </main>
      </div>
    </div>
  );
}
