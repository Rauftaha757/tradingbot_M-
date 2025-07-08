import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import os


class QuoteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.quotes_data = []

    def fetch_page(self, page_number):
        url = f"{self.base_url}/page/{page_number}/"
        print(f"[+] Fetching: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.text

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        quote_blocks = soup.find_all("div", class_="quote")

        if not quote_blocks:
            return False

        for quote in quote_blocks:
            text = quote.find("span", class_="text").text.strip()
            author = quote.find("small", class_="author").text.strip()
            tags = [tag.text for tag in quote.find_all("a", class_="tag")]
            self.quotes_data.append({
                "quote": text,
                "author": author,
                "tags": ", ".join(tags)
            })
        return True

    def scrape_all(self):
        print("Scraping quotes from all pages...")
        page = 1
        while True:
            html = self.fetch_page(page)
            if html is None or not self.parse_page(html):
                break
            time.sleep(0.3)
            page += 1
        print(f"[✔] Scraped {len(self.quotes_data)} quotes.")

    def save_to_csv(self, filename="quotes.csv"):
        df = pd.DataFrame(self.quotes_data)
        df.to_csv(filename, index=False)
        print(f"[💾] Saved {len(df)} quotes to '{filename}'.")

    def save_to_json(self, filename="quotes.json"):
        df = pd.DataFrame(self.quotes_data)
        df.to_json(filename, orient="records", indent=2)
        print(f"[💾] Saved {len(df)} quotes to '{filename}'.")

    def get_random_quote(self):
        if not self.quotes_data:
            return None
        return random.choice(self.quotes_data)

    def search_by_author(self, name):
        results = [q for q in self.quotes_data if name.lower() in q['author'].lower()]
        return results

    def search_by_tag(self, tag):
        results = [q for q in self.quotes_data if tag.lower() in q['tags'].lower()]
        return results


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def display_quote(quote):
    print("\n" + "-"*60)
    print(f"\"{quote['quote']}\"\n\n— {quote['author']}")
    print(f"Tags: {quote['tags']}")
    print("-"*60 + "\n")


def main_menu(scraper):
    while True:
        print("\n====== Quote Scraper CLI ======")
        print("1. Show random quote")
        print("2. Search by author")
        print("3. Search by tag")
        print("4. Save quotes to CSV")
        print("5. Save quotes to JSON")
        print("6. Exit")
        choice = input("Select an option (1-6): ")

        if choice == "1":
            quote = scraper.get_random_quote()
            if quote:
                display_quote(quote)
            else:
                print("No quotes loaded.")

        elif choice == "2":
            author = input("Enter author name: ").strip()
            results = scraper.search_by_author(author)
            print(f"\nFound {len(results)} quotes.")
            for q in results:
                display_quote(q)

        elif choice == "3":
            tag = input("Enter tag keyword: ").strip()
            results = scraper.search_by_tag(tag)
            print(f"\nFound {len(results)} quotes.")
            for q in results:
                display_quote(q)

        elif choice == "4":
            scraper.save_to_csv()

        elif choice == "5":
            scraper.save_to_json()

        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    clear_console()
    scraper = QuoteScraper("https://quotes.toscrape.com")
    scraper.scrape_all()
    main_menu(scraper)
