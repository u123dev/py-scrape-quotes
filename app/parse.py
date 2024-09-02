import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def next_page_url(page_soup: BeautifulSoup) -> int | None:
    page = page_soup.select_one(".next > a")
    if page is None:
        return None
    page = page.attrs["href"]
    return page


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    quote = Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )
    return quote


def get_qoutes(url: str) -> list[Quote]:

    quotes = []
    next_url = ""

    while next_url is not None:
        page = requests.get(urljoin(url, next_url)).content
        soup = BeautifulSoup(page, "html.parser")

        next_url = next_page_url(soup)

        qoutes_per_page = soup.select(".row > .col-md-8 .quote")
        quotes.extend([parse_single_quote(qoute) for qoute in qoutes_per_page])

    return quotes


def write_to_csv(quotes: list[Quote], output_file: str) -> None:
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    quotes = get_qoutes(BASE_URL)
    write_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
