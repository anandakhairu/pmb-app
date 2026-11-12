import { AdminShell } from "@/components/admin/shell";
import { ADMIN_AKTIF } from "@/lib/data-admin";

export const metadata = {
  title: {
    template: "%s | Admin Back-Office PMB",
    default: "Admin Back-Office PMB",
  },
  description: "Panel kendali verifikasi berkas, analytics pendaftar, dan master data PMB.",
};

export default function AdminLayout({ children }) {
  return <AdminShell admin={ADMIN_AKTIF}>{children}</AdminShell>;
}
