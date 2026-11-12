import { BookOpen, GraduationCap, Layers, Plus, School } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MASTER_JALUR, MASTER_PRODI } from "@/lib/data-admin";

export const metadata = {
  title: "Master Data PMB",
};

export default function MasterDataPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-neutral-900 sm:text-3xl">
          Master Data PMB
        </h1>
        <p className="mt-1 text-sm text-neutral-600">
          Kelola data program studi, kuota penerimaan, dan konfigurasi jalur seleksi.
        </p>
      </div>

      {/* SEKSI 1: PROGRAM STUDI */}
      <div className="rounded-2xl border border-neutral-200/80 bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between pb-4 border-b border-neutral-100">
          <div className="flex items-center gap-2.5">
            <div className="flex size-9 items-center justify-center rounded-xl bg-[#4B6E5A]/15 text-[#2F4A3B]">
              <School className="size-4.5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-neutral-900">Katalog Program Studi & Kuota</h2>
              <p className="text-xs text-neutral-500">Tabel master program studi di database Prisma</p>
            </div>
          </div>
          <Button size="sm" className="h-8.5 rounded-xl bg-[#4B6E5A] px-3.5 text-xs font-semibold text-white hover:bg-[#5C836A]">
            <Plus className="mr-1 size-3.5" /> Tambah Prodi
          </Button>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs font-bold uppercase tracking-wider text-neutral-400 border-b border-neutral-200/80">
              <tr>
                <th className="py-3 px-3">Kode</th>
                <th className="py-3 px-3">Program Studi</th>
                <th className="py-3 px-3">Jenjang</th>
                <th className="py-3 px-3">Fakultas</th>
                <th className="py-3 px-3">Kapasitas Kuota</th>
                <th className="py-3 px-3">Terisi</th>
                <th className="py-3 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 text-neutral-700">
              {MASTER_PRODI.map((prodi) => {
                const persen = Math.round((prodi.terisi / prodi.kuota) * 100);
                return (
                  <tr key={prodi.kode} className="hover:bg-neutral-50/70">
                    <td className="py-3.5 px-3 font-mono font-bold text-neutral-800">{prodi.kode}</td>
                    <td className="py-3.5 px-3 font-semibold text-neutral-900">{prodi.nama}</td>
                    <td className="py-3.5 px-3">
                      <Badge variant="outline" className="text-xs font-mono">{prodi.jenjang}</Badge>
                    </td>
                    <td className="py-3.5 px-3 text-xs text-neutral-600">{prodi.fakultas}</td>
                    <td className="py-3.5 px-3 font-mono font-medium">{prodi.kuota} Kursi</td>
                    <td className="py-3.5 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 rounded-full bg-neutral-100 overflow-hidden">
                          <div className="h-full bg-[#4B6E5A]" style={{ width: `${persen}%` }} />
                        </div>
                        <span className="text-xs font-semibold text-neutral-600">{persen}%</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-3 text-right">
                      <Badge variant="success" className="text-xs font-semibold">Aktif</Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* SEKSI 2: JALUR PENDAFTARAN */}
      <div className="rounded-2xl border border-neutral-200/80 bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between pb-4 border-b border-neutral-100">
          <div className="flex items-center gap-2.5">
            <div className="flex size-9 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
              <Layers className="size-4.5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-neutral-900">Jalur Pendaftaran & Tarif Biaya</h2>
              <p className="text-xs text-neutral-500">Konfigurasi jalur SNBP, SNBT, dan Seleksi Mandiri</p>
            </div>
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs font-bold uppercase tracking-wider text-neutral-400 border-b border-neutral-200/80">
              <tr>
                <th className="py-3 px-3">Kode Jalur</th>
                <th className="py-3 px-3">Nama Jalur Seleksi</th>
                <th className="py-3 px-3">Biaya Formulir</th>
                <th className="py-3 px-3 text-right">Status Pendaftaran</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 text-neutral-700">
              {MASTER_JALUR.map((jalur) => (
                <tr key={jalur.kode} className="hover:bg-neutral-50/70">
                  <td className="py-3.5 px-3 font-mono font-bold text-neutral-800">{jalur.kode}</td>
                  <td className="py-3.5 px-3 font-semibold text-neutral-900">{jalur.nama}</td>
                  <td className="py-3.5 px-3 font-mono text-neutral-700">
                    {jalur.biaya === 0 ? "Gratis" : `Rp ${jalur.biaya.toLocaleString("id-ID")}`}
                  </td>
                  <td className="py-3.5 px-3 text-right">
                    <Badge variant={jalur.status === "BUKA" ? "success" : "secondary"} className="text-xs font-bold">
                      {jalur.status === "BUKA" ? "Pendaftaran Buka" : "Ditutup"}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
