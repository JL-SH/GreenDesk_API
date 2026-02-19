from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.device_repository import DeviceRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.device import Device


class DeviceService:
    def __init__(self, db: Session):
        self.device_repo = DeviceRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def create_device(self, device_data: dict) -> Device:
        return self.device_repo.create(device_data)

    def get_device_by_id(self, device_id: int) -> Device:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return device

    def get_all_devices(self, category: str = None, status: str = None) -> list[Device]:
        return self.device_repo.get_all(category, status)

    def loan_device(self, device_id: int, user_id: int, days: int = 7) -> Device:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        if device.status != "available":
            raise HTTPException(status_code=400, detail="Equipo no disponible")

        device.status = "loaned"
        device.owner_id = user_id
        device.return_date = datetime.now() + timedelta(days=days)
        
        return self.device_repo.update(device)

    def return_device(self, device_id: int) -> Device:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        if device.status == "available":
            raise HTTPException(status_code=400, detail="El dispositivo ya está disponible")
        
        old_status = device.status
        device.status = "available"
        device.owner_id = None
        device.return_date = None
        
        updated_device = self.device_repo.update(device)
        
        self.audit_repo.create({
            "target_model": "Device",
            "target_id": device_id,
            "action": "return",
            "changes": {"previous_status": old_status, "returned_at": str(datetime.now())}
        })
        
        return updated_device

    def get_device_history(self, device_id: int) -> list:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        history = self.audit_repo.get_by_model_and_id("Device", device_id)
        if not history:
            raise HTTPException(status_code=404, detail="No hay historial para este dispositivo")
        
        return history
