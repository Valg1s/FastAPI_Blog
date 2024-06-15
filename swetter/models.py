from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Time,desc

from swetter.database.db import Base


class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True, nullable=False)
    user_password_hash = Column(String, nullable=False)
    user_created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def get_user_by_username(cls, db, username):
        return db.query(cls).filter(cls.user_name == username).first()

    @classmethod
    def create_user(cls, db, username, hash_password):
        new_user = cls(user_name=username, user_password_hash=hash_password)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)




class Post(Base):
    __tablename__ = "Post"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    post_title = Column(String, nullable=False)
    post_content = Column(String, nullable=False)
    post_auto_answer = Column(Boolean, nullable=False)
    post_delay = Column(Time, default=datetime.strptime('00:01:00', '%H:%M:%S').time())
    post_created_at = Column(DateTime, default=datetime.utcnow)
    post_blocked = Column(Boolean, default=False)
    post_blocked_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "post_title": self.post_title,
            "post_content": self.post_content,
            "post_auto_answer": self.post_auto_answer,
            "post_delay": self.post_delay,
            "post_created_at": self.post_created_at
        }

    def update(self, db, post_title=None, post_content=None,
               post_auto_answer=None, post_delay=None, post_blocked=None, post_blocked_at=None):

        if post_title is not None:
            self.post_title = post_title
        if post_content is not None:
            self.post_content = post_content
        if post_auto_answer is not None:
            self.post_auto_answer = post_auto_answer
        if post_delay is not None:
            self.post_delay = post_delay
        if post_blocked is not None:
            self.post_blocked = post_blocked
        if post_blocked_at is not None:
            self.post_blocked_at = post_blocked_at

        db.commit()
        db.refresh(self)

    @classmethod
    def get_post_by_id(cls,db, post_id):
        return db.query(cls).filter(cls.post_id == post_id).first()

    @classmethod
    def get_user_posts(cls, db, user_id):
        return db.query(cls).filter((cls.user_id == user_id) & (cls.post_blocked == False)).all()

    @classmethod
    def create_post(cls, db,user_id,  post_title, post_content,
                    post_auto_answer, post_delay=None, post_blocked=None, post_blocked_at=None):
        new_post = cls(user_id=user_id,post_title=post_title, post_content=post_content,
                       post_auto_answer=post_auto_answer, post_delay=post_delay,
                       post_blocked = post_blocked, post_blocked_at=post_blocked_at)

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return new_post

    @classmethod
    def get_all_posts(cls, db):
        return db.query(cls).filter(cls.post_blocked == False).order_by(desc(cls.post_created_at)).all()


class Comment(Base):
    __tablename__ = "Comment"

    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('Post.post_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    comment_content = Column(String, nullable=False)
    comment_created_at = Column(DateTime, default=datetime.utcnow)
    comment_blocked = Column(Boolean, default=False)
    comment_blocked_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "comment_id": self.comment_id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "comment_content": self.comment_content,
            "comment_created_at": self.comment_created_at
        }

    def update(self, db, comment_content=None, comment_blocked=None, comment_blocked_at=None):
        if comment_content is not None:
            self.comment_content = comment_content
        if comment_blocked is not None:
            self.comment_blocked = comment_blocked
        if comment_blocked_at is not None:
            self.comment_blocked_at = comment_blocked_at

        db.commit()
        db.refresh(self)

    @classmethod
    def get_comment_by_id(cls, db, comment_id):
        return db.query(cls).filter(cls.comment_id == comment_id).first()

    @classmethod
    def get_post_comments(cls, db, post_id):
        return db.query(cls).filter((cls.post_id == post_id) & (cls.comment_blocked == False)).all()

    @classmethod
    def get_user_comments(cls, db, user_id):
        return db.query(cls).filter((cls.user_id == user_id) & (cls.comment_blocked == False)).order_by(
            desc(cls.comment_created_at)).all()

    @classmethod
    def create_comment(cls, db, post_id, user_id, comment_content, comment_blocked=None, comment_blocked_at=None):
        new_comment = cls(
            post_id=post_id,
            user_id=user_id,
            comment_content=comment_content,
            comment_blocked=comment_blocked,
            comment_blocked_at=comment_blocked_at
        )

        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        return new_comment


class CommentReply(Base):
    __tablename__ = "Reply_Comment"

    reply_id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey('Comment.comment_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    reply_content = Column(String, nullable=False)
    reply_created_at = Column(DateTime, default=datetime.utcnow)
    reply_blocked = Column(Boolean, default=False)
    reply_blocked_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "reply_id": self.reply_id,
            "comment_id": self.comment_id,
            "user_id": self.user_id,
            "reply_content": self.reply_content,
            "reply_created_at": self.reply_created_at
        }

    def update(self, db, reply_content=None, reply_blocked=None, reply_blocked_at=None):
        if reply_content is not None:
            self.reply_content = reply_content
        if reply_blocked is not None:
            self.reply_blocked = reply_blocked
        if reply_blocked_at is not None:
            self.reply_blocked_at = reply_blocked_at

        db.commit()
        db.refresh(self)

    @classmethod
    def get_reply_by_id(cls, db, reply_id):
        return db.query(cls).filter(cls.reply_id == reply_id).first()

    @classmethod
    def get_comment_replies(cls, db, comment_id):
        return db.query(cls).filter((cls.comment_id == comment_id) & (cls.reply_blocked == False)).all()

    @classmethod
    def create_reply(cls, db, comment_id, user_id, reply_content, reply_blocked=None, reply_blocked_at=None):
        new_reply = cls(
            comment_id=comment_id,
            user_id=user_id,
            reply_content=reply_content,
            reply_blocked=reply_blocked,
            reply_blocked_at=reply_blocked_at
        )

        db.add(new_reply)
        db.commit()
        db.refresh(new_reply)

        return new_reply
