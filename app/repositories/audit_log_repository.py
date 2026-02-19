from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log_data: dict) -> AuditLog:
        log = AuditLog(**log_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_model_and_id(self, target_model: str, target_id: int) -> list[AuditLog]:
        return self.db.query(AuditLog).filter(
            AuditLog.target_model == target_model,
            AuditLog.target_id == target_id
        ).order_by(AuditLog.created_at.desc()).all()

    def get_all(self) -> list[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
