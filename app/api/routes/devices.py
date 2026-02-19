from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.device import DeviceCreate, DeviceOut
from app.schemas.audit_log import AuditLogOut
from app.services.device_service import DeviceService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/", response_model=DeviceOut, status_code=201)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    service = DeviceService(db)
    new_device = service.create_device(device.model_dump())
    
    service.audit_repo.create({
        "target_model": "Device",
        "target_id": new_device.id,
        "action": "create",
        "changes": {"new_state": device.model_dump()}
    })
    
    return new_device


@router.get("/", response_model=List[DeviceOut])
def read_devices(category: str = None, status: str = None, db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.get_all_devices(category, status)


@router.get("/{device_id}", response_model=DeviceOut)
def get_device(device_id: int, db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.get_device_by_id(device_id)


@router.patch("/{device_id}/loan/{user_id}", response_model=DeviceOut)
def loan_device(device_id: int, user_id: int, days: int = 7, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    service = DeviceService(db)
    return service.loan_device(device_id, user_id, days)


@router.patch("/{device_id}/return", response_model=DeviceOut)
def return_device(device_id: int, db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.return_device(device_id)


@router.get("/{device_id}/history", response_model=List[AuditLogOut])
def get_device_history(device_id: int, db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.get_device_history(device_id)
