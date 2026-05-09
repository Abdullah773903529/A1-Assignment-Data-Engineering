from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
from models import user, project
from routs import user as user_router
from routs import project as project_router
from routs import task as task_router

user.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Project with PostgreSQL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router.router)
app.include_router(project_router.router)
app.include_router(task_router.router)

@app.get("/")
def root():
    return {
        "message": "API is running",
        "docs": "/docs",
        "static_page": "/static/index.html"
    }