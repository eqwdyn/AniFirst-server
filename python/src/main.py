import asyncio
import logging
from typing import Any, Dict, Optional

from anime_parsers_ru.errors import NoResults
from aiokafka import AIOKafkaConsumer

from getNewReleases import getNewReleases
from getTrending import getTrending
from getFullInfo import get_full_info
from searchByTitle import search_by_title_shikimori
from getHeroAnime import get_hero_anime
from getGenres import get_shikimori_genres
from getAnimesByGenre import get_animes_by_genre

from utils.consume_messages import consume_msg
from utils.kafka_konsumer import kafka_consumer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@kafka_consumer("get_new_releases")
async def consume_new_releases(consumer: AIOKafkaConsumer) -> None:
    async for msg in consumer:
        try:
            payload = msg.value
            if payload is None:
                logger.warning("Payload is None for get_new_releases")
                await consume_msg(msg, {"message": "Payload is missing", "error": "Missing"})
                continue

            limit = payload.get("limit", 1)
            page = payload.get("page", 1)

            new_releases = await getNewReleases(limit, page)
            await consume_msg(msg, new_releases)
        except NoResults as e:
            logger.error("NoResults in get_new_releases: %s", e, exc_info=True)
            await consume_msg(msg, {"message": "No results found", "error": "Not found"})
        except Exception as e:
            # Ловим всё остальное, чтобы не уронить консьюмер
            logger.exception("Unexpected error in get_new_releases")
            await consume_msg(msg, {"message": "Internal server error", "error": "Unknown error"})


@kafka_consumer("get_trending")
async def consume_trending(consumer: AIOKafkaConsumer) -> None:
    async for msg in consumer:
        try:
            payload = msg.value
            if payload is None:
                logger.warning("Payload is None for get_trending")
                await consume_msg(msg, {"message": "Payload is missing", "error": "Missing"})
                continue

            limit = payload.get('limit', 1)
            page = payload.get('page', 1)
            logger.info("Limit: %d, Page: %d", limit, page)

            trending = await getTrending(limit, page)
            await consume_msg(msg, trending)
        except NoResults as e:
            logger.error("NoResults in get_trending: %s", e, exc_info=True)
            await consume_msg(msg, {"message": "No results found", "error": "Not found"})
        except Exception as e:
            logger.exception("Unexpected error in get_trending")
            await consume_msg(msg, {"message": "Internal server error", "error": "Unknown error"})


@kafka_consumer("get_genres")
async def consume_genres(consumer: AIOKafkaConsumer) -> None:
    async for msg in consumer:
        try:
            trending = await get_shikimori_genres()
            await consume_msg(msg, trending)
        except Exception as e:
            logger.exception("Unexpected error in get_genres")
            await consume_msg(msg, {"message": "Internal server error", "error": "Unknown error"})


@kafka_consumer("get_hero_anime")
async def consume_hero_anime(consumer: AIOKafkaConsumer) -> None:
    async for msg in consumer:
        try:
            logger.info("Message to hero")
            hero = await get_hero_anime()
            await consume_msg(msg, hero)
        except Exception as e:
            logger.exception("Unexpected error in get_hero_anime")
            await consume_msg(msg, {"message": "Internal server error", "error": "Unknown error"})


