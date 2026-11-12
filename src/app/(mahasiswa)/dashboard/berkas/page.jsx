import { UnggahBerkas } from "@/components/mahasiswa/unggah-berkas";
import { gabungkanBerkas, getDataMahasiswa } from "@/lib/data-mahasiswa";

export const metadata = { title: "Unggah Berkas" };

export default async function BerkasPage() {
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

      <UnggahBerkas dokumen={gabungkanBerkas(berkas, formulir.jalur.kode)} statusBerkas={formulir.statusBerkas} />
    </div>
  );
}
