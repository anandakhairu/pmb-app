"use client";

import { useState } from "react";
import { Calendar, Check, CheckCircle2, Layers, Loader2, Lock, Unlock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toggleJalurPendaftaranAction } from "@/lib/server/actions";
function getPeriodeJalur(kode) {
  switch (kode) {
    case "SNBP":
      return "3 Feb – 4 Mar 2027";
    case "SNBT":
      return "1 – 15 Apr 2027";
    case "MANDIRI":
      return "1 Mei – 30 Jun 2027";
    default:
      return "Sesuai Kalender Akademik";
  }
}

export function JalurManager({ initialJalur }) {
  const [daftarJalur, setDaftarJalur] = useState(initialJalur || []);
  const [loadingKode, setLoadingKode] = useState(null);
  const [pesanSukses, setPesanSukses] = useState(null);
  const [pesanError, setPesanError] = useState(null);

  async function handleToggle(kode, statusSekarang) {
    const statusBaru = !statusSekarang;
    setLoadingKode(kode);
    setPesanSukses(null);
    setPesanError(null);

    // Optimistic UI update
    setDaftarJalur((prev) =>
      prev.map((j) => (j.kode === kode ? { ...j, aktif: statusBaru } : j))
    );

    try {
      const res = await toggleJalurPendaftaranAction({
        kodeJalur: kode,
        aktif: statusBaru,
      });

      if (res.success) {
        setPesanSukses(
          `Pendaftaran ${kode === "MANDIRI" ? "Seleksi Mandiri" : kode} berhasil ${
            statusBaru ? "DIBUKA" : "DITUTUP"
          }!`
        );
      } else {
        // Revert on failure
        setDaftarJalur((prev) =>
          prev.map((j) => (j.kode === kode ? { ...j, aktif: statusSekarang } : j))
        );
        setPesanError(res.error || "Gagal mengubah status pendaftaran jalur.");
      }
    } catch {
      setDaftarJalur((prev) =>
        prev.map((j) => (j.kode === kode ? { ...j, aktif: statusSekarang } : j))
      );
      setPesanError("Terjadi kesalahan jaringan.");
    } finally {
      setLoadingKode(null);
    }
  }

  return (
    <div className="rounded-2xl border border-neutral-200/80 bg-white p-6 shadow-xs space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-neutral-100 gap-3">
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
            <Layers className="size-4.5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-neutral-900">
              Jalur Pendaftaran & Buka/Tutup Seleksi
            </h2>
            <p className="text-xs text-neutral-500">
              Admin dapat membuka atau menutup pendaftaran jalur (SNBP, SNBT, dan Seleksi Mandiri) secara langsung
            </p>
          </div>
        </div>
      </div>

      {pesanSukses && (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50/80 p-3 text-xs font-semibold text-emerald-800 animate-in fade-in">
          <CheckCircle2 className="size-4 text-emerald-600 shrink-0" />
          <span>{pesanSukses}</span>
        </div>
      )}

      {pesanError && (
        <div className="rounded-xl border border-rose-200 bg-rose-50/80 p-3 text-xs font-semibold text-rose-800 animate-in fade-in">
          {pesanError}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs font-bold uppercase tracking-wider text-neutral-400 border-b border-neutral-200/80">
            <tr>
              <th className="py-3 px-3">Kode Jalur</th>
              <th className="py-3 px-3">Nama Jalur Seleksi</th>
              <th className="py-3 px-3">Periode & Jadwal</th>
              <th className="py-3 px-3">Biaya Pendaftaran</th>
              <th className="py-3 px-3">Status Saat Ini</th>
              <th className="py-3 px-3 text-right">Aksi Admin</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100 text-neutral-700">
            {daftarJalur.map((jalur) => {
              const sedangProses = loadingKode === jalur.kode;
              const isBuka = jalur.aktif;

              return (
                <tr key={jalur.kode} className="hover:bg-neutral-50/70 transition-colors">
                  <td className="py-4 px-3 font-mono font-bold text-neutral-800">
                    {jalur.kode}
                  </td>
                  <td className="py-4 px-3">
                    <p className="font-semibold text-neutral-900">{jalur.nama}</p>
                    <p className="text-xs text-neutral-500">
                      {jalur.kode === "MANDIRI"
                        ? "Ujian Mandiri CBT Kampus & Verifikasi Berkas"
                        : jalur.kode === "SNBP"
                        ? "Penilaian Rapor & Sertifikat Prestasi"
                        : "Ujian Tulis Berbasis Komputer Nasional"}
                    </p>
                  </td>
                  <td className="py-4 px-3">
                    <div className="flex items-center gap-1.5 font-bold text-neutral-800 text-xs">
                      <Calendar className="size-3.5 text-[#4B6E5A] shrink-0" />
                      <span>{jalur.periode || getPeriodeJalur(jalur.kode)}</span>
                    </div>
                    <p className="text-[11px] text-neutral-500 mt-0.5">
                      Pengumuman: {jalur.pengumuman || "15 Juli 2027"}
                    </p>
                  </td>
                  <td className="py-4 px-3 font-mono text-neutral-700">
                    {jalur.biaya === 0 ? "Gratis" : `Rp ${jalur.biaya.toLocaleString("id-ID")}`}
                  </td>
                  <td className="py-4 px-3">
                    <Badge
                      variant={isBuka ? "success" : "secondary"}
                      className="text-xs font-bold inline-flex items-center gap-1.5"
                    >
                      <span
                        className={`size-1.5 rounded-full ${
                          isBuka ? "bg-emerald-500 animate-pulse" : "bg-neutral-400"
                        }`}
                      />
                      {isBuka ? "Pendaftaran Buka" : "Ditutup"}
                    </Badge>
                  </td>
                  <td className="py-4 px-3 text-right">
                    <Button
                      type="button"
                      size="sm"
                      disabled={sedangProses}
                      onClick={() => handleToggle(jalur.kode, isBuka)}
                      className={`h-8.5 rounded-xl px-3.5 text-xs font-semibold transition-all ${
                        isBuka
                          ? "border border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100"
                          : "bg-[#4B6E5A] text-white hover:bg-[#3B5746]"
                      }`}
                    >
                      {sedangProses ? (
                        <>
                          <Loader2 className="mr-1.5 size-3.5 animate-spin" />
                          <span>Menyimpan...</span>
                        </>
                      ) : isBuka ? (
                        <>
                          <Lock className="mr-1.5 size-3.5" />
                          <span>Tutup Pendaftaran</span>
                        </>
                      ) : (
                        <>
                          <Unlock className="mr-1.5 size-3.5" />
                          <span>Buka Pendaftaran</span>
                        </>
                      )}
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
