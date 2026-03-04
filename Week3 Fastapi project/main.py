from fastapi import FastAPI
from database import engine
from models import user, project
from routs import user as user_router
from routs import project as project_router

#
user.Base.metadata.create_all(bind=engine)
project.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Project with PostgreSQL")


app.include_router(user_router.router)
app.include_router(project_router.router)

@app.get("/")
def root():
    return {"message": "Hello World! API is running."}