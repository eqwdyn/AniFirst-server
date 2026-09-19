import json
import asyncio
from  anime_parsers_ru.errors import NoResults
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from getNewReleases import getNewReleases, get_new_releases_kodik
from getTrending import getTrending, get_trending_kodik
from getFullInfo import get_full_info
from searchByTitle import search_by_title
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
    # print("Message consumed!", "\n", msg)
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


async def consume_new_releases():
    new_releases_consumer = AIOKafkaConsumer(
        'get_new_releases',
        bootstrap_servers='localhost:9092',
        group_id='anifirst-kafka',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )
    await new_releases_consumer.start()

    try:
        async for msg in new_releases_consumer:
            payload = msg.value
            limit = payload.get('limit', 1)
            new_releases = await getNewReleases(limit)
            await _consume_msg(msg, new_releases)
    finally:
        await new_releases_consumer.stop()

async def consume_new_releases_kodik():
    consumer = AIOKafkaConsumer(
        'get_new_releases_kodik',
        bootstrap_servers='localhost:9092',
        group_id='anifirst-kafka',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            payload = msg.value
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
    finally:
        await consumer.stop()


async def consume_trending():
    consumer = AIOKafkaConsumer(
        'get_trending',
        bootstrap_servers='localhost:9092',
        group_id='anifirst-kafka',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            payload = msg.value
            limit = payload.get('limit', 1)
            print("Limit: ", limit, "\n")
            trending = await getTrending(limit)
            await _consume_msg(msg, trending)
    finally:
        await consumer.stop()

async def consume_trending_kodik():
    consumer = AIOKafkaConsumer(
        'get_trending_kodik',
        bootstrap_servers='localhost:9092',
        group_id='anifirst-kafka',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            payload = msg.value
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
    finally:
        await consumer.stop()


async def consume_hero_anime():
    consumer = AIOKafkaConsumer(
        'get_hero_anime',
        bootstrap_servers='localhost:9092',
        group_id='anifirst-kafka',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            print("Message to hero")
            hero = await get_hero_anime()
            # print(hero)
            await _consume_msg(msg, hero)
    finally:
        await consumer.stop()


async def consume_search():
    consumer = AIOKafkaConsumer(
        'search_animes',
        bootstrap_servers='localhost:9092',
        group_id='anifirst-kafka',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            payload = msg.value

            try:
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
    finally:
        await consumer.stop()


async def consume_full_info():
    consumer = AIOKafkaConsumer(
        'get_full_info',
        bootstrap_servers='localhost:9092',
        group_id='anifirst-kafka',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            print("Message consumed!", "\n", msg)
            
            payload = msg.value
            # print(json.dumps(msg.value))
            try:
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


            # print(json.dumps(info))
            await _consume_msg(msg, info)
    finally:
        await consumer.stop()



async def main():
    await asyncio.gather(
        consume_new_releases(),
        consume_new_releases_kodik(),
        consume_trending(),
        consume_trending_kodik(),
        consume_hero_anime(),
        consume_full_info(),
        consume_search()
    )

asyncio.run(main())