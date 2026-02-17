from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GreenDesk API",
    description="Sistema de gestión de inventario para prácticas profesionales",
    version="0.1.0"
)

@app.get("/devices/", response_model=list[schemas.DeviceOut])
def read_devices(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    devices = db.query(models.Device).offset(skip).limit(limit).all()
    return devices

@app.post("/devices/", response_model=schemas.DeviceOut, status_code=201)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.serial_number == device.serial_number).first()
    if db_device:
        raise HTTPException(status_code=400, detail="Serial number already registered")
    
    new_device = models.Device(**device.model_dump())
    
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device