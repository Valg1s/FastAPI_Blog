from swetter.models import CommentReply
from tests.conftest import client, TestingSessionLocal


def test_create_reply():
    response = client.post(
        "/reply/",
        json={"comment_id": 1, "reply_content": "Test Reply"}
    )
    assert response.status_code == 200
    assert response.json()["reply_content"] == "Test Reply"


def test_create_reply_with_blocked_content():
    response = client.post(
        "/reply/",
        json={"comment_id": 1, "reply_content": "I wanna kill you"}
    )
    assert response.status_code in [403, 500]
    # assert response.json() == {"Error": "Comment reply contains prohibited content. Post was blocked"}


def test_get_reply():
    # Сначала создаем ответ на комментарий
    reply = CommentReply.create_reply(db=TestingSessionLocal(), comment_id=1, user_id=1, reply_content="Test Reply",
                                      reply_blocked=False)
    response = client.get(f"/reply/{reply.reply_id}")
    assert response.status_code == 200
    assert response.json()["reply_content"] == "Test Reply"


def test_update_reply():
    reply = CommentReply.create_reply(db=TestingSessionLocal(), comment_id=1, user_id=1, reply_content="Test Reply",
                                      reply_blocked=False)
    # Затем обновляем его
    response = client.put(
        f"/reply/{reply.reply_id}",
        json={"reply_content": "Updated Reply"}
    )
    assert response.status_code == 200
    assert response.json()["reply_content"] == "Updated Reply"


def test_delete_reply():
    # Сначала создаем ответ на комментарий
    reply = CommentReply.create_reply(db=TestingSessionLocal(), comment_id=1, user_id=1, reply_content="Test Reply",
                                      reply_blocked=False)
    # Затем удаляем его
    response = client.delete(f"/reply/{reply.reply_id}")
    assert response.status_code == 200
    # Проверяем, что ответ действительно удален
    response = client.get(f"/reply/{reply.reply_id}")
    assert response.status_code == 404


def test_get_comment_replies():
    # Сначала создаем несколько ответов на комментарий
    CommentReply.create_reply(db=TestingSessionLocal(), comment_id=1, user_id=1, reply_content="Test Reply 1",
                              reply_blocked=False)
    CommentReply.create_reply(db=TestingSessionLocal(), comment_id=1, user_id=1, reply_content="Test Reply 2",
                              reply_blocked=False)

    response = client.get("/replies/1")
    assert response.status_code == 200
    assert len(response.json()) == 2
