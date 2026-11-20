import { Suspense } from "react";
import { notFound } from "next/navigation";
import { SplitViewVerifikasi } from "@/components/admin/split-view-verifikasi";
import { getDetailPendaftarAdmin } from "@/lib/data-admin";
import { prisma } from "@/lib/prisma";

export async function generateStaticParams() {
  try {
    const pendaftars = await prisma.formulirPendaftaran.findMany({ select: { id: true } });
    return pendaftars.map((p) => ({ id: p.id }));
  } catch {
    return [];
  }
}

export async function generateMetadata({ params }) {
  const p = await params;
  const pendaftar = await getDetailPendaftarAdmin(p.id);
  if (!pendaftar) return { title: "Verifikasi Berkas" };

  return {
    title: `Verifikasi ${pendaftar.mahasiswa?.namaLengkap || "Pendaftar"} (${pendaftar.nomorPendaftaran || "-"})`,
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
