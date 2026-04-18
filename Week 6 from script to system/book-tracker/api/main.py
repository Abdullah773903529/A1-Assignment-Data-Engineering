from fastapi import FastAPI, HTTPException
from db.database import SessionLocal
from db.models import Book
from sqlalchemy import func

app = FastAPI(
    title="Book Tracker API",
    description="API for scraped books data",
    version="1.0.0"
)


def get_db():
    return SessionLocal()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/books")
def get_books():
    db = get_db()
    books = db.query(Book).all()
    db.close()
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    db = get_db()
    book = db.query(Book).filter(Book.id == book_id).first()
    db.close()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@app.get("/stats")
def get_stats():
    db = get_db()

    total_books = db.query(Book).count()
    avg_price = db.query(func.avg(Book.price)).scalar()

    db.close()

    return {
        "total_books": total_books,
        "average_price": round(avg_price, 2) if avg_price else 0
    }

