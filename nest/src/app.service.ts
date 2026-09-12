import {
  Inject,
  Injectable,
  InternalServerErrorException,
} from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { catchError, firstValueFrom, timeout } from 'rxjs';

@Injectable()
export class AppService {
  constructor(@Inject('KAFKA_CLIENT') private client: ClientKafka) {}

  async onModuleInit() {
    this.client.subscribeToResponseOf('get_new_releases');
    await this.client.connect();
  }

  async getNewReleases(limit: number) {
    console.log('Get new Releases');

    return firstValueFrom(
      this.client.send('get_new_releases', { limit }).pipe(
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
