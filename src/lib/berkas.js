// Aturan dan helper berkas yang aman dipakai di komponen client.
// Nilainya harus sama dengan CHECK constraint chk_berkas_ukuran dan
// chk_berkas_mime di prisma/constraints.sql (validasi lapis 1 di UI,
// lapis 2 di server, lapis 3 di database).

export const BATAS_UKURAN_BYTE = 5 * 1024 * 1024; // 5 MB
export const TIPE_BERKAS = ["application/pdf", "image/jpeg", "image/png"];
export const ACCEPT_BERKAS = ".pdf,.jpg,.jpeg,.png";

export const LABEL_VERIFIKASI = {
  BELUM_ADA: "Belum diunggah", // bukan nilai enum: belum ada baris berkas_dokumen
  MENUNGGU: "Menunggu verifikasi",
  VALID: "Terverifikasi",
  REVISI: "Perlu revisi",
};

export function formatUkuran(byte) {
  if (byte < 1024 * 1024) return `${Math.max(1, Math.round(byte / 1024))} KB`;
  return `${(byte / (1024 * 1024)).toFixed(1)} MB`;
}

/** Kembalikan pesan error, atau null bila berkas boleh diunggah. */
export function validasiBerkas(file) {
  if (!TIPE_BERKAS.includes(file.type)) {
    return "Format tidak didukung. Gunakan PDF, JPG, atau PNG.";
  }
  if (file.size <= 0) return "Berkas kosong. Pilih berkas lain.";
  if (file.size > BATAS_UKURAN_BYTE) {
    return `Ukuran ${formatUkuran(file.size)} melebihi batas ${formatUkuran(BATAS_UKURAN_BYTE)}.`;
  }
  return null;
}
