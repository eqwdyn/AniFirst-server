import { Injectable, NotFoundException } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto.js';
import { UpdateUserDto } from './dto/update-user.dto.js';
import { PrismaService } from '../../core/prisma/prisma.service.js';

@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

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

  async addToFavorite(shikimoriId: number, userId: number): Promise<void> {
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
  async deleteFromFavorite(shikimoriId: number, userId: number): Promise<void> {
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

  async addLastViewed(shikimoriId: number, userId: number): Promise<void> {
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
    shikimoriId: number,
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
