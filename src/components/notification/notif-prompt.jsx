"use client";

import { useEffect, useState } from "react";
import { Bell, BellOff, Check, CheckCircle2, Loader2, ShieldCheck, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  daftarkanPerangkatAction,
  hapusPerangkatAction,
  cekStatusPerangkatAction,
} from "@/lib/server/notification-actions";

/**
 * Konversi kunci VAPID public base64url ke Uint8Array yang dibutuhkan PushManager
 */
function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function NotifikasiWebPushPrompt({
  userType = "MAHASISWA",
  userId,
  namaPengguna,
  compact = false,
}) {
  const [didukung, setDidukung] = useState(false);
  const [izin, setIzin] = useState("default"); // default | granted | denied
  const [terdaftar, setTerdaftar] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pesan, setPesan] = useState(null);

  useEffect(() => {
    if (typeof window !== "undefined" && "serviceWorker" in navigator && "PushManager" in window) {
      setDidukung(true);
      setIzin(Notification.permission);

      // Cek apakah service worker sudah punya subscription aktif
      navigator.serviceWorker.ready.then(async (reg) => {
        try {
          const sub = await reg.pushManager.getSubscription();
          if (sub) {
            const status = await cekStatusPerangkatAction(sub.endpoint);
            setTerdaftar(status.terdaftar);
          }
        } catch {
          // ignore
        }
      });
    }
  }, []);

  async function aktifkanNotifikasi() {
    setLoading(true);
    setPesan(null);

    try {
      if (!didukung) {
        throw new Error("Browser ini tidak mendukung Web Push Notification.");
      }

      // 1. Minta izin pengguna melalui interaksi klik eksplisit
      const hasilIzin = await Notification.requestPermission();
      setIzin(hasilIzin);

      if (hasilIzin !== "granted") {
        throw new Error("Izin notifikasi tidak diberikan oleh browser.");
      }

      // 2. Daftarkan Service Worker
      const reg = await navigator.serviceWorker.register("/sw.js");
      await navigator.serviceWorker.ready;

      // 3. Ambil VAPID Public Key dari environment
      const vapidKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
      if (!vapidKey) {
        throw new Error("NEXT_PUBLIC_VAPID_PUBLIC_KEY belum dikonfigurasi.");
      }

      // 4. Buat langganan PushManager
      const convertedVapidKey = urlBase64ToUint8Array(vapidKey);
      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedVapidKey,
      });

      const rawSub = subscription.toJSON();
      if (!rawSub.keys || !rawSub.keys.p256dh || !rawSub.keys.auth) {
        throw new Error("Kunci enkripsi browser tidak lengkap.");
      }

      // 5. Simpan ke database PostgreSQL via Server Action
      const res = await daftarkanPerangkatAction({
        endpoint: subscription.endpoint,
        p256dh: rawSub.keys.p256dh,
        authKey: rawSub.keys.auth,
        userAgent: navigator.userAgent,
        userType,
        userId,
      });

      if (!res.success) {
        throw new Error(res.error);
      }

      setTerdaftar(true);
      setPesan({
        sukses: true,
        teks: "Notifikasi Web Push aktif! Anda akan menerima update status langsung di browser ini.",
      });
    } catch (err) {
      console.error("Gagal aktivasi push:", err);
      setPesan({ sukses: false, teks: err.message });
    } finally {
      setLoading(false);
    }
  }

  async function nonaktifkanNotifikasi() {
    setLoading(true);
    setPesan(null);
    try {
      const reg = await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.getSubscription();
      if (sub) {
        await hapusPerangkatAction(sub.endpoint);
        await sub.unsubscribe();
      }
      setTerdaftar(false);
      setPesan({ sukses: true, teks: "Notifikasi Web Push telah dinonaktifkan untuk perangkat ini." });
    } catch (err) {
      setPesan({ sukses: false, teks: "Gagal menonaktifkan notifikasi: " + err.message });
    } finally {
      setLoading(false);
    }
  }

  if (!didukung) {
    return null; // Sembunyikan jika browser tidak mendukung
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {terdaftar ? (
          <Badge variant="success" className="text-xs font-semibold flex items-center gap-1.5 py-1 px-3">
            <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
            Web Push Aktif
          </Badge>
        ) : (
          <Button
            size="sm"
            variant="outline"
            onClick={aktifkanNotifikasi}
            disabled={loading}
            className="h-8 rounded-lg text-xs font-semibold border-[#4B6E5A]/30 text-[#4B6E5A] hover:bg-[#4B6E5A]/5"
          >
            {loading ? <Loader2 className="size-3 animate-spin mr-1" /> : <Bell className="size-3 mr-1" />}
            Aktifkan Push
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-[#4B6E5A]/25 bg-linear-to-r from-[#4B6E5A]/8 via-white to-white p-5 shadow-xs">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div className="flex items-start gap-3.5">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[#4B6E5A] text-white shadow-xs">
            {terdaftar ? <Bell className="size-5" /> : <BellOff className="size-5" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-extrabold text-neutral-900">
                Web Push Notification (Pemberitahuan Real-Time)
              </h3>
              {terdaftar && (
                <Badge variant="success" className="text-[10px] font-bold py-0.5">
                  Terhubung Aktif
                </Badge>
              )}
            </div>
            <p className="mt-1 text-xs text-neutral-600 max-w-xl leading-relaxed">
              Dapatkan pemberitahuan seketika di layar HP atau laptop saat panitia selesai memverifikasi berkas, meminta revisi, atau mengumumkan kelulusan.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          {terdaftar ? (
            <Button
              size="sm"
              variant="outline"
              onClick={nonaktifkanNotifikasi}
              disabled={loading}
              className="h-9 rounded-xl border-neutral-300 text-xs font-semibold text-neutral-600 hover:text-rose-600 hover:border-rose-300"
            >
              {loading ? <Loader2 className="size-3.5 animate-spin mr-1.5" /> : null}
              Matikan Notifikasi
            </Button>
          ) : (
            <Button
              size="sm"
              onClick={aktifkanNotifikasi}
              disabled={loading || izin === "denied"}
              className="h-9 rounded-xl bg-[#4B6E5A] px-4 text-xs font-bold text-white hover:bg-[#5C836A] shadow-xs"
            >
              {loading ? (
                <>
                  <Loader2 className="size-3.5 animate-spin mr-1.5" /> Menghubungkan...
                </>
              ) : (
                <>
                  <Sparkles className="size-3.5 mr-1.5" /> Aktifkan Notifikasi Browser
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {pesan && (
        <div
          className={`mt-4 flex items-center justify-between rounded-xl p-3 text-xs font-medium border ${
            pesan.sukses
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-rose-200 bg-rose-50 text-rose-800"
          }`}
        >
          <span>{pesan.teks}</span>
          <button type="button" onClick={() => setPesan(null)} className="ml-2 hover:opacity-75">
            <X className="size-3.5" />
          </button>
        </div>
      )}

      {izin === "denied" && (
        <p className="mt-3 text-[11px] text-amber-700 bg-amber-50 border border-amber-200/80 rounded-lg p-2.5">
          ⚠️ Izin notifikasi browser diblokir. Klik ikon gembok di bilah alamat browser untuk mengizinkan notifikasi PMB.
        </p>
      )}
    </div>
  );
}
