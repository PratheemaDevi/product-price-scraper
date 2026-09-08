# Automated Product Price Tracker

A Python scraper that monitors product listings on an e-commerce-style
site, cleans the data, and delivers it as a spreadsheet — automatically,
on a schedule if needed.

## What it does

1. Scrapes every page of a product listing (handles pagination
   automatically, stopping based on actual page content rather than
   trusting a site's self-reported page count — a real inconsistency
   found and handled during development)
2. Cleans price data into proper numeric values using pandas
3. Saves results to a dated CSV file
4. Optionally emails the CSV as an attachment
5. Designed to run unattended via a scheduler (Windows Task Scheduler /
   cron) for daily automated monitoring

## Why this approach

Many real listing pages report inconsistent metadata (e.g. claiming
more pages exist than actually contain data). Rather than trusting a
page's self-reported total, this scraper loops until it actually
encounters an empty page — a more robust approach for real-world,
imperfect websites.

## Features

- **Defensive pagination** — stops based on real page content, not
  unreliable site metadata
- **Retry logic** — retries a failed page request before giving up
- **Clean numeric price data** — strips currency symbols/commas and
  converts to proper numbers for analysis
- **Optional automated email delivery** — send results straight to an
  inbox, ideal for scheduled daily runs
- **Logging** — all activity logged with timestamps to `scraper.log`
- **Schedulable** — built to run via Task Scheduler (Windows) or cron
  (Mac/Linux) with zero manual intervention after setup

## Usage

```bash
pip install requests beautifulsoup4 pandas

# Scrape and save to CSV only:
python product_price_tracker.py

# Scrape, save, and email results:
python product_price_tracker.py --email recipient@example.com --from-email you@gmail.com --app-password your16digitapppassword
```

## Example output (`products_2026-09-08.csv`)

| name | link | price | date_scraped |
|---|---|---|---|
| Box of Chocolate Candy | https://web-scraping.dev/product/1 | 24.99 | 2026-09-08 |
| Dark Red Energy Potion | https://web-scraping.dev/product/2 | 4.99 | 2026-09-08 |

## Scheduling for daily automated runs

On Windows, this can be wired into Task Scheduler to run daily,
including delivering results by email automatically — useful for price
monitoring, competitor tracking, or inventory watch use cases.

## Adapting this for your site

The scraping logic (`parse_products`) is the only part that's specific
to this particular site's HTML structure — everything else (retry
logic, pagination handling, CSV export, email delivery, scheduling) is
reusable as-is. Happy to adapt the selectors to your target website.
