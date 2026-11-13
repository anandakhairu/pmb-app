import { Suspense } from "react";
import { UnggahBerkas } from "@/components/mahasiswa/unggah-berkas";
import { gabungkanBerkas, getDataMahasiswa } from "@/lib/data-mahasiswa";

export const metadata = { title: "Unggah Berkas" };

export default function BerkasPage() {
  return (
    <Suspense fallback={<div className="py-12 text-center text-sm text-neutral-500">Memuat berkas pendaftar...</div>}>
      <KontenBerkas />
    </Suspense>
  );
}

async function KontenBerkas() {
  const { formulir, berkas } = await getDataMahasiswa();

  return (
    <div>
      <header className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-[#2F4A3B]">Unggah berkas</h1>
        <p className="mt-2 max-w-xl text-[15px] leading-relaxed text-neutral-600">
          Unggah dokumen yang diminta untuk jalur {formulir.jalur.nama}. Panitia memeriksa setiap berkas
          setelah kamu mengirimnya.
        </p>
      </header>

      <UnggahBerkas formulirId={formulir.id} dokumen={gabungkanBerkas(berkas, formulir.jalur.kode)} statusBerkas={formulir.statusBerkas} />
    </div>
  );
}
