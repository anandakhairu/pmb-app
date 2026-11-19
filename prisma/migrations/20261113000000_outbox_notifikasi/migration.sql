-- CreateEnum
CREATE TYPE "status_outbox" AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

-- CreateTable
CREATE TABLE "outbox_notifikasi" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "target_id" UUID NOT NULL,
    "target_type" VARCHAR(20) NOT NULL,
    "judul" VARCHAR(200) NOT NULL,
    "pesan" TEXT NOT NULL,
    "url" VARCHAR(500) NOT NULL DEFAULT '/dashboard',
    "tag" VARCHAR(100),
    "idempotency_key" VARCHAR(255) NOT NULL,
    "status" "status_outbox" NOT NULL DEFAULT 'PENDING',
    "attempt_count" INTEGER NOT NULL DEFAULT 0,
    "last_error" TEXT,
    "locked_at" TIMESTAMPTZ(6),
    "delivered_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "outbox_notifikasi_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "outbox_notifikasi_idempotency_key_key" ON "outbox_notifikasi"("idempotency_key");

-- CreateIndex
CREATE INDEX "outbox_notifikasi_status_created_at_idx" ON "outbox_notifikasi"("status", "created_at");

-- CreateIndex
CREATE INDEX "outbox_notifikasi_target_id_status_idx" ON "outbox_notifikasi"("target_id", "status");
