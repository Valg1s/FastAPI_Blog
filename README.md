# FastAPI_Blog

## Content
- [Description](#description)
- [Installation](#installation)
- [Run project](#run-project)
- [Tests](#tests)
- [API Endpoints](#api-endpoints)

## Description

Time: 12h

## Installation

For download project:

`git clone https://github.com/Valg1s/FastAPI_Blog.git`

After that, you need create a virtual environment and download modulers from '__requirements.txt__'

```
cd Path/To/Folder/FastAPI_Blog

python -m venv venv

venv/Scripts/activate

pip install -r requirements.txt
```
_This code for Windows OS. If you have another, please read documantation for python-venv for your OS_

In project folder(FastAPI_Blog) please create '__.env__' file with stucture:

```
# you can take from jwt documentation or FastAPI + jwt documentation
SECRET_KEY=""

# can be HS256
ALGORITHM=""

# can be 30
ACCESS_TOKEN_EXPIRE_MINUTES=""

# your Gemini API key
GEMINI_API_KEY="" 
```

After this steps, you can run project

## Run project

For run progect, you need use this commands:

```
cd Path/To/Folder/FastAPI_Blog

uvicorn main:app --reload
```

After that, you can go on Swagger UI page for tests http://127.0.0.1:8000/docs

## Tests

For tests, you need use this commands:

```
cd Path/To/Folder/FastAPI_Blog

pytest
```

## Api endpoints

- Registration:
  POST /registration/

  Creates a new user if the user does not already exist, or returns an error.

  Request Body:

    - username: The username of the new user.
    - password: The password for the new user.

  Response:

    - Status: 201 Created on successful user creation.
    - Exception: HTTPException with status code 400 and header {"Cannot create": "User with this name already exists"} if the user already exists.

  Example request:

  `curl -X POST "http://localhost:8000/registration/" -H "Content-Type: application/json" -d '{"username": "newuser", "password": "newpassword"}'`

- Login:
   POST /login/

  Logs in a user by username and password. Returns a token.

  Request Body:

    - username: The username of the user.
    - password: The password of the user.

  Response:

    - Token: Returns a token if the user is authenticated.
    - Exception: HTTPException with status code 401 and detail "Incorrect username or password" if the username or password is incorrect.

  Example request:

  `curl -X POST "http://localhost:8000/login/" -d "username=user&password=pass" -H "Content-Type: application/x-www-form-urlencoded"`

- Post Endpoints:
  GET /post/{post_id}

  Get a post by its ID.

  Parameters:

    - post_id: The ID of the post.

  Response:

    - PostResponse: Returns the post data.
    - Exception: JSONResponse with status code 404 if the post is not found.
    - Exception: JSONResponse with status code 406 if the post is blocked.

  Example request:

  `curl -X GET "http://localhost:8000/post/1"`

  POST /post/

  Create a new post from user data. Checks if the post contains prohibited content before creating it.

  Request Body:

    - post_title: The title of the post.
    - post_content: The content of the post.
    - post_auto_answer: Boolean indicating if auto answer is enabled.
    - post_delay: Optional delay time for the post.

  Response:

    - PostResponse: Returns the created post data.
    - Exception: JSONResponse with status code 403 if the post contains prohibited content.
    - Exception: JSONResponse with status code 500 if there are problems with Gemini.

  Example request:

  `curl -X POST "http://localhost:8000/post/" -H "Content-Type: application/json" -d '{"post_title": "My Post", "post_content": "This is the content", "post_auto_answer": true, "post_delay": "00:10:00"}'`

  PUT /post/{post_id}

  Update a post by its ID.

  Parameters:

    - post_id: The ID of the post.

  Request Body:

    - post_title: The updated title of the post (optional).
    - post_content: The updated content of the post (optional).
    - post_auto_answer: Updated boolean indicating if auto answer is enabled (optional).
    - post_delay: Updated delay time for the post (optional).

  Response:

    - PostResponse: Returns the updated post data.
    - Exception: JSONResponse with status code 404 if the post is not found.
    - Exception: JSONResponse with status code 406 if the post is blocked.
    - Exception: JSONResponse with status code 403 if the updated post contains prohibited content.

  Example request:

  `curl -X PUT "http://localhost:8000/post/1" -H "Content-Type: application/json" -d '{"post_title": "Updated Post", "post_content": "Updated content"}'`

  DELETE /post/{post_id}

  Delete a post by its ID.

  Parameters:

    - post_id: The ID of the post.

  Response:

    - Status: 200 OK on successful deletion.
    - Exception: JSONResponse with status code 404 if the post is not found.
    - Exception: JSONResponse with status code 406 if the post is blocked.

  Example request:

  `curl -X DELETE "http://localhost:8000/post/1"`

  GET /posts/{user_id}

  Get all posts by a user ID.

  Parameters:

    - user_id: The ID of the user.

  Response:

    - List[PostResponse]: Returns a list of the user's posts.

  Example request:

  `curl -X GET "http://localhost:8000/posts/1"`

  GET /posts/

  Get all posts.

  Response:

    - List[PostResponse]: Returns a list of all posts.

  Example request:

  `curl -X GET "http://localhost:8000/posts/"`

- Comment Endpoints
  GET /comment/{comment_id}

  Get a comment by its ID.

  Parameters:

    - comment_id: The ID of the comment.

  Response:

    - CommentResponse: Returns the comment data.
    - Exception: JSONResponse with status code 404 if the comment is not found.
    - Exception: JSONResponse with status code 406 if the comment is blocked.

  Example request:

  `curl -X GET "http://localhost:8000/comment/1"`

  POST /comment/

  Create a new comment from user data. Checks if the comment contains prohibited content before creating it.

  Request Body:

    - post_id: The ID of the associated post.
    - comment_content: The content of the comment.

  Response:

    - CommentResponse: Returns the created comment data.
    - Exception: JSONResponse with status code 403 if the comment contains prohibited content.
    - Exception: JSONResponse with status code 500 if there are problems with Gemini.

  Example request:

  `curl -X POST "http://localhost:8000/comment/" -H "Content-Type: application/json" -d '{"post_id": 1, "comment_content": "This is a comment"}'`

  PUT /comment/{comment_id}

  Update a comment by its ID.

  Parameters:

    - comment_id: The ID of the comment.

  Request Body:

    - comment_content: The updated content of the comment.

  Response:

    - CommentResponse: Returns the updated comment data.
    - Exception: JSONResponse with status code 404 if the comment is not found.
    - Exception: JSONResponse with status code 406 if the comment is blocked.
    - Exception: JSONResponse with status code 403 if the updated comment contains prohibited content.

  Example request:

  `curl -X PUT "http://localhost:8000/comment/1" -H "Content-Type: application/json" -d '{"comment_content": "Updated comment"}'`

  DELETE /comment/{comment_id}

  Delete a comment by its ID.

  Parameters:

    - comment_id: The ID of the comment.

  Response:

    - Status: 200 OK on successful deletion.
    - Exception: JSONResponse with status code 404 if the comment is not found.
    - Exception: JSONResponse with status code 406 if the comment is blocked.

  Example request:

  `curl -X DELETE "http://localhost:8000/comment/1"`

  GET /comments/{user_id}

  Get all comments by a user ID.

  Parameters:

    - user_id: The ID of the user.

  Response:

    - List[CommentResponse]: Returns a list of the user's comments.

  Example request:

  `curl -X GET "http://localhost:8000/comments/1"`

  GET /comments/{post_id}

  Get all comments for a specific post by post ID.

  Parameters:

    - post_id: The ID of the post.

  Response:

    - List[CommentResponse]: Returns a list of the comments for the post.

  Example request:

  `curl -X GET "http://localhost:8000/comments/1"`

  - Reply Endpoints
  GET /reply/{reply_id}

  Get a reply by its ID.

  Parameters:

    - reply_id: The ID of the reply.

  Response:

    - ReplyResponse: Returns the reply data.
    - Exception: JSONResponse with status code 404 if the reply is not found.
    - Exception: JSONResponse with status code 406 if the reply is blocked.

  Example request:

  `curl -X GET "http://localhost:8000/reply/1"`

  POST /reply/

  Create a new reply from user data. Checks if the reply contains prohibited content before creating it.

  Request Body:

    - comment_id: The ID of the associated comment.
    - reply_content: The content of the reply.

  Response:

    - ReplyResponse: Returns the created reply data.
    - Exception: JSONResponse with status code 403 if the reply contains prohibited content.
    - Exception: JSONResponse with status code 500 if there are problems with Gemini.

  Example request:

  `curl -X POST "http://localhost:8000/reply/" -H "Content-Type: application/json" -d '{"comment_id": 1, "reply_content": "This is a reply"}'`

  PUT /reply/{reply_id}

  Update a reply by its ID.

  Parameters:

    - reply_id: The ID of the reply.

  Request Body:

    - reply_content: The updated content of the reply.

  Response:

    - ReplyResponse: Returns the updated reply data.
    - Exception: JSONResponse with status code 404 if the reply is not found.
    - Exception: JSONResponse with status code 406 if the reply is blocked.
    - Exception: JSONResponse with status code 403 if the updated reply contains prohibited content.

  Example request:

  `curl -X PUT "http://localhost:8000/reply/1" -H "Content-Type: application/json" -d '{"reply_content": "Updated reply"}'`

  DELETE /reply/{reply_id}

  Delete a reply by its ID.

  Parameters:

    - reply_id: The ID of the reply.

  Response:

    - Status: 200 OK on successful deletion.
    - Exception: JSONResponse with status code 404 if the reply is not found.
    - Exception: JSONResponse with status code 406 if the reply is blocked.

  Example request:

  `curl -X DELETE "http://localhost:8000/reply/1"`

  GET /replies/{comment_id}

  Get all replies for a specific comment by comment ID.

  Parameters:

    - comment_id: The ID of the comment.

  Response:

    - List[ReplyResponse]: Returns a list of the replies for the comment.

  Example request:

  curl -X GET "http://localhost:8000/replies/1"
