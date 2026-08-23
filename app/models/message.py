from datetime import datetime

from sqlalchemy import (BigInteger, DateTime,String,Text)

from sqlalchemy.orm import (Mapped,mapped_column)

from app.database.base import Base

class Message(Base):
    __tablename__ = "messages"

    id:Mapped[int] = mapped_column(BigInteger,primary_key=True,autoincrement=True)

    user_id:Mapped[str] = mapped_column(String(255),nullable=False,index=True)

    conversation_id:Mapped[str] = mapped_column(String(255),nullable=False,index=True)
    role:Mapped[str] = mapped_column(String(255),nullable=False)

    content:Mapped[str]=mapped_column(Text,nullable=False)

    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=datetime.utcnow)