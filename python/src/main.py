import json
import asyncio
from functools import wraps
from anime_parsers_ru.errors import NoResults
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from getNewReleases import getNewReleases, get_new_releases_kodik
from getTrending import getTrending, get_trending_kodik
from getFullInfo import get_full_info
from searchByTitle import search_by_title, search_by_title_shikimori
from getHeroAnime import get_hero_anime


def _decode(v):
    return v.decode('utf-8') if isinstance(v, (bytes, bytearray)) else v


def _proccess_reply(headers):
    reply_to = headers.get('kafka_replyTopic')
    if reply_to is None:
        reply_to = 'get_new_releases.reply'
        print("WARNING: kafka_replyTopic not found, fallback: ", reply_to)
    else:
        reply_to = _decode(reply_to)

    correlation_id = headers.get('kafka_correlationId')
    if correlation_id is None:
        print("WARNING: kafka_correlationId not found — NestJS не сопоставит ответ!")

    out_headers = []
    if correlation_id is not None:
        if not isinstance(correlation_id, (bytes, bytearray)):
            correlation_id = str(correlation_id).encode('utf-8')
        out_headers.append(('kafka_correlationId', correlation_id))

    return reply_to, out_headers, correlation_id


async def _consume_msg(msg, data):
    headers = {}
    if msg.headers:
        for key, val in msg.headers:
            headers[_decode(key)] = val

    reply_to, out_headers, correlation_id = _proccess_reply(headers)

    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda m: json.dumps(m).encode('utf-8'),
    )
    await producer.start()

    await producer.send(
        reply_to,
        value=data,
        headers=out_headers,
    )
    await producer.flush()

    await producer.stop()
    print('Response sent to: ', reply_to, 'corrId: ', correlation_id, "items count: ", len(data))


def kafka_consumer(topic: str, group_id: str = "anifirst-kafka", **kwargs):
    """Декоратор: создаёт consumer, стартует его, передаёт в функцию, останавливает."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs_inner):
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers="localhost:9092",
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                enable_auto_commit=True,
                **kwargs,
            )
            await consumer.start()
            try:
                return await func(consumer, *args, **kwargs_inner)
            finally:
                await consumer.stop()

        return wrapper

    return decorator


@kafka_consumer("get_new_releases")
async def consume_new_releases(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value
        assert payload is not None
        limit = payload.get("limit", 1)
        page = payload.get("page", 1)
        new_releases = await getNewReleases(limit, page)
        await _consume_msg(msg, new_releases)


@kafka_consumer("get_new_releases_kodik")
async def consume_new_releases_kodik(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value
        assert payload is not None
        limit = payload.get('limit', 10)
        print("Limit: ", limit, "\n")
        trending = await get_new_releases_kodik(limit)

        parsed = []
        for item in trending:
            try:
                md = item["material_data"]
                if md["anime_poster_url"] == None or md["title"] == None or item["shikimori_id"] == None:
                    continue

                parsed.append(item)
            except:
                print("WARN: error while getting params of anime from kodik. This item was skipped")
                continue

        parsed = parsed[:limit]
        await _consume_msg(msg, parsed)


@kafka_consumer("get_trending")
async def consume_trending(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value
        assert payload is not None
        limit = payload.get('limit', 1)
        page = payload.get('page', 1)
        print("Limit: ", limit, "\n")
        trending = await getTrending(limit, page)
        await _consume_msg(msg, trending)


@kafka_consumer("get_trending_kodik")
async def consume_trending_kodik(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value
        assert payload is not None
        limit = payload.get('limit', 10)
        print("Limit: ", limit, "\n")
        trending = await get_trending_kodik(limit)

        parsed = []
        for item in trending:
            try:
                md = item["material_data"]
                if md["anime_poster_url"] == None or md["title"] == None or item["shikimori_id"] == None:
                    continue

                parsed.append(item)
            except:
                print("WARN: error while getting params of anime from kodik. This item was skipped")
                continue

        parsed = parsed[:limit]
        await _consume_msg(msg, parsed)


@kafka_consumer("get_hero_anime")
async def consume_hero_anime(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        print("Message to hero")
        hero = await get_hero_anime()
        await _consume_msg(msg, hero)


@kafka_consumer("search_animes")
async def consume_search(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value

        try:
            assert payload is not None
            title = payload['title']
        except:
            print("WARNING: title is missing")
            data = {"message": "title is missing", "error": "Missing"}
            await _consume_msg(msg, data)
            continue

        if not title:
            print("WARNING: title is undefiend")
            data = {"message": "title is undefiend", "error": "Missing"}
            await _consume_msg(msg, data)
            continue

        print("Title: ", title, "\n")
        try:
            trending = await search_by_title(title)
        except NoResults:
            print("ERROR: Anime was not found by title: ", title)
            data = {"message": f"Anime was not found by title: {title}", "error": "Not found"}
            await _consume_msg(msg, data)
            continue
        except:
            data = {"message": "Unknown error", "error": "Unknown error"}
            await _consume_msg(msg, data)
            continue

        await _consume_msg(msg, trending)


@kafka_consumer("search_animes_shikimori")
async def consume_search_shikimori(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value

        try:
            assert payload is not None
            title = payload['title']
        except:
            print("WARNING: title is missing")
            data = {"message": "title is missing", "error": "Missing"}
            await _consume_msg(msg, data)
            continue

        if not title:
            print("WARNING: title is undefiend")
            data = {"message": "title is undefiend", "error": "Missing"}
            await _consume_msg(msg, data)
            continue

        print("Title: ", title, "\n")
        try:
            trending = await search_by_title_shikimori(title)
        except NoResults:
            print("ERROR: Anime was not found by title: ", title)
            data = {"message": f"Anime was not found by title: {title}", "error": "Not found"}
            await _consume_msg(msg, data)
            continue
        except:
            data = {"message": "Unknown error", "error": "Unknown error"}
            await _consume_msg(msg, data)
            continue

        await _consume_msg(msg, trending)


@kafka_consumer("get_full_info")
async def consume_full_info(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        print("Message consumed!", "\n", msg)

        payload = msg.value
        try:
            assert payload is not None
            id = payload['shikimori_id']
        except:
            print("WARNING: shikimori_id is missing")
            data = {"message": "Shikimori_id is missing", "error": "Missing"}
            await _consume_msg(msg, data)
            continue

        if not id:
            print("WARNING: Id is undefiend")
            data = {"message": "Id is undefiend", "error": "Missing"}
            await _consume_msg(msg, data)
            continue

        try:
            info = await get_full_info(id)
        except NoResults:
            print("ERROR: Anime was not found by shikimory id: ", id)
            data = {"message": f"Anime was not found by shikimory id: {id}", "error": "Not found"}
            await _consume_msg(msg, data)
            continue

        await _consume_msg(msg, info)


async def main():
    await asyncio.gather(
        consume_new_releases(), # type: ignore
        consume_new_releases_kodik(), # type: ignore
        consume_trending(), # type: ignore
        consume_trending_kodik(), # type: ignore
        consume_hero_anime(), # type: ignore
        consume_full_info(), # type: ignore
        consume_search(), # type: ignore
        consume_search_shikimori() # type: ignore
    )

asyncio.run(main())
