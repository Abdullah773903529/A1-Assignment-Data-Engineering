import requests
from bs4 import BeautifulSoup
import re
from db.database import SessionLocal
from db.models import Book

session = SessionLocal()

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

def clean_price(price_text):
    cleaned = re.sub(r"[^\d.]", "", price_text)
    return float(cleaned)

print("Starting scraping...")

for page in range(1, 4):
    url = BASE_URL.format(page)
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    for b in books:
        title = b.h3.a["title"]

        price_text = b.find("p", class_="price_color").text
        price = clean_price(price_text)

        rating_class = b.p["class"][1]
        rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }.get(rating_class, 0)

        book = Book(
            title=title,
            price=price,
            rating=rating
        )

        session.add(book)

session.commit()
session.close()

print("Done → Data inserted into PostgreSQL")