import json
import logging
import pika

logger = logging.getLogger(__name__)

RABBIT_HOST = "localhost"
CARS_EXCHANGE = "cars_events_exchange"
CARS_QUEUE = "cars_events_queue"
DEALERS_EXCHANGE = "dealers_events_exchange"
DEALERS_QUEUE = "dealers_events_queue"


class RabbitMQEventPublisher:
    """Публикует события в fanout-exchange RabbitMQ.

    Объявление exchange и очереди выполняется один раз при первом подключении.
    Если брокер недоступен, ошибка логируется, а API продолжает работу
    (событие теряется — это осознанный компромисс, см. контрольный вопрос 7).
    """
    def __init__(self, host: str = RABBIT_HOST):
        self.host = host
        self._connection: pika.BlockingConnection | None = None
        self._channel: pika.adapters.blocking_connection.BlockingChannel | None = None
        self._ready = False

    # Инициализация инфраструктуры
    def _ensure_ready(self) -> None:
        if self._ready:
            return
        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            self._channel = self._connection.channel()

            # Объявляем exchange и очередь для автомобилей
            self._channel.exchange_declare(
                exchange=CARS_EXCHANGE, exchange_type="fanout", durable=True
            )
            self._channel.queue_declare(queue=CARS_QUEUE, durable=True)
            self._channel.queue_bind(queue=CARS_QUEUE, exchange=CARS_EXCHANGE)

            # Объявляем exchange и очередь для дилеров
            self._channel.exchange_declare(
                exchange=DEALERS_EXCHANGE, exchange_type="fanout", durable=True
            )
            self._channel.queue_declare(queue=DEALERS_QUEUE, durable=True)
            self._channel.queue_bind(queue=DEALERS_QUEUE, exchange=DEALERS_EXCHANGE)

            self._ready = True
            logger.info("RabbitMQ: инфраструктура готова")
        except Exception as e:
            logger.error("RabbitMQ: не удалось подключиться — %s", e)
            self._connection = None
            self._channel = None
            self._ready = False

    # Публикация
    def publish_car_event(self, event_type: str, car: dict) -> None:
        self._publish(CARS_EXCHANGE, {"eventType": event_type, "car": car})

    def publish_dealer_event(self, event_type: str, dealer: dict) -> None:
        self._publish(DEALERS_EXCHANGE, {"eventType": event_type, "dealer": dealer})

    def init_infrastructure(self) -> bool:
        """Подключается и объявляет exchange/queue. Возвращает True при успехе."""
        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, connection_attempts=3)
            )
            self._channel = self._connection.channel()
            for exchange, queue in (
                    (CARS_EXCHANGE, CARS_QUEUE),
                    (DEALERS_EXCHANGE, DEALERS_QUEUE),
            ):
                self._channel.exchange_declare(
                    exchange=exchange, exchange_type="fanout", durable=True
                )
                self._channel.queue_declare(queue=queue, durable=True)
                self._channel.queue_bind(queue=queue, exchange=exchange)
            self._ready = True
            logger.info("RabbitMQ: инфраструктура готова (exchange+queue объявлены)")
            return True
        except Exception as e:
            logger.error("RabbitMQ: не удалось подключиться — %s", e)
            self._connection = None
            self._channel = None
            self._ready = False
            return False

    def _publish(self, exchange: str, payload: dict) -> None:
        self._ensure_ready()
        if not self._channel or not self._connection or not self._connection.is_open:
            logger.warning("RabbitMQ: канал недоступен, событие пропущено")
            return
        try:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._channel.basic_publish(
                exchange=exchange,
                routing_key="",  # fanout игнорирует routing_key
                body=body,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,  # persistent
                ),
            )
            logger.info("RabbitMQ: отправлено событие %s", payload.get("eventType"))
        except Exception as e:
            logger.error("RabbitMQ: ошибка публикации — %s", e)
            # Переподключение при следующей попытке
            self._ready = False
            self._channel = None
            self._connection = None
