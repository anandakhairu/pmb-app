import Link from "next/link";
import {
  ArrowRight,
  Check,
  CircleAlert,
  CircleCheck,
  Clock,
  Info,
  TriangleAlert,
} from "lucide-react";
import { LABEL_VERIFIKASI } from "@/lib/berkas";
import { cn } from "@/lib/utils";

/* ------------------------------ BADGE STATUS ------------------------------ */

const GAYA_BADGE = {
  BELUM_ADA: "border-neutral-200 bg-neutral-100 text-neutral-600",
  MENUNGGU: "border-[#4B6E5A]/20 bg-[#4B6E5A]/8 text-[#2F4A3B]",
  VALID: "border-[#4B6E5A]/30 bg-[#4B6E5A] text-white",
  REVISI: "border-[#D97706]/30 bg-[#D97706]/10 text-[#B45309]",
};

const IKON_BADGE = {
  BELUM_ADA: CircleAlert,
  MENUNGGU: Clock,
  VALID: Check,
  REVISI: TriangleAlert,
};

/** status = BELUM_ADA | MENUNGGU | VALID | REVISI */
export function StatusBadge({ status, className }) {
  const Ikon = IKON_BADGE[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold",
        GAYA_BADGE[status],
        className,
      )}
    >
      <Ikon className="size-3.5" aria-hidden />
      {LABEL_VERIFIKASI[status]}
    </span>
  );
}

/* --------------------------- KOTAK PEMBERITAHUAN --------------------------- */

const GAYA_NOTIF = {
  info: { kotak: "border-neutral-200 bg-white", ikon: "text-[#4B6E5A]", Ikon: Info },
  tunggu: { kotak: "border-neutral-200 bg-white", ikon: "text-[#4B6E5A]", Ikon: Clock },
  peringatan: { kotak: "border-[#D97706]/30 bg-[#D97706]/5", ikon: "text-[#D97706]", Ikon: TriangleAlert },
  sukses: { kotak: "border-[#4B6E5A]/30 bg-[#4B6E5A]/5", ikon: "text-[#4B6E5A]", Ikon: CircleCheck },
};

/**
 * Pemberitahuan dengan satu aksi. nada = info | tunggu | peringatan | sukses.
 * Aksi opsional: { href, label }.
 */
export function Pemberitahuan({ nada = "info", judul, isi, aksi }) {
  const { kotak, ikon, Ikon } = GAYA_NOTIF[nada];
  return (
    <div
      role={nada === "peringatan" ? "alert" : "status"}
      className={cn("flex gap-4 rounded-xl border p-5", kotak)}
    >
      <Ikon className={cn("mt-0.5 size-5 shrink-0", ikon)} aria-hidden />
      <div className="min-w-0 flex-1">
        <p className="text-[15px] font-bold text-neutral-900">{judul}</p>
        <p className="mt-1 text-sm leading-relaxed text-neutral-600">{isi}</p>
        {aksi && (
          <Link
            href={aksi.href}
            className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-[#4B6E5A] underline-offset-4 hover:text-[#2F4A3B] hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4B6E5A]"
          >
            {aksi.label}
            <ArrowRight className="size-4" aria-hidden />
          </Link>
        )}
      </div>
    </div>
  );
}

/* --------------------------------- STEPPER -------------------------------- */

const TAHAP = [
  { judul: "Draft", ket: "Isi formulir" },
  { judul: "Berkas", ket: "Unggah dokumen" },
  { judul: "Verifikasi", ket: "Diperiksa panitia" },
  { judul: "Hasil", ket: "Pengumuman seleksi" },
];

/**
 * Stepper horizontal. indeks = tahap yang sedang berjalan (0 sampai 3);
 * indeks 4 berarti semua tahap selesai. peringatan = tahap berjalan butuh perbaikan.
 */
export function Stepper({ indeks, peringatan = false }) {
  return (
    <ol className="grid grid-cols-4" aria-label="Tahapan pendaftaran">
      {TAHAP.map((t, i) => {
        const selesai = i < indeks;
        const berjalan = i === indeks;
        const bermasalah = berjalan && peringatan;
        return (
          <li
            key={t.judul}
            aria-current={berjalan ? "step" : undefined}
            className="relative flex flex-col items-center text-center"
          >
            {/* Garis penghubung ke tahap berikutnya */}
            {i < TAHAP.length - 1 && (
              <span
                aria-hidden
                className={cn(
                  "absolute left-1/2 top-[18px] h-0.5 w-full",
                  selesai ? "bg-[#4B6E5A]" : "bg-neutral-200",
                )}
              />
            )}
            <span
              className={cn(
                "relative z-10 flex size-9 items-center justify-center rounded-full border-2 text-sm font-bold",
                selesai && "border-[#4B6E5A] bg-[#4B6E5A] text-white",
                berjalan && !bermasalah && "border-[#4B6E5A] bg-white text-[#4B6E5A]",
                bermasalah && "border-[#D97706] bg-white text-[#D97706]",
                !selesai && !berjalan && "border-neutral-200 bg-white text-neutral-400",
              )}
            >
              {selesai ? (
                <Check className="size-4" aria-hidden />
              ) : bermasalah ? (
                <TriangleAlert className="size-4" aria-hidden />
              ) : (
                i + 1
              )}
            </span>
            <span
              className={cn(
                "mt-3 text-[13px] font-bold sm:text-sm",
                selesai || berjalan ? "text-neutral-900" : "text-neutral-400",
              )}
            >
              {t.judul}
            </span>
            <span className="mt-0.5 hidden text-xs text-neutral-500 sm:block">
              {bermasalah ? "Perlu perbaikan" : t.ket}
            </span>
            <span className="sr-only">
              {selesai ? "Selesai" : berjalan ? (bermasalah ? "Perlu perbaikan" : "Sedang berjalan") : "Belum dimulai"}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
