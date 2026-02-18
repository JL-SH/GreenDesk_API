import time
from datetime import datetime, timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import models, schemas
from app.db import get_db

app = FastAPI(
    title="GreenDesk Inventory API",
    description="API profesional para gestión de activos con Auditoría JSONB y Migraciones",
    version="1.0.0"
)

MODEL_MAP = {
    "devices": models.Device,
    "logs": models.AuditLog,
    "users": models.User  
}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.post("/users/", response_model=schemas.UserOut, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/devices/", response_model=schemas.DeviceOut, status_code=201, tags=["Devices"])
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    new_device = models.Device(**device.model_dump())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    log = models.AuditLog(
        target_model="Device",
        target_id=new_device.id,
        action="create",
        changes={"new_state": device.model_dump()} 
    )
    db.add(log)
    db.commit()
    
    return new_device

@app.get("/devices/", response_model=List[schemas.DeviceOut], tags=["Devices"])
def read_devices(category: str = None, status: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Device)
    if category: query = query.filter(models.Device.category == category)
    if status: query = query.filter(models.Device.status == status)
    return query.all()

@app.patch("/devices/{device_id}/loan/{user_id}", response_model=schemas.DeviceOut, tags=["Inventory Operations"])
def loan_device(device_id: int, user_id: int, days: int = 7, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not device: raise HTTPException(404, "Equipo no encontrado")
    if not user: raise HTTPException(404, "Usuario no encontrado")
    if device.status != "available": raise HTTPException(400, "Equipo no disponible")

    device.status = "loaned"
    device.owner_id = user_id
    device.return_date = datetime.now() + timedelta(days=days)
    
    db.commit()
    db.refresh(device)
    return device

@app.patch("/devices/{device_id}/return", response_model=schemas.DeviceOut, tags=["Inventory Operations"])
def return_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    if device.status == "available":
        raise HTTPException(status_code=400, detail="El dispositivo ya está disponible")
    
    old_status = device.status
    
    device.status = "available"
    device.owner_id = None    
    device.return_date = None 
    
    log = models.AuditLog(
        target_model="Device",
        target_id=device.id,
        action="return",
        changes={"previous_status": old_status, "returned_at": str(datetime.now())}
    )
    db.add(log)
    db.commit()
    db.refresh(device)
    
    return device

@app.get("/devices/{device_id}/history", response_model=List[schemas.AuditLogOut], tags=["Inventory Operations"])
def get_device_history(device_id: int, db: Session = Depends(get_db)):
    history = db.query(models.AuditLog).filter(
        models.AuditLog.target_model == "Device",
        models.AuditLog.target_id == device_id
    ).order_by(models.AuditLog.created_at.desc()).all()
    
    if not history:
        raise HTTPException(status_code=404, detail="No hay historial para este dispositivo")
        
    return history

@app.get("/generic/{model_name}/{item_id}", tags=["Generic Utility"])
def get_any_model(model_name: str, item_id: int, db: Session = Depends(get_db)):
    model_class = MODEL_MAP.get(model_name.lower())
    
    if not model_class:
        raise HTTPException(status_code=404, detail="Modelo no registrado")

    item = db.query(model_class).filter(model_class.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="No se encontró el recurso")
        
    return item

@app.get("/generic/{model_name}", tags=["Generic Utility"])
def get_all_generic(model_name: str, db: Session = Depends(get_db)):
    model_class = MODEL_MAP.get(model_name.lower())
    
    if not model_class:
        raise HTTPException(status_code=404, detail=f"El modelo '{model_name}' no existe")

    items = db.query(model_class).all()
    
    return items
