from api_repositories import CarRepository, DealerRepository
from event_decorators import (
    EventPublishingCarRepository,
    EventPublishingDealerRepository,
)
from event_publisher import RabbitMQEventPublisher

# Единственный экземпляр публикатора на всё приложение
_publisher = RabbitMQEventPublisher()


def get_publisher() -> RabbitMQEventPublisher:
    """Возвращает единственный экземпляр публикатора.

    Нужен для lifespan в api_main.py — там вызывается
    publisher.init_infrastructure() при старте приложения.
    """
    return _publisher


def get_car_repository() -> CarRepository:
    """Возвращает обёрнутый репозиторий (контроллер видит только CarRepository)."""
    return EventPublishingCarRepository(CarRepository(), _publisher)


def get_dealer_repository() -> DealerRepository:
    """Возвращает обёрнутый репозиторий дилеров."""
    return EventPublishingDealerRepository(DealerRepository(), _publisher)
