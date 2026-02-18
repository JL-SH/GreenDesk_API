from typing import Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    id: int
    target_model: str
    target_id: int
    action: str
    changes: Dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
