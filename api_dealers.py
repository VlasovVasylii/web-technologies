from fastapi import APIRouter, Depends, HTTPException, Response, status
from api_models import Dealer, DealerCreate, DealerUpdate
from api_repositories import DealerRepository
from api_dependencies import get_dealer_repository

router = APIRouter(prefix="/api/dealers", tags=["Dealers"])


@router.get("", response_model=list[Dealer])
def get_all_dealers(
    repo: DealerRepository = Depends(get_dealer_repository),
) -> list[Dealer]:
    """GET /api/dealers — 200 OK со списком (пустой — тоже 200)."""
    return repo.get_all()


@router.get("/{dealer_id}", response_model=Dealer)
def get_dealer_by_id(
    dealer_id: int,
    repo: DealerRepository = Depends(get_dealer_repository),
) -> Dealer:
    """GET /api/dealers/{id} — 200 OK или 404 Not Found."""
    dealer = repo.get_by_id(dealer_id)
    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealer


@router.post("", response_model=Dealer, status_code=status.HTTP_201_CREATED)
def create_dealer(
    payload: DealerCreate,
    repo: DealerRepository = Depends(get_dealer_repository),
) -> Dealer:
    """POST /api/dealers — 201 Created."""
    return repo.create(payload)


@router.put("/{dealer_id}", response_model=Dealer)
def update_dealer(
    dealer_id: int,
    payload: DealerUpdate,
    repo: DealerRepository = Depends(get_dealer_repository),
) -> Dealer:
    """PUT /api/dealers/{id} — 200 OK или 404 Not Found."""
    dealer = repo.update(dealer_id, payload)
    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealer


@router.delete("/{dealer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dealer(
    dealer_id: int,
    repo: DealerRepository = Depends(get_dealer_repository),
) -> Response:
    """DELETE /api/dealers/{id} — 204 No Content.

        Благодаря ON DELETE SET NULL все машины этого дилера
        остаются в БД, но с dealer_id = NULL.
        """
    if not repo.delete(dealer_id):
        raise HTTPException(status_code=404, detail="Dealer not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)