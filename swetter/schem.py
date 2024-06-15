from datetime import time, datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserSchem(BaseModel):
    username: str
    password: str


class PostCreateRequest(BaseModel):
    post_title: str
    post_content: str
    post_auto_answer: bool
    post_delay: time | None


class PostUpdateRequest(BaseModel):
    post_title: str | None = None
    post_content: str | None = None
    post_auto_answer: bool | None = None
    post_delay: time | None = None


class PostResponse(BaseModel):
    post_id: int
    user_id: int
    post_title: str
    post_content: str
    post_auto_answer: bool
    post_delay: time | None
    post_created_at: datetime


class CommentCreateRequest(BaseModel):
    post_id: int
    comment_content: str


class CommentUpdateRequest(BaseModel):
    comment_content: str


class CommentResponse(BaseModel):
    comment_id: int
    post_id: int
    user_id: int
    comment_content: str
    comment_created_at: datetime


class ReplyCreateRequest(BaseModel):
    comment_id: int
    reply_content: str


class ReplyUpdateRequest(BaseModel):
    reply_content: str


class ReplyResponse(BaseModel):
    reply_id: int
    comment_id: int
    user_id: int
    reply_content: str
    reply_created_at: datetime
