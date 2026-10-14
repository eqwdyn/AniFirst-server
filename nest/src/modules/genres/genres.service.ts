import { Injectable } from '@nestjs/common';
import { KafkaService } from '../../core/kafka/kafka.service.js';

@Injectable()
export class GenresService {
  constructor(private readonly kafkaClient: KafkaService) {}

  async getShikimoriGenres(): Promise<Record<string, string>> {
    const kafkaResponse = await this.kafkaClient.firstValue('get_genres', {});

    return kafkaResponse;
  }
  async getAnimesByGenres(genres: string[], startPage = 1): Promise<any[]> {
    const kafkaResponse = await this.kafkaClient.firstValue(
      'get_animes_by_genres',
      { genres, start_page: startPage },
    );

    console.log(
      'getAnimeByGenres handle \nGenres: ',
      genres.toString(),
      '\nResponse: ',
      JSON.stringify(kafkaResponse, null, 2),
    );

    return kafkaResponse;
  }
}
