# import json
# from kafka import KafkaConsumer, KafkaProducer

# from getNewReleases import getNewReleases

# token = "56a768d08f43091901c44b54fe970049"

# print("Started")

# consumer = KafkaConsumer(
#     'get_new_releases',
#     bootstrap_servers='localhost:9092',
#     group_id='anifirst-kafka',
#     value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#     auto_offset_reset='latest',
# )

# producer = KafkaProducer(
#     bootstrap_servers='localhost:9092',
#     value_serializer=lambda m: json.dumps(m).encode('utf-8'),
# )


# for msg in consumer:
#     print("Message consumed!", "\n", msg)
#     payload = msg.value
#     limit = payload.get('limit', 10)
#     print("Limit param: ", limit)

#     data = getNewReleases(token, limit=limit)

#     response = {
#         'data': [
#             {'title': i.title, 'shikimori_id': i.shikimori_id, 'link': i.link}
#             for i in data.results
#         ],
#     }

#     headers = {}
#     if msg.headers:
#         for key, val in msg.headers:
#             headers[key] = val

#     # reply_to = None
#     # for key in ("kafka_replyTopic", 'kafka_replyTo', 'reply-to', 'replyTo', b'kafka_replyTo', b'reply-to', b'replyTo', "kafka_correlationId"):
#     #     if key in headers:

#     #         break

#     val = headers["kafka_replyTopic"]
#     reply_to = val.decode('utf-8') if isinstance(val, bytes) else val

#     if not reply_to:
#         print("WARNING: reply-to header not found! Using fallback (this is likely wrong).")
#         reply_to = 'get_new_releases.reply'

#     producer.send(reply_to, response)
#     producer.flush()
#     print("Response sent to: ", reply_to)


import json
from kafka import KafkaConsumer, KafkaProducer
from getNewReleases import getNewReleases

token = "56a768d08f43091901c44b54fe970049"
print('Started')

consumer = KafkaConsumer(
    'get_new_releases',
    bootstrap_servers='localhost:9092',
    group_id='anifirst-kafka',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda m: json.dumps(m).encode('utf-8'),
)


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


for msg in consumer:
    print("Message consumed!", "\n", msg)
    payload = msg.value
    limit = payload.get('limit', 10)
    print("Limit param: ", limit)

    data = getNewReleases(limit)
    response = {
        # 'data': [
        #     {'title': i.title, 'shikimori_id': i.shikimori_id, 'link': i.link}
        #     for i in data.results
        # ],
        'data': data,
    }

    headers = {}
    if msg.headers:
        for key, val in msg.headers:
            headers[_decode(key)] = val

    reply_to, out_headers, correlation_id = _proccess_reply(headers)

    producer.send(
        reply_to,
        value=response,
        headers=out_headers,
    )
    producer.flush()
    print('Response sent to: ', reply_to, 'corrId: ', correlation_id)
