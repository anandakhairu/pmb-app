"use client";

import { useMemo, useState } from "react";
import { Calculator, HandCoins, ShieldCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { FAKULTAS_LIST, PRODI } from "@/lib/data-publik";

/* Aturan golongan (mockup, sesuaikan dengan kebijakan kampus):
   penghasilan per tanggungan = penghasilan orang tua / jumlah tanggungan
   di bawah Rp 1 juta      -> golongan 1
   Rp 1 juta sampai 2,5 juta -> golongan 2
   di atas Rp 2,5 juta     -> golongan 3
   Untuk 2 tanggungan, batasnya setara Rp 2 juta dan Rp 5 juta per bulan. */
const BATAS_PER_ORANG = [1_000_000, 2_500_000];

const TANGGUNGAN = [
  { value: "1", label: "1 orang" },
  { value: "2", label: "2 orang" },
  { value: "3", label: "3 orang" },
  { value: "4", label: "4 orang" },
  { value: "5", label: "5 orang atau lebih" },
];

const PRODI_PER_FAKULTAS = FAKULTAS_LIST.map((f) => ({
  fakultas: f,
  daftar: PRODI.filter((p) => p.fakultas === f),
}));

const POIN = [
  { icon: Calculator, judul: "Hitungan langsung", isi: "Hasil muncul seketika saat data diisi, tanpa perlu login." },
  { icon: ShieldCheck, judul: "Dasar yang jelas", isi: "Golongan ditentukan dari penghasilan per tanggungan, dan tarif berbeda tiap program studi." },
  { icon: HandCoins, judul: "Termasuk KIP-Kuliah", isi: "Aktifkan opsi KIP-K untuk melihat biaya yang ditanggung beasiswa." },
];

const rupiah = new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 });
const juta = (n) => `Rp ${new Intl.NumberFormat("id-ID", { maximumFractionDigits: 1 }).format(n / 1_000_000)} juta`;

function hitungGolongan(penghasilan, tanggungan) {
  const perOrang = penghasilan / tanggungan;
  if (perOrang < BATAS_PER_ORANG[0]) return 1;
  if (perOrang <= BATAS_PER_ORANG[1]) return 2;
  return 3;
}

