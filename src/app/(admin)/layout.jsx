import { Suspense } from "react";
import { AdminShell } from "@/components/admin/shell";
import { getAdminAktif } from "@/lib/data-admin";

export const metadata = {
  title: {
    template: "%s | Admin Back-Office PMB",
    default: "Admin Back-Office PMB",
  },
  description: "Panel kendali verifikasi berkas, analytics pendaftar, dan master data PMB.",
};

export default function AdminLayout({ children }) {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center text-sm text-neutral-500">Memuat panel admin...</div>}>
      <KontenAdminLayout>{children}</KontenAdminLayout>
    </Suspense>
  );
}

async function KontenAdminLayout({ children }) {
  const admin = await getAdminAktif();
  return <AdminShell admin={admin}>{children}</AdminShell>;
}
