import { Controller, Get, Query } from '@nestjs/common';
import { AppService } from './app.service.js';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getNewReleases(@Query('limit') limit: string) {
    return this.appService.getNewReleases(
      Number(limit) > 0 ? Number(limit) : 10,
    );
  }
}
