import {
  Controller,
  Post,
  Body,
  Res,
  HttpCode,
  HttpStatus,
  Req,
  UnauthorizedException,
} from '@nestjs/common';
import { AuthService } from './auth.service.js';
import { CreateUserDto } from '../users/dto/create-user.dto.js';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import type { Request } from 'express';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('login')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Логин' })
  @ApiResponse({ status: 200, description: 'Авторизация прошла успешно' })
  async login(
    @Body() dto: CreateUserDto,
    @Res({ passthrough: true }) res: any,
  ) {
    const payload = await this.authService.validateUser(dto);
    const accessToken = this.authService.generateAccessToken(payload);
    const refreshToken = this.authService.generateRefreshToken({
      id: payload.id,
    });

    res.cookie('refresh_token', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge:
        this.parseEnvValDaysToMs(process.env.JWT_REFRESH_EXPIRES_IN) ??
        7 * 24 * 60 * 60 * 1000,
      path: '/',
    });

    return { accessToken };
  }

  @Post('register')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Регистрация' })
  @ApiResponse({ status: 201, description: 'Регистрация прошла успешно' })
  async register(
    @Body() dto: CreateUserDto,
    @Res({ passthrough: true }) res: any,
  ) {
    const payload = await this.authService.createUser(dto);
    const accessToken = this.authService.generateAccessToken(payload);
    const refreshToken = this.authService.generateRefreshToken({
      id: payload.id,
    });

    res.cookie('refresh_token', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge:
        this.parseEnvValDaysToMs(process.env.JWT_REFRESH_EXPIRES_IN) ??
        7 * 24 * 60 * 60 * 1000,
      path: '/',
    });

    return { accessToken };
  }

  @Post('refresh')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Обновление токена' })
  @ApiResponse({ status: 201, description: 'Регистрация прошла успешно' })
  async refresh(@Req() req: Request) {
    const refreshToken = req.cookies['refresh_token'];
    if (!refreshToken) {
      throw new UnauthorizedException('Refresh token not found in cookies');
    }

    const payload = await this.authService.verifyRefreshToken(refreshToken);
    const accessToken = this.authService.generateAccessToken(payload);

    return { accessToken };
  }

  private parseEnvValDaysToMs(val: string | undefined): number | null {
    if (!val) {
      return null;
    }

    const match = val.match(/^(\d+)d$/);
    if (!match) {
      return null;
    }
    const countOfDays = Number(match[1]);
    return countOfDays * 24 * 60 * 60 * 1000;
  }
}
