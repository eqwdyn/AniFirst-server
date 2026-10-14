import {
  Controller,
  Get,
  InternalServerErrorException,
  Param,
  Query,
  UseInterceptors,
} from '@nestjs/common';
import { CacheInterceptor, CacheTTL } from '@nestjs/cache-manager';
import { GenresService } from './genres.service.js';

@Controller('genres')
@UseInterceptors(CacheInterceptor)
@CacheTTL(60 * 1000)
export class GenresController {
  constructor(private readonly genresService: GenresService) {}

  @Get()
  getShikimoriGenres() {
    return this.genresService.getShikimoriGenres();
  }

  @Get(':name')
  getAnimesByGenre(@Param('name') name: string, @Query('page') page: string) {
    return this.genresService.getAnimesByGenres(
      [name],
      Number(page) ?? undefined,
    );
  }
}
