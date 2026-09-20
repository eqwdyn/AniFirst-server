from functools import wraps
from aiokafka import AIOKafkaConsumer
import json


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