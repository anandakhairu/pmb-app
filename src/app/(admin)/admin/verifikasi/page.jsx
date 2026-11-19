import { Suspense } from "react";
import Link from "next/link";
import {
  AlertCircle,
  FileCheck2,
  Search,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getDaftarPendaftarAdmin } from "@/lib/data-admin";
import { formatTanggal } from "@/lib/data-mahasiswa";

export const metadata = {
  title: "Antrean Verifikasi Berkas",
};

const STATUS_BADGE = {
  DRAFT: { label: "Draft", variant: "secondary" },
  DIKIRIM: { label: "Perlu Verifikasi", variant: "warning" },
  DALAM_REVIEW: { label: "Sedang Diperiksa", variant: "info" },
  REVISI: { label: "Revisi Berkas", variant: "warning" },
  TERVERIFIKASI: { label: "Terverifikasi", variant: "success" },
};

export default function AntreanVerifikasiPage({ searchParams }) {
  return (
    <Suspense fallback={<div className="py-12 text-center text-sm text-neutral-500">Memuat antrean verifikasi...</div>}>
      <KontenAntrean searchParams={searchParams} />
    </Suspense>
  );
}

async function KontenAntrean({ searchParams }) {
  const sp = await searchParams;
  const statusFilter = sp?.status || "SEMUA";
  const jalurFilter = sp?.jalur || "SEMUA";
  const prodiFilter = sp?.prodi || "SEMUA";
  const query = sp?.q || "";

  const daftarPendaftar = await getDaftarPendaftarAdmin({
    status: statusFilter,
    jalur: jalurFilter,
    prodi: prodiFilter,
    q: query,
  });

  const antreCount = daftarPendaftar.filter(
    (p) => p.statusBerkas === "DIKIRIM" || p.statusBerkas === "DALAM_REVIEW"
  ).length;

  return (
    <div className="space-y-6">
      {/* ----------------------------- HEADER ----------------------------- */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-neutral-900 sm:text-3xl">
              Antrean Verifikasi Berkas
            </h1>
            <Badge className="bg-[#4B6E5A]/15 text-[#2F4A3B] border-none font-bold text-xs">
              {antreCount} Perlu Ditinjau
            </Badge>
          </div>
          <p className="mt-1 text-sm text-neutral-600">
            Periksa dokumen pendaftaran, validasi data, dan terbitkan status verifikasi atau permintaan revisi.
          </p>
        </div>
      </div>

      {/* ----------------------------- FILTER TABS CEPAT ----------------------------- */}
      <div className="flex flex-wrap items-center gap-2 border-b border-neutral-200/80 pb-3">
        {[
          { key: "SEMUA", label: "Semua Status" },
          { key: "DIKIRIM", label: "Perlu Verifikasi" },
          { key: "DALAM_REVIEW", label: "Sedang Diperiksa" },
          { key: "REVISI", label: "Perlu Revisi" },
          { key: "TERVERIFIKASI", label: "Terverifikasi" },
        ].map((tab) => {
          const aktif = statusFilter === tab.key;
          return (
            <Link
              key={tab.key}
              href={`/admin/verifikasi?status=${tab.key}&jalur=${jalurFilter}&prodi=${prodiFilter}&q=${query}`}
              className={`rounded-xl px-4 py-2 text-xs font-bold transition-all ${
                aktif
                  ? "bg-[#4B6E5A] text-white shadow-xs"
                  : "bg-white text-neutral-600 border border-neutral-200/80 hover:bg-neutral-50 hover:text-neutral-900"
              }`}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>

      {/* ----------------------------- FILTER BAR & SEARCH ----------------------------- */}
      <div className="grid gap-3 sm:grid-cols-12">
        <div className="relative sm:col-span-6 lg:col-span-6">
          <form method="GET" action="/admin/verifikasi">
            <input type="hidden" name="status" value={statusFilter} />
            <input type="hidden" name="jalur" value={jalurFilter} />
            <input type="hidden" name="prodi" value={prodiFilter} />
            <Search className="absolute left-3.5 top-3 size-4 text-neutral-400" />
            <Input
              name="q"
              defaultValue={query}
              placeholder="Cari berdasarkan nama, nomor pendaftaran, atau NIK..."
              className="h-10 rounded-xl border-neutral-200/90 pl-10 text-sm shadow-none focus-visible:outline-[#4B6E5A]"
            />
          </form>
        </div>

        <div className="flex gap-2 sm:col-span-6 lg:col-span-6 justify-end">
          <Button asChild variant="outline" className="h-10 rounded-xl border-neutral-200 text-xs font-semibold text-neutral-700">
            <Link href="/admin/verifikasi">Reset Filter</Link>
          </Button>
        </div>
      </div>

      {/* ----------------------------- TABEL ANTREAN ----------------------------- */}
      <div className="rounded-2xl border border-neutral-200/80 bg-white shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-neutral-50/70 border-b border-neutral-200/80 text-xs font-bold uppercase tracking-wider text-neutral-400">
              <tr>
                <th className="py-4 px-6">Calon Mahasiswa</th>
                <th className="py-4 px-4">Pilihan Prodi</th>
                <th className="py-4 px-4">Jalur</th>
                <th className="py-4 px-4">Kelengkapan Dokumen</th>
                <th className="py-4 px-4">Status Berkas</th>
                <th className="py-4 px-4">Waktu Masuk</th>
                <th className="py-4 pr-6 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 text-neutral-700">
              {daftarPendaftar.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-sm text-neutral-500">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <AlertCircle className="size-8 text-neutral-300" />
                      <p className="font-semibold text-neutral-700">Tidak ada pendaftar dalam filter ini</p>
                      <p className="text-xs text-neutral-400">Coba ubah status filter atau kata kunci pencarian Anda.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                daftarPendaftar.map((p) => {
                  const badgeInfo = STATUS_BADGE[p.statusBerkas] || { label: p.statusBerkas, variant: "secondary" };
                  const validCount = p.berkas.filter((b) => b.statusVerifikasi === "VALID").length;
                  const totalCount = p.berkas.length;

                  return (
                    <tr key={p.id} className="transition-colors hover:bg-neutral-50/80">
                      <td className="py-4.5 px-6">
                        <div className="font-bold text-neutral-900">
                          {p.mahasiswa.namaLengkap}
                        </div>
                        <div className="text-xs text-neutral-400 font-mono mt-0.5">
                          {p.nomorPendaftaran} • {p.mahasiswa.asalSekolah?.namaSekolah}
                        </div>
                      </td>
                      <td className="py-4.5 px-4">
                        <div className="font-medium text-neutral-900">{p.prodi.nama}</div>
                        <div className="text-xs text-neutral-500">{p.prodi.jenjang} - {p.prodi.kode}</div>
                      </td>
                      <td className="py-4.5 px-4 font-medium text-neutral-800">
                        <span className="rounded-md bg-neutral-100 px-2.5 py-1 text-xs font-semibold">
                          {p.jalur.nama}
                        </span>
                      </td>
                      <td className="py-4.5 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 rounded-full bg-neutral-100 overflow-hidden">
                            <div
                              className="h-full bg-[#4B6E5A]"
                              style={{ width: `${(validCount / (totalCount || 1)) * 100}%` }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-neutral-600">
                            {validCount}/{totalCount} Valid
                          </span>
                        </div>
                      </td>
                      <td className="py-4.5 px-4">
                        <Badge variant={badgeInfo.variant} className="font-semibold text-xs">
                          {badgeInfo.label}
                        </Badge>
                      </td>
                      <td className="py-4.5 px-4 text-xs text-neutral-500 whitespace-nowrap">
                        {formatTanggal(p.finalisasiAt)}
                      </td>
                      <td className="py-4.5 pr-6 text-right">
                        <Button asChild size="sm" className="h-8.5 rounded-xl bg-[#4B6E5A] px-4 text-xs font-semibold text-white hover:bg-[#5C836A] shadow-xs">
                          <Link href={`/admin/verifikasi/${p.id}`} className="flex items-center gap-1.5">
                            <FileCheck2 className="size-3.5" />
                            Verifikasi
                          </Link>
                        </Button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
