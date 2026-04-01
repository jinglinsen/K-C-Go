from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
import enum
import datetime
from database import Base

class RoleEnum(str, enum.Enum):
    guest = "guest"
    user = "user"
    admin = "admin"
    super_admin = "super_admin"

class PostStatusEnum(str, enum.Enum):
    draft = "draft"
    published = "published"
    deleted = "deleted"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default=RoleEnum.user.value)
    avatar = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String) # Stored as comma separated string for simplicity in sqlite fallback
    category = Column(String, default="General")
    status = Column(String, default=PostStatusEnum.published.value)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    last_activity = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    level = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    # For nested comments, one could define self-referential relationships if needed
    replies = relationship("Comment", backref="parent", remote_side=[id])

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
