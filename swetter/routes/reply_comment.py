import datetime
from time import sleep
from typing import List

from fastapi import APIRouter, Response, Depends
from fastapi.responses import JSONResponse

from swetter.models import CommentReply
from swetter.schem import ReplyCreateRequest, ReplyUpdateRequest, ReplyResponse
from swetter.utils.deps import get_current_user
from swetter.utils.deps import get_db
from swetter.utils.gemini import get_data_from_gemini, create_reply_by_gemini

router = APIRouter(dependencies=[Depends(get_current_user)])


def create_auto_reply(db, post_owner_id, post, comment):
    '''
    Create an auto-reply for a comment.
    :param db: db session
    :param post_owner_id: ID of the post owner
    :param post: Post object
    :param comment: Comment object
    '''

    auto_reply_content = None

    while auto_reply_content is None:
        auto_reply_content = create_reply_by_gemini(post.post_title, post.post_content, comment.comment_content)
        sleep(3)

    CommentReply.create_reply(db, comment.comment_id, post_owner_id, auto_reply_content)


@router.get("/reply/{reply_id}", response_model=ReplyResponse)
async def get_reply(reply_id: int, db=Depends(get_db)):
    '''
    Get reply by reply id.
    :param reply_id: reply id in database
    :param db: db session
    :return: ReplyResponse with reply data or JSONResponse with error if reply not exists
    '''

    reply = CommentReply.get_reply_by_id(db, reply_id)

    if not reply:
        return JSONResponse(status_code=404, content={"Not Found": "Comment reply with this id not found"})
    if reply.reply_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Comment reply is blocked"})

    return ReplyResponse(**reply.to_dict())


@router.post("/reply/", response_model=ReplyResponse)
async def create_reply(form_data: ReplyCreateRequest, db=Depends(get_db), current_user=Depends(get_current_user)):
    '''
    Create reply from user data. Before creating, check if reply contains prohibited content.
    :param form_data: reply content and associated comment id
    :param db: db session
    :param current_user: user who sends the request
    :return: ReplyResponse with reply data or JSONResponse with error if reply contains prohibited content or problems with Gemini
    '''

    data = form_data.dict()
    data["user_id"] = current_user.user_id

    need_to_block = get_data_from_gemini(reply_content=data['reply_content'])

    if need_to_block is None:
        return JSONResponse(status_code=500, content={"Error": "Please, try again later"})

    data["reply_blocked"] = need_to_block

    if need_to_block:
        data["reply_blocked_at"] = datetime.datetime.utcnow()

    new_reply = CommentReply.create_reply(db, **data)

    if need_to_block:
        return JSONResponse(status_code=403,
                            content={"Error": "Comment reply contains prohibited content. Reply was blocked"})

    return ReplyResponse(**new_reply.to_dict())


@router.put("/reply/{reply_id}", response_model=ReplyResponse)
async def update_reply(reply_id: int, form_data: ReplyUpdateRequest, db=Depends(get_db)):
    '''
    Update reply by reply id.
    :param reply_id: reply id in database
    :param form_data: data to update the reply
    :param db: db session
    :return: ReplyResponse with updated reply data or JSONResponse with error if reply not exists or is blocked
    '''

    reply = CommentReply.get_reply_by_id(db, reply_id)

    if not reply:
        return JSONResponse(status_code=404, content={"Not Found": "Comment reply with this id not found"})
    if reply.reply_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Comment reply is blocked"})

    data = form_data.dict()
    reply_content = data.get('reply_content', None)

    need_to_block = get_data_from_gemini(reply_content=reply_content)

    data["reply_blocked"] = need_to_block

    if need_to_block:
        data["reply_blocked_at"] = datetime.datetime.utcnow()

    reply.update(db, **data)

    if need_to_block:
        return JSONResponse(status_code=403,
                            content={"Error": "Comment reply contains prohibited content. Reply was blocked"})

    return ReplyResponse(**reply.to_dict())


@router.delete("/reply/{reply_id}")
async def delete_reply(reply_id: int, db=Depends(get_db)):
    '''
    Delete reply by reply id.
    :param reply_id: reply id in database
    :param db: db session
    :return: Response with status code 200 or JSONResponse with error if reply not exists or is blocked
    '''

    reply = CommentReply.get_reply_by_id(db, reply_id)

    if not reply:
        return JSONResponse(status_code=404, content={"Not Found": "Comment reply with this id not found"})
    if reply.reply_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Comment reply is blocked"})

    db.delete(reply)
    db.commit()

    return Response(status_code=200)


@router.get("/replies/{comment_id}", response_model=List[ReplyResponse])
async def get_comment_replies(comment_id: int, db=Depends(get_db)):
    '''
    Get all replies for a specific comment by comment id.
    :param comment_id: comment id in database
    :param db: db session
    :return: List of ReplyResponse with replies for the comment
    '''

    replies = CommentReply.get_comment_replies(db, comment_id)
    result = [ReplyResponse(**reply.to_dict()) for reply in replies]

    return result
