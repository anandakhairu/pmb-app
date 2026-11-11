"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  AuthShell,
  FieldError,
  PasswordInput,
  inputClass,
  labelClass,
} from "@/components/auth/auth-shell";

// Validasi lapis 1 (UI). Skema yang sama nanti dipindah ke src/validations/auth.js
// supaya bisa dipakai juga oleh API Route (lapis 2).
const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, "Email wajib diisi")
    .email("Format email tidak valid"),
  password: z.string().min(1, "Kata sandi wajib diisi"),
});

export default function LoginPage() {
  const router = useRouter();
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [remember, setRemember] = useState(false);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setFormError(null);

    const data = new FormData(e.currentTarget);
    const parsed = loginSchema.safeParse({
      email: data.get("email"),
      password: data.get("password"),
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
      // TODO (langkah Supabase Auth):
      // const { error } = await supabase.auth.signInWithPassword({
      //   email: parsed.data.email,
      //   password: parsed.data.password,
      // });
      // if (error) throw error;
      // `remember` menentukan apakah sesi disimpan persisten.
      await new Promise((resolve) => setTimeout(resolve, 700)); // simulasi

      router.push("/dashboard");
    } catch {
      setFormError("Email atau kata sandi tidak cocok. Periksa lalu coba lagi.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell>
      <h1 className="text-3xl font-extrabold tracking-tight text-neutral-900">
        Masuk ke portal
      </h1>
      <p className="mt-3 text-[15px] text-neutral-500">
        Belum punya akun?{" "}
        <Link
          href="/register"
          className="font-semibold text-[#4B6E5A] underline-offset-4 hover:underline"
        >
          Daftar sekarang
        </Link>
      </p>

      <form onSubmit={onSubmit} noValidate className="mt-10 space-y-6">
        {formError && (
          <p
            role="alert"
            className="rounded-lg border border-[#D97706]/30 bg-[#D97706]/5 px-4 py-3 text-sm font-medium text-[#B45309]"
          >
            {formError}
          </p>
        )}

        <div>
          <Label htmlFor="email" className={labelClass}>
            Email
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
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className={labelClass}>
              Kata sandi
            </Label>
            <Link
              href="/lupa-sandi"
              className="text-[13px] font-semibold text-[#4B6E5A] underline-offset-4 hover:underline"
            >
              Lupa kata sandi?
            </Link>
          </div>
          <div className="mt-2">
            <PasswordInput
              id="password"
              name="password"
              autoComplete="current-password"
              placeholder="Masukkan kata sandi"
              aria-invalid={!!errors.password}
            />
          </div>
          <FieldError message={errors.password} />
        </div>

        <div className="flex items-center gap-3">
          <Checkbox
            id="remember"
            checked={remember}
            onCheckedChange={(v) => setRemember(v === true)}
            className="size-[18px] rounded-[5px] border-neutral-300 data-[state=checked]:border-[#4B6E5A] data-[state=checked]:bg-[#4B6E5A]"
          />
          <Label
            htmlFor="remember"
            className="text-sm font-medium text-neutral-600"
          >
            Ingat saya
          </Label>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="h-12 w-full rounded-lg bg-[#4B6E5A] text-[15px] font-semibold text-white hover:bg-[#5C836A] disabled:opacity-70"
        >
          {loading ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Memproses
            </>
          ) : (
            "Masuk Portal"
          )}
        </Button>
      </form>
    </AuthShell>
  );
}
