"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FAKULTAS_LIST, PRODI } from "@/lib/data-publik";

const BATCH = 12;

export function ProgramStudi() {
  const [cari, setCari] = useState("");
  const [fakultas, setFakultas] = useState("semua");
  const [tampil, setTampil] = useState(BATCH);

  const hasil = useMemo(() => {
    const q = cari.trim().toLowerCase();
    return PRODI.filter(
      (p) =>
        (fakultas === "semua" || p.fakultas === fakultas) &&
        (q === "" || p.nama.toLowerCase().includes(q)),
    );
  }, [cari, fakultas]);

  return (
    <section id="program-studi" className="scroll-mt-16 bg-white py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <h2 className="max-w-md text-3xl font-extrabold leading-tight tracking-tight text-[#2F4A3B] sm:text-4xl">
            {PRODI.length} program studi, {FAKULTAS_LIST.length} fakultas
          </h2>
          <p className="max-w-md text-base leading-relaxed text-neutral-600">
            Cari berdasarkan nama atau saring per fakultas.
          </p>
        </div>

        <div className="mt-10 grid gap-3 sm:grid-cols-[1fr_20rem]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-neutral-400" />
            <Input
              value={cari}
              onChange={(e) => { setCari(e.target.value); setTampil(BATCH); }}
              placeholder="Cari program studi"
              aria-label="Cari program studi"
              className="h-12 rounded-lg border-neutral-200 bg-white pl-11 text-[15px] shadow-none focus-visible:border-[#4B6E5A] focus-visible:ring-[3px] focus-visible:ring-[#4B6E5A]/15"
            />
          </div>
          <Select value={fakultas} onValueChange={(v) => { setFakultas(v); setTampil(BATCH); }}>
            <SelectTrigger
              aria-label="Saring fakultas"
              className="h-12 w-full rounded-lg border-neutral-200 bg-white px-4 text-[15px] shadow-none focus:border-[#4B6E5A] focus:ring-[3px] focus:ring-[#4B6E5A]/15"
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="semua">Semua fakultas</SelectItem>
              {FAKULTAS_LIST.map((f) => (
                <SelectItem key={f} value={f}>{f}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {hasil.length === 0 ? (
          <p className="mt-12 text-center text-[15px] text-neutral-500">
            Tidak ada program studi yang cocok dengan pencarianmu.
          </p>
        ) : (
          <ul className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {hasil.slice(0, tampil).map((p) => (
              <li key={p.value} className="flex flex-col rounded-xl border border-neutral-200 p-5 transition-colors hover:border-[#4B6E5A]">
                <p className="text-[15px] font-bold leading-snug text-neutral-900">{p.nama}</p>
                <p className="mt-1 text-[13px] leading-snug text-neutral-500">{p.fakultas}</p>
                <div className="mt-auto flex items-center gap-2 pt-5 text-xs font-semibold">
                  <span className="rounded-md bg-[#E8F0EC] px-2 py-1 text-[#4B6E5A]">{p.jenjang}</span>
                  <span className="text-neutral-500">Akreditasi {p.akreditasi}</span>
                </div>
              </li>
            ))}
          </ul>
        )}

        {hasil.length > tampil && (
          <div className="mt-8 flex justify-center">
            <Button
              variant="outline"
              onClick={() => setTampil((n) => n + BATCH)}
              className="h-11 rounded-lg border-neutral-300 px-6 text-sm font-semibold text-neutral-800 hover:border-[#4B6E5A] hover:bg-transparent hover:text-[#4B6E5A]"
            >
              Tampilkan lebih banyak ({hasil.length - tampil} lagi)
            </Button>
          </div>
        )}
      </div>
    </section>
  );
}