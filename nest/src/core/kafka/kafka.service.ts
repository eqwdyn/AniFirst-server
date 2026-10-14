import {
  Inject,
  Injectable,
  InternalServerErrorException,
  OnModuleInit,
} from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { catchError, firstValueFrom, timeout } from 'rxjs';

@Injectable()
export class KafkaService implements OnModuleInit {
  constructor(@Inject('KAFKA_CLIENT') private client: ClientKafka) {}

  async onModuleInit() {
    this.client.subscribeToResponseOf('get_new_releases');
    this.client.subscribeToResponseOf('get_trending');

    this.client.subscribeToResponseOf('get_genres');
    this.client.subscribeToResponseOf('get_animes_by_genres');

    this.client.subscribeToResponseOf('get_hero_anime');
    this.client.subscribeToResponseOf('get_full_info');

    this.client.subscribeToResponseOf('search_animes');
    await this.client.connect();
  }

  firstValue(topic: string, data?: Object): Promise<any> {
    return firstValueFrom(
      this.client.send(topic, data).pipe(
        timeout({ each: 10000 }),
        catchError((err) => {
          if (err.name === 'TimeoutError') {
            console.error('Kafka request timed out');
            throw new InternalServerErrorException(
              'Service is slow or unavailable',
            );
          }
          console.error('Kafka request failed', err);
          throw new InternalServerErrorException('Failed to fetch releases');
        }),
      ),
    );
  }
}
