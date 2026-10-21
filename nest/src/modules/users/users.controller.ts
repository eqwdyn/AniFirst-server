import {
  Controller,
  Delete,
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

  @Post('/favorite/:id')
  @Authorization()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Добавить аниме в избранное' })
  @ApiResponse({ status: 201 })
  async addToFavorite(
    @Authorized('id') userId: number,
    @Param('id') id: string,
  ) {
    await this.usersService.addToFavorite(Number(id), userId);
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
    await this.usersService.deleteFromFavorite(Number(id), userId);
  }

  @Post('last-viewed/:id')
  @Authorization()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Добавить аниме в последнее' })
  @ApiResponse({ status: 201 })
  async addLastViewed(
    @Authorized('id') userId: number,
    @Param('id') id: string,
  ) {
    await this.usersService.addLastViewed(Number(id), userId);
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
    await this.usersService.deleteFromLastViewed(Number(id), userId);
  }
}
