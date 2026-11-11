"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";

// Menampilkan foto dari public/images/. Kalau file belum ada atau gagal
// dimuat, otomatis tampil placeholder bermerek. Atur ukuran/bentuk lewat className.
export function Foto({ src, alt, className = "", priority = false, sizes }) {
  const [gagal, setGagal] = useState(false);
  const ref = useRef(null);

  // Menangkap kegagalan muat yang terjadi sebelum React aktif (setelah SSR).
  useEffect(() => {
    const el = ref.current;
    if (el && el.complete && el.naturalWidth === 0) setGagal(true);
  }, []);

  return (
    <div className={`relative overflow-hidden bg-[#E1E6E2] ${className}`}>
      {src && !gagal ? (
        <Image
          ref={ref}
          src={src}
          alt={alt}
          fill
          priority={priority}
          sizes={sizes ?? "(min-width: 1024px) 45vw, 100vw"}
          className="object-cover"
          onError={() => setGagal(true)}
        />
      ) : (
        <div
          role="img"
          aria-label={`Tempat foto: ${alt}`}
          className="absolute inset-0 flex flex-col items-center justify-center gap-3"
        >
          <Image
            src="/admitra-mark.png"
            alt=""
            width={360}
            height={242}
            className="h-12 w-auto opacity-30"
          />
          <span className="px-4 text-center text-xs font-medium text-[#4B6E5A]/60">
            {alt}
          </span>
        </div>
      )}
    </div>
  );
}