import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata = {
  title: {
    default: "ADMITRA | Portal Penerimaan Mahasiswa Baru Terpadu",
    template: "%s | ADMITRA",
  },
  description:
    "Daftar, unggah berkas, dan pantau hasil seleksi penerimaan mahasiswa baru dalam satu portal.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="id" className="scroll-smooth">
      <body
        className={`${jakarta.className} bg-[#F5F6F5] text-neutral-900 antialiased`}
      >
        {children}
      </body>
    </html>
  );
}