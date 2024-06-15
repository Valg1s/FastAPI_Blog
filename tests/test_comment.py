from swetter.models import Comment
from tests.conftest import client, TestingSessionLocal


def test_create_comment():
    response = client.post(
        "/comment/",
        json={"post_id": 1, "comment_content": "Test Comment"}
    )
    assert response.status_code == 200
    assert response.json()["comment_content"] == "Test Comment"


def test_create_comment_with_blocked_content():
    response = client.post(
        "/comment/",
        json={"post_id": 1, "comment_content": "I wanna kill you"}
    )
    assert response.status_code in [403, 500]
    #assert response.json() == {"Error": "Comment contains prohibited content. Post was blocked"}


def test_get_comment():
    comment = Comment.create_comment(db=TestingSessionLocal(), post_id=1, user_id=1, comment_content="Test Comment", comment_blocked=False)
    response = client.get(f"/comment/{comment.comment_id}")
    assert response.status_code == 200
    assert response.json()["comment_content"] == "Test Comment"


def test_update_comment():
    comment = Comment.create_comment(db=TestingSessionLocal(), post_id=1, user_id=1, comment_content="Test Comment", comment_blocked=False)
    # Затем обновляем его
    response = client.put(
        f"/comment/{comment.comment_id}",
        json={"comment_content": "Updated Comment"}
    )
    assert response.status_code == 200
    assert response.json()["comment_content"] == "Updated Comment"


def test_delete_comment():
    comment = Comment.create_comment(db=TestingSessionLocal(), post_id=1, user_id=1, comment_content="Test Comment", comment_blocked=False)
    # Затем удаляем его
    response = client.delete(f"/comment/{comment.comment_id}")
    assert response.status_code == 200
    # Проверяем, что комментарий действительно удален
    response = client.get(f"/comment/{comment.comment_id}")
    assert response.status_code == 404


def test_get_user_comments():
    Comment.create_comment(db=TestingSessionLocal(), post_id=1, user_id=1, comment_content="Test Comment 1", comment_blocked=False)
    Comment.create_comment(db=TestingSessionLocal(), post_id=1, user_id=1, comment_content="Test Comment 2", comment_blocked=False)

    response = client.get("/comments/1")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_comments_for_post():
    Comment.create_comment(db=TestingSessionLocal(), post_id=1, user_id=1, comment_content="Test Comment 1", comment_blocked=False)
    Comment.create_comment(db=TestingSessionLocal(), post_id=1, user_id=1, comment_content="Test Comment 2", comment_blocked=False)

    response = client.get("/comments/1")
    assert response.status_code == 200
    assert len(response.json()) == 3
