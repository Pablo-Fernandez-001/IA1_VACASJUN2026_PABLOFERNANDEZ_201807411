from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Provider, User
from app.schemas.dto import ProviderIn, ProviderOut

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("", response_model=list[ProviderOut])
def list_providers(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Provider).order_by(Provider.name.asc()).all()


@router.get("/{provider_id}", response_model=ProviderOut)
def get_provider(provider_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return provider


@router.post("", response_model=ProviderOut)
def create_provider(payload: ProviderIn, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Provider).filter(Provider.nit == payload.nit).first():
        raise HTTPException(status_code=409, detail="Ya existe un proveedor con ese NIT")
    provider = Provider(**payload.model_dump())
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.put("/{provider_id}", response_model=ProviderOut)
def update_provider(
    provider_id: int,
    payload: ProviderIn,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    provider = db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    duplicated = db.query(Provider).filter(Provider.nit == payload.nit, Provider.id != provider_id).first()
    if duplicated:
        raise HTTPException(status_code=409, detail="Otro proveedor ya usa ese NIT")
    for key, value in payload.model_dump().items():
        setattr(provider, key, value)
    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/{provider_id}")
def delete_provider(provider_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = db.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    db.delete(provider)
    db.commit()
    return {"deleted": True, "id": provider_id}
