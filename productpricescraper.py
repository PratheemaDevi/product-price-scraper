import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date
import smtplib
from email.message import EmailMessage
import os

os.chdir(r"C:\Users\pdthe\PyCharmMiscProject")

def scrape_products():
    all_data = []
    page = 1
    while True:
        url = f"https://web-scraping.dev/products?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.select("div.row.product")
        if not products:
            break
        for p in products:
            name = p.select_one("h3.mb-0 a").text.strip()
            link = p.select_one("h3.mb-0 a")["href"]
            price = p.select_one("div.price").text.strip()
            all_data.append({"name": name, "price": price, "link": link, "date_scraped": date.today()})
        page += 1

    df = pd.DataFrame(all_data)
    df["price"] = df["price"].str.replace(r"[^\d.]", "", regex=True).astype(float)
    filename = f"products_{date.today()}.csv"
    df.to_csv(filename, index=False)
    return filename

def email_csv(filename, to_email):
    msg = EmailMessage()
    msg["Subject"] = f"Daily Product Scrape - {date.today()}"
    msg["From"] = "pdtheema71@gmail.com"
    msg["To"] ="pdtheema71@gmail.com"
    msg.set_content("Attached is today's scraped product data.")

    with open(filename, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="csv", filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("pdtheema71@gmail.com", "sftnotffettfbanw")  # your app password, no spaces
        smtp.send_message(msg)

if __name__ == "__main__":
    file = scrape_products()
    email_csv(file, "pdtheema71@gmail.com")  # send to yourself first
    print(f"Done! Sent {file} to your inbox.")