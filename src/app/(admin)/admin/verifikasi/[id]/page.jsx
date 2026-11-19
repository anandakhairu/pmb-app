import { Suspense } from "react";
import { notFound } from "next/navigation";
import { SplitViewVerifikasi } from "@/components/admin/split-view-verifikasi";
import { DAFTAR_PENDAFTAR_MOCK, getDetailPendaftarAdmin } from "@/lib/data-admin";

export function generateStaticParams() {
  return DAFTAR_PENDAFTAR_MOCK.map((p) => ({
    id: p.id,
  }));
}

export async function generateMetadata({ params }) {
  const p = await params;
  const pendaftar = await getDetailPendaftarAdmin(p.id);
  if (!pendaftar) return { title: "Verifikasi Berkas" };

  return {
    title: `Verifikasi ${pendaftar.mahasiswa.namaLengkap} (${pendaftar.nomorPendaftaran})`,
  };
}

export default function DetailVerifikasiPage({ params }) {
  return (
    <Suspense fallback={<div className="py-12 text-center text-sm text-neutral-500">Memuat berkas pendaftar...</div>}>
      <KontenDetail params={params} />
    </Suspense>
  );
}

async function KontenDetail({ params }) {
  const p = await params;
  const pendaftar = await getDetailPendaftarAdmin(p.id);

  if (!pendaftar) {
    notFound();
  }

  return <SplitViewVerifikasi pendaftar={pendaftar} />;
}
