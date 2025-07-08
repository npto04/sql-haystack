import logging
import re
from typing import Dict, List, Tuple

import pandas as pd
import psycopg

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def clean_price(price: str) -> float:
    """Convert price from '₹123' format to float."""
    if pd.isna(price):
        raise ValueError("Price is not a number")
    return float(re.sub(r"[^\d.]", "", str(price)))


def clean_percentage(percentage: str) -> int:
    """Convert percentage from '15%' format to integer."""
    if pd.isna(percentage):
        raise ValueError("Percentage is not a number")
    return int(re.sub(r"[^\d]", "", str(percentage)))


def clean_rating_count(count: str) -> int:
    """Convert rating count from '1,234' format to integer."""
    if pd.isna(count):
        raise ValueError("Rating count is not a number")
    return int(re.sub(r"[^\d]", "", str(count)))


def process_dataframe(df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
    """Process dataframe and return products and reviews data."""
    products = []
    reviews = []

    for _, row in df.iterrows():
        # Process product data
        product = {
            "product_id": row["product_id"],
            "product_name": str(row["product_name"]),
            "category": str(row["category"]),
            "discounted_price": clean_price(str(row["discounted_price"])),
            "actual_price": clean_price(str(row["actual_price"])),
            "discount_percentage": clean_percentage(str(row["discount_percentage"])),
            "rating": float(row["rating"]) if pd.notna(row["rating"]).item() else None,
            "rating_count": clean_rating_count(str(row["rating_count"])),
            "about_product": row["about_product"],
            "img_link": row["img_link"],
            "product_link": row["product_link"],
        }
        products.append(product)

        # Process review data if available
        if pd.notna(row["review_id"]).item():
            review = {
                "review_id": row["review_id"],
                "product_id": row["product_id"],
                "user_id": row["usplaer_id"],
                "user_name": row["user_name"],
                "review_title": row["review_title"],
                "review_content": row.get(
                    "review_content", None
                ),  # Some rows might not have review content
            }
            reviews.append(review)

    return products, reviews


def insert_data(conn: psycopg.Connection, products: List[Dict], reviews: List[Dict]):
    """Insert data into PostgreSQL database."""
    with conn.cursor() as cur:
        # Insert products
        for product in products:
            cur.execute(
                """
                INSERT INTO amazon_products (
                    product_id, product_name, category, discounted_price,
                    actual_price, discount_percentage, rating, rating_count,
                    about_product, img_link, product_link
                ) VALUES (
                    %(product_id)s, %(product_name)s, %(category)s, %(discounted_price)s,
                    %(actual_price)s, %(discount_percentage)s, %(rating)s, %(rating_count)s,
                    %(about_product)s, %(img_link)s, %(product_link)s
                ) ON CONFLICT (product_id) DO NOTHING
            """,
                product,
            )

        # Insert reviews
        for review in reviews:
            cur.execute(
                """
                INSERT INTO product_reviews (
                    review_id, product_id, user_id, user_name,
                    review_title, review_content
                ) VALUES (
                    %(review_id)s, %(product_id)s, %(user_id)s, %(user_name)s,
                    %(review_title)s, %(review_content)s
                ) ON CONFLICT (review_id) DO NOTHING
            """,
                review,
            )


def main():
    import os

    import dotenv

    dotenv.load_dotenv()
    # Database connection parameters
    db_params = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    try:
        # Read CSV file
        logging.info("Reading CSV file...")
        df = pd.read_csv("data/amazon.csv")
        logging.info(f"Read {len(df)} rows from CSV")

        # Process data
        logging.info("Processing data...")
        products, reviews = process_dataframe(df)
        logging.info(f"Processed {len(products)} products and {len(reviews)} reviews")

        # Connect to database and insert data
        logging.info("Connecting to database...")
        with psycopg.connect(**db_params) as conn:
            logging.info("Inserting data...")
            insert_data(conn, products, reviews)
            conn.commit()
            logging.info("Data insertion completed successfully")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
