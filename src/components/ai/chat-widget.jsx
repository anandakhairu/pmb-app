"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Loader2, Send, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const QUICK_PROMPTS_DEFAULT = [
  "Kapan pendaftaran Mandiri dibuka?",
  "Apa saja syarat berkas wajib?",
  "Berapa biaya seleksi Mandiri & SNBT?",
  "Apa saja program studi di ADMITRA?",
];

const QUICK_PROMPTS_BERKAS = [
  "Format & ukuran maksimal file?",
  "Bagaimana jika ijazah belum terbit?",
  "Apakah slip gaji orang tua wajib?",
  "Syarat dokumen pendaftaran lengkap?",
];

export function FormattedMessage({ text, isUser }) {
  if (isUser) {
    return <div className="whitespace-pre-wrap">{text}</div>;
  }

  const lines = text.split("\n");
  const renderedBlocks = [];
  let currentList = [];
  let isNumbered = false;

  const flushList = (keyPrefix) => {
    if (currentList.length === 0) return;
    if (isNumbered) {
      renderedBlocks.push(
        <div key={`${keyPrefix}-num`} className="my-2 space-y-2">
          {currentList.map((item, idx) => (
            <div key={idx} className="flex items-start gap-2.5">
              <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-[#4B6E5A]/15 text-[10px] font-bold text-[#4B6E5A] ring-1 ring-[#4B6E5A]/30">
                {item.num}
              </span>
              <div className="flex-1 text-[12px] leading-relaxed text-neutral-800">
                {renderInline(item.text)}
              </div>
            </div>
          ))}
        </div>
      );
    } else {
      renderedBlocks.push(
        <div key={`${keyPrefix}-bullet`} className="my-2 space-y-1.5">
          {currentList.map((item, idx) => (
            <div key={idx} className="flex items-start gap-2.5">
              <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-[#4B6E5A]" />
              <div className="flex-1 text-[12px] leading-relaxed text-neutral-800">
                {renderInline(item.text)}
              </div>
            </div>
          ))}
        </div>
      );
    }
    currentList = [];
  };

  const renderInline = (str) => {
    if (!str) return null;
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
        return (
          <strong key={i} className="font-bold text-neutral-900">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList(`gap-${i}`);
      return;
    }

    // Numbered list: "1. Pas Foto"
    const numMatch = trimmed.match(/^(\d+)[\.\)]\s+(.*)/);
    if (numMatch) {
      if (currentList.length > 0 && !isNumbered) flushList(`switch-${i}`);
      isNumbered = true;
      currentList.push({ num: numMatch[1], text: numMatch[2] });
      return;
    }

    // Bullet list: "• Item" or "- Item" or "* Item"
    const bulletMatch = trimmed.match(/^([•\-\*])\s+(.*)/);
    if (bulletMatch) {
      if (currentList.length > 0 && isNumbered) flushList(`switch-${i}`);
      isNumbered = false;
      currentList.push({ text: bulletMatch[2] });
      return;
    }

    flushList(`line-${i}`);

    // Section header badge: "📄 DOKUMEN UTAMA" or "📑 DOKUMEN KHUSUS"
    if (trimmed.startsWith("📄") || trimmed.startsWith("📑")) {
      renderedBlocks.push(
        <div
          key={`header-${i}`}
          className="mt-3 mb-1.5 rounded-lg border border-[#4B6E5A]/20 bg-[#4B6E5A]/5 px-2.5 py-1 text-[11px] font-bold text-[#3B5746]"
        >
          {trimmed}
        </div>
      );
      return;
    }

    // Callout tip: "💡 Tips"
    if (trimmed.startsWith("💡")) {
      renderedBlocks.push(
        <div
          key={`tip-${i}`}
          className="mt-3 rounded-lg border border-amber-200 bg-amber-50/80 p-2.5 text-[11px] leading-relaxed text-amber-900"
        >
          {renderInline(trimmed)}
        </div>
      );
      return;
    }

    // Regular paragraph
    renderedBlocks.push(
      <p key={`p-${i}`} className="my-1.5 text-[12px] leading-relaxed text-neutral-700">
        {renderInline(trimmed)}
      </p>
    );
  });

  flushList("end");

  return <div className="space-y-0.5">{renderedBlocks}</div>;
}

