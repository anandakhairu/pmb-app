# Background Worker Operations & Runbook — PMB-APP

This guide provides operational runbooks for developing, deploying, monitoring, and troubleshooting the standalone notification background worker.

---

## 1. Quick Start & Execution Commands

### Development Mode
Ensure Redis is running (or configured via `REDIS_URL` in `.env`), then start the worker:
```bash
npm run worker
# or directly:
node --env-file=.env src/workers/notification-worker.js
```

### Production Deployment (Systemd / PM2 / Docker)
The worker must run as an independent, persistent process alongside Next.js.

**Using PM2:**
```bash
pm2 start src/workers/notification-worker.js --name "pmb-notification-worker" --env .env
pm2 logs pmb-notification-worker
```

**Using Systemd (`/etc/systemd/system/pmb-worker.service`):**
```ini
[Unit]
Description=PMB Background Notification Worker
After=network.target redis.target

[Service]
Type=simple
User=pmbapp
WorkingDirectory=/var/www/pmb-app
ExecStart=/usr/bin/node --env-file=/var/www/pmb-app/.env src/workers/notification-worker.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

---

## 2. Worker Lifecycle & Shutdown Protocol

* **Concurrency:** Defaults to `2` concurrent jobs per worker thread with rate limiter `20` dispatches per second.
* **Graceful Shutdown (`SIGINT` / `SIGTERM`):**
  1. Stops accepting new jobs from BullMQ.
  2. Awaits completion of currently in-flight Web Push HTTPS dispatches.
  3. Closes Redis connections (`connection.quit()`).
  4. Disconnects Prisma client pool (`prisma.$disconnect()`).
  5. Exits cleanly with status code `0`.

---

## 3. Error Handling & Invalidation Strategy

| Push Service Response | Classification | Worker Action |
| :--- | :--- | :--- |
| **HTTP 201 Created** | Success | Log successful dispatch; update `perangkat_notifikasi.terakhir_dipakai = NOW()`. |
| **HTTP 404 Not Found**| Expired Subscription | Browser endpoint no longer exists; set `aktif = false` in database. |
| **HTTP 410 Gone** | Revoked Subscription | User uninstalled PWA or revoked permission; set `aktif = false` in database. |
| **HTTP 429 Too Many Req** | Rate Limited | Transient error; BullMQ automatically retries with exponential backoff (delay 2s, 4s, 8s). |
| **HTTP 5xx Server Error** | Push Provider Outage| Transient error; BullMQ retries up to 3 attempts before marking failed. |
| **Network ECONNREFUSED**| Redis / DB Connection | Handled by connection retry strategy; fails safe without crashing web app. |

---

## 4. Redis Memory & Eviction Policy

* **Policy:** Set Redis `maxmemory-policy=noeviction` in `redis.conf`.
* **Rationale:** BullMQ queues rely on persistent stream data. Evicting queue keys under memory pressure corrupts queue state.
