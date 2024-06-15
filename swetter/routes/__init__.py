from fastapi import APIRouter

from . import auth, posts, comments, reply_comment

router = APIRouter()
router.include_router(auth.router)
router.include_router(posts.router)
router.include_router(comments.router)
router.include_router(reply_comment.router)

