"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  ChevronDown,
  FileText,
  FolderUp,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  MessageSquareText,
  Sliders,
  User,
} from "lucide-react";
import { Button } from "@/components/ui/button";

function getActiveSession() {
  if (typeof window === "undefined") return null;
  try {
    const local = localStorage.getItem("pmb_session");
    if (local) return JSON.parse(local);
  } catch {}
  try {
    const match = document.cookie.match(/(?:^|;\s*)pmb_session=([^;]+)/);
    if (match) return JSON.parse(decodeURIComponent(match[1]));
  } catch {}
  return null;
}

export function UserNav() {
  const [user, setUser] = useState(null);
  const [menuBuka, setMenuBuka] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    let batalkan = false;

    const sync = async () => {
      const active = getActiveSession();
      if (!batalkan) setUser(active);

      // Sinkronkan nama lengkap asli sesuai ijazah/database jika ada email aktif
      if (active?.email) {
        try {
          const { ambilProfilPenggunaAction } = await import("@/lib/server/actions");
          const profil = await ambilProfilPenggunaAction(active.email);
          if (!batalkan && profil?.nama && profil.nama !== active.nama) {
            const updated = { ...active, nama: profil.nama, role: profil.role };
            try {
              localStorage.setItem("pmb_session", JSON.stringify(updated));
            } catch {}
            document.cookie = `pmb_session=${encodeURIComponent(JSON.stringify(updated))}; path=/; max-age=604800; SameSite=Lax`;
            setUser(updated);
          }
        } catch {}
      }
    };

    window.addEventListener("storage", sync);
    window.addEventListener("pmb_session_event", sync);

    const timer = setTimeout(sync, 0);

    return () => {
      batalkan = true;
      clearTimeout(timer);
      window.removeEventListener("storage", sync);
      window.removeEventListener("pmb_session_event", sync);
    };
  }, []);

  // Tutup dropdown saat klik di luar
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setMenuBuka(false);
      }
    }
    if (menuBuka) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [menuBuka]);

  function handleLogout() {
    try {
      localStorage.removeItem("pmb_session");
    } catch {}
    document.cookie = "pmb_session=; path=/; max-age=0;";
    setUser(null);
    setMenuBuka(false);
    window.dispatchEvent(new Event("pmb_session_event"));
  }

  if (user) {
    const isAdmin = user.role === "ADMIN";
    const inisial = user.nama ? user.nama.slice(0, 2).toUpperCase() : "AU";

    return (
      <div className="relative flex items-center gap-2.5" ref={dropdownRef}>
        {/* Tombol Profil dengan Dropdown Pengaturan */}
        <button
          type="button"
          onClick={() => setMenuBuka((prev) => !prev)}
          className="flex items-center gap-2.5 rounded-xl border border-neutral-200/90 bg-white px-3 py-1.5 shadow-2xs transition-all hover:border-[#4B6E5A] focus-visible:outline-2 focus-visible:outline-[#4B6E5A]"
          aria-expanded={menuBuka}
          aria-haspopup="true"
        >
          <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-[#4B6E5A] text-xs font-bold text-white shadow-2xs">
            {inisial}
          </span>
          <div className="flex flex-col text-left">
            <span className="text-xs font-bold text-neutral-900 leading-tight">
              {user.nama}
            </span>
            <span className="text-[10px] text-neutral-500 font-medium">
              {isAdmin ? "Admin PMB" : "Calon Mahasiswa"}
            </span>
          </div>
          <ChevronDown
            className={`size-3.5 text-neutral-400 transition-transform ${
              menuBuka ? "rotate-180" : ""
            }`}
          />
        </button>

        {/* Tombol Cepat Buka Dashboard */}
        <Button
          asChild
          className="hidden sm:flex h-10 rounded-lg bg-[#4B6E5A] px-4 text-sm font-semibold text-white hover:bg-[#5C836A] shadow-xs"
        >
          <Link href={isAdmin ? "/admin" : "/dashboard"}>
            {isAdmin ? "Panel Admin" : "Buka Dashboard"}
          </Link>
        </Button>

        {/* DROPDOWN MENU PENGATURAN PROFIL */}
        {menuBuka && (
          <div className="absolute right-0 top-full mt-2 w-64 rounded-2xl border border-neutral-200/90 bg-white p-2 shadow-xl animate-in fade-in zoom-in-95 z-50">
            {/* Header Profil */}
            <div className="border-b border-neutral-100 p-3 pb-3.5">
              <p className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">
                Akun Terhubung
              </p>
              <p className="mt-1 font-bold text-neutral-900 text-sm truncate">
                {user.nama}
              </p>
              <p className="text-xs text-neutral-500 truncate font-mono">
                {user.email}
              </p>
              <span className="mt-2 inline-block rounded-md bg-[#4B6E5A]/10 px-2 py-0.5 text-[10px] font-bold text-[#4B6E5A]">
                {isAdmin ? "Administrator Panitia" : "Akun Calon Mahasiswa"}
              </span>
            </div>

            {/* Menu Navigasi Profil */}
            <div className="py-2 text-xs space-y-0.5">
              <Link
                href={isAdmin ? "/admin" : "/dashboard"}
                onClick={() => setMenuBuka(false)}
                className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-neutral-700 hover:bg-neutral-100 hover:text-[#4B6E5A] font-medium"
              >
                <LayoutDashboard className="size-4 text-neutral-500" />
                <span>{isAdmin ? "Dashboard Analytics" : "Beranda Dashboard"}</span>
              </Link>

              {!isAdmin ? (
                <>
                  <Link
                    href="/dashboard/biodata"
                    onClick={() => setMenuBuka(false)}
                    className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-neutral-700 hover:bg-neutral-100 hover:text-[#4B6E5A] font-medium"
                  >
                    <User className="size-4 text-neutral-500" />
                    <span>Lengkapi Biodata</span>
                  </Link>
                  <Link
                    href="/dashboard/berkas"
                    onClick={() => setMenuBuka(false)}
                    className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-neutral-700 hover:bg-neutral-100 hover:text-[#4B6E5A] font-medium"
                  >
                    <FolderUp className="size-4 text-neutral-500" />
                    <span>Unggah Berkas</span>
                  </Link>
                  <Link
                    href="/dashboard/kelulusan"
                    onClick={() => setMenuBuka(false)}
                    className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-neutral-700 hover:bg-neutral-100 hover:text-[#4B6E5A] font-medium"
                  >
                    <GraduationCap className="size-4 text-neutral-500" />
                    <span>Hasil Seleksi</span>
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/admin/verifikasi"
                    onClick={() => setMenuBuka(false)}
                    className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-neutral-700 hover:bg-neutral-100 hover:text-[#4B6E5A] font-medium"
                  >
                    <FileText className="size-4 text-neutral-500" />
                    <span>Antrean Verifikasi Berkas</span>
                  </Link>
                  <Link
                    href="/admin/chat"
                    onClick={() => setMenuBuka(false)}
                    className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-neutral-700 hover:bg-neutral-100 hover:text-[#4B6E5A] font-medium"
                  >
                    <MessageSquareText className="size-4 text-neutral-500" />
                    <span>Chat ADMITRA</span>
                  </Link>
                  <Link
                    href="/admin/pengaturan"
                    onClick={() => setMenuBuka(false)}
                    className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-neutral-700 hover:bg-neutral-100 hover:text-[#4B6E5A] font-medium"
                  >
                    <Sliders className="size-4 text-neutral-500" />
                    <span>Pengaturan Sistem</span>
                  </Link>
                </>
              )}
            </div>

            {/* Tombol Logout */}
            <div className="border-t border-neutral-100 pt-1">
              <button
                type="button"
                onClick={handleLogout}
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-xs font-semibold text-rose-600 hover:bg-rose-50 transition-colors"
              >
                <LogOut className="size-4 text-rose-500" />
                <span>Keluar dari Akun</span>
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Button asChild variant="ghost" className="h-10 rounded-lg px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-200/60">
        <Link href="/login">Masuk</Link>
      </Button>
      <Button asChild className="h-10 rounded-lg bg-[#4B6E5A] px-5 text-sm font-semibold text-white hover:bg-[#5C836A]">
        <Link href="/register">Daftar</Link>
      </Button>
    </div>
  );
}

export function HeroCta() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    let batalkan = false;

    const sync = async () => {
      const active = getActiveSession();
      if (!batalkan) setUser(active);

      // Sinkronkan nama lengkap asli sesuai ijazah/database jika ada email aktif
      if (active?.email) {
        try {
          const { ambilProfilPenggunaAction } = await import("@/lib/server/actions");
          const profil = await ambilProfilPenggunaAction(active.email);
          if (!batalkan && profil?.nama && profil.nama !== active.nama) {
            const updated = { ...active, nama: profil.nama, role: profil.role };
            try {
              localStorage.setItem("pmb_session", JSON.stringify(updated));
            } catch {}
            document.cookie = `pmb_session=${encodeURIComponent(JSON.stringify(updated))}; path=/; max-age=604800; SameSite=Lax`;
            setUser(updated);
          }
        } catch {}
      }
    };

    window.addEventListener("storage", sync);
    window.addEventListener("pmb_session_event", sync);

    const timer = setTimeout(sync, 0);

    return () => {
      batalkan = true;
      clearTimeout(timer);
      window.removeEventListener("storage", sync);
      window.removeEventListener("pmb_session_event", sync);
    };
  }, []);

  if (user) {
    return (
      <div className="mt-10 flex flex-col gap-3 sm:flex-row">
        <Button asChild size="lg" className="h-12 rounded-lg bg-[#4B6E5A] px-8 text-[15px] font-semibold text-white hover:bg-[#5C836A]">
          <Link href={user.role === "ADMIN" ? "/admin" : "/dashboard"}>
            Lanjutkan ke Dashboard ({user.nama?.split(" ")[0] || "Saya"})
          </Link>
        </Button>
        <Button asChild size="lg" variant="outline" className="h-12 rounded-lg border-[#4B6E5A]/30 bg-transparent px-8 text-[15px] font-semibold text-[#4B6E5A] hover:bg-[#4B6E5A]/5 hover:text-[#4B6E5A]">
          <Link href="#simulasi-ukt">Simulasi UKT</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mt-10 flex flex-col gap-3 sm:flex-row">
      <Button asChild size="lg" className="h-12 rounded-lg bg-[#4B6E5A] px-8 text-[15px] font-semibold text-white hover:bg-[#5C836A]">
        <Link href="/register">Daftar Sekarang</Link>
      </Button>
      <Button asChild size="lg" variant="outline" className="h-12 rounded-lg border-[#4B6E5A]/30 bg-transparent px-8 text-[15px] font-semibold text-[#4B6E5A] hover:bg-[#4B6E5A]/5 hover:text-[#4B6E5A]">
        <Link href="#simulasi-ukt">Simulasi UKT</Link>
      </Button>
    </div>
  );
}
