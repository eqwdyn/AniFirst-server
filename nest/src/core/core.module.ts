import { Module } from '@nestjs/common';
import { CacheModule } from '@nestjs/cache-manager';
import { AnimesModule } from '../modules/animes/animes.module.js';
import { ServeStaticModule } from '@nestjs/serve-static';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { GenresModule } from '../modules/genres/genres.module.js';
import { UsersModule } from '../modules/users/users.module.js';
import { AuthModule } from '../modules/auth/auth.module.js';
import { ConfigModule } from '@nestjs/config';

const __dirname = dirname(fileURLToPath(import.meta.url));
@Module({
  imports: [
    CacheModule.register({
      isGlobal: true,
    }),
    ServeStaticModule.forRoot({
      rootPath: join(__dirname, '..', '..', 'static'),
      serveRoot: '/static',
    }),
    ConfigModule.forRoot({ isGlobal: true }),
    AnimesModule,
    GenresModule,
    UsersModule,
    AuthModule,
  ],
})
export class CoreModule {}
