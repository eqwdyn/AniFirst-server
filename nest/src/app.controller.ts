import { Controller, Get, Param, Query, UseInterceptors } from '@nestjs/common';
import { AppService } from './app.service.js';
import { CacheInterceptor, CacheTTL } from '@nestjs/cache-manager';

@Controller()
@UseInterceptors(CacheInterceptor)
@CacheTTL(60 * 1000)
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('new-releases')
  getNewReleases(@Query('limit') limit: string) {
    console.log('Get new releases');

    return this.appService.getNewReleases(
      Number(limit) > 0 ? Number(limit) : 1,
    );
  }

  @Get('new-releases-kodik')
  getNewReleasesKodik(@Query('limit') limit: string) {
    return this.appService.getNewReleasesKodik(
      Number(limit) > 0 ? Number(limit) : 20,
    );
  }

  @Get('trending')
  getTrending(@Query('limit') limit: string) {
    return this.appService.getTrending(Number(limit) > 0 ? Number(limit) : 1);
  }

  @Get('trending-kodik')
  getTrendingKodik(@Query('limit') limit: string) {
    return this.appService.getTrendingKodik(
      Number(limit) > 0 ? Number(limit) : 20,
    );
  }

  @Get('hero-anime')
  getHeroAnime() {
    return this.appService.getHeroAnime();
  }

  @Get('anime/:id')
  getAnimeById(@Param('id') id: string) {
    return this.appService.getAnimeById(id);
  }

  @Get('search/:title')
  searchAnimes(@Param('title') title: string) {
    return this.appService.searchAnimes(title);
  }
}
