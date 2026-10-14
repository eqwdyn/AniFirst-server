import { Module } from '@nestjs/common';
import { CacheModule } from '@nestjs/cache-manager';
import { AnimesModule } from '../modules/animes/animes.module.js';
import { ServeStaticModule } from '@nestjs/serve-static';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Получаем директорию текущего файла (для ES modules / import.meta)
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
    AnimesModule,
  ],
})
export class CoreModule {}
