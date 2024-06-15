import datetime
from typing import List

from fastapi import APIRouter, Response, Depends
from fastapi.responses import JSONResponse

from swetter import scheduler
from swetter.models import Comment, Post
from swetter.routes.reply_comment import create_auto_reply
from swetter.schem import CommentResponse, CommentCreateRequest, CommentUpdateRequest
from swetter.utils.deps import get_current_user
from swetter.utils.deps import get_db
from swetter.utils.gemini import get_data_from_gemini

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/comment/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db=Depends(get_db)):
    '''
    Get comment by comment id.
    :param comment_id: comment id in database
    :param db: db session
    :return: CommentResponse with comment data or JSONResponse with error if comment not exists
    '''

    comment = Comment.get_comment_by_id(db, comment_id)

    if not comment:
        return JSONResponse(status_code=404, content={"Not Found": "Comment with this id not found"})
    if comment.comment_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Comment is blocked"})

    return CommentResponse(**comment.to_dict())


@router.post("/comment/", response_model=CommentResponse)
async def create_comment(form_data: CommentCreateRequest, db=Depends(get_db),
                         current_user=Depends(get_current_user)):
    '''
    Create comment from user data. Before creating, check if comment contains prohibited content.
    :param form_data: comment content and associated post id
    :param db: db session
    :param current_user: user who sends the request
    :return: CommentResponse with comment data or JSONResponse with error if comment contains prohibited content or problems with Gemini
    '''

    data = form_data.dict()

    post = Post.get_post_by_id(db, data["post_id"])

    if not post:
        return JSONResponse(status_code=404, content={"Not Found": "Post with this id not found"})
    if post.post_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Post is blocked"})

    data["user_id"] = current_user.user_id

    need_to_block = get_data_from_gemini(comment_content=data['comment_content'])

    if need_to_block is None:
        return JSONResponse(status_code=500, content={"Error": "Please, try again later"})

    data["comment_blocked"] = need_to_block

    if need_to_block:
        data["comment_blocked_at"] = datetime.datetime.utcnow()

    new_comment = Comment.create_comment(db, **data)

    if need_to_block:
        return JSONResponse(status_code=403,
                            content={"Error": "Comment contains prohibited content. Comment was blocked"})

    if post.post_auto_answer:
        delay = datetime.timedelta(hours=post.post_delay.hour, minutes=post.post_delay.minute,
                                   seconds=post.post_delay.second)
        run_time = datetime.datetime.now() + delay
        scheduler.add_job(create_auto_reply, 'date', (db, post.user_id, post, new_comment), run_date=run_time)

    return CommentResponse(**new_comment.to_dict())


@router.put("/comment/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, form_data: CommentUpdateRequest,
                         db=Depends(get_db)):
    '''
    Update comment by comment id.
    :param comment_id: comment id in database
    :param form_data: data to update the comment
    :param db: db session
    :return: CommentResponse with updated comment data or JSONResponse with error if comment not exists or is blocked
    '''

    comment = Comment.get_comment_by_id(db, comment_id)

    if not comment:
        return JSONResponse(status_code=404, content={"Not Found": "Comment with this id not found"})
    if comment.comment_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Comment is blocked"})

    data = form_data.dict()
    comment_content = data.get('comment_content', None)

    need_to_block = get_data_from_gemini(comment_content=comment_content)

    data["comment_blocked"] = need_to_block

    if need_to_block:
        data["comment_blocked_at"] = datetime.datetime.utcnow()

    comment.update(db, **data)

    if need_to_block:
        return JSONResponse(status_code=403,
                            content={"Error": "Comment contains prohibited content. Comment was blocked"})

    return CommentResponse(**comment.to_dict())


@router.delete("/comment/{comment_id}")
async def delete_comment(comment_id: int, db=Depends(get_db)):
    '''
    Delete comment by comment id.
    :param comment_id: comment id in database
    :param db: db session
    :return: Response with status code 200 or JSONResponse with error if comment not exists or is blocked
    '''

    comment = Comment.get_comment_by_id(db, comment_id)

    if not comment:
        return JSONResponse(status_code=404, content={"Not Found": "Comment with this id not found"})
    if comment.comment_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Comment is blocked"})

    db.delete(comment)
    db.commit()

    return Response(status_code=200)


@router.get("/comments/{user_id}", response_model=List[CommentResponse])
async def get_user_comments(user_id: int, db=Depends(get_db)):
    '''
    Get all comments by user id.
    :param user_id: user id in database
    :param db: db session
    :return: List of CommentResponse with user's comments
    '''

    user_comments = Comment.get_user_comments(db, user_id)
    result = [CommentResponse(**comment.to_dict()) for comment in user_comments]

    return result


@router.get("/comments/{post_id}", response_model=List[CommentResponse])
async def get_comments_for_posts(post_id: int, db=Depends(get_db)):
    '''
    Get all comments for a specific post by post id.
    :param post_id: post id in database
    :param db: db session
    :return: List of CommentResponse with comments for the post
    '''

    comments = Comment.get_post_comments(db, post_id)
    result = [CommentResponse(**comment.to_dict()) for comment in comments]

    return result
