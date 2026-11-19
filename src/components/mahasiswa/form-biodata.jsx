"use client";

import { useState } from "react";
import { z } from "zod";
import { CircleCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { FieldError, inputClass, labelClass } from "@/components/auth/auth-shell";
import { simpanBiodataAction } from "@/lib/server/actions";

// Validasi lapis 1 (UI). Pola sengaja sama dengan CHECK constraint di
// prisma/constraints.sql: chk_maba_nik_16_digit, chk_maba_no_hp,
// chk_sekolah_npsn, chk_sekolah_tahun_lulus, chk_sekolah_nilai.
// Nanti dipindah ke src/validations/ agar dipakai juga oleh server (lapis 2).
const wajib = (pesan) => z.string().trim().min(1, pesan);

const biodataSchema = z.object({
  namaLengkap: z.string().trim().min(3, "Nama minimal 3 karakter").max(150, "Nama maksimal 150 karakter"),
  nik: z.string().trim().regex(/^[0-9]{16}$/, "NIK harus 16 digit angka"),
  tempatLahir: wajib("Tempat lahir wajib diisi").max(100, "Maksimal 100 karakter"),
  tanggalLahir: wajib("Tanggal lahir wajib diisi"),
  jenisKelamin: z.enum(["LAKI_LAKI", "PEREMPUAN"], { message: "Pilih jenis kelamin" }),
  noHp: z.string().trim().regex(/^(\+62|62|0)8[0-9]{8,12}$/, "Gunakan format 08xxxxxxxxxx"),
  alamat: wajib("Alamat wajib diisi"),
  kotaKabupaten: wajib("Kota atau kabupaten wajib diisi"),
  provinsi: wajib("Provinsi wajib diisi"),
  namaSekolah: wajib("Nama sekolah wajib diisi").max(200, "Maksimal 200 karakter"),
  npsn: z.string().trim().regex(/^([0-9]{8})?$/, "NPSN harus 8 digit angka"),
  jenisSekolah: z.enum(["SMA", "SMK", "MA", "Paket C"], { message: "Pilih jenis sekolah" }),
  jurusan: wajib("Jurusan wajib diisi"),
  tahunLulus: z
    .string()
    .trim()
    .regex(/^[0-9]{4}$/, "Isi tahun 4 digit")
    .refine((v) => Number(v) >= 2000 && Number(v) <= 2100, "Tahun harus antara 2000 dan 2100"),
  nilaiRataRata: z
    .string()
    .trim()
    .regex(/^[0-9]{1,3}([.,][0-9]{1,2})?$/, "Isi angka, contoh 86,5")
    .refine((v) => Number(v.replace(",", ".")) <= 100, "Nilai maksimal 100"),
});

function Bidang({ id, label, galat, children, className }) {
  return (
    <div className={className}>
      <Label htmlFor={id} className={labelClass}>{label}</Label>
      <div className="mt-2">{children}</div>
      <FieldError message={galat} />
    </div>
  );
}

export function FormBiodata({ mahasiswa, sekolah, terkunci = false }) {
  const [galat, setGalat] = useState({});
  const [galatForm, setGalatForm] = useState(null);
  const [tersimpan, setTersimpan] = useState(false);
  const [menyimpan, setMenyimpan] = useState(false);

  const nilaiAwal = { ...mahasiswa, ...sekolah };

  function teks(nama, props = {}) {
    return (
      <Input
        id={nama}
        name={nama}
        defaultValue={nilaiAwal[nama] ?? ""}
        disabled={terkunci}
        aria-invalid={!!galat[nama]}
        className={inputClass}
        {...props}
      />
    );
  }

  async function onSubmit(e) {
    e.preventDefault();
    setGalatForm(null);
    setTersimpan(false);

    const data = Object.fromEntries(new FormData(e.currentTarget));
    const hasil = biodataSchema.safeParse(data);

    if (!hasil.success) {
      const berikut = {};
      for (const isu of hasil.error.issues) {
        const kunci = isu.path[0];
        if (!berikut[kunci]) berikut[kunci] = isu.message;
      }
      setGalat(berikut);
      return;
    }

    setGalat({});
    setMenyimpan(true);
    try {
      const res = await simpanBiodataAction({
        ...hasil.data,
        mahasiswaId: mahasiswa.id,
      });
      if (!res.success) {
        throw new Error(res.error);
      }
      setTersimpan(true);
    } catch (err) {
      setGalatForm(err.message || "Data belum tersimpan. Periksa koneksi lalu coba lagi.");
    } finally {
      setMenyimpan(false);
    }
  }

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-12">
      {terkunci && (
        <p role="status" className="rounded-xl border border-neutral-200 bg-white p-4 text-sm text-neutral-600">
          Formulir sudah dikirim, jadi biodata tidak bisa diubah lagi. Hubungi panitia bila ada data yang keliru.
        </p>
      )}

      <fieldset className="grid gap-6 sm:grid-cols-2">
        <legend className="mb-6 text-lg font-extrabold text-neutral-900">Data pribadi</legend>
        <Bidang id="namaLengkap" label="Nama lengkap" galat={galat.namaLengkap} className="sm:col-span-2">
          {teks("namaLengkap", { autoComplete: "name" })}
        </Bidang>
        <Bidang id="nik" label="NIK" galat={galat.nik}>
          {teks("nik", { inputMode: "numeric", maxLength: 16, placeholder: "16 digit" })}
        </Bidang>
        <Bidang id="noHp" label="Nomor WhatsApp" galat={galat.noHp}>
          {teks("noHp", { type: "tel", autoComplete: "tel", placeholder: "08xxxxxxxxxx" })}
        </Bidang>
        <Bidang id="tempatLahir" label="Tempat lahir" galat={galat.tempatLahir}>
          {teks("tempatLahir")}
        </Bidang>
        <Bidang id="tanggalLahir" label="Tanggal lahir" galat={galat.tanggalLahir}>
          {teks("tanggalLahir", { type: "date" })}
        </Bidang>
        <Bidang id="jenisKelamin" label="Jenis kelamin" galat={galat.jenisKelamin}>
          <Select name="jenisKelamin" defaultValue={nilaiAwal.jenisKelamin ?? undefined} disabled={terkunci}>
            <SelectTrigger id="jenisKelamin" aria-invalid={!!galat.jenisKelamin} className="h-12 w-full rounded-lg border-neutral-200 bg-white px-4 text-[15px] shadow-none">
              <SelectValue placeholder="Pilih" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="LAKI_LAKI">Laki-laki</SelectItem>
              <SelectItem value="PEREMPUAN">Perempuan</SelectItem>
            </SelectContent>
          </Select>
        </Bidang>
        <Bidang id="alamat" label="Alamat" galat={galat.alamat} className="sm:col-span-2">
          {teks("alamat", { autoComplete: "street-address" })}
        </Bidang>
        <Bidang id="kotaKabupaten" label="Kota atau kabupaten" galat={galat.kotaKabupaten}>
          {teks("kotaKabupaten")}
        </Bidang>
        <Bidang id="provinsi" label="Provinsi" galat={galat.provinsi}>
          {teks("provinsi")}
        </Bidang>
      </fieldset>

      <fieldset className="grid gap-6 sm:grid-cols-2">
        <legend className="mb-6 text-lg font-extrabold text-neutral-900">Asal sekolah</legend>
        <Bidang id="namaSekolah" label="Nama sekolah" galat={galat.namaSekolah} className="sm:col-span-2">
          {teks("namaSekolah")}
        </Bidang>
        <Bidang id="npsn" label="NPSN (opsional)" galat={galat.npsn}>
          {teks("npsn", { inputMode: "numeric", maxLength: 8, placeholder: "8 digit" })}
        </Bidang>
        <Bidang id="jenisSekolah" label="Jenis sekolah" galat={galat.jenisSekolah}>
          <Select name="jenisSekolah" defaultValue={nilaiAwal.jenisSekolah ?? undefined} disabled={terkunci}>
            <SelectTrigger id="jenisSekolah" aria-invalid={!!galat.jenisSekolah} className="h-12 w-full rounded-lg border-neutral-200 bg-white px-4 text-[15px] shadow-none">
              <SelectValue placeholder="Pilih" />
            </SelectTrigger>
            <SelectContent>
              {["SMA", "SMK", "MA", "Paket C"].map((j) => (
                <SelectItem key={j} value={j}>{j}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Bidang>
        <Bidang id="jurusan" label="Jurusan" galat={galat.jurusan}>
          {teks("jurusan")}
        </Bidang>
        <Bidang id="tahunLulus" label="Tahun lulus" galat={galat.tahunLulus}>
          {teks("tahunLulus", { inputMode: "numeric", maxLength: 4, placeholder: "2027" })}
        </Bidang>
        <Bidang id="nilaiRataRata" label="Nilai rata-rata rapor" galat={galat.nilaiRataRata}>
          {teks("nilaiRataRata", { inputMode: "decimal", placeholder: "86,5" })}
        </Bidang>
      </fieldset>

      {!terkunci && (
        <div className="flex flex-col gap-4 border-t border-neutral-200 pt-8 sm:flex-row sm:items-center sm:justify-between">
          <div aria-live="polite" className="text-sm">
            {tersimpan && (
              <p className="flex items-center gap-2 font-semibold text-[#2F4A3B]">
                <CircleCheck className="size-4 text-[#4B6E5A]" aria-hidden />
                Biodata tersimpan
              </p>
            )}
            {galatForm && <p role="alert" className="font-medium text-[#B45309]">{galatForm}</p>}
          </div>
          <Button
            type="submit"
            disabled={menyimpan}
            className="h-12 rounded-lg bg-[#4B6E5A] px-8 text-[15px] font-semibold text-white hover:bg-[#5C836A] disabled:opacity-70"
          >
            {menyimpan ? (<><Loader2 className="size-4 animate-spin" aria-hidden />Menyimpan</>) : "Simpan biodata"}
          </Button>
        </div>
      )}
    </form>
  );
}
