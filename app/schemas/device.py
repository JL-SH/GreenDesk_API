from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DeviceBase(BaseModel):
    serial_number: str
    model: str
    category: str


class DeviceCreate(DeviceBase):
    pass


class DeviceOut(DeviceBase):
    id: int
    status: str
    return_date: Optional[datetime] = None
    owner_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
