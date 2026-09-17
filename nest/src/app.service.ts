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
    this.client.subscribeToResponseOf('get_trending');
    this.client.subscribeToResponseOf('get_full_info');
    await this.client.connect();
  }

  async getAnimeById(shikimori_id: string) {
    console.log(shikimori_id);

    const responseFromPython = await this.firstValueFromKafka('get_full_info', {
      shikimori_id,
    });

    const item = responseFromPython[0];
    const md = item.material_data;

    const parsed = {
      shikimori_id: item.shikimori_id,
      title: item.title,
      title_orig: item.title_orig,
      description: md.anime_description || md.description,
      genres: md.anime_genres,
      rating: Math.ceil(
        (md.shikimori_rating + md.kinopoisk_rating + md.imdb_rating) / 3,
      ),
      episodes: md.episodes_total,
      status: md.anime_status,
      studio: md.anime_studios.join(' & '),
      posterUrl: md.anime_poster_url, // постер из Shikimori
      playerUrl: 'https:' + item.link, // ссылка на плеер Kodik
      screenshots: item.screenshots, // скриншоты из Kodik
      year: item.year,
      kind: md.anime_kind,
      duration: md.duration,
      countries: md.countries,
      ageRating: md.rating_mpaa,
      minimalAge: md.minimal_age,
    };

    return parsed;
  }

  async getNewReleases(limit: number) {
    const responseFromPython = await this.firstValueFromKafka(
      'get_new_releases',
      { limit },
    );

    return responseFromPython;
  }

  async getTrending(limit: number) {
    const responseFromPython = await this.firstValueFromKafka('get_trending', {
      limit,
    });

    return responseFromPython;
  }

  private firstValueFromKafka(topic: string, data: Object): Promise<any> {
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
