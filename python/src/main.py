import json
import asyncio
from getNewReleases import getNewReleases
from getTrending import getTrending
from getFullInfo import get_full_info
from  anime_parsers_ru.errors import NoResults


from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


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
        consume_trending(),
        consume_full_info()
    )

asyncio.run(main())