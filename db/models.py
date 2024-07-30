from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from db.base_config import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String)
    user_id = Column(String)
    message_id = Column(String)
    text = Column(String)
    photo = Column(String)
    caption = Column(String)
    approved = Column(Boolean, default=False)
    group_topic = Column(String)
    assessment = Column(Integer)
