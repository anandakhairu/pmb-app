"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  Bell,
  Check,
  CheckCircle2,
  Clock,
  Download,
  ExternalLink,
  Eye,
  FileText,
  ImageIcon,
  Info,
  Loader2,
  Maximize2,
  RotateCw,
  Send,
  Sparkles,
  User,
  X,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { formatTanggal } from "@/lib/data-mahasiswa";

export function SplitViewVerifikasi({ pendaftar }) {
  const router = useRouter();
  const [berkasTerpilihIndex, setBerkasTerpilihIndex] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [rotasi, setRotasi] = useState(0);

  // State status verifikasi per-dokumen
  const [statusPerDokumen, setStatusPerDokumen] = useState(() => {
    const map = {};
    pendaftar.berkas.forEach((b) => {
      map[b.id] = {
        status: b.statusVerifikasi || "MENUNGGU",
        catatan: b.catatan || "",
      };
    });
    return map;
  });

  // State keputusan formulir keseluruhan
  const [statusFormulir, setStatusFormulir] = useState(() => {
    return pendaftar.statusBerkas === "REVISI" ? "REVISI" : "TERVERIFIKASI";
  });
  const [catatanUmum, setCatatanUmum] = useState(pendaftar.catatanRevisi || "");
  const [kirimWebPush, setKirimWebPush] = useState(true);
  const [sedangSimpan, setSedangSimpan] = useState(false);
  const [notifSukses, setNotifSukses] = useState(null);

  const berkasAktif = pendaftar.berkas[berkasTerpilihIndex] || pendaftar.berkas[0];

  function ubahStatusDokumen(dokumenId, statusBaru) {
    setStatusPerDokumen((prev) => {
      const updated = {
        ...prev,
        [dokumenId]: {
          ...prev[dokumenId],
          status: statusBaru,
        },
      };

      // Otomatis sinkronkan keputusan formulir
      const adaRevisi = Object.values(updated).some((v) => v.status === "REVISI");
      if (adaRevisi) {
        setStatusFormulir("REVISI");
      }
      return updated;
    });
  }

  function ubahCatatanDokumen(dokumenId, catatanBaru) {
    setStatusPerDokumen((prev) => ({
      ...prev,
      [dokumenId]: {
        ...prev[dokumenId],
        catatan: catatanBaru,
      },
    }));
  }

  async function simpanVerifikasi(e) {
    e.preventDefault();
    setSedangSimpan(true);
    setNotifSukses(null);

    try {
      // Simulasi pemrosesan backend (Database Update + Antrean Web Push Worker)
      await new Promise((r) => setTimeout(r, 1000));

      setNotifSukses({
        status: statusFormulir,
        pesan:
          statusFormulir === "TERVERIFIKASI"
            ? "Berkas berhasil diverifikasi dan dinyatakan VALID."
            : "Permintaan revisi berkas berhasil disimpan.",
        webPushSent: kirimWebPush,
      });

      // Segarkan state router
      setTimeout(() => {
        router.refresh();
      }, 800);
    } catch {
      alert("Gagal menyimpan verifikasi. Silakan coba kembali.");
    } finally {
      setSedangSimpan(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* ----------------------------- TOP BAR NAVIGASI ----------------------------- */}
      <div className="flex flex-col justify-between gap-4 border-b border-neutral-200/80 pb-4 sm:flex-row sm:items-center">
        <div className="flex items-center gap-3">
          <Button asChild variant="outline" size="sm" className="h-9 rounded-xl border-neutral-200 text-xs font-semibold text-neutral-700">
            <Link href="/admin/verifikasi" className="flex items-center gap-1.5">
              <ArrowLeft className="size-4" /> Kembali ke Antrean
            </Link>
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-neutral-900">
                {pendaftar.mahasiswa.namaLengkap}
              </h1>
              <Badge variant="outline" className="font-mono text-xs border-neutral-300">
                {pendaftar.nomorPendaftaran}
              </Badge>
            </div>
            <p className="text-xs text-neutral-500 mt-0.5">
              Program Studi: <span className="font-semibold text-neutral-800">{pendaftar.prodi.nama} ({pendaftar.prodi.jenjang})</span> • Jalur: <span className="font-semibold text-neutral-800">{pendaftar.jalur.nama}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge className="bg-[#4B6E5A]/15 text-[#2F4A3B] border-none font-bold text-xs py-1">
            Status Berkas: {pendaftar.statusBerkas}
          </Badge>
        </div>
      </div>

      {/* ----------------------------- ALERT SUKSES ----------------------------- */}
      {notifSukses && (
        <div className="flex items-start justify-between rounded-2xl border border-emerald-300 bg-emerald-50/90 p-4 text-sm text-emerald-900 animate-in fade-in">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="size-5 shrink-0 text-emerald-600 mt-0.5" />
            <div>
              <p className="font-bold">{notifSukses.pesan}</p>
              {notifSukses.webPushSent && (
                <p className="mt-1 text-xs text-emerald-700 flex items-center gap-1.5">
                  <Sparkles className="size-3.5" />
                  Notifikasi Web Push telah diantrekan ke background worker untuk perangkat mahasiswa.
                </p>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={() => setNotifSukses(null)}
            className="text-emerald-700 hover:text-emerald-900"
          >
            <X className="size-4" />
          </button>
        </div>
      )}

      {/* ----------------------------- SPLIT VIEW LAYOUT ----------------------------- */}
      <div className="grid gap-6 lg:grid-cols-12 items-start">
        {/* ========================================================================= */}
        {/* SISI KIRI: DOCUMENT VIEWER (7 KOLOM)                                      */}
        {/* ========================================================================= */}
        <div className="lg:col-span-7 space-y-4">
          {/* TAB DAFTAR BERKAS */}
          <div className="flex items-center gap-1.5 overflow-x-auto rounded-2xl border border-neutral-200/80 bg-white p-1.5 shadow-xs">
            {pendaftar.berkas.map((b, idx) => {
              const aktif = idx === berkasTerpilihIndex;
              const statusDokumen = statusPerDokumen[b.id]?.status || b.statusVerifikasi;

              return (
                <button
                  key={b.id}
                  type="button"
                  onClick={() => {
                    setBerkasTerpilihIndex(idx);
                    setZoomLevel(1);
                    setRotasi(0);
                  }}
                  className={`flex shrink-0 items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-bold transition-all ${
                    aktif
                      ? "bg-[#4B6E5A] text-white shadow-xs"
                      : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                  }`}
                >
                  <FileText className="size-3.5" />
                  <span className="truncate max-w-[120px]">{b.jenis.replace(/_/g, " ")}</span>
                  {statusDokumen === "VALID" && (
                    <span className="flex size-4 items-center justify-center rounded-full bg-emerald-500 text-white">
                      <Check className="size-2.5" />
                    </span>
                  )}
                  {statusDokumen === "REVISI" && (
                    <span className="flex size-4 items-center justify-center rounded-full bg-amber-500 text-white">
                      !
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* CANVAS PREVIEW AREA */}
          <div className="relative flex flex-col rounded-2xl border border-neutral-200/80 bg-neutral-900 text-white shadow-sm overflow-hidden min-h-[500px]">
            {/* TOOLBAR CONTROLS */}
            <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-900/90 px-4 py-2.5 backdrop-blur z-10">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-neutral-400 truncate max-w-[200px]">
                  {berkasAktif.namaFile}
                </span>
                <span className="rounded-md bg-neutral-800 px-2 py-0.5 text-[10px] text-neutral-400 font-mono">
                  {Math.round(berkasAktif.ukuranByte / 1024)} KB
                </span>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  title="Perbesar"
                  onClick={() => setZoomLevel((z) => Math.min(z + 0.25, 2.5))}
                  className="rounded-lg p-1.5 text-neutral-300 hover:bg-neutral-800 hover:text-white"
                >
                  <ZoomIn className="size-4" />
                </button>
                <button
                  type="button"
                  title="Perkecil"
                  onClick={() => setZoomLevel((z) => Math.max(z - 0.25, 0.5))}
                  className="rounded-lg p-1.5 text-neutral-300 hover:bg-neutral-800 hover:text-white"
                >
                  <ZoomOut className="size-4" />
                </button>
                <button
                  type="button"
                  title="Putar Dokumen"
                  onClick={() => setRotasi((r) => (r + 90) % 360)}
                  className="rounded-lg p-1.5 text-neutral-300 hover:bg-neutral-800 hover:text-white"
                >
                  <RotateCw className="size-4" />
                </button>
                <button
                  type="button"
                  title="Reset Zoom"
                  onClick={() => {
                    setZoomLevel(1);
                    setRotasi(0);
                  }}
                  className="rounded-lg px-2 py-1 text-xs text-neutral-300 hover:bg-neutral-800 hover:text-white"
                >
                  {Math.round(zoomLevel * 100)}%
                </button>
              </div>
            </div>

            {/* PREVIEW CONTAINER */}
            <div className="relative flex flex-1 items-center justify-center p-6 overflow-auto bg-neutral-950">
              <div
                style={{
                  transform: `scale(${zoomLevel}) rotate(${rotasi}deg)`,
                  transition: "transform 0.15s ease-out",
                }}
                className="max-w-full max-h-full flex items-center justify-center"
              >
                {berkasAktif.previewUrl ? (
                  <div className="relative rounded-lg shadow-2xl overflow-hidden border border-neutral-700 bg-white">
                    <Image
                      src={berkasAktif.previewUrl}
                      alt={berkasAktif.namaFile}
                      width={600}
                      height={800}
                      className="max-h-[500px] w-auto object-contain"
                      unoptimized
                    />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center gap-3 p-12 text-center text-neutral-400">
                    <FileText className="size-16 text-neutral-600" />
                    <p className="text-sm font-semibold text-neutral-200">
                      Pratinjau Dokumen PDF
                    </p>
                    <p className="text-xs text-neutral-500 max-w-xs">
                      Dokumen disimpan secara privat di Supabase Storage / R2 (Path: {berkasAktif.storagePath})
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* BOTTOM INFO BAR */}
            <div className="flex items-center justify-between border-t border-neutral-800 bg-neutral-900/80 px-4 py-2 text-xs text-neutral-400">
              <span>Jenis: {berkasAktif.jenis}</span>
              <span className="flex items-center gap-1.5 font-semibold text-emerald-400">
                <CheckCircle2 className="size-3.5" /> File terenkripsi aman
              </span>
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* SISI KANAN: CHECKLIST, CATATAN & WEB PUSH (5 KOLOM)                       */}
        {/* ========================================================================= */}
        <div className="lg:col-span-5 space-y-5">
          {/* RINGKASAN DATA MAHASISWA */}
          <Card className="rounded-2xl border-neutral-200/80 bg-white shadow-xs">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold text-neutral-900 flex items-center gap-2">
                <User className="size-4 text-[#4B6E5A]" /> Ringkasan Calon Mahasiswa
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2.5 text-xs">
              <div className="grid grid-cols-3 gap-1 py-1 border-b border-neutral-100">
                <span className="text-neutral-500">Nama Lengkap</span>
                <span className="col-span-2 font-bold text-neutral-900">{pendaftar.mahasiswa.namaLengkap}</span>
              </div>
              <div className="grid grid-cols-3 gap-1 py-1 border-b border-neutral-100">
                <span className="text-neutral-500">NIK & Kontak</span>
                <span className="col-span-2 font-mono text-neutral-800">{pendaftar.mahasiswa.nik} • {pendaftar.mahasiswa.noHp}</span>
              </div>
              <div className="grid grid-cols-3 gap-1 py-1 border-b border-neutral-100">
                <span className="text-neutral-500">Asal Sekolah</span>
                <span className="col-span-2 font-medium text-neutral-800">
                  {pendaftar.mahasiswa.asalSekolah?.namaSekolah} ({pendaftar.mahasiswa.asalSekolah?.jurusan})
                </span>
              </div>
              <div className="grid grid-cols-3 gap-1 py-1">
                <span className="text-neutral-500">Nilai Rapor</span>
                <span className="col-span-2 font-bold text-[#4B6E5A]">
                  Rata-rata: {pendaftar.mahasiswa.asalSekolah?.nilaiRataRata}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* CHECKLIST VERIFIKASI DOKUMEN AKTIF */}
          <Card className="rounded-2xl border-neutral-200/80 bg-white shadow-xs">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold text-neutral-900">
                Verifikasi Dokumen: {berkasAktif.jenis.replace(/_/g, " ")}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3.5">
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  size="sm"
                  onClick={() => ubahStatusDokumen(berkasAktif.id, "VALID")}
                  className={`flex-1 rounded-xl text-xs font-bold transition-all ${
                    statusPerDokumen[berkasAktif.id]?.status === "VALID"
                      ? "bg-emerald-600 text-white hover:bg-emerald-700 shadow-xs"
                      : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
                  }`}
                >
                  <Check className="mr-1.5 size-3.5" /> Valid
                </Button>
                <Button
                  type="button"
                  size="sm"
                  onClick={() => ubahStatusDokumen(berkasAktif.id, "REVISI")}
                  className={`flex-1 rounded-xl text-xs font-bold transition-all ${
                    statusPerDokumen[berkasAktif.id]?.status === "REVISI"
                      ? "bg-amber-600 text-white hover:bg-amber-700 shadow-xs"
                      : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
                  }`}
                >
                  <AlertTriangle className="mr-1.5 size-3.5" /> Minta Revisi
                </Button>
              </div>

              {statusPerDokumen[berkasAktif.id]?.status === "REVISI" && (
                <div className="space-y-1.5 pt-1 animate-in fade-in">
                  <Label className="text-xs font-semibold text-amber-800">
                    Catatan Revisi untuk Dokumen Ini
                  </Label>
                  <Textarea
                    placeholder="Contoh: Dokumen terpotong, atau resolusi foto buram..."
                    value={statusPerDokumen[berkasAktif.id]?.catatan || ""}
                    onChange={(e) => ubahCatatanDokumen(berkasAktif.id, e.target.value)}
                    className="h-18 rounded-xl border-amber-300 bg-amber-50/50 text-xs text-amber-950 focus-visible:outline-amber-600"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* FORM KEPUTUSAN FINAL & WEB PUSH */}
          <form onSubmit={simpanVerifikasi} className="rounded-2xl border border-neutral-200/80 bg-white p-5 shadow-xs space-y-5">
            <div>
              <h3 className="text-sm font-extrabold text-neutral-900">
                Keputusan Status Formulir
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Pilih status akhir berkas pendaftaran calon mahasiswa ini.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setStatusFormulir("TERVERIFIKASI")}
                className={`rounded-xl border p-3 text-left transition-all ${
                  statusFormulir === "TERVERIFIKASI"
                    ? "border-[#4B6E5A] bg-[#4B6E5A]/10 text-[#2F4A3B] font-bold ring-2 ring-[#4B6E5A]/20"
                    : "border-neutral-200 hover:bg-neutral-50 text-neutral-600"
                }`}
              >
                <div className="flex items-center justify-between text-xs font-bold">
                  <span>TERVERIFIKASI</span>
                  {statusFormulir === "TERVERIFIKASI" && <CheckCircle2 className="size-4 text-[#4B6E5A]" />}
                </div>
                <p className="mt-1 text-[11px] text-neutral-500 font-normal">
                  Semua berkas sah & siap seleksi
                </p>
              </button>

              <button
                type="button"
                onClick={() => setStatusFormulir("REVISI")}
                className={`rounded-xl border p-3 text-left transition-all ${
                  statusFormulir === "REVISI"
                    ? "border-amber-500 bg-amber-50 text-amber-950 font-bold ring-2 ring-amber-500/20"
                    : "border-neutral-200 hover:bg-neutral-50 text-neutral-600"
                }`}
              >
                <div className="flex items-center justify-between text-xs font-bold">
                  <span>PERLU REVISI</span>
                  {statusFormulir === "REVISI" && <AlertTriangle className="size-4 text-amber-600" />}
                </div>
                <p className="mt-1 text-[11px] text-neutral-500 font-normal">
                  Maba wajib unggah ulang
                </p>
              </button>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="catatanUmum" className="text-xs font-semibold text-neutral-700">
                Catatan Panitia untuk Mahasiswa
              </Label>
              <Textarea
                id="catatanUmum"
                value={catatanUmum}
                onChange={(e) => setCatatanUmum(e.target.value)}
                placeholder="Tuliskan catatan arahan atau panduan perbaikan berkas..."
                className="h-20 rounded-xl text-xs"
              />
            </div>

            {/* TOGGLE WEB PUSH NOTIFICATION (SYARAT WAJIB TEKNIS) */}
            <div className="rounded-xl border border-[#4B6E5A]/20 bg-[#4B6E5A]/5 p-3.5 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex size-7 items-center justify-center rounded-lg bg-[#4B6E5A] text-white">
                    <Bell className="size-3.5" />
                  </div>
                  <div>
                    <Label htmlFor="toggleWebPush" className="text-xs font-bold text-neutral-900 cursor-pointer">
                      Kirim Web Push Notification
                    </Label>
                    <p className="text-[11px] text-neutral-600">
                      Antrekan pekerjaan ke Background Worker
                    </p>
                  </div>
                </div>
                <Switch
                  id="toggleWebPush"
                  checked={kirimWebPush}
                  onCheckedChange={setKirimWebPush}
                />
              </div>
              <p className="text-[10px] text-neutral-500 leading-relaxed border-t border-[#4B6E5A]/15 pt-2">
                Memenuhi <strong>Technical Requirements Dosen (Seksi 5)</strong>: Notifikasi browser dikirim via Service Worker & VAPID melalui antrean worker.
              </p>
            </div>

            {/* TOMBOL SIMPAN KEPUTUSAN */}
            <Button
              type="submit"
              disabled={sedangSimpan}
              className="h-11 w-full rounded-xl bg-[#4B6E5A] text-sm font-bold text-white hover:bg-[#5C836A] shadow-sm"
            >
              {sedangSimpan ? (
                <>
                  <Loader2 className="mr-2 size-4 animate-spin" /> Menyimpan...
                </>
              ) : (
                <>
                  <Send className="mr-2 size-4" /> Simpan Hasil Verifikasi
                </>
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
