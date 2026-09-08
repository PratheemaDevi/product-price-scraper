"""
Automated Product Price Tracker
---------------------------------
Scrapes product listings (name, price, link) from a paginated e-commerce
site, cleans the price data, saves it to a dated CSV file, and optionally
emails the results.

Handles pagination defensively (stops based on actual page content, not
a site's self-reported page count, since these can be inconsistent).

Usage:
    python product_price_tracker.py
    python product_price_tracker.py --email your_email@gmail.com
"""

import sys
import time
import logging
import argparse
import smtplib
from datetime import date
from email.message import EmailMessage

import requests
import pandas as pd
from bs4 import BeautifulSoup

# ---- Configuration ----
BASE_URL = "https://web-scraping.dev/products"
MAX_RETRIES = 2
REQUEST_DELAY = 1  # seconds between page requests, to be polite to the server

# ---- Logging setup ----
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a URL and return its parsed HTML, retrying on failure."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            last_error = e
            logger.warning(f"Attempt {attempt} failed for {url}: {e}")
            time.sleep(1)
    raise last_error


def parse_products(soup: BeautifulSoup) -> list:
    """Extract product name, price, and link from a page's parsed HTML."""
    products = []
    for row in soup.select("div.row.product"):
        link_tag = row.select_one("h3.mb-0 a")
        price_tag = row.select_one("div.price")
        if not link_tag or not price_tag:
            continue
        products.append({
            "name": link_tag.text.strip(),
            "link": link_tag["href"],
            "price": price_tag.text.strip(),
            "date_scraped": date.today().strftime("%Y-%m-%d"),
        })
    return products


def scrape_all_pages(base_url: str = BASE_URL) -> pd.DataFrame:
    """Loop through every page of listings until an empty page is found."""
    all_products = []
    page = 1

    while True:
        url = f"{base_url}?page={page}"
        soup = fetch_page(url)
        products = parse_products(soup)

        if not products:
            logger.info(f"No products found on page {page}. Stopping.")
            break

        all_products.extend(products)
        logger.info(f"Page {page}: {len(products)} products scraped")
        page += 1
        time.sleep(REQUEST_DELAY)

    df = pd.DataFrame(all_products)
    if not df.empty:
        df["price"] = df["price"].str.replace(r"[^\d.]", "", regex=True).astype(float)
    return df


def save_to_csv(df: pd.DataFrame) -> str:
    """Save the DataFrame to a dated CSV file and return its filename."""
    filename = f"products_{date.today().strftime('%Y-%m-%d')}.csv"
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(df)} products to {filename}")
    return filename


def email_csv(filename: str, to_email: str, from_email: str, app_password: str):
    """Email the CSV file as an attachment using Gmail's SMTP server."""
    msg = EmailMessage()
    msg["Subject"] = f"Daily Product Scrape - {date.today().strftime('%Y-%m-%d')}"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content("Attached is today's scraped product data.")

    with open(filename, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="csv", filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)

    logger.info(f"Emailed {filename} to {to_email}")


def run(email_to: str = None, from_email: str = None, app_password: str = None):
    """Main entry point: scrape, clean, save, and optionally email results."""
    logger.info("Starting product scrape")
    df = scrape_all_pages()
    filename = save_to_csv(df)
    print(f"Saved {len(df)} products to {filename}")

    if email_to and from_email and app_password:
        email_csv(filename, email_to, from_email, app_password)
        print(f"Emailed results to {email_to}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape product listings and optionally email results.")
    parser.add_argument("--email", help="Recipient email address")
    parser.add_argument("--from-email", help="Sender Gmail address")
    parser.add_argument("--app-password", help="Gmail App Password (not your normal password)")
    args = parser.parse_args()

    run(args.email, args.from_email, args.app_password)
