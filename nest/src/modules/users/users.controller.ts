import {
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Post,
} from '@nestjs/common';
import { UsersService } from './users.service.js';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import { Authorized } from '../../shared/decorators/authorized.decorator.js';
import { Authorization } from '../../shared/decorators/auth.decorator.js';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get('/favorite')
  @Authorization()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Получить список избранных аниме' })
  @ApiResponse({ status: 200 })
  async getFavorite(@Authorized('id') userId: number) {
    return this.usersService.getFavorite(userId);
  }

  @Post('/favorite/:id')
  @Authorization()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Добавить аниме в избранное' })
  @ApiResponse({ status: 201 })
  async addToFavorite(
    @Authorized('id') userId: number,
    @Param('id') id: string,
  ) {
    await this.usersService.addToFavorite(id, userId);
  }

  @Delete('/favorite/:id')
  @Authorization()
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Удалить аниме из избранное' })
  @ApiResponse({ status: 204 })
  async deleteFromFavorite(
    @Authorized('id') userId: number,
    @Param('id') id: string,
  ) {
    await this.usersService.deleteFromFavorite(id, userId);
  }

  @Get('/last-viewed')
  @Authorization()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Получить список недавно просмотренных аниме' })
  @ApiResponse({ status: 200 })
  async getLastViewed(@Authorized('id') userId: number) {
    return this.usersService.getLastViewed(userId);
  }

  @Post('/last-viewed/:id')
  @Authorization()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Добавить аниме в последнее' })
  @ApiResponse({ status: 201 })
  async addToLastViewed(
    @Authorized('id') userId: number,
    @Param('id') id: string,
  ) {
    await this.usersService.addLastViewed(id, userId);
  }

  @Delete('/last-viewed/:id')
  @Authorization()
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Удалить аниме из избранное' })
  @ApiResponse({ status: 204 })
  async deleteFromLastViewed(
    @Authorized('id') userId: number,
    @Param('id') id: string,
  ) {
    await this.usersService.deleteFromLastViewed(id, userId);
  }
}
