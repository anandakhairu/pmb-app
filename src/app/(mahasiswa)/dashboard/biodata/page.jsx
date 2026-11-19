import { Suspense } from "react";
import { FormBiodata } from "@/components/mahasiswa/form-biodata";
import { getDataMahasiswa } from "@/lib/data-mahasiswa";

export const metadata = { title: "Biodata" };

export default function BiodataPage() {
  return (
    <Suspense fallback={<div className="py-12 text-center text-sm text-neutral-500">Memuat biodata pendaftar...</div>}>
      <KontenBiodata />
    </Suspense>
  );
}

async function KontenBiodata() {
  const { mahasiswa, sekolah, formulir } = await getDataMahasiswa();
  const terkunci = formulir.statusBerkas !== "DRAFT" && formulir.statusBerkas !== "REVISI";

  return (
    <div>
      <header className="mb-10">
        <h1 className="text-3xl font-extrabold tracking-tight text-[#2F4A3B]">Biodata</h1>
        <p className="mt-2 max-w-xl text-[15px] leading-relaxed text-neutral-600">
          Pastikan data sesuai KTP dan ijazah. Data ini dipakai panitia saat memeriksa berkasmu.
        </p>
      </header>
      <FormBiodata mahasiswa={mahasiswa} sekolah={sekolah} terkunci={terkunci} />
    </div>
  );
}
