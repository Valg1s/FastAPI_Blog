import os.path
from fastapi import FastAPI

from swetter.database.db import engine, Base
from swetter.database.fill_db import populate_db
from swetter.routes import router
from swetter import scheduler

database_exists = os.path.exists("blog.db")
Base.metadata.create_all(bind=engine)

if not database_exists:
    populate_db()

app = FastAPI()

app.include_router(router)


scheduler.start()
