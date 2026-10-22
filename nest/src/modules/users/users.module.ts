import { Module } from '@nestjs/common';
import { UsersService } from './users.service.js';
import { UsersController } from './users.controller.js';
import { PrismaModule } from '../../core/prisma/prisma.module.js';
import { AnimesModule } from '../animes/animes.module.js';

@Module({
  imports: [PrismaModule, AnimesModule],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
