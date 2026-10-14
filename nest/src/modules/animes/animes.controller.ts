import {
  Controller,
  Get,
  InternalServerErrorException,
  Param,
  Query,
  UseInterceptors,
} from '@nestjs/common';
import { CacheInterceptor, CacheTTL } from '@nestjs/cache-manager';
import { AnimesService } from './animes.service.js';

@Controller()
@UseInterceptors(CacheInterceptor)
@CacheTTL(60 * 1000)
export class AnimesController {
  constructor(private readonly animesService: AnimesService) {}

  @Get('new-releases')
  getNewReleases(@Query('limit') limit: string, @Query('page') page: string) {
    console.log('Get new releases');

    return this.animesService.getNewReleases(
      Number(limit) > 0 ? Number(limit) : 1,
      Number(page) > 0 ? Number(page) : 1,
    );
  }

  @Get('trending')
  getTrending(@Query('limit') limit: string, @Query('page') page: string) {
    return this.animesService.getTrending(
      Number(limit) > 0 ? Number(limit) : 1,
      Number(page) > 0 ? Number(page) : 1,
    );
  }

  @Get('genres/shikimori')
  getShikimoriGenres() {
    return this.animesService.getShikimoriGenres();
  }

  @Get('genres/:name')
  getAnimesByGenre(@Param('name') name: string, @Query('page') page: string) {
    return this.animesService.getAnimeByGenres(
      [name],
      Number(page) ?? undefined,
    );
  }

  @Get('hero-anime')
  getHeroAnime() {
    return this.animesService.getHeroAnime();
  }

  @Get('anime/:id')
  async getAnimeById(@Param('id') id: string) {
    const animes = await this.animesService.getAnimeById(id);
    if (!animes) {
      throw new InternalServerErrorException();
    }

    return animes;
  }

  @Get('search-kodik/:title')
  searchAnimes(@Param('title') title: string) {
    return this.animesService.searchAnimes(title);
  }

  @Get('search-shikimori/:title')
  searchAnimesShikimori(@Param('title') title: string) {
    return this.animesService.searchAnimesShikimori(title);
  }
}
