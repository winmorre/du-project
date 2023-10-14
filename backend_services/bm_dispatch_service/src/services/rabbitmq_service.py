import structlog
import pika
from pika import DeliveryMode

from configs.settings import get_settings

_settings = get_settings()

Logger = structlog.getLogger(__name__)


class RabbitMqService:
    def __init__(self, host, port, amqp_url=None):
        self._port = port
        self._host = host
        self._url = amqp_url
        self._channel = self.channel()

    def _connection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(parameters=pika.ConnectionParameters(
            host=_settings.rabbitmq_host,
            port=_settings.rabbitmq_port,
        ))

    def channel(self):
        return self._connection().channel()

    def declare_queue(self, queue):
        return self._channel.queue_declare(queue=queue, exclusive=True).method.queue

    def bind_queue(self, exchange_name: str, queue):
        return self._channel.queue_bind(exchange=exchange_name, queue=queue)

    def declare_exchange(self, exchange_name="pipa", exchange_type="fanout"):
        return self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            auto_delete=False,
            durable=True,
            passive=False,
        )

    def emit(self, exchange, routing_key, msg):
        self._channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=bytes(msg),
            properties=pika.BasicProperties(
                content_type="context/plain",
                delivery_mode=DeliveryMode.Transient,
            )
        )

    def receive(self, exchange, queue, on_message, routing_key=''):
        result = self._channel.queue_bind(
            queue=queue,
            exchange=exchange,
            routing_key=routing_key,
        )
        self._channel.basic_qos(prefetch_count=2)
