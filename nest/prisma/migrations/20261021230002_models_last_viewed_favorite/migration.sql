/*
  Warnings:

  - You are about to drop the column `favorite` on the `User` table. All the data in the column will be lost.
  - You are about to drop the column `lastViewed` on the `User` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "User" DROP COLUMN "favorite",
DROP COLUMN "lastViewed";

-- CreateTable
CREATE TABLE "Favorite" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "shikimoriId" INTEGER NOT NULL,

    CONSTRAINT "Favorite_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LastViewed" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "shikimoriId" INTEGER NOT NULL,

    CONSTRAINT "LastViewed_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Favorite_userId_shikimoriId_key" ON "Favorite"("userId", "shikimoriId");

-- CreateIndex
CREATE UNIQUE INDEX "LastViewed_userId_shikimoriId_key" ON "LastViewed"("userId", "shikimoriId");

-- AddForeignKey
ALTER TABLE "Favorite" ADD CONSTRAINT "Favorite_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LastViewed" ADD CONSTRAINT "LastViewed_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
