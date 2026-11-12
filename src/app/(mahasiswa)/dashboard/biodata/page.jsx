import { FormBiodata } from "@/components/mahasiswa/form-biodata";
import { getDataMahasiswa } from "@/lib/data-mahasiswa";

export const metadata = { title: "Biodata" };

export default async function BiodataPage() {
  const { mahasiswa, sekolah, formulir } = await getDataMahasiswa();
  // Setelah formulir dikirim, biodata dikunci (status_berkas bukan DRAFT).
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
