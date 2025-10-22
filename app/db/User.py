from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.db.database import Base


# Enum for role of user
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


# User table model
class UserModel(Base):
    __tablename__ = "users_table"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[UserRole] = mapped_column(ENUM(UserRole, name="user_role", create_type=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), default="None", nullable=True)
    surname: Mapped[str] = mapped_column(String(255), default="None", nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=datetime.utcnow,
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id}, email={self.email}, role={self.role}>"
