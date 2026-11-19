// =============================================================================
// AI PROVIDER ADAPTER: 9ROUTER / OPENAI-COMPATIBLE
// =============================================================================

const AI_BASE_URL = process.env.AI_BASE_URL || "http://43.156.176.43:20128/v1";
const AI_API_KEY = process.env.AI_API_KEY || "";
const AI_CHAT_MODEL = process.env.AI_CHAT_MODEL || "radoxai/gemini-3.7-flash";
const AI_ENABLED = process.env.AI_ENABLED === "true";

/**
 * Mengirim prompt percakapan ke endpoint 9Router VPS
 * @param {Array<{ role: 'system'|'user'|'assistant', content: string }>} messages
 * @param {Object} options
 * @returns {Promise<{ success: boolean, content?: string, model?: string, error?: string }>}
 */
export async function kirimPesanAI(messages, options = {}) {
  if (!AI_ENABLED) {
    return {
      success: false,
      error: "Fitur AI dinonaktifkan di pengaturan sistem (AI_ENABLED=false).",
    };
  }

  const model = options.model || AI_CHAT_MODEL;
  const temperature = options.temperature ?? 0.2;
  const max_tokens = options.max_tokens || 800;

  try {
    const res = await fetch(`${AI_BASE_URL}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${AI_API_KEY}`,
      },
      body: JSON.stringify({
        model,
        messages,
        temperature,
        max_tokens,
      }),
      signal: AbortSignal.timeout(options.timeoutMs || 25000),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`9Router error (${res.status}): ${errText.slice(0, 150)}`);
    }

    const raw = await res.text();
    // 9Router SSE streaming split
    const cleanJson = raw.split("data: [DONE]")[0].trim();
    const data = JSON.parse(cleanJson);

    const content = data.choices?.[0]?.message?.content?.trim();
    if (!content) {
      throw new Error("Respon model kosong dari 9Router.");
    }

    return {
      success: true,
      content,
      model: data.model || model,
    };
  } catch (err) {
    console.error("[9Router AI Error]:", err.message);
    return {
      success: false,
      error: "Gagal memproses permintaan AI: " + err.message,
    };
  }
}
