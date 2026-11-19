import { kirimPesanAI } from "../src/lib/ai/provider.js";

async function main() {
  console.log("=================================================");
  console.log("🧪 TESTING 9ROUTER INTEGRATION DARI VPS");
  console.log("=================================================\n");

  const prompt = [
    {
      role: "system",
      content: "Anda adalah asisten AI resmi Penerimaan Mahasiswa Baru (PMB) Universitas ADMITRA. Jawab pertanyaan calon mahasiswa secara ramah, formal, dan ringkas dalam Bahasa Indonesia.",
    },
    {
      role: "user",
      content: "Halo, apa saja 3 jalur seleksi yang tersedia di PMB ADMITRA?",
    },
  ];

  console.log("Mengirim pesan ke 9Router...");
  const start = Date.now();
  const res = await kirimPesanAI(prompt);
  const elapsed = Date.now() - start;

  if (res.success) {
    console.log(`✅ BERHASIL TERHUBUNG DALAM ${elapsed}ms!`);
    console.log(`🤖 Model yang digunakan: ${res.model}\n`);
    console.log("--- JAWABAN CHATBOT ---");
    console.log(res.content);
    console.log("------------------------\n");
  } else {
    console.error("❌ GAGAL:", res.error);
    process.exit(1);
  }
}

main();
