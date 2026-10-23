from api_models import Car, CarCreate, CarUpdate, Dealer, DealerCreate, DealerUpdate
from api_repositories import CarRepository, DealerRepository
from event_publisher import RabbitMQEventPublisher


class EventPublishingCarRepository:
    """Обёртка над CarRepository, добавляющая публикацию событий.

    Реализует тот же интерфейс, что и CarRepository, поэтому контроллер
    не знает, обёрнут репозиторий или нет.
    """

    def __init__(self, inner: CarRepository, publisher: RabbitMQEventPublisher):
        self._inner = inner
        self._publisher = publisher

    # ---- делегирование чтения ----
    def get_all(self) -> list[Car]:
        return self._inner.get_all()

    def get_by_id(self, car_id: int) -> Car | None:
        return self._inner.get_by_id(car_id)

    # ---- изменение с событием ----
    def create(self, data: CarCreate) -> Car:
        car = self._inner.create(data)          # сначала БД
        self._publisher.publish_car_event("CREATE", car.model_dump())
        return car

    def update(self, car_id: int, data: CarUpdate) -> Car | None:
        car = self._inner.update(car_id, data)  # сначала БД
        if car is not None:
            self._publisher.publish_car_event("UPDATE", car.model_dump())
        return car

    def delete(self, car_id: int) -> bool:
        # нужно получить данные до удаления, чтобы отправить их в событии
        car = self._inner.get_by_id(car_id)
        if car is None:
            return False
        ok = self._inner.delete(car_id)         # сначала БД
        if ok:
            self._publisher.publish_car_event("DELETE", car.model_dump())
        return ok


class EventPublishingDealerRepository:
    """Аналогичная обёртка для дилеров."""

    def __init__(self, inner: DealerRepository, publisher: RabbitMQEventPublisher):
        self._inner = inner
        self._publisher = publisher

    def get_all(self) -> list[Dealer]:
        return self._inner.get_all()

    def get_by_id(self, dealer_id: int) -> Dealer | None:
        return self._inner.get_by_id(dealer_id)

    def create(self, data: DealerCreate) -> Dealer:
        dealer = self._inner.create(data)
        self._publisher.publish_dealer_event("CREATE", dealer.model_dump())
        return dealer

    def update(self, dealer_id: int, data: DealerUpdate) -> Dealer | None:
        dealer = self._inner.update(dealer_id, data)
        if dealer is not None:
            self._publisher.publish_dealer_event("UPDATE", dealer.model_dump())
        return dealer

    def delete(self, dealer_id: int) -> bool:
        dealer = self._inner.get_by_id(dealer_id)
        if dealer is None:
            return False
        ok = self._inner.delete(dealer_id)
        if ok:
            self._publisher.publish_dealer_event("DELETE", dealer.model_dump())
        return ok