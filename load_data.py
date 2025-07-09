import logging
import re
from typing import Any, Dict, List, Tuple

import pandas as pd
import psycopg

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def clean_price(price: str) -> float:
    """Convert price from '₹123' format to float."""
    if price.strip() == "" or price.lower() == "nan":
        return 0.0
    try:
        return float(re.sub(r"[^\d.]", "", price))
    except ValueError:
        raise ValueError(f"Price {price} is not a number")


def clean_percentage(percentage: str) -> int:
    """Convert percentage from '15%' format to integer."""
    if percentage.strip() == "" or percentage.lower() == "nan":
        return 0
    try:
        return int(re.sub(r"[^\d]", "", percentage))
    except ValueError:
        raise ValueError(f"Percentage {percentage} is not a number")


def clean_rating_count(count: str) -> int:
    """Convert rating count from '1,234' format to integer."""
    if count.strip() == "" or count.lower() == "nan":
        return 0
    try:
        return int(re.sub(r"[^\d]", "", count))
    except ValueError:
        raise ValueError(f"Rating count {count} is not a number")


def clean_rating(rating: Any) -> float | None:
    """Clean and convert rating to float, handling non-numeric values."""
    if pd.isna(rating):
        return None

    rating_str = str(rating).strip()
    if not rating_str or rating_str.lower() == "nan":
        return None

    cleaned_rating = re.sub(r"[^\d.]", "", rating_str)
    if not cleaned_rating:
        return None

    try:
        return float(cleaned_rating)
    except ValueError:
        # Handles cases like '1.2.3' which become invalid
        return None


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
            "rating": clean_rating(row["rating"]),
            "rating_count": clean_rating_count(str(row["rating_count"])),
            "about_product": row["about_product"],
            "img_link": row["img_link"],
            "product_link": row["product_link"],
        }
        products.append(product)

        # Process review data if available
        if bool(pd.notna(row["review_id"])):
            review = {
                "review_id": row["review_id"],
                "product_id": row["product_id"],
                "user_id": row["user_id"],
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
            try:
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
            except psycopg.errors.StringDataRightTruncation as e:
                logging.error(
                    f"Error inserting review due to data truncation: {review}"
                )
                for key, value in review.items():
                    if isinstance(value, str):
                        logging.error(f"Length of '{key}': {len(value)}")
                raise e


def main():
    import os

    import dotenv
    from pydantic import PostgresDsn

    dotenv.load_dotenv()

    # Database connection parameters
    db_params = PostgresDsn.build(
        scheme="postgresql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        path=os.getenv("DB_NAME"),
    ).unicode_string()

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
        with psycopg.connect(db_params) as conn:
            logging.info("Inserting data...")
            try:
                insert_data(conn, products, reviews)
                conn.commit()
                logging.info("Data insertion completed successfully")
            except Exception as e:
                logging.exception(f"An error occurred: {str(e)}")
                conn.rollback()
                raise
            finally:
                conn.close()

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
