from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
import datetime

import models, schemas, auth, database
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Community Hub API")

# Setup CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication & Registration
@app.post("/api/v1/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    # first user becomes super admin
    is_first = db.query(models.User).count() == 0
    role = models.RoleEnum.super_admin.value if is_first else models.RoleEnum.user.value
    new_user = models.User(username=user.username, password_hash=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/user/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

# Posts
@app.get("/api/v1/posts", response_model=List[schemas.PostOut])
def get_posts(skip: int = 0, limit: int = 20, tab: str = "latest", category: Optional[str] = None, tag: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(models.Post)
    if category:
        query = query.filter(models.Post.category == category)
    if tag:
        query = query.filter(models.Post.tags.contains(tag))

    if tab == "latest":
        query = query.order_by(models.Post.last_activity.desc())
    elif tab == "top":
        query = query.order_by((models.Post.view_count + models.Post.like_count + models.Post.comment_count).desc())
    elif tab == "hot":
        query = query.order_by(models.Post.comment_count.desc(), models.Post.last_activity.desc())
    else:
        query = query.order_by(models.Post.created_at.desc())

    posts = query.offset(skip).limit(limit).all()
    
    # Calculate participants
    for p in posts:
        user_ids = {c.user_id for c in p.comments}
        user_ids.add(p.user_id)
        participants_ids = []
        for uid in user_ids:
            if len(participants_ids) >= 5:
                break
            participants_ids.append(uid)
        participants = db.query(models.User).filter(models.User.id.in_(participants_ids)).all()
        p.participants = participants

    return posts

@app.get("/api/v1/posts/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, db: Session = Depends(database.get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.view_count += 1
    db.commit()
    db.refresh(post)
    
    user_ids = {c.user_id for c in post.comments}
    user_ids.add(post.user_id)
    participants_ids = []
    for uid in user_ids:
        if len(participants_ids) >= 5:
            break
        participants_ids.append(uid)
    participants = db.query(models.User).filter(models.User.id.in_(participants_ids)).all()
    post.participants = participants

    return post

@app.post("/api/v1/posts", response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if post.category == "Announce" and current_user.role != models.RoleEnum.super_admin.value:
        raise HTTPException(status_code=403, detail="只有超级管理员才能在社区公告栏发帖")
    new_post = models.Post(**post.dict(), user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.post("/api/v1/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # Simple like logic. A real app uses Redis + DB delayed sync.
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    existing_like = db.query(models.Like).filter(models.Like.post_id == post_id, models.Like.user_id == current_user.id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Already liked")
    new_like = models.Like(post_id=post_id, user_id=current_user.id)
    post.like_count += 1
    db.add(new_like)
    db.commit()
    return {"message": "Liked successfully", "like_count": post.like_count}

@app.post("/api/v1/posts/{post_id}/comments", response_model=schemas.CommentOut)
def add_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    # depth calculation
    level = 1
    if comment.parent_id:
        parent = db.query(models.Comment).filter(models.Comment.id == comment.parent_id).first()
        if parent:
            level = parent.level + 1
            if level > 3:
                raise HTTPException(status_code=400, detail="Max Comment Depth is 3")
    
    new_comment = models.Comment(
        **comment.dict(), 
        post_id=post_id, 
        user_id=current_user.id,
        level=level
    )
    post.comment_count += 1
    post.last_activity = datetime.datetime.utcnow()
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@app.get("/api/v1/posts/{post_id}/comments", response_model=List[schemas.CommentOut])
def get_comments(post_id: int, db: Session = Depends(database.get_db)):
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(models.Comment.created_at.asc()).all()
    return comments
