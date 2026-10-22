import { Module } from '@nestjs/common';
import { AnimesService } from './animes.service.js';
import { AnimesController } from './animes.controller.js';
import { KafkaModule } from '../../core/kafka/kafka.module.js';

@Module({
  providers: [AnimesService],
  controllers: [AnimesController],
  imports: [KafkaModule],
  exports: [AnimesService],
})
export class AnimesModule {}
