import { ApiProperty } from '@nestjs/swagger';
import { IsString, Length } from 'class-validator';

export class CreateUserDto {
  @ApiProperty({
    description: 'Логин',
    example: 'eqwdy',
    required: true,
    minLength: 2,
  })
  @IsString()
  @Length(2)
  login: string;

  @ApiProperty({
    description: 'Пароль',
    example: '123456',
    required: true,
    minLength: 4,
  })
  @IsString()
  @Length(4)
  password: string;
}
