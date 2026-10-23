from fastapi import APIRouter, Depends, HTTPException, Response, status
from api_models import Car, CarCreate, CarUpdate
from api_repositories import CarRepository
from api_dependencies import get_car_repository

router = APIRouter(prefix="/api/cars", tags=["Cars"])


@router.get("", response_model=list[Car])
def get_all_cars(repo: CarRepository = Depends(get_car_repository)) -> list[Car]:
    """GET /api/cars — 200 OK со списком (пустой — тоже 200)."""
    return repo.get_all()


@router.get("/{car_id}", response_model=Car)
def get_car_by_id(
    car_id: int,
    repo: CarRepository = Depends(get_car_repository),
) -> Car:
    """GET /api/cars/{id} — 200 OK или 404 Not Found."""
    car = repo.get_by_id(car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.post("", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(
    payload: CarCreate,
    repo: CarRepository = Depends(get_car_repository),
) -> Car:
    """POST /api/cars — создаёт машину из JSON-тела.

        Коды ответа:
          201 Created — успешно создана, тело = созданный объект;
          422 Unprocessable Entity — некорректное тело (валидация Pydantic);
          400 Bad Request — нарушение FK (dealer_id не существует).
        """
    try:
        return repo.create(payload)
    except Exception as e:
        if "FOREIGN KEY" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid dealer_id: {payload.dealer_id}",
            )
        raise


@router.put("/{car_id}", response_model=Car)
def update_car(
    car_id: int,
    payload: CarUpdate,
    repo: CarRepository = Depends(get_car_repository),
) -> Car:
    """PUT /api/cars/{id} — полная замена полей.

        Коды ответа:
          200 OK — объект обновлён, тело = обновлённый объект;
          404 Not Found — машины с таким id нет;
          400 Bad Request — FK-нарушение;
          422 Unprocessable Entity — некорректное тело.
        """
    try:
        car = repo.update(car_id, payload)
    except Exception as e:
        if "FOREIGN KEY" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid dealer_id: {payload.dealer_id}",
            )
        raise
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    repo: CarRepository = Depends(get_car_repository),
) -> Response:
    """DELETE /api/cars/{id}

        Коды ответа:
          204 No Content — объект удалён (тела нет);
          404 Not Found — машины с таким id нет.
        """
    if not repo.delete(car_id):
        raise HTTPException(status_code=404, detail="Car not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
