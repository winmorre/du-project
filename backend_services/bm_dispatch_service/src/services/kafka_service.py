import asyncio
from asyncio import Future
from threading import Thread

import structlog
from confluent_kafka import Message, Producer, KafkaException
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField

from configs.settings import get_settings

_settings = get_settings()
Logger = structlog.getLogger(__name__)


class AioProducer:
    def __init__(self, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._producer = Producer(AioProducer._producer_config())
        self.cancelled = False
        self._poll_thread = Thread(target=self._poll_loop, daemon=True, name="kafka.service")
        self._poll_thread.start()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    @staticmethod
    def _producer_config():
        return {
            "bootstrap.servers": _settings.kafka_servers,
            "sasl.mechanism":"PLAIN",
        }

    def _poll_loop(self):
        while not self.cancelled:
            self._producer.poll(0.1)

    def close(self):
        self.cancelled = True
        self._poll_thread.join()

    def produce_(self, topic, value) -> Future:
        """
        An awaitable produce  method
        """
        result = self._loop.create_future()

        def ack(err, msg: Message):
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)

        self._producer.produce(topic=topic, value=value, on_delivery=ack)
        return result

    def produce(self, topic, value, msg_type, key, on_delivery=None):
        result = self._loop.create_future()

        def ack(err, msg: Message):
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)

            if on_delivery:
                Logger.info("record on delivery",
                            key=msg.key(),
                            topic=msg.topic(),
                            partition=msg.partition(),
                            offset=msg.offset())
                self._loop.call_soon_threadsafe(result.set_result, msg)

        str_serializer = StringSerializer("utf_8")
        self._producer.produce(
            key=str_serializer(str(key)),
            topic=topic,
            value=str_serializer(str(value)),
            on_delivery=ack
        )

        return result


aio_producer = AioProducer()
