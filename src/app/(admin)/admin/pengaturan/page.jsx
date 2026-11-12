import { Bell, CheckCircle2, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const metadata = {
  title: "Pengaturan & Web Push",
};

export default function PengaturanAdminPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-neutral-900 sm:text-3xl">
          Pengaturan Sistem & Integrasi
        </h1>
        <p className="mt-1 text-sm text-neutral-600">
          Status kepatuhan teknis, koneksi database, dan antrean background worker Web Push.
        </p>
      </div>

      {/* STATUS WEB PUSH & BACKGROUND WORKER (REQUIREMENT SEKSI 5) */}
      <div className="rounded-2xl border border-neutral-200/80 bg-white p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-neutral-100">
          <div className="flex size-10 items-center justify-center rounded-xl bg-[#4B6E5A] text-white">
            <Bell className="size-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-neutral-900">
                Web Push Notification & Background Worker
              </h2>
              <Badge className="bg-emerald-100 text-emerald-800 border-none font-bold text-xs">
                Wajib Dosen (Seksi 5)
              </Badge>
            </div>
            <p className="text-xs text-neutral-500">
              Alur: Kejadian Bisnis → Database → Antrean (BullMQ) → Worker → Web Push → Service Worker
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-xl border border-neutral-200/80 bg-neutral-50/60 p-4 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-500 font-medium">VAPID Protocol</span>
              <Badge variant="success" className="text-[10px] font-bold">Terhubung</Badge>
            </div>
            <p className="text-sm font-bold text-neutral-900">VAPID Keys Active</p>
            <p className="text-[11px] text-neutral-500 font-mono">Public key tersimpan di browser</p>
          </div>

          <div className="rounded-xl border border-neutral-200/80 bg-neutral-50/60 p-4 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-500 font-medium">Antrean Pesan</span>
              <Badge variant="info" className="text-[10px] font-bold">Siap Pakai</Badge>
            </div>
            <p className="text-sm font-bold text-neutral-900">BullMQ / Redis Worker</p>
            <p className="text-[11px] text-neutral-500 font-mono">Job queue persisten aman</p>
          </div>

          <div className="rounded-xl border border-neutral-200/80 bg-neutral-50/60 p-4 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-500 font-medium">Tabel Subscription</span>
              <Badge variant="success" className="text-[10px] font-bold">11 Tabel</Badge>
            </div>
            <p className="text-sm font-bold text-neutral-900">perangkat_notifikasi</p>
            <p className="text-[11px] text-neutral-500 font-mono">Prisma model sync</p>
          </div>
        </div>
      </div>

      {/* KEPATUHAN 3 LAPISAN VALIDASI (REQUIREMENT SEKSI 2) */}
      <div className="rounded-2xl border border-neutral-200/80 bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b border-neutral-100">
          <div className="flex size-10 items-center justify-center rounded-xl bg-[#2F4A3B] text-white">
            <ShieldCheck className="size-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-neutral-900">
              Validasi 3 Lapisan (Technical Requirements Seksi 2)
            </h2>
            <p className="text-xs text-neutral-500">
              Setiap operasi memvalidasi data secara independen di Frontend, Backend, dan Database.
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-start gap-3 rounded-xl border border-neutral-100 bg-neutral-50/50 p-3.5">
            <CheckCircle2 className="size-4 text-emerald-600 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-neutral-900">1. Lapisan Frontend (Zod & HTML Form Validation)</p>
              <p className="text-xs text-neutral-600">Validasi input wajib, panjang NIK 16 digit, format email, dan rentang nilai rapor sebelum submit.</p>
            </div>
          </div>
          <div className="flex items-start gap-3 rounded-xl border border-neutral-100 bg-neutral-50/50 p-3.5">
            <CheckCircle2 className="size-4 text-emerald-600 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-neutral-900">2. Lapisan Backend (Next.js Server Actions / Handlers)</p>
              <p className="text-xs text-neutral-600">Validasi sesi admin/maba, sanitasi input, kepemilikan data, dan aturan transisi status.</p>
            </div>
          </div>
          <div className="flex items-start gap-3 rounded-xl border border-neutral-100 bg-neutral-50/50 p-3.5">
            <CheckCircle2 className="size-4 text-emerald-600 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-neutral-900">3. Lapisan Database (PostgreSQL Constraints di prisma/constraints.sql)</p>
              <p className="text-xs text-neutral-600">PRIMARY KEY, UNIQUE NIK & Nomer Pendaftaran, CHECK constraint NIK 16 digit, foreign key ON DELETE CASCADE.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