export function ChatBox({ onTutup }) {
  const pathname = usePathname();
  const isHalamanBerkas = pathname?.includes("/berkas");
  const quickPrompts = isHalamanBerkas ? QUICK_PROMPTS_BERKAS : QUICK_PROMPTS_DEFAULT;

  const [pesanInput, setPesanInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatLog, setChatLog] = useState([
    {
      sender: "assistant",
      text: isHalamanBerkas
        ? "Halo! Saya **ADMITRA**. Ada yang bisa dibantu mengenai format dokumen, batas ukuran 5MB, atau berkas pendaftaran?"
        : "Halo! Saya **ADMITRA**, asisten informasi PMB Universitas ADMITRA 2027/2028. Ada yang bisa dibantu mengenai jalur pendaftaran, persyaratan berkas, atau estimasi UKT?",
    },
  ]);

  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog]);

  async function kirim(pesanTeks) {
    const teks = (pesanTeks || pesanInput).trim();
    if (!teks || loading) return;

    const pesanBaru = { sender: "user", text: teks };
    setChatLog((prev) => [...prev, pesanBaru]);
    setPesanInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: teks,
          history: chatLog,
        }),
      });

      const data = await res.json();
      if (data.success && data.reply) {
        setChatLog((prev) => [...prev, { sender: "assistant", text: data.reply }]);
      } else {
        setChatLog((prev) => [
          ...prev,
          {
            sender: "assistant",
            text: data.error || "Maaf, terjadi gangguan saat memproses pertanyaan Anda.",
          },
        ]);
      }
    } catch {
      setChatLog((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: "Gagal terhubung ke pusat informasi. Silakan periksa koneksi internet Anda.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[520px] w-[360px] max-w-full flex-col rounded-3xl border border-neutral-200/90 bg-white shadow-2xl overflow-hidden sm:w-[400px]">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-neutral-100 bg-[#4B6E5A] px-5 py-3.5 text-white">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-2xl bg-white/15 p-1 shadow-xs">
            <Image
              src="/admitra-avatar.png"
              alt="ADMITRA"
              width={40}
              height={40}
              className="size-8 object-contain"
            />
          </div>
          <div>
            <h3 className="text-sm font-bold leading-tight tracking-wide">ADMITRA</h3>
            <p className="text-[11px] text-white/80">Layanan Informasi PMB Terpadu</p>
          </div>
        </div>
        {onTutup && (
          <button
            type="button"
            onClick={onTutup}
            className="rounded-lg p-1.5 text-white/80 hover:bg-white/10 hover:text-white"
            aria-label="Tutup chat"
          >
            <X className="size-4.5" />
          </button>
        )}
      </div>

      {/* CHAT LOG / THREAD */}
      <div className="flex-1 space-y-3.5 overflow-y-auto p-4 text-xs leading-relaxed bg-neutral-50/50">
        {chatLog.map((c, i) => (
          <div
            key={i}
            className={`flex ${c.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[88%] rounded-2xl p-3.5 shadow-2xs ${
                c.sender === "user"
                  ? "bg-[#4B6E5A] text-white rounded-br-xs font-medium"
                  : "bg-white border border-neutral-200/90 text-neutral-800 rounded-bl-xs"
              }`}
            >
              <FormattedMessage text={c.text} isUser={c.sender === "user"} />
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-2xl border border-neutral-200 bg-white p-3 text-neutral-500 shadow-2xs">
              <Loader2 className="size-3.5 animate-spin text-[#4B6E5A]" />
              <span>Mengetik jawaban...</span>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* QUICK CHIP SUGGESTIONS */}
      {chatLog.length === 1 && (
        <div className="border-t border-neutral-100 bg-white p-2.5">
          <p className="mb-1.5 px-2 text-[10px] font-bold text-neutral-400 uppercase">
            Pertanyaan Populer:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {quickPrompts.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => kirim(q)}
                className="rounded-lg border border-neutral-200 bg-neutral-50 px-2.5 py-1 text-[11px] font-medium text-neutral-600 hover:border-[#4B6E5A] hover:bg-[#4B6E5A]/5 hover:text-[#4B6E5A]"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* INPUT FORM */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          kirim();
        }}
        className="flex items-center gap-2 border-t border-neutral-200/80 bg-white p-3"
      >
        <input
          type="text"
          value={pesanInput}
          onChange={(e) => setPesanInput(e.target.value)}
          placeholder="Tanyakan seputar PMB..."
          disabled={loading}
          className="h-10 flex-1 rounded-xl border border-neutral-200 px-3.5 text-xs text-neutral-900 placeholder:text-neutral-400 focus:outline-2 focus:outline-[#4B6E5A] disabled:opacity-50"
        />
        <Button
          type="submit"
          size="sm"
          disabled={!pesanInput.trim() || loading}
          className="h-10 w-10 shrink-0 rounded-xl bg-[#4B6E5A] p-0 text-white hover:bg-[#5C836A] shadow-xs"
        >
          <Send className="size-4" />
        </Button>
      </form>
    </div>
  );
}

/**
 * Floating Chat Widget untuk Halaman Publik & Dashboard Mahasiswa
 * Sembunyikan di area Admin Back-Office (/admin/*) dan Halaman Autentikasi (/login, /register).
 * Mahasiswa di /dashboard/* (khususnya saat upload dokumen /dashboard/berkas) dan landing page (/) tetap memiliki toggle chat di kanan bawah.
 */
export function ChatWidget() {
  const pathname = usePathname();
  const [buka, setBuka] = useState(false);

  // Sembunyikan di area admin dan halaman login/register
  const isHidden =
    pathname?.startsWith("/admin") ||
    pathname === "/login" ||
    pathname === "/register";

  if (isHidden) {
    return null;
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!buka && (
        <button
          type="button"
          onClick={() => setBuka(true)}
          className="group flex items-center gap-2.5 rounded-full bg-[#4B6E5A] pl-2.5 pr-5 py-2 text-white shadow-xl transition-all hover:bg-[#3B5746] hover:scale-105 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#4B6E5A]"
        >
          <div className="relative flex size-9 items-center justify-center rounded-full bg-white/15 p-1 shadow-xs">
            <Image
              src="/admitra-chat-bot.png"
              alt="ADMITRA Mascot"
              width={36}
              height={36}
              className="size-7 object-contain"
            />
            <span className="absolute -top-0.5 -right-0.5 size-2 rounded-full bg-emerald-400 ring-2 ring-[#4B6E5A]" />
          </div>
          <span className="text-sm font-bold tracking-wider">ADMITRA</span>
        </button>
      )}
      {buka && (
        <div className="animate-in slide-in-from-bottom-5">
          <ChatBox onTutup={() => setBuka(false)} />
        </div>
      )}
    </div>
  );
}

