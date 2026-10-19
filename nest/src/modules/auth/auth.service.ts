import {
  Injectable,
  NotFoundException,
  UnauthorizedException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { compare, genSalt, hash } from 'bcrypt';
import { CreateUserDto } from '../users/dto/create-user.dto.js';
import { UsersService } from '../users/users.service.js';

@Injectable()
export class AuthService {
  constructor(
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
    private readonly usersService: UsersService,
  ) {}

  async validateUser(dto: CreateUserDto) {
    const user = await this.usersService.findByLogin(dto.login);
    if (!user) throw new UnauthorizedException('Invalid credentials');

    const isValidPassword = await this.comparePassword(
      dto.password,
      user.password,
    );
    if (!isValidPassword)
      throw new UnauthorizedException('Invalid credentials');

    return { id: user.id, login: user.login };
  }

  async createUser(dto: CreateUserDto) {
    const hashedPass = await this.hashPassword(dto.password);
    const user = await this.usersService.create({
      login: dto.login,
      password: hashedPass,
    });

    return { id: user.id, login: user.login };
  }

  generateAccessToken(payload: { id: number; login: string }) {
    return this.jwtService.sign(payload);
  }

  generateRefreshToken(payload: { id: number }) {
    return this.jwtService.sign(payload, {
      expiresIn: this.configService.get('JWT_REFRESH_EXPIRES_IN', '7d'),
    });
  }

  async verifyRefreshToken(refreshToken: string): Promise<{
    id: number;
    login: string;
  }> {
    const payload = this.jwtService.verify(refreshToken, {
      secret: this.configService.get('JWT_REFRESH_SECRET'),
    });

    const user = await this.usersService.findById(payload.id);
    if (!user) {
      throw new UnauthorizedException('Uncorrect credentials');
    }

    return { id: user.id, login: user.login };
  }

  private async comparePassword(
    password: string,
    hash: string,
  ): Promise<boolean> {
    return compare(password, hash);
  }

  private async hashPassword(password: string) {
    const salt = await genSalt(10);
    return hash(password, salt);
  }
}
