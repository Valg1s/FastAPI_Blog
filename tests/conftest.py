import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from swetter.main import app  # Замените на фактический путь к вашему FastAPI приложению
from swetter.models import Base, User, Post, Comment
from swetter.utils.deps import get_db, get_current_user


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базу данных для тестирования
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_user():
    return User(user_id=1, user_name="testuser", user_password_hash="testhash")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Удаляем и пересоздаем таблицы перед каждым тестом
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Добавляем фиктивного пользователя, пост и комментарий в базу данных
    db = TestingSessionLocal()
    post = Post(post_id=1, user_id=1, post_title="Test Post", post_content="Test Content", post_auto_answer=False, post_delay=None, post_blocked=False)
    db.add(post)
    comment = Comment(comment_id=1, post_id=1, user_id=1, comment_content="Test Comment", comment_blocked=False)
    db.add(comment)
    db.commit()
    db.close()
    yield
    # Дополнительно можно очистить данные после каждого теста, если требуется
    Base.metadata.drop_all(bind=engine)
