"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  AuthShell,
  FieldError,
  PasswordInput,
  inputClass,
  labelClass,
} from "@/components/auth/auth-shell";

// Validasi lapis 1 (UI). Pola nomor WhatsApp sengaja sama dengan CHECK constraint
// chk_maba_no_hp di constraints.sql. Nanti dipindah ke src/validations/auth.js.
const registerSchema = z
  .object({
    namaLengkap: z
      .string()
      .trim()
      .min(3, "Nama minimal 3 karakter")
      .max(150, "Nama maksimal 150 karakter"),
    email: z
      .string()
      .trim()
      .min(1, "Email wajib diisi")
      .email("Format email tidak valid"),
    noWa: z
      .string()
      .trim()
      .regex(/^(\+62|62|0)8[0-9]{8,12}$/, "Gunakan format 08xxxxxxxxxx"),
    password: z
      .string()
      .min(8, "Minimal 8 karakter")
      .regex(/[A-Za-z]/, "Harus mengandung huruf")
      .regex(/[0-9]/, "Harus mengandung angka"),
    konfirmasi: z.string().min(1, "Konfirmasi kata sandi wajib diisi"),
  })
  .refine((d) => d.password === d.konfirmasi, {
    path: ["konfirmasi"],
    message: "Kata sandi tidak sama",
  });

export default function RegisterPage() {
  const router = useRouter();
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setFormError(null);

    const data = new FormData(e.currentTarget);
    const parsed = registerSchema.safeParse({
      namaLengkap: data.get("namaLengkap"),
      email: data.get("email"),
      noWa: data.get("noWa"),
      password: data.get("password"),
      konfirmasi: data.get("konfirmasi"),
    });

    if (!parsed.success) {
      const next = {};
      for (const issue of parsed.error.issues) {
        const key = issue.path[0];
        if (!next[key]) next[key] = issue.message;
      }
      setErrors(next);
      return;
    }

    setErrors({});
    setLoading(true);

    try {
      // TODO (langkah Supabase Auth + Prisma):
      // 1. supabase.auth.signUp({ email, password })
      // 2. Server action: buat baris calon_mahasiswa (auth_user_id, email, nama_lengkap, no_hp)
      await new Promise((resolve) => setTimeout(resolve, 900)); // simulasi

      router.push("/login");
    } catch {
      setFormError("Pendaftaran akun belum berhasil. Coba lagi sebentar lagi.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell wide>
      <h1 className="text-3xl font-extrabold tracking-tight text-neutral-900">
        Buat akun pendaftar
      </h1>
      <p className="mt-3 text-[15px] text-neutral-500">
        Sudah punya akun?{" "}
        <Link
          href="/login"
          className="font-semibold text-[#4B6E5A] underline-offset-4 hover:underline"
        >
          Masuk
        </Link>
      </p>

      <form onSubmit={onSubmit} noValidate className="mt-10">
        {formError && (
          <p
            role="alert"
            className="mb-6 rounded-lg border border-[#D97706]/30 bg-[#D97706]/5 px-4 py-3 text-sm font-medium text-[#B45309]"
          >
            {formError}
          </p>
        )}

        <div className="grid gap-x-6 gap-y-6 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Label htmlFor="namaLengkap" className={labelClass}>
              Nama lengkap
            </Label>
            <Input
              id="namaLengkap"
              name="namaLengkap"
              autoComplete="name"
              placeholder="Sesuai KTP atau ijazah"
              aria-invalid={!!errors.namaLengkap}
              className={`mt-2 ${inputClass}`}
            />
            <FieldError message={errors.namaLengkap} />
          </div>

          <div>
            <Label htmlFor="email" className={labelClass}>
              Email aktif
            </Label>
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="nama@email.com"
              aria-invalid={!!errors.email}
              className={`mt-2 ${inputClass}`}
            />
            <FieldError message={errors.email} />
          </div>

          <div>
            <Label htmlFor="noWa" className={labelClass}>
              Nomor WhatsApp
            </Label>
            <Input
              id="noWa"
              name="noWa"
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder="08123456789"
              aria-invalid={!!errors.noWa}
              className={`mt-2 ${inputClass}`}
            />
            <FieldError message={errors.noWa} />
          </div>

          <div>
            <Label htmlFor="password" className={labelClass}>
              Kata sandi
            </Label>
            <div className="mt-2">
              <PasswordInput
                id="password"
                name="password"
                autoComplete="new-password"
                placeholder="Minimal 8 karakter"
                aria-invalid={!!errors.password}
              />
            </div>
            {errors.password ? (
              <FieldError message={errors.password} />
            ) : (
              <p className="mt-1.5 text-[13px] text-neutral-400">
                Gabungan huruf dan angka.
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="konfirmasi" className={labelClass}>
              Konfirmasi kata sandi
            </Label>
            <div className="mt-2">
              <PasswordInput
                id="konfirmasi"
                name="konfirmasi"
                autoComplete="new-password"
                placeholder="Ulangi kata sandi"
                aria-invalid={!!errors.konfirmasi}
              />
            </div>
            <FieldError message={errors.konfirmasi} />
          </div>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="mt-10 h-12 w-full rounded-lg bg-[#4B6E5A] text-[15px] font-semibold text-white hover:bg-[#5C836A] disabled:opacity-70"
        >
          {loading ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Membuat akun
            </>
          ) : (
            "Buat akun"
          )}
        </Button>

        <p className="mt-5 text-center text-[13px] leading-relaxed text-neutral-400">
          Dengan membuat akun, Anda menyetujui ketentuan penggunaan portal
          penerimaan mahasiswa baru.
        </p>
      </form>
    </AuthShell>
  );
}