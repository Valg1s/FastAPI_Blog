from passlib.context import CryptContext
from sqlalchemy.orm import Session

from swetter.database.db import SessionLocal
from swetter.models import User, Post, Comment, CommentReply
from swetter.routes.auth import get_password_hash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def populate_db():
    db: Session = SessionLocal()

    try:
        admin_username = "admin"
        admin_password = "admin"
        admin_password_hash = get_password_hash(admin_password)

        User.create_user(db, username=admin_username, hash_password=admin_password_hash)

        admin = User.get_user_by_username(db, admin_username)

        if admin:
            post_title = "Admin Post"
            post_content = "This is an admin post."
            post_auto_answer = True

            post = Post.create_post(
                db,
                user_id=admin.user_id,
                post_title=post_title,
                post_content=post_content,
                post_auto_answer=post_auto_answer
            )

            comment_content = "This is a comment on the admin post."
            comment = Comment.create_comment(
                db,
                post_id=post.post_id,
                user_id=admin.user_id,
                comment_content=comment_content
            )

            reply_content = "This is a reply to the admin's comment."
            CommentReply.create_reply(
                db,
                comment_id=comment.comment_id,
                user_id=admin.user_id,
                reply_content=reply_content
            )

        else:
            print("Admin user could not be created.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

