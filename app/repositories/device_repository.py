from sqlalchemy.orm import Session
from app.models.device import Device


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, device_data: dict) -> Device:
        device = Device(**device_data)
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def get_by_id(self, device_id: int) -> Device:
        return self.db.query(Device).filter(Device.id == device_id).first()

    def get_all(self, category: str = None, status: str = None) -> list[Device]:
        query = self.db.query(Device)
        if category:
            query = query.filter(Device.category == category)
        if status:
            query = query.filter(Device.status == status)
        return query.all()

    def update(self, device: Device) -> Device:
        self.db.commit()
        self.db.refresh(device)
        return device
