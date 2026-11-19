import Redis from "ioredis";

// =============================================================================
// REDIS CONNECTION CONFIGURATION FOR BULLMQ
// =============================================================================

const REDIS_URL = process.env.REDIS_URL || "redis://127.0.0.1:6379";

/**
 * Membuat instance koneksi IORedis dengan konfigurasi standar BullMQ
 * - maxRetriesPerRequest: null (Wajib untuk BullMQ)
 * - enableReadyCheck: false
 */
export function createRedisConnection() {
  const connection = new Redis(REDIS_URL, {
    maxRetriesPerRequest: null,
    enableReadyCheck: false,
    lazyConnect: true,
    connectTimeout: 2000,
    retryStrategy(times) {
      // Bounded retry: if Redis host is not reachable, do not hang forever
      if (times > 2) return null;
      return 500;
    },
    reconnectOnError() {
      return false;
    },
  });

  connection.on("error", () => {
    // Suppress unhandled event emitter error
  });

  return connection;
}

// Singleton connection untuk producer
let sharedProducerConnection = null;

export function getProducerConnection() {
  if (!sharedProducerConnection) {
    sharedProducerConnection = createRedisConnection();
  }
  return sharedProducerConnection;
}