@kafka_consumer("get_animes_by_genres")
async def consume_get_animes_by_genres(consumer: AIOKafkaConsumer) -> None:
    async for msg in consumer:
        try:
            payload = msg.value
            if payload is None:
                logger.warning("Payload is None for get_animes_by_genres")
                await consume_msg(msg, {"message": "Payload is missing", "error": "Missing"})
                continue

            payload_genres: Optional[list] = None
            start_page = 1

            try:
                payload_genres = payload['genres']
                start_page = payload['start_page']
            except KeyError as e:
                logger.warning("Missing key in payload for get_animes_by_genres: %s", e)
                await consume_msg(msg, {"message": "genre or start_page is missing", "error": "Missing"})
                continue

            if not payload_genres or len(payload_genres) == 0:
                logger.warning("Genres list is empty for get_animes_by_genres")
                await consume_msg(msg, {"message": "genres is missing", "error": "Missing"})
                continue

            logger.info("Genres: %s", payload_genres)

            trueGenres_map: dict[str, str] = await get_shikimori_genres()

            matched_genres: list[str] = []
            for eng_name, ru_name in trueGenres_map.items():
                for payload_genre in payload_genres:
                    if payload_genre in eng_name:
                        matched_genres.append(ru_name)

            if not matched_genres:
                logger.warning("No matching genres found for: %s", payload_genres)
                await consume_msg(msg, {
                    "message": f"No matching genres found for: {payload_genres}",
                    "error": "NotFound"
                })
                continue

            animes = await get_animes_by_genre(matched_genres, start_page=start_page)
            await consume_msg(msg, animes)
            logger.info("Matched genres: %s", matched_genres)
        except NoResults as e:
            logger.error("NoResults in get_animes_by_genres: %s", e, exc_info=True)
            await consume_msg(msg, {
                "message": f"Animes was not found by genre: {payload_genres}",
                "error": "Not found"
            })
        except Exception as e:
            logger.exception("Unexpected error in get_animes_by_genres")
            await consume_msg(msg, {"message": "Internal server error", "error": "Unknown error"})


@kafka_consumer("search_animes")
async def consume_search(consumer: AIOKafkaConsumer) -> None:
    async for msg in consumer:
        try:
            payload = msg.value
            if payload is None:
                logger.warning("Payload is None for search_animes")
                await consume_msg(msg, {"message": "Payload is missing", "error": "Missing"})
                continue

            title = payload.get('title')
            if title is None or not title:
                logger.warning("Title is missing or empty for search_animes")
                await consume_msg(msg, {"message": "title is missing", "error": "Missing"})
                continue

            logger.info("Title: %s", title)
            trending = await search_by_title_shikimori(title)
            await consume_msg(msg, trending)
        except NoResults as e:
            logger.error("NoResults in search_animes: %s", e, exc_info=True)
            await consume_msg(msg, {"message": f"Anime was not found by title: {title}", "error": "Not found"})
        except Exception as e:
            logger.exception("Unexpected error in search_animes")
            await consume_msg(msg, {"message": "Internal server error", "error": "Unknown error"})


@kafka_consumer("get_full_info")
async def consume_full_info(consumer: AIOKafkaConsumer) -> None:
    async for msg in consumer:
        try:
            logger.info("Message consumed: %s", msg)
            payload = msg.value
            if payload is None:
                logger.warning("Payload is None for get_full_info")
                await consume_msg(msg, {"message": "Payload is missing", "error": "Missing"})
                continue

            shikimori_id = payload.get('shikimori_id')
            if shikimori_id is None or not shikimori_id:
                logger.warning("shikimori_id is missing or empty for get_full_info")
                await consume_msg(msg, {"message": "Shikimori_id is missing", "error": "Missing"})
                continue

            info = await get_full_info(shikimori_id)
            await consume_msg(msg, info)
        except NoResults as e:
            logger.error("NoResults in get_full_info: %s", e, exc_info=True)
            await consume_msg(msg, {
                "message": f"Anime was not found by shikimori id: {shikimori_id}",
                "error": "Not found"
            })
        except Exception as e:
            logger.exception("Unexpected error in get_full_info")
            await consume_msg(msg, {"message": "Internal server error", "error": "Unknown error"})


async def run_consumer(func, *args, **kwargs) -> None:
    """Запускает функцию-консьюмер и перехватывает любые ошибки на уровне задачи."""
    try:
        await func(*args, **kwargs)
    except Exception as e:
        logger.exception("Critical error in consumer task: %s", e)
        # Важно: не останавливаем сервис, просто логируем и задача завершается


async def main() -> None:
    # Запускаем каждый консьюмер как отдельную задачу, чтобы падение одного не ломало другие
    tasks = [
        asyncio.create_task(run_consumer(consume_new_releases)),
        asyncio.create_task(run_consumer(consume_trending)),
        asyncio.create_task(run_consumer(consume_hero_anime)),
        asyncio.create_task(run_consumer(consume_full_info)),
        asyncio.create_task(run_consumer(consume_search)),
        asyncio.create_task(run_consumer(consume_genres)),
        asyncio.create_task(run_consumer(consume_get_animes_by_genres)),
    ]

    # Ждём завершения всех задач (они будут работать бесконечно, пока не будет остановлен процесс)
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
