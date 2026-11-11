import Image from "next/image";
import Link from "next/link";

// Ikon + tulisan ADMITRA untuk navbar, footer, dan header mobile.
// putih = true untuk latar gelap (footer).
export function Logo({ putih = false, className = "" }) {
  return (
    <Link
      href="/"
      aria-label="ADMITRA, ke beranda"
      className={`flex items-center gap-2.5 ${className}`}
    >
      <Image
        src={putih ? "/admitra-mark-putih.png" : "/admitra-mark.png"}
        alt=""
        width={360}
        height={242}
        priority
        className="h-8 w-auto"
      />
      <span
        className={`text-[17px] font-extrabold tracking-[0.14em] ${
          putih ? "text-white" : "text-[#222B35]"
        }`}
      >
        ADMITRA
      </span>
    </Link>
  );
}