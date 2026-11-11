"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Logo } from "@/components/logo";
import { cn } from "@/lib/utils";

/** Gaya input & label yang dipakai bersama oleh halaman login dan register. */
export const inputClass =
  "h-12 rounded-lg border-neutral-200 bg-white px-4 text-[15px] shadow-none placeholder:text-neutral-400 focus-visible:border-[#4B6E5A] focus-visible:ring-[3px] focus-visible:ring-[#4B6E5A]/15";

export const labelClass = "text-[13px] font-semibold text-neutral-700";

/**
 * Layout split-screen 100vh.
 * Kiri (desktop saja): panel Dark Sage Green dengan logo ADMITRA.
 * Kanan: area form.
 */
export function AuthShell({ children, wide = false }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <aside className="hidden flex-col justify-between bg-[#4B6E5A] p-12 text-white lg:flex xl:p-16">
        <div aria-hidden />

        <div className="flex flex-col items-center text-center">
          <Link href="/" aria-label="ADMITRA, ke beranda">
            <Image
              src="/admitra-logo-putih.png"
              alt="ADMITRA"
              width={720}
              height={662}
              priority
              className="h-auto w-60 xl:w-72"
            />
          </Link>
          <p className="mt-10 max-w-sm text-base leading-relaxed text-white/70">
            Satu akun untuk seluruh proses pendaftaran, dari pengisian formulir
            sampai pengumuman hasil seleksi.
          </p>
        </div>

        <p className="text-center text-sm text-white/50">&copy; 2026 ADMITRA</p>
      </aside>

      <main className="flex min-h-screen flex-col bg-white px-6 py-8 sm:p-12">
        <div className="mb-10 lg:hidden">
          <Logo />
        </div>

        <div className="flex flex-1 items-center justify-center">
          <div className={cn("w-full", wide ? "max-w-xl" : "max-w-sm")}>
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}

/** Pesan error validasi di bawah field. Memakai aksen amber dari palet. */
export function FieldError({ message }) {
  if (!message) return null;
  return (
    <p role="alert" className="mt-1.5 text-[13px] font-medium text-[#B45309]">
      {message}
    </p>
  );
}

/** Input kata sandi dengan tombol tampilkan/sembunyikan. */
export function PasswordInput({ className, ...props }) {
  const [show, setShow] = useState(false);

  return (
    <div className="relative">
      <Input
        {...props}
        type={show ? "text" : "password"}
        className={cn(inputClass, "pr-12", className)}
      />
      <button
        type="button"
        onClick={() => setShow((v) => !v)}
        aria-label={show ? "Sembunyikan kata sandi" : "Tampilkan kata sandi"}
        className="absolute inset-y-0 right-0 flex w-12 items-center justify-center rounded-r-lg text-neutral-400 transition-colors hover:text-neutral-700 focus-visible:outline-none focus-visible:text-[#4B6E5A]"
      >
        {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
      </button>
    </div>
  );
}