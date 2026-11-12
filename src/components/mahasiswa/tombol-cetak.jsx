"use client";

import { Printer } from "lucide-react";
import { Button } from "@/components/ui/button";

/** Membuka dialog cetak browser. Pilih "Simpan sebagai PDF" untuk mendapatkan berkas PDF. */
export function TombolCetak() {
  return (
    <Button
      type="button"
      onClick={() => window.print()}
      className="h-12 rounded-lg bg-white px-6 text-[15px] font-semibold text-[#2F4A3B] hover:bg-white/90 print:hidden"
    >
      <Printer className="size-4" aria-hidden />
      Cetak bukti kelulusan PDF
    </Button>
  );
}
