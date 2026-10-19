import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { CoreModule } from './core/core.module.js';
import cookieParser from 'cookie-parser';

async function bootstrap() {
  const PORT = process.env.PORT ?? 7000;

  const app = await NestFactory.create(CoreModule);
  app.enableCors();
  app.use(cookieParser());

  const config = new DocumentBuilder()
    .setTitle('Пример API')
    .setDescription('Описание API для примера')
    .setVersion('1.0')
    .addTag('example', 'Пример ресурса')
    .build();

  const document = SwaggerModule.createDocument(app, config);

  SwaggerModule.setup('docs', app, document);

  await app.listen(PORT);
  console.log('Server started on Port: ', PORT);
}
await bootstrap();
