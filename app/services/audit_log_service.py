from sqlalchemy.orm import Session
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session):
        self.repository = AuditLogRepository(db)

    def create_log(self, log_data: dict):
        return self.repository.create(log_data)

    def get_logs_by_model_and_id(self, target_model: str, target_id: int) -> list:
        return self.repository.get_by_model_and_id(target_model, target_id)

    def get_all_logs(self) -> list:
        return self.repository.get_all()
