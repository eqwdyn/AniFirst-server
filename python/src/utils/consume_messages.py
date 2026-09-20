from aiokafka import AIOKafkaProducer
import json



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


async def consume_msg(msg, data):
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
