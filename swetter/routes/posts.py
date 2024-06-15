import datetime
from typing import List

from fastapi import APIRouter, Response, Depends
from fastapi.responses import JSONResponse

from swetter.models import Post
from swetter.schem import PostCreateRequest, PostUpdateRequest, PostResponse
from swetter.utils.deps import get_current_user
from swetter.utils.deps import get_db
from swetter.utils.gemini import get_data_from_gemini

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/post/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db=Depends(get_db)):
    '''
    Get post by post id.
    :param post_id: post id in database
    :param db: db session
    :return: PostResponse with post data or JSONResponse with error if post not exists
    '''

    post = Post.get_post_by_id(db, post_id)

    if not post:
        return JSONResponse(status_code=404, content={"Not Found": "Post with this id not found"})
    if post.post_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Post is blocked"})

    return PostResponse(**post.to_dict())


@router.post("/post/", response_model=PostResponse)
async def create_post(form_data: PostCreateRequest, db=Depends(get_db),
                      current_user=Depends(get_current_user)):
    '''
    Create post from user data. Before creating, check if post contains prohibited content.
    :param form_data: post title, post content and options for auto answer
    :param db: db session
    :param current_user: user who sends the request
    :return: PostResponse with post data or JSONResponse with error if post contains prohibited content
    or problems with Gemini
    '''

    data = form_data.dict()
    data["user_id"] = current_user.user_id

    need_to_block = get_data_from_gemini(post_title=data['post_title'], post_content=data['post_content'])

    if need_to_block is None:
        return JSONResponse(status_code=500, content={"Error": "Please, try again later"})

    data["post_blocked"] = need_to_block

    if need_to_block:
        data["post_blocked_at"] = datetime.datetime.utcnow()

    new_post = Post.create_post(db, **data)

    if need_to_block:
        return JSONResponse(status_code=403, content={"Error": "Post contains prohibited content. Post was blocked"})

    return PostResponse(**new_post.to_dict())


@router.put("/post/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, form_data: PostUpdateRequest, db=Depends(get_db)):
    '''
    Update post by post id.
    :param post_id: post id in database
    :param form_data: data to update the post
    :param db: db session
    :return: PostResponse with updated post data or JSONResponse with error if post not exists or is blocked
    '''

    post = Post.get_post_by_id(db, post_id)

    if not post:
        return JSONResponse(status_code=404, content={"Not Found": "Post with this id not found"})
    if post.post_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Post is blocked"})

    data = form_data.dict()
    post_title = data.get('post_title', None)
    post_content = data.get('post_content', None)

    need_to_block = get_data_from_gemini(post_title=post_title, post_content=post_content)

    data["post_blocked"] = need_to_block

    if need_to_block:
        data["post_blocked_at"] = datetime.datetime.utcnow()

    post.update(db, **data)

    if need_to_block:
        return JSONResponse(status_code=403, content={"Error": "Post contains prohibited content. Post was blocked"})

    return PostResponse(**post.to_dict())


@router.delete("/post/{post_id}")
async def delete_post(post_id: int, db=Depends(get_db)):
    '''
    Delete post by post id.
    :param post_id: post id in database
    :param db: db session
    :return: Response with status code 200 or JSONResponse with error if post not exists or is blocked
    '''

    post = Post.get_post_by_id(db, post_id)

    if not post:
        return JSONResponse(status_code=404, content={"Not Found": "Post with this id not found"})
    if post.post_blocked:
        return JSONResponse(status_code=406, content={"Blocked": "Post is blocked"})

    db.delete(post)
    db.commit()

    return Response(status_code=200)


@router.get("/posts/{user_id}", response_model=List[PostResponse])
async def get_user_posts(user_id: int, db=Depends(get_db)):
    '''
    Get all posts by user id.
    :param user_id: user id in database
    :param db: db session
    :return: List of PostResponse with user's posts
    '''

    user_posts = Post.get_user_posts(db, user_id)
    result = [PostResponse(**post.to_dict()) for post in user_posts]

    return result


@router.get("/posts/", response_model=List[PostResponse])
async def get_all_posts(db=Depends(get_db)):
    '''
    Get all posts.
    :param db: db session
    :return: List of PostResponse with all posts
    '''

    posts = Post.get_all_posts(db)
    result = [PostResponse(**post.to_dict()) for post in posts]

    return result