export function KalkulatorUkt() {
  const [prodi, setProdi] = useState("");
  const [penghasilan, setPenghasilan] = useState(""); // hanya digit
  const [tanggungan, setTanggungan] = useState("3");
  const [kip, setKip] = useState(false);

  const prodiTerpilih = PRODI.find((p) => p.value === prodi);
  const t = Number(tanggungan);
  const b1 = BATAS_PER_ORANG[0] * t;
  const b2 = BATAS_PER_ORANG[1] * t;
  const rentang = [`Di bawah ${juta(b1)}`, `${juta(b1)} sampai ${juta(b2)}`, `Di atas ${juta(b2)}`];

  const golongan = useMemo(() => {
    if (!prodi || penghasilan === "") return null;
    return hitungGolongan(Number(penghasilan), t);
  }, [prodi, penghasilan, t]);

  const biaya = golongan && prodiTerpilih ? prodiTerpilih.ukt[golongan - 1] : 0;
  const penghasilanTampil = penghasilan ? new Intl.NumberFormat("id-ID").format(Number(penghasilan)) : "";

  const fieldClass = "h-12 rounded-lg border-neutral-200 bg-white px-4 text-[15px] shadow-none placeholder:text-neutral-400 focus-visible:border-[#4B6E5A] focus-visible:ring-[3px] focus-visible:ring-[#4B6E5A]/15";
  const triggerClass = "mt-2 h-12 w-full rounded-lg border-neutral-200 bg-white px-4 text-[15px] shadow-none focus:border-[#4B6E5A] focus:ring-[3px] focus:ring-[#4B6E5A]/15";
  const labelClass = "text-[13px] font-semibold text-neutral-700";

  return (
    <section id="simulasi-ukt" className="scroll-mt-16 bg-white py-20 sm:py-28">
      <div className="mx-auto grid max-w-6xl gap-12 px-6 lg:grid-cols-12 lg:gap-16">
        <div className="lg:col-span-5">
          <h2 className="text-3xl font-extrabold leading-tight tracking-tight text-[#2F4A3B] sm:text-4xl">
            Hitung Estimasi Biaya Kuliahmu Transparan
          </h2>
          <p className="mt-5 max-w-md text-base leading-relaxed text-neutral-600">
            Pilih salah satu dari {PRODI.length} program studi, isi penghasilan orang tua, dan lihat perkiraan UKT per semester sebelum kamu mendaftar.
          </p>
          <ul className="mt-10 space-y-6">
            {POIN.map((p) => {
              const Icon = p.icon;
              return (
                <li key={p.judul} className="flex gap-4">
                  <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-[#4B6E5A]/10 text-[#4B6E5A]">
                    <Icon className="size-5" />
                  </span>
                  <div>
                    <p className="text-[15px] font-bold text-neutral-900">{p.judul}</p>
                    <p className="mt-1 text-sm leading-relaxed text-neutral-600">{p.isi}</p>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="lg:col-span-7">
          <Card className="rounded-xl border-neutral-200 bg-white p-0 shadow-xl ring-0">
            <CardContent className="space-y-6 p-6 sm:p-10">
              <div>
                <Label htmlFor="prodi" className={labelClass}>Program studi target</Label>
                <Select value={prodi} onValueChange={setProdi}>
                  <SelectTrigger id="prodi" className={triggerClass}>
                    <SelectValue placeholder="Pilih program studi" />
                  </SelectTrigger>
                  <SelectContent className="max-h-80">
                    {PRODI_PER_FAKULTAS.map((g) => (
                      <SelectGroup key={g.fakultas}>
                        <SelectLabel>{g.fakultas}</SelectLabel>
                        {g.daftar.map((p) => (
                          <SelectItem key={p.value} value={p.value}>{p.nama}</SelectItem>
                        ))}
                      </SelectGroup>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-6 sm:grid-cols-2">
                <div>
                  <Label htmlFor="penghasilan" className={labelClass}>Penghasilan orang tua per bulan</Label>
                  <div className="relative mt-2">
                    <span className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-[15px] font-medium text-neutral-400">Rp</span>
                    <Input
                      id="penghasilan"
                      inputMode="numeric"
                      autoComplete="off"
                      placeholder="0"
                      value={penghasilanTampil}
                      onChange={(e) => setPenghasilan(e.target.value.replace(/\D/g, "").slice(0, 12))}
                      className={`${fieldClass} pl-12`}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="tanggungan" className={labelClass}>Jumlah tanggungan</Label>
                  <Select value={tanggungan} onValueChange={setTanggungan}>
                    <SelectTrigger id="tanggungan" className={triggerClass}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {TANGGUNGAN.map((o) => (
                        <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex items-center justify-between gap-4 rounded-lg border border-neutral-200 px-4 py-3.5">
                <div>
                  <Label htmlFor="kip" className="text-[15px] font-semibold text-neutral-800">Saya penerima KIP-Kuliah</Label>
                  <p className="mt-0.5 text-[13px] text-neutral-500">UKT ditanggung beasiswa jika lolos verifikasi.</p>
                </div>
                <Switch id="kip" checked={kip} onCheckedChange={setKip} className="data-[state=checked]:bg-[#4B6E5A]" />
              </div>

              <div aria-live="polite" className="rounded-xl bg-[#E8F0EC] p-6 sm:p-8">
                {golongan ? (
                  <>
                    <p className="text-sm font-medium text-[#4B6E5A]">Estimasi UKT per semester</p>
                    <p className="mt-2 text-4xl font-extrabold tracking-tight text-[#2F4A3B] sm:text-5xl">
                      {rupiah.format(kip ? 0 : biaya)}
                    </p>
                    <p className="mt-3 text-[15px] leading-relaxed text-[#2F4A3B]/80">
                      {kip ? (
                        <>Ditanggung KIP-Kuliah. Tanpa beasiswa, kamu berada di Golongan {golongan} ({rupiah.format(biaya)}).</>
                      ) : (
                        <>
                          Golongan {golongan} untuk <span className="font-semibold">{prodiTerpilih.nama}</span>, {prodiTerpilih.fakultas}.
                          Penghasilan per tanggungan sekitar {rupiah.format(Math.round(Number(penghasilan) / t))}.
                        </>
                      )}
                    </p>
                    <ul className="mt-6 grid gap-2 sm:grid-cols-3">
                      {[1, 2, 3].map((g) => {
                        const aktif = g === golongan;
                        return (
                          <li
                            key={g}
                            className={aktif ? "rounded-lg bg-[#4B6E5A] px-4 py-3 text-white" : "rounded-lg border border-[#4B6E5A]/20 px-4 py-3 text-[#2F4A3B]/70"}
                          >
                            <p className="text-sm font-bold">Golongan {g}</p>
                            <p className={aktif ? "mt-0.5 text-xs text-white/80" : "mt-0.5 text-xs"}>{rentang[g - 1]}</p>
                            <p className="mt-2 text-sm font-semibold">{rupiah.format(prodiTerpilih.ukt[g - 1])}</p>
                          </li>
                        );
                      })}
                    </ul>
                  </>
                ) : (
                  <p className="text-[15px] leading-relaxed text-[#2F4A3B]/70">
                    {!prodi ? "Pilih program studi dan isi penghasilan untuk melihat estimasi UKT." : "Isi penghasilan orang tua untuk melihat estimasi UKT."}
                  </p>
                )}
              </div>

              <p className="text-[13px] leading-relaxed text-neutral-500">
                <span className="font-semibold text-[#D97706]">Catatan:</span> ini hanya simulasi. Golongan UKT final dan status KIP-Kuliah ditetapkan setelah panitia memverifikasi dokumen Anda.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}