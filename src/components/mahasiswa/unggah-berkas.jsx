"use client";

import { useState } from "react";
import { CircleCheck, FileText, Loader2, Send, TriangleAlert, Upload, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/mahasiswa/status";
import {
  ACCEPT_BERKAS,
  BATAS_UKURAN_BYTE,
  formatUkuran,
  validasiBerkas,
} from "@/lib/berkas";
import { cn } from "@/lib/utils";

const jeda = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * dokumen: hasil gabungkanBerkas() (daftar dokumen + berkas yang sudah ada).
 * statusBerkas: status_berkas pada formulir.
 */
export function UnggahBerkas({ dokumen, statusBerkas }) {
  const [status, setStatus] = useState(statusBerkas);
  const [daftar, setDaftar] = useState(dokumen);
  const [pilihan, setPilihan] = useState({}); // jenis -> File yang menunggu diunggah
  const [galat, setGalat] = useState({}); // jenis -> pesan error
  const [sibuk, setSibuk] = useState({}); // jenis -> sedang diunggah
  const [seretDi, setSeretDi] = useState(null);
  const [mengirim, setMengirim] = useState(false);
  const [galatKirim, setGalatKirim] = useState(null);

  const formulirBisaDiubah = status === "DRAFT" || status === "REVISI";
  const wajib = daftar.filter((d) => d.wajib);
  const wajibLengkap = wajib.every((d) => d.berkas);
  const adaRevisi = daftar.some((d) => d.status === "REVISI");
  const bisaKirim = formulirBisaDiubah && wajibLengkap && !adaRevisi;

  function pilihBerkas(jenis, file) {
    if (!file) return;
    const pesan = validasiBerkas(file);
    setGalat((g) => ({ ...g, [jenis]: pesan }));
    setPilihan((p) => ({ ...p, [jenis]: pesan ? undefined : file }));
  }

  async function unggah(jenis) {
    const file = pilihan[jenis];
    if (!file) return;
    setSibuk((s) => ({ ...s, [jenis]: true }));
    setGalat((g) => ({ ...g, [jenis]: null }));

    try {
      // TODO (Supabase Storage + server action/route handler):
      // 1. Server memvalidasi ulang tipe, ukuran, dan kepemilikan formulir (lapis 2).
      // 2. Berkas disimpan ke bucket privat, path disimpan ke berkas_dokumen.storage_path.
      // 3. Unggah ulang jenis yang sama = replace (unik pada formulir_id + jenis).
      await jeda(800); // simulasi

      setDaftar((d) =>
        d.map((x) =>
          x.jenis === jenis
            ? {
                ...x,
                status: "MENUNGGU",
                berkas: {
                  jenis,
                  statusVerifikasi: "MENUNGGU",
                  catatan: null,
                  namaFile: file.name,
                  mimeType: file.type,
                  ukuranByte: file.size,
                },
              }
            : x,
        ),
      );
      setPilihan((p) => ({ ...p, [jenis]: undefined }));
    } catch {
      setGalat((g) => ({ ...g, [jenis]: "Berkas gagal diunggah. Periksa koneksi lalu coba lagi." }));
    } finally {
      setSibuk((s) => ({ ...s, [jenis]: false }));
    }
  }

  async function kirim() {
    setGalatKirim(null);
    setMengirim(true);
    try {
      // TODO: server action yang mengubah status_berkas menjadi DIKIRIM, menerbitkan
      // nomor_pendaftaran + finalisasi_at, lalu mengantre notifikasi Web Push ke admin.
      await jeda(900); // simulasi
      setStatus("DIKIRIM");
    } catch {
      setGalatKirim("Berkas belum terkirim. Coba lagi beberapa saat.");
    } finally {
      setMengirim(false);
    }
  }

  return (
    <div>
      {!formulirBisaDiubah && (
        <p
          role="status"
          className="mb-6 flex items-start gap-3 rounded-xl border border-neutral-200 bg-white p-4 text-sm text-neutral-600"
        >
          <CircleCheck className="mt-0.5 size-4 shrink-0 text-[#4B6E5A]" aria-hidden />
          {status === "TERVERIFIKASI"
            ? "Semua berkas sudah terverifikasi, jadi tidak bisa diubah lagi."
            : "Berkas sudah terkirim dan sedang diproses panitia. Pengunggahan dikunci sampai pemeriksaan selesai."}
        </p>
      )}

      <ul className="divide-y divide-neutral-200 border-y border-neutral-200">
        {daftar.map((d) => {
          const bisaDiubah = formulirBisaDiubah && d.status !== "VALID";
          const file = pilihan[d.jenis];
          const pesan = galat[d.jenis];
          const idInput = `berkas-${d.jenis}`;
          const idPetunjuk = `petunjuk-${d.jenis}`;

          return (
            <li key={d.jenis} className="py-7">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="text-[15px] font-bold text-neutral-900">
                    {d.nama}
                    <span className="ml-2 text-xs font-medium text-neutral-500">
                      {d.wajib ? "Wajib" : "Opsional"}
                    </span>
                  </h3>
                  <p id={idPetunjuk} className="mt-1 text-sm text-neutral-500">{d.petunjuk}</p>
                </div>
                <StatusBadge status={d.status} />
              </div>

              {d.status === "REVISI" && d.berkas?.catatan && (
                <p className="mt-4 flex items-start gap-2.5 rounded-lg border border-[#D97706]/30 bg-[#D97706]/5 px-4 py-3 text-sm text-[#B45309]">
                  <TriangleAlert className="mt-0.5 size-4 shrink-0" aria-hidden />
                  <span><span className="font-semibold">Catatan panitia: </span>{d.berkas.catatan}</span>
                </p>
              )}

              {d.berkas && !file && (
                <p className="mt-4 flex items-center gap-2.5 text-sm text-neutral-700">
                  <FileText className="size-4 shrink-0 text-[#4B6E5A]" aria-hidden />
                  <span className="truncate font-medium">{d.berkas.namaFile}</span>
                  <span className="shrink-0 text-neutral-500">{formatUkuran(d.berkas.ukuranByte)}</span>
                </p>
              )}

              {bisaDiubah && (
                <div className="mt-4">
                  {file ? (
                    <div className="flex flex-wrap items-center gap-3 rounded-lg border border-neutral-200 bg-white p-3 pl-4">
                      <FileText className="size-4 shrink-0 text-[#4B6E5A]" aria-hidden />
                      <span className="min-w-0 flex-1 truncate text-sm font-medium text-neutral-900">{file.name}</span>
                      <span className="text-sm text-neutral-500">{formatUkuran(file.size)}</span>
                      <Button
                        type="button"
                        onClick={() => unggah(d.jenis)}
                        disabled={sibuk[d.jenis]}
                        className="h-9 rounded-lg bg-[#4B6E5A] px-4 text-sm font-semibold text-white hover:bg-[#5C836A]"
                      >
                        {sibuk[d.jenis] ? (
                          <><Loader2 className="size-4 animate-spin" aria-hidden />Mengunggah</>
                        ) : (
                          "Unggah"
                        )}
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        aria-label={`Batalkan pilihan berkas ${d.nama}`}
                        disabled={sibuk[d.jenis]}
                        onClick={() => setPilihan((p) => ({ ...p, [d.jenis]: undefined }))}
                        className="size-9 rounded-lg text-neutral-500"
                      >
                        <X aria-hidden />
                      </Button>
                    </div>
                  ) : (
                    <label
                      htmlFor={idInput}
                      onDragOver={(e) => { e.preventDefault(); setSeretDi(d.jenis); }}
                      onDragLeave={() => setSeretDi(null)}
                      onDrop={(e) => {
                        e.preventDefault();
                        setSeretDi(null);
                        pilihBerkas(d.jenis, e.dataTransfer.files?.[0]);
                      }}
                      className={cn(
                        "flex cursor-pointer flex-col items-center rounded-lg border-2 border-dashed px-6 py-8 text-center transition-colors focus-within:border-[#4B6E5A] focus-within:ring-[3px] focus-within:ring-[#4B6E5A]/15",
                        seretDi === d.jenis
                          ? "border-[#4B6E5A] bg-[#4B6E5A]/5"
                          : "border-neutral-300 bg-white hover:border-[#4B6E5A]/60 hover:bg-[#4B6E5A]/[0.03]",
                      )}
                    >
                      <Upload className="size-6 text-[#4B6E5A]" aria-hidden />
                      <span className="mt-3 text-sm font-semibold text-neutral-900">
                        {d.berkas ? "Pilih berkas pengganti" : "Seret berkas ke sini"}
                        <span className="font-normal text-neutral-500"> atau </span>
                        <span className="text-[#4B6E5A] underline underline-offset-4">telusuri</span>
                      </span>
                      <span className="mt-1.5 text-xs text-neutral-500">
                        PDF, JPG, atau PNG. Maksimal {formatUkuran(BATAS_UKURAN_BYTE)}.
                      </span>
                      <input
                        id={idInput}
                        type="file"
                        accept={ACCEPT_BERKAS}
                        aria-describedby={idPetunjuk}
                        aria-invalid={!!pesan}
                        className="sr-only"
                        onChange={(e) => {
                          pilihBerkas(d.jenis, e.target.files?.[0]);
                          e.target.value = ""; // izinkan memilih berkas yang sama lagi
                        }}
                      />
                    </label>
                  )}
                  {pesan && (
                    <p role="alert" className="mt-2 text-[13px] font-medium text-[#B45309]">{pesan}</p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>

      {formulirBisaDiubah && (
        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-neutral-500" aria-live="polite">
            {!wajibLengkap
              ? "Unggah semua dokumen wajib untuk melanjutkan."
              : adaRevisi
                ? "Unggah ulang berkas yang perlu direvisi untuk melanjutkan."
                : "Semua dokumen wajib sudah diunggah."}
          </p>
          <div className="sm:text-right">
            <Button
              type="button"
              onClick={kirim}
              disabled={!bisaKirim || mengirim}
              className="h-12 w-full rounded-lg bg-[#4B6E5A] px-8 text-[15px] font-semibold text-white hover:bg-[#5C836A] disabled:opacity-50 sm:w-auto"
            >
              {mengirim ? (
                <><Loader2 className="size-4 animate-spin" aria-hidden />Mengirim</>
              ) : (
                <><Send className="size-4" aria-hidden />{status === "REVISI" ? "Kirim ulang perbaikan" : "Kirim untuk verifikasi"}</>
              )}
            </Button>
            {galatKirim && (
              <p role="alert" className="mt-2 text-[13px] font-medium text-[#B45309]">{galatKirim}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
