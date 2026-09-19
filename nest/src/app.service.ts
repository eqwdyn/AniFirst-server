import {
  Inject,
  Injectable,
  InternalServerErrorException,
} from '@nestjs/common';
import { ClientKafka } from '@nestjs/microservices';
import { catchError, firstValueFrom, timeout } from 'rxjs';
import { IAnimeKodik } from './interfaces/AnimeKodik.js';

@Injectable()
export class AppService {
  constructor(@Inject('KAFKA_CLIENT') private client: ClientKafka) {}

  async onModuleInit() {
    this.client.subscribeToResponseOf('get_new_releases');
    this.client.subscribeToResponseOf('get_new_releases_kodik');

    this.client.subscribeToResponseOf('get_trending');
    this.client.subscribeToResponseOf('get_trending_kodik');

    this.client.subscribeToResponseOf('get_hero_anime');
    this.client.subscribeToResponseOf('get_full_info');
    this.client.subscribeToResponseOf('search_animes');
    await this.client.connect();
  }

  async getAnimeById(shikimori_id: string) {
    console.log(shikimori_id);

    const responseFromPython = await this.firstValueFromKafka('get_full_info', {
      shikimori_id,
    });

    const item = responseFromPython[0];
    return this.parseAnimeFromKodik(item);
  }

  async getNewReleases(limit: number) {
    const responseFromPython = await this.firstValueFromKafka(
      'get_new_releases',
      { limit },
    );

    return responseFromPython;
  }

  async getNewReleasesKodik(limit: number): Promise<IAnimeKodik[]> {
    const responseFromPython = await this.firstValueFromKafka(
      'get_new_releases_kodik',
      {
        limit,
      },
    );
    console.log(JSON.stringify(responseFromPython, null, 2));

    return responseFromPython.map((item: any) =>
      this.parseAnimeFromKodik(item),
    );
  }

  async getTrending(limit: number) {
    const responseFromPython = await this.firstValueFromKafka('get_trending', {
      limit,
    });

    return responseFromPython;
  }

  async getTrendingKodik(limit: number): Promise<IAnimeKodik[]> {
    const responseFromPython = await this.firstValueFromKafka(
      'get_trending_kodik',
      {
        limit,
      },
    );
    console.log(JSON.stringify(responseFromPython, null, 2));

    return responseFromPython.map((item: any) =>
      this.parseAnimeFromKodik(item),
    );
  }

  async getHeroAnime() {
    const responseFromPython = await this.firstValueFromKafka(
      'get_hero_anime',
      {},
    );

    const md = responseFromPython.material_data;
    const parsed = {
      title: md.title,
      description: md.description,
      tags: md.anime_genres,
      posterUrl: md.anime_poster_url,
      shikimori_id: responseFromPython.shikimori_id,
    };

    return parsed;
  }

  async searchAnimes(title: string) {
    const responseFromPython = await this.firstValueFromKafka('search_animes', {
      title,
    });

    return responseFromPython;
  }

  private parseAnimeFromKodik(item: any): IAnimeKodik {
    const md = item.material_data;
    console.log(md);

    const parsed: IAnimeKodik = {
      shikimori_id: item.shikimori_id,
      title: md.anime_title,
      title_orig: item.title_orig,
      description: md.anime_description || md.description,
      genres: md.anime_genres,
      tags: md.anime_genres,
      rating:
        this._calcRating([
          md.shikimori_rating,
          md.kinopoisk_rating,
          md.imdb_rating,
        ]) ?? 0,
      episodes: md.episodes_total,
      status: md.anime_status,
      studio: md.anime_studios
        ? md.anime_studios.length > 1
          ? md.anime_studios.join(' & ')
          : md.anime_studios.length
            ? md.anime_studios[0]
            : 'Unknown'
        : 'Unknown',
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

  private _calcRating(ratings: number[]): number | null {
    if (!ratings.length) {
      return null;
    }

    const total = ratings.reduce((acc, r) => {
      const isCurInvalid = typeof r !== 'number' || Number.isNaN(r);
      const isAccInvalid = typeof acc !== 'number' || Number.isNaN(acc);
      if (isCurInvalid && isAccInvalid) return 0;

      if (isCurInvalid) {
        console.warn('Обнаружено невалидное значение в ratings:', r);
        return acc;
      }

      if (isAccInvalid) {
        return acc;
      }

      return acc + r;
    }, 0);

    const value = total / ratings.length;
    return Math.round(value * 10) / 10;
  }

  private firstValueFromKafka(topic: string, data?: Object): Promise<any> {
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
