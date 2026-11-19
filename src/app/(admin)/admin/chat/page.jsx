import { AdminChatRoom } from "@/components/admin/chat-room";

export const metadata = {
  title: "Chat ADMITRA",
  description: "Layanan konsultasi dan informasi terpadu Penerimaan Mahasiswa Baru Universitas ADMITRA.",
};

export default function AdminChatPage() {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-neutral-900 sm:text-3xl">
          Chat ADMITRA
        </h1>
        <p className="mt-1 text-sm text-neutral-600">
          Konsultasi interaktif dan penelusuran informasi resmi Penerimaan Mahasiswa Baru ADMITRA 2027/2028.
        </p>
      </div>

      <AdminChatRoom />
    </div>
  );
}
