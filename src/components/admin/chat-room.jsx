"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import {
  HelpCircle,
  Loader2,
  MessageSquareText,
  RotateCcw,
  Send,
  Sparkles,
} from "lucide-react";
import { FormattedMessage } from "@/components/ai/chat-widget";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const QUICK_PROMPTS = [
  "Kapan pendaftaran Mandiri dibuka?",
  "Apa saja syarat berkas wajib?",
  "Berapa rincian biaya pendaftaran tiap jalur?",
  "Apa saja 5 program studi di ADMITRA dan kuotanya?",
  "Bagaimana simulasi pengelompokan UKT?",
];

const INITIAL_MESSAGE = {
  sender: "assistant",
  text:
    "Halo! Selamat datang di Chat ADMITRA.\n\n" +
    "Layanan ini terhubung dengan basis pengetahuan resmi PMB Universitas ADMITRA 2027/2028. " +
    "Anda dapat menanyakan jadwal pembukaan jalur, verifikasi persyaratan berkas, kuota prodi, atau simulasi UKT.",
};

export function AdminChatRoom() {
  const [pesanInput, setPesanInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatLog, setChatLog] = useState([INITIAL_MESSAGE]);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog, loading]);

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
        setChatLog((prev) => [
          ...prev,
          {
            sender: "assistant",
            text: data.reply,
            fallback: data.fallback,
            model: data.model,
          },
        ]);
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

  function resetChat() {
    setChatLog([INITIAL_MESSAGE]);
  }

  return (
    <div className="flex h-[calc(100dvh-130px)] min-h-[580px] flex-col rounded-2xl border border-neutral-200/90 bg-white shadow-xs overflow-hidden">
      {/* ----------------------------- CHAT ROOM TOPBAR ----------------------------- */}
      <div className="flex items-center justify-between border-b border-neutral-200/80 bg-neutral-50/70 px-5 py-3.5">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-white p-1 border border-neutral-200/80 shadow-xs">
            <Image
              src="/admitra-avatar.png"
              alt="ADMITRA Mascot"
              width={40}
              height={40}
              className="size-8 object-contain"
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-neutral-900">
                Pusat Informasi dan Konsultasi ADMITRA
              </h2>
              <Badge
                variant="outline"
                className="border-emerald-300 bg-emerald-50 text-[10px] font-bold text-emerald-800"
              >
                <span className="mr-1 size-1.5 rounded-full bg-emerald-500 inline-block animate-pulse" />
                Live 2027/2028
              </Badge>
            </div>
            <p className="text-[11px] text-neutral-500">
              Basis data resmi pendaftaran, jadwal, verifikasi berkas, dan ketentuan UKT
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={resetChat}
          className="flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-semibold text-neutral-600 transition-colors hover:bg-neutral-100 hover:text-neutral-900"
          title="Bersihkan percakapan dan mulai baru"
        >
          <RotateCcw className="size-3.5" />
          <span className="hidden sm:inline">Mulai Ulang</span>
        </button>
      </div>

      {/* ----------------------------- CHAT MESSAGES STREAM ----------------------------- */}
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 space-y-5 bg-[#FAFBF9]">
        <div className="mx-auto max-w-3xl space-y-4">
          {chatLog.map((c, i) => (
            <div
              key={i}
              className={`flex ${c.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              {c.sender === "assistant" && (
                <div className="mr-3 flex size-8 shrink-0 items-center justify-center rounded-xl bg-white p-1 border border-neutral-200/80 shadow-2xs">
                  <Image
                    src="/admitra-avatar.png"
                    alt="ADMITRA"
                    width={32}
                    height={32}
                    className="size-6 object-contain"
                  />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-4 shadow-2xs ${
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
            <div className="flex justify-start items-center gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-[#4B6E5A]/15 text-[#4B6E5A]">
                <MessageSquareText className="size-4" />
              </div>
              <div className="flex items-center gap-2 rounded-2xl border border-neutral-200 bg-white px-4 py-3 text-xs text-neutral-500 shadow-2xs">
                <Loader2 className="size-4 animate-spin text-[#4B6E5A]" />
                <span>Menyiapkan informasi resmi...</span>
              </div>
            </div>
          )}

          <div ref={endRef} />
        </div>
      </div>

      {/* ----------------------------- QUICK PROMPTS CHIPS ----------------------------- */}
      <div className="border-t border-neutral-200/60 bg-white px-4 py-2.5 sm:px-6">
        <div className="mx-auto max-w-3xl">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            <span className="shrink-0 flex items-center gap-1 text-[11px] font-bold text-neutral-400 uppercase">
              <HelpCircle className="size-3" />
              Pertanyaan Populer:
            </span>
            {QUICK_PROMPTS.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => kirim(q)}
                className="shrink-0 rounded-lg border border-neutral-200 bg-neutral-50 px-2.5 py-1 text-[11px] font-medium text-neutral-700 transition-colors hover:border-[#4B6E5A] hover:bg-[#4B6E5A]/5 hover:text-[#4B6E5A]"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ----------------------------- INPUT BOTTOM BAR ----------------------------- */}
      <div className="border-t border-neutral-200/90 bg-white p-3.5 sm:px-6 sm:py-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            kirim();
          }}
          className="mx-auto flex max-w-3xl items-center gap-2.5"
        >
          <input
            type="text"
            value={pesanInput}
            onChange={(e) => setPesanInput(e.target.value)}
            placeholder="Tanyakan jadwal pendaftaran, syarat berkas, prodi, atau biaya kuliah..."
            disabled={loading}
            className="h-11 flex-1 rounded-xl border border-neutral-200 px-4 text-sm text-neutral-900 placeholder:text-neutral-400 focus:outline-2 focus:outline-[#4B6E5A] disabled:opacity-50"
          />
          <Button
            type="submit"
            disabled={!pesanInput.trim() || loading}
            className="h-11 px-5 rounded-xl bg-[#4B6E5A] text-white hover:bg-[#3B5746] font-semibold text-sm shadow-xs flex items-center gap-2"
          >
            <span>Kirim</span>
            <Send className="size-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
