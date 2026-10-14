import { Module } from '@nestjs/common';
import { GenresService } from './genres.service.js';
import { GenresController } from './genres.controller.js';
import { KafkaModule } from '../../core/kafka/kafka.module.js';

@Module({
  providers: [GenresService],
  controllers: [GenresController],
  imports: [KafkaModule],
})
export class GenresModule {}
