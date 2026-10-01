from sqlalchemy.orm import Session
from app import models


def create_notification(db: Session, user_id: int, message: str):
    notification = models.Notification(user_id=user_id, message=message)
    db.add(notification)
    db.commit()