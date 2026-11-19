// =============================================================================
// SSRF & PUSH SERVICE ENDPOINT VALIDATOR (DEFENSE-IN-DEPTH)
// Standard: RFC 8030 / W3C Push Service Origins
// =============================================================================

export const EXACT_PUSH_HOSTS = [
  "fcm.googleapis.com",
  "android.googleapis.com",
  "updates.push.services.mozilla.com",
  "push.services.mozilla.com",
  "web.push.apple.com",
];

export const SUBDOMAIN_PUSH_HOSTS = [
  "push.apple.com",
  "notify.windows.com",
];

/**
 * Validasi ketat endpoint push browser untuk mencegah SSRF (Server-Side Request Forgery)
 * - Menolak skema non-HTTPS
 * - Menolak userinfo (@, username, password)
 * - Menolak port non-standar (hanya port 443 yang diizinkan)
 * - Menolak literal IPv4, IPv6, loopback, link-local, dan cloud metadata IPs
 * - Mencocokkan hostname secara tepat terhadap allowlist resmi W3C push provider
 *
 * @param {string} endpointStr
 * @returns {boolean}
 */
export function isValidPushEndpoint(endpointStr) {
  try {
    if (typeof endpointStr !== "string" || endpointStr.includes("@")) {
      return false;
    }

    const url = new URL(endpointStr);
    if (url.protocol !== "https:") return false;
    if (url.username || url.password) return false;
    if (url.port && url.port !== "443" && url.port !== "") return false;

    // Normalisasi hostname: lowercase dan hapus trailing dot
    const host = url.hostname.toLowerCase().replace(/\.$/, "");

    // Tolak literal IPv4, IPv6, localhost, loopback, link-local metadata
    if (
      /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(host) ||
      host === "localhost" ||
      host.endsWith(".localhost") ||
      host.endsWith(".local") ||
      host.endsWith(".internal") ||
      host.includes(":") || // IPv6
      host.includes("[")
    ) {
      return false;
    }

    // 1. Cek exact host match
    if (EXACT_PUSH_HOSTS.includes(host)) return true;

    // 2. Cek subdomain match untuk provider yang memakai regional gateway (Apple APNs & Windows WNS)
    return SUBDOMAIN_PUSH_HOSTS.some(
      (allowed) => host === allowed || host.endsWith("." + allowed)
    );
  } catch {
    return false;
  }
}
