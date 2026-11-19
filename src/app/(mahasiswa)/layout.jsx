import { Suspense } from "react";
import { MahasiswaShell } from "@/components/mahasiswa/shell";
import { getDataMahasiswa } from "@/lib/data-mahasiswa";

export const metadata = {
  title: "Portal Pendaftar",
};

export default function MahasiswaLayout({ children }) {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center text-sm text-neutral-500">Memuat portal pendaftar...</div>}>
      <KontenMahasiswaLayout>{children}</KontenMahasiswaLayout>
    </Suspense>
  );
}

async function KontenMahasiswaLayout({ children }) {
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
