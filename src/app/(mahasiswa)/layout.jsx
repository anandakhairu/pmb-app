import { MahasiswaShell } from "@/components/mahasiswa/shell";
import { getDataMahasiswa } from "@/lib/data-mahasiswa";

export const metadata = {
  title: "Portal Pendaftar",
};

// Catatan: begitu getDataMahasiswa() membaca sesi (cookies), bungkus bagian
// yang membacanya dengan <Suspense> karena next.config.mjs memakai cacheComponents.
export default async function MahasiswaLayout({ children }) {
  const { mahasiswa, formulir } = await getDataMahasiswa();

  return (
    <MahasiswaShell
      nama={mahasiswa.namaLengkap}
      nomor={formulir.nomorPendaftaran}
      perhatian={{ berkas: formulir.statusBerkas === "REVISI" }}
    >
      {children}
    </MahasiswaShell>
  );
}
