import { Injectable, NotFoundException } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto.js';
import { UpdateUserDto } from './dto/update-user.dto.js';
import { PrismaService } from '../../core/prisma/prisma.service.js';
import { AnimesService } from '../animes/animes.service.js';

@Injectable()
export class UsersService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly animeService: AnimesService,
  ) {}

  async create(dto: CreateUserDto) {
    const user = await this.prisma.user.create({ data: dto });
    return user;
  }

  async findByLogin(login: string) {
    const user = await this.prisma.user.findFirst({
      where: { login },
    });
    return user;
  }
  async findById(id: number) {
    const user = await this.prisma.user.findFirst({
      where: { id },
    });
    return user;
  }

  async getFavorite(userId: number) {
    const favorites = await this.prisma.favorite.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });

    const animePromises = favorites.map((fav) =>
      this.animeService.getAnimeById(fav.shikimoriId),
    );

    const animes = await Promise.all(animePromises);

    return animes;
  }
  async addToFavorite(shikimoriId: string, userId: number): Promise<void> {
    const exists = await this.checkUserExists(userId);
    if (!exists) {
      throw new NotFoundException(`User with id ${userId} not found`);
    }

    await this.prisma.favorite.upsert({
      where: {
        userId_shikimoriId: {
          userId,
          shikimoriId,
        },
      },
      create: {
        userId,
        shikimoriId,
      },
      update: {
        shikimoriId,
      },
    });
  }
  async deleteFromFavorite(shikimoriId: string, userId: number): Promise<void> {
    const exists = await this.checkUserExists(userId);
    if (!exists) {
      throw new NotFoundException(`User with id ${userId} not found`);
    }

    await this.prisma.favorite.delete({
      where: {
        userId_shikimoriId: {
          userId,
          shikimoriId,
        },
      },
    });
  }

  async getLastViewed(userId: number) {
    const lastViewed = await this.prisma.lastViewed.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });

    const animePromises = lastViewed.map((viewed) =>
      this.animeService.getAnimeById(viewed.shikimoriId),
    );

    const animes = await Promise.all(animePromises);

    return animes;
  }
  async addLastViewed(shikimoriId: string, userId: number): Promise<void> {
    const exists = await this.checkUserExists(userId);
    if (!exists) {
      throw new NotFoundException(`User with id ${userId} not found`);
    }

    await this.prisma.lastViewed.upsert({
      where: {
        userId_shikimoriId: {
          userId,
          shikimoriId,
        },
      },
      create: {
        userId,
        shikimoriId,
      },
      update: {
        shikimoriId,
      },
    });
  }
  async deleteFromLastViewed(
    shikimoriId: string,
    userId: number,
  ): Promise<void> {
    const exists = await this.checkUserExists(userId);
    if (!exists) {
      throw new NotFoundException(`User with id ${userId} not found`);
    }

    await this.prisma.lastViewed.delete({
      where: {
        userId_shikimoriId: {
          userId,
          shikimoriId,
        },
      },
    });
  }

  private async checkUserExists(id: number) {
    const user = await this.prisma.user.findFirst({
      where: { id },
      select: { id: true },
    });

    return !!user;
  }
}
