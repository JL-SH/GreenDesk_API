from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.device import Device
from app.models.user import User
from app.models.audit_log import AuditLog

router = APIRouter(tags=["Generic Utility"])

MODEL_MAP = {
    "devices": Device,
    "logs": AuditLog,
    "users": User  
}


@router.get("/generic/{model_name}/{item_id}")
def get_any_model(model_name: str, item_id: int, db: Session = Depends(get_db)):
    model_class = MODEL_MAP.get(model_name.lower())
    
    if not model_class:
        raise HTTPException(status_code=404, detail="Modelo no registrado")

    item = db.query(model_class).filter(model_class.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="No se encontró el recurso")
        
    return item


@router.get("/generic/{model_name}")
def get_all_generic(model_name: str, db: Session = Depends(get_db)):
    model_class = MODEL_MAP.get(model_name.lower())
    
    if not model_class:
        raise HTTPException(status_code=404, detail=f"El modelo '{model_name}' no existe")

    items = db.query(model_class).all()
    
    return items
