import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


class QuoteScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.quotes_data = []

    def fetch_page(self, page_number):
        url = f"{self.base_url}/page/{page_number}/"
        print(f"[+] Fetching: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[-] Failed to retrieve page {page_number}")
            return None
        return response.text

    def parse_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        quote_blocks = soup.find_all("div", class_="quote")
        if not quote_blocks:
            return False  # No quotes = last page

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

    def scrape_all(self, max_pages=10):
        for page in range(1, max_pages + 1):
            html = self.fetch_page(page)
            if html is None or not self.parse_page(html):
                print("[*] No more quotes found or failed to fetch.")
                break
            time.sleep(0.5)  # Be nice to servers

    def save_to_csv(self, filename="quotes.csv"):
        df = pd.DataFrame(self.quotes_data)
        df.to_csv(filename, index=False)
        print(f"[✔] Saved {len(df)} quotes to '{filename}'.")


if __name__ == "__main__":
    scraper = QuoteScraper("https://quotes.toscrape.com")
    scraper.scrape_all(max_pages=5)
    scraper.save_to_csv()
