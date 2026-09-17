import { Controller, Get, Param, Query } from '@nestjs/common';
import { AppService } from './app.service.js';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('new-releases')
  getNewReleases(@Query('limit') limit: string) {
    return this.appService.getNewReleases(
      Number(limit) > 0 ? Number(limit) : 10,
    );
  }

  @Get('trending')
  getTrending(@Query('limit') limit: string) {
    return this.appService.getTrending(Number(limit) > 0 ? Number(limit) : 10);
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
