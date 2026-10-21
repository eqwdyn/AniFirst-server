import { Injectable } from '@nestjs/common';
import { KafkaService } from '../../core/kafka/kafka.service.js';

@Injectable()
export class AnimesService {
  constructor(private readonly kafkaClient: KafkaService) {}

  async getAnimeById(shikimori_id: string) {
    const responseFromPython = await this.kafkaClient.firstValue(
      'get_full_info',
      {
        shikimori_id,
      },
    );

    console.log(JSON.stringify(responseFromPython, null, 2));

    try {
      const parsed = this.parseAnimeFromKodik(
        responseFromPython.kodik_results[0],
      );
      const related = responseFromPython.related.filter(
        (item: any) => item.type !== 'Реклама',
      );

      return {
        ...parsed,
        related,
      };
    } catch (e) {
      console.error(e);
      return null;
    }
  }

  async getNewReleases(limit: number, page: number) {
    const responseFromPython = await this.kafkaClient.firstValue(
      'get_new_releases',
      { limit, page },
    );

    const animes = responseFromPython.map((item: any) => ({
      ...item,
      posterUrl: item.poster,
    }));

    return animes;
  }

  async getTrending(limit: number, page: number) {
    const responseFromPython = await this.kafkaClient.firstValue(
      'get_trending',
      {
        limit,
        page,
      },
    );

    const animes = responseFromPython.map((item: any) => ({
      ...item,
      posterUrl: item.poster,
    }));

    return animes;
  }

  async getHeroAnime() {
    const responseFromPython = await this.kafkaClient.firstValue(
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

  async searchAnimesShikimori(title: string) {
    const responseFromPython = await this.kafkaClient.firstValue(
      'search_animes',
      {
        title,
      },
    );

    const animes = responseFromPython.map((item: any) => ({
      ...item,
      posterUrl: item.poster,
    }));

    return animes;
  }

  private parseAnimeFromKodik(item: any) {
    const md = item.material_data;
    console.log(md);

    const parsed = {
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
}
