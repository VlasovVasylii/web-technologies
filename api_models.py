from pydantic import BaseModel, ConfigDict, Field


# ----------------------------- CAR -----------------------------

class CarBase(BaseModel):
    """Поля, которые клиент передаёт при создании/обновлении."""
    firm: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    power: int = Field(..., ge=0, le=2000)
    color: str = Field(..., min_length=1, max_length=50)
    price: int = Field(..., ge=0)
    dealer_id: int | None = None


class CarCreate(CarBase):
    """Тело POST /api/cars — без id (его генерирует БД)."""
    pass


class CarUpdate(CarBase):
    """Тело PUT /api/cars/{id} — полная замена, id берётся из пути."""
    pass


class Car(BaseModel):
    """Ответ API — с id."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    firm: str
    model: str
    year: int
    power: int
    color: str
    price: int
    dealer_id: int | None = None


# ---------------------------- DEALER ---------------------------

class DealerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=200)
    area: str = Field(default="", max_length=100)
    rating: float = Field(..., ge=0.0, le=5.0)


class DealerCreate(DealerBase):
    pass


class DealerUpdate(DealerBase):
    pass


class Dealer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
    address: str
    area: str
    rating: float