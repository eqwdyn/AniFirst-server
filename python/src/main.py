import asyncio
from anime_parsers_ru.errors import NoResults
from aiokafka import AIOKafkaConsumer
from getNewReleases import getNewReleases, get_new_releases_kodik
from getTrending import getTrending, get_trending_kodik
from getFullInfo import get_full_info
from searchByTitle import search_by_title, search_by_title_shikimori
from getHeroAnime import get_hero_anime
from utils.consume_messages import consume_msg
from utils.kafka_konsumer import kafka_consumer


@kafka_consumer("get_new_releases")
async def consume_new_releases(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value
        assert payload is not None
        limit = payload.get("limit", 1)
        page = payload.get("page", 1)
        new_releases = await getNewReleases(limit, page)
        await consume_msg(msg, new_releases)


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
        await consume_msg(msg, parsed)


@kafka_consumer("get_trending")
async def consume_trending(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        payload = msg.value
        assert payload is not None
        limit = payload.get('limit', 1)
        page = payload.get('page', 1)
        print("Limit: ", limit, "\n")
        trending = await getTrending(limit, page)
        await consume_msg(msg, trending)


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
        await consume_msg(msg, parsed)


@kafka_consumer("get_hero_anime")
async def consume_hero_anime(consumer: AIOKafkaConsumer):
    async for msg in consumer:
        print("Message to hero")
        hero = await get_hero_anime()
        await consume_msg(msg, hero)


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
            await consume_msg(msg, data)
            continue

        if not title:
            print("WARNING: title is undefiend")
            data = {"message": "title is undefiend", "error": "Missing"}
            await consume_msg(msg, data)
            continue

        print("Title: ", title, "\n")
        try:
            trending = await search_by_title(title)
        except NoResults:
            print("ERROR: Anime was not found by title: ", title)
            data = {"message": f"Anime was not found by title: {title}", "error": "Not found"}
            await consume_msg(msg, data)
            continue
        except:
            data = {"message": "Unknown error", "error": "Unknown error"}
            await consume_msg(msg, data)
            continue

        await consume_msg(msg, trending)


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
            await consume_msg(msg, data)
            continue

        if not title:
            print("WARNING: title is undefiend")
            data = {"message": "title is undefiend", "error": "Missing"}
            await consume_msg(msg, data)
            continue

        print("Title: ", title, "\n")
        try:
            trending = await search_by_title_shikimori(title)
        except NoResults:
            print("ERROR: Anime was not found by title: ", title)
            data = {"message": f"Anime was not found by title: {title}", "error": "Not found"}
            await consume_msg(msg, data)
            continue
        except:
            data = {"message": "Unknown error", "error": "Unknown error"}
            await consume_msg(msg, data)
            continue

        await consume_msg(msg, trending)


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
            await consume_msg(msg, data)
            continue

        if not id:
            print("WARNING: Id is undefiend")
            data = {"message": "Id is undefiend", "error": "Missing"}
            await consume_msg(msg, data)
            continue

        try:
            info = await get_full_info(id)
        except NoResults:
            print("ERROR: Anime was not found by shikimory id: ", id)
            data = {"message": f"Anime was not found by shikimory id: {id}", "error": "Not found"}
            await consume_msg(msg, data)
            continue

        await consume_msg(msg, info)


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
