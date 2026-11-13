// =============================================================================
// PMB-APP SERVICE WORKER — WEB PUSH NOTIFICATION
// Standard: W3C Push API, Notifications API
// =============================================================================

self.addEventListener("install", (event) => {
  // Activate worker immediately
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  // Claim all active clients
  event.waitUntil(self.clients.claim());
});

/**
 * Push Event Listener
 * Menerima payload terenkripsi dari Web Push service (VAPID authenticated)
 */
self.addEventListener("push", (event) => {
  let data = {
    title: "Pemberitahuan PMB",
    body: "Ada pembaruan status pendaftaran Anda.",
    url: "/dashboard",
    tag: "pmb-notification",
  };

  if (event.data) {
    try {
      const parsed = event.data.json();
      data = { ...data, ...parsed };
    } catch {
      data.body = event.data.text() || data.body;
    }
  }

  const options = {
    body: data.body,
    icon: data.icon || "/admitra-mark.png",
    badge: data.badge || "/admitra-mark-putih.png",
    tag: data.tag || "pmb-status",
    renotify: true,
    data: {
      url: data.url || "/dashboard",
      timestamp: Date.now(),
    },
    actions: [
      {
        action: "buka",
        title: "Buka Portal",
      },
    ],
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

/**
 * Notification Click Event Listener
 * Menangani klik pengguna pada banner notifikasi browser
 */
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  // Validasi URL: Hanya izinkan path internal aplikasi (mencegah open redirect)
  let targetPath = event.notification.data?.url || "/dashboard";
  if (!targetPath.startsWith("/")) {
    targetPath = "/dashboard";
  }

  const targetUrl = new URL(targetPath, self.location.origin).href;

  event.waitUntil(
    self.clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clientList) => {
        // Jika ada tab yang sudah membuka aplikasi, fokuskan tab tersebut
        for (const client of clientList) {
          if (client.url.startsWith(self.location.origin) && "focus" in client) {
            client.navigate(targetUrl);
            return client.focus();
          }
        }
        // Jika belum ada tab yang terbuka, buka tab baru
        if (self.clients.openWindow) {
          return self.clients.openWindow(targetUrl);
        }
      })
  );
});
