import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  Clock,
  Eye,
  FileCheck2,
  GraduationCap,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDaftarPendaftarAdmin, getStatistikAdmin } from "@/lib/data-admin";
import { formatTanggal } from "@/lib/data-mahasiswa";

export const metadata = {
  title: "Analytics & Ringkasan",
};

const STATUS_BADGE = {
  DRAFT: { label: "Draft", variant: "secondary" },
  DIKIRIM: { label: "Perlu Verifikasi", variant: "warning" },
  DALAM_REVIEW: { label: "Sedang Diperiksa", variant: "info" },
  REVISI: { label: "Revisi Berkas", variant: "warning" },
  TERVERIFIKASI: { label: "Terverifikasi", variant: "success" },
};

export default async function AdminDashboardPage() {
  const stats = await getStatistikAdmin();
  const pendaftarTerbaru = await getDaftarPendaftarAdmin();

  return (
    <div className="space-y-8">
      {/* ----------------------------- HEADER & WELCOME ----------------------------- */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-neutral-900 sm:text-3xl">
              Dashboard Analytics & Ringkasan
            </h1>
            <Badge className="bg-[#4B6E5A]/15 text-[#2F4A3B] border-none font-bold text-xs">
              Periode 2027/2028
            </Badge>
          </div>
          <p className="mt-1.5 text-sm text-neutral-600">
            Pantau arus pendaftaran mahasiswa baru, antrean verifikasi berkas, dan status kelulusan.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button asChild className="rounded-xl bg-[#4B6E5A] px-5 text-sm font-semibold text-white hover:bg-[#5C836A] shadow-sm">
            <Link href="/admin/verifikasi" className="flex items-center gap-2">
              <FileCheck2 className="size-4" />
              Buka Antrean Verifikasi
              <span className="ml-1 rounded-full bg-white/20 px-2 py-0.5 text-xs font-bold">
                {stats.perluVerifikasi}
              </span>
            </Link>
          </Button>
        </div>
      </div>

      {/* ----------------------------- 4 KARTU METRIK UTAMA ----------------------------- */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Card 1: Total Pendaftar */}
        <Card className="rounded-2xl border-neutral-200/80 bg-white shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-600">
              Total Pendaftar
            </CardTitle>
            <div className="flex size-9 items-center justify-center rounded-xl bg-neutral-100 text-neutral-700">
              <Users className="size-4.5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold text-neutral-900">
              {stats.totalPendaftar.toLocaleString("id-ID")}
            </div>
            <p className="mt-1 flex items-center gap-1.5 text-xs text-neutral-500">
              <span className="font-semibold text-emerald-600">+12%</span> dibanding gelombang lalu
            </p>
          </CardContent>
        </Card>

        {/* Card 2: Perlu Verifikasi */}
        <Card className="rounded-2xl border-[#D97706]/30 bg-[#D97706]/5 shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-semibold text-[#B45309]">
              Perlu Verifikasi
            </CardTitle>
            <div className="flex size-9 items-center justify-center rounded-xl bg-[#D97706]/20 text-[#B45309]">
              <Clock className="size-4.5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold text-[#92400E]">
              {stats.perluVerifikasi}
            </div>
            <p className="mt-1 text-xs text-[#B45309]">
              Menunggu pemeriksaan panitia
            </p>
          </CardContent>
        </Card>

        {/* Card 3: Berkas Revisi */}
        <Card className="rounded-2xl border-neutral-200/80 bg-white shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-600">
              Berkas Revisi
            </CardTitle>
            <div className="flex size-9 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
              <AlertTriangle className="size-4.5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold text-neutral-900">
              {stats.revisi}
            </div>
            <p className="mt-1 text-xs text-neutral-500">
              Menunggu unggah ulang dari maba
            </p>
          </CardContent>
        </Card>

        {/* Card 4: Dinyatakan Lulus */}
        <Card className="rounded-2xl border-[#4B6E5A]/30 bg-[#4B6E5A]/5 shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-semibold text-[#2F4A3B]">
              Dinyatakan Lulus
            </CardTitle>
            <div className="flex size-9 items-center justify-center rounded-xl bg-[#4B6E5A]/20 text-[#2F4A3B]">
              <GraduationCap className="size-4.5" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-extrabold text-[#2F4A3B]">
              {stats.lulus}
            </div>
            <p className="mt-1 text-xs text-[#4B6E5A]">
              Tingkat penerimaan ~29%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* ----------------------------- BANNER QUICK VERIFY ----------------------------- */}
      <div className="relative overflow-hidden rounded-2xl border border-[#4B6E5A]/25 bg-linear-to-r from-[#4B6E5A]/15 via-white to-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex size-2 rounded-full bg-amber-500 animate-pulse" />
              <p className="text-xs font-bold tracking-wider text-[#2F4A3B] uppercase">
                Prioritas Hari Ini
              </p>
            </div>
            <h2 className="text-lg font-bold text-neutral-900">
              Ada {stats.perluVerifikasi} berkas pendaftar baru yang menunggu verifikasi panitia
            </h2>
            <p className="text-xs text-neutral-600">
              Lakukan pemeriksaan berkas foto, KTP/KK, rapor, dan ijazah melalui panel split-view.
            </p>
          </div>
          <Button asChild className="rounded-xl bg-[#4B6E5A] px-6 text-sm font-semibold text-white hover:bg-[#5C836A] shadow-xs">
            <Link href="/admin/verifikasi">
              Periksa Sekarang <ArrowRight className="ml-1.5 size-4" />
            </Link>
          </Button>
        </div>
      </div>

      {/* ----------------------------- TABEL PENDAFTAR TERBARU ----------------------------- */}
      <div className="rounded-2xl border border-neutral-200/80 bg-white p-6 shadow-xs">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center pb-5 border-b border-neutral-100">
          <div>
            <h3 className="text-lg font-bold text-neutral-900">
              Pendaftar Masuk Terbaru
            </h3>
            <p className="text-xs text-neutral-500">
              Data pendaftaran mahasiswa yang masuk secara real-time ke sistem.
            </p>
          </div>
          <Link
            href="/admin/verifikasi"
            className="flex items-center gap-1.5 text-xs font-bold text-[#4B6E5A] hover:underline"
          >
            Lihat semua antrean verifikasi <ArrowRight className="size-3.5" />
          </Link>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-neutral-200/80 text-xs font-bold uppercase tracking-wider text-neutral-400">
                <th className="py-3.5 pr-4">Nomor & Nama</th>
                <th className="py-3.5 px-4">Program Studi</th>
                <th className="py-3.5 px-4">Jalur</th>
                <th className="py-3.5 px-4">Status Berkas</th>
                <th className="py-3.5 px-4">Waktu Finalisasi</th>
                <th className="py-3.5 pl-4 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 text-neutral-700">
              {pendaftarTerbaru.map((p) => {
                const badgeInfo = STATUS_BADGE[p.statusBerkas] || { label: p.statusBerkas, variant: "secondary" };
                return (
                  <tr key={p.id} className="transition-colors hover:bg-neutral-50/70">
                    <td className="py-4 pr-4">
                      <div className="font-bold text-neutral-900">
                        {p.mahasiswa.namaLengkap}
                      </div>
                      <div className="text-xs text-neutral-400 font-mono mt-0.5">
                        {p.nomorPendaftaran} • NIK: {p.mahasiswa.nik}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-medium text-neutral-900">
                        {p.prodi.nama}
                      </div>
                      <div className="text-xs text-neutral-500">
                        {p.prodi.jenjang} • {p.prodi.fakultas}
                      </div>
                    </td>
                    <td className="py-4 px-4 font-medium text-neutral-800">
                      <span className="rounded-md bg-neutral-100 px-2 py-1 text-xs font-semibold">
                        {p.jalur.kode}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <Badge variant={badgeInfo.variant} className="font-semibold text-xs">
                        {badgeInfo.label}
                      </Badge>
                    </td>
                    <td className="py-4 px-4 text-xs text-neutral-500 whitespace-nowrap">
                      {formatTanggal(p.finalisasiAt)}
                    </td>
                    <td className="py-4 pl-4 text-right">
                      <Button asChild size="sm" variant="outline" className="h-8 rounded-lg border-neutral-300 px-3 text-xs font-semibold hover:border-[#4B6E5A] hover:bg-[#4B6E5A]/5 hover:text-[#4B6E5A]">
                        <Link href={`/admin/verifikasi/${p.id}`} className="flex items-center gap-1.5">
                          <Eye className="size-3.5" />
                          Periksa
                        </Link>
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
