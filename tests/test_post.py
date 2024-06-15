from swetter.models import Post
from tests.conftest import client, TestingSessionLocal


def test_create_post():
    response = client.post(
        "/post/",
        json={"post_title": "Test Title", "post_content": "Test Content", "post_auto_answer": False, "post_delay": None}
    )
    assert response.status_code == 200
    assert response.json()["post_title"] == "Test Title"
    assert response.json()["post_content"] == "Test Content"


def test_create_post_with_blocked_content():
    response = client.post(
        "/post/",
        json={"post_title": "I wanna kill you", "post_content": "Blocked Content", "post_auto_answer": False,
              "post_delay": None}
    )
    assert response.status_code in [403, 500]
    # assert response.json() == {"Error": "Post contains prohibited content. Post was blocked"}


def test_get_post():
    # Сначала создаем пост
    post = Post.create_post(db=TestingSessionLocal(), user_id=1, post_title="Test Title", post_content="Test Content",
                            post_auto_answer=False, post_delay=None, post_blocked=False)
    response = client.get(f"/post/{post.post_id}")
    assert response.status_code == 200
    assert response.json()["post_title"] == "Test Title"
    assert response.json()["post_content"] == "Test Content"


def test_update_post():
    # Сначала создаем пост
    post = Post.create_post(db=TestingSessionLocal(), user_id=1, post_title="Test Title", post_content="Test Content",
                            post_auto_answer=False, post_delay=None, post_blocked=False)
    # Затем обновляем его
    response = client.put(
        f"/post/{post.post_id}",
        json={"post_title": "Updated Title", "post_content": "Updated Content"}
    )
    assert response.status_code == 200
    assert response.json()["post_title"] == "Updated Title"
    assert response.json()["post_content"] == "Updated Content"


def test_delete_post():
    # Сначала создаем пост
    post = Post.create_post(db=TestingSessionLocal(), user_id=1, post_title="Test Title", post_content="Test Content",
                            post_auto_answer=False, post_delay=None, post_blocked=False)
    # Затем удаляем его
    response = client.delete(f"/post/{post.post_id}")
    assert response.status_code == 200
    # Проверяем, что пост действительно удален
    response = client.get(f"/post/{post.post_id}")
    assert response.status_code == 404


def test_get_user_posts():
    # Сначала создаем несколько постов
    Post.create_post(db=TestingSessionLocal(), user_id=1, post_title="Test Title 1", post_content="Test Content 1",
                     post_auto_answer=False, post_delay=None, post_blocked=False)
    Post.create_post(db=TestingSessionLocal(), user_id=1, post_title="Test Title 2", post_content="Test Content 2",
                     post_auto_answer=False, post_delay=None, post_blocked=False)
    response = client.get("/posts/1")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_all_posts():
    # Сначала создаем несколько постов
    Post.create_post(db=TestingSessionLocal(), user_id=1, post_title="Test Title 1", post_content="Test Content 1",
                     post_auto_answer=False, post_delay=None, post_blocked=False)
    Post.create_post(db=TestingSessionLocal(), user_id=1, post_title="Test Title 2", post_content="Test Content 2",
                     post_auto_answer=False, post_delay=None, post_blocked=False)
    response = client.get("/posts/")
    assert response.status_code == 200
    assert len(response.json()) == 3
