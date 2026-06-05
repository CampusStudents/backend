# parse_russiaedu.py
import csv
import json
import re
import time
from dataclasses import asdict, dataclass
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://russiaedu.ru"
START_URL = f"{BASE_URL}/vuz/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; university-parser/1.0)",
    "Accept-Language": "ru,en;q=0.8",
}

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1
MIN_SHORT_NAME_LENGTH = 2
MAX_SHORT_NAME_LENGTH = 20
REGION_TITLE_PARTS_COUNT = 2

REGION_CODES = [
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38", "39", "40",
    "41", "42", "43", "44", "45", "46", "47", "48", "49", "50",
    "51", "52", "53", "54", "55", "56", "57", "58", "59", "60",
    "61", "62", "63", "64", "65", "66", "67", "68", "69", "70",
    "71", "72", "73", "74", "75", "76", "77", "78", "79", "82",
    "83", "86", "87", "89", "92",
]


@dataclass
class University:
    name: str
    short_name: str | None
    city: str | None
    region: str | None
    url: str


def get_soup(url: str) -> BeautifulSoup:
    resp = request_with_retries("get", url, headers=HEADERS, timeout=30)
    return BeautifulSoup(resp.text, "html.parser")


def post_json(url: str, data: dict[str, str | int]) -> dict:
    headers = {
        **HEADERS,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }
    resp = request_with_retries("post", url, headers=headers, data=data, timeout=30)
    return resp.json()


def request_with_retries(method: str, url: str, **kwargs) -> requests.Response:
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
        except requests.RequestException as exc:
            last_error = exc
            if attempt == MAX_RETRIES:
                break
            time.sleep(RETRY_DELAY_SECONDS * attempt)
        else:
            return resp

    assert last_error is not None
    raise last_error


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    clean_url = urlunparse(parsed._replace(query="", fragment=""))
    return clean_url.rstrip("/") + "/"


def extract_short_name(name: str) -> str | None:
    if "," in name:
        first = name.split(",", 1)[0].strip()
        if MIN_SHORT_NAME_LENGTH <= len(first) <= MAX_SHORT_NAME_LENGTH:
            return first
    return None


def extract_city(text: str) -> str | None:
    patterns = [
        r"\bг\.\s*([А-ЯЁа-яё\-\s]+)",
        r"\bгород\s+([А-ЯЁа-яё\-\s]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            city = match.group(1)
            city = re.split(r"[,.;\n]", city)[0]
            return clean_text(city)

    return None


def extract_region_name(soup: BeautifulSoup) -> str | None:
    title = clean_text(soup.title.text if soup.title else None)
    if title and "|" in title:
        parts = [part.strip() for part in title.split("|")]
        if len(parts) >= REGION_TITLE_PARTS_COUNT:
            return clean_text(parts[1])
    return None


def extract_search_provider(soup: BeautifulSoup, page_url: str) -> str | None:
    catalog = soup.select_one("#js-catalog[data-search-provider]")
    if not catalog:
        return None

    provider = catalog.get("data-search-provider")
    if not provider:
        return None

    return urljoin(page_url, provider)


def collect_university_links_from_api(provider_url: str) -> set[str]:
    links = set()
    page_number = 1
    per_page = 500

    while True:
        data = post_json(
            provider_url,
            {
                "pp": per_page,
                "pageNumber": page_number,
            },
        )
        items = data.get("rating") or []

        for item in items:
            link = item.get("link")
            if link:
                links.add(normalize_url(urljoin(BASE_URL, link)))

        total_count = int(data.get("totalCount") or len(links))
        if not items or len(links) >= total_count:
            break

        page_number += 1

    return links


def collect_university_links(region_code: str) -> tuple[str | None, set[str]]:
    url = f"{BASE_URL}/vuz/{region_code}"
    soup = get_soup(url)
    region = extract_region_name(soup)

    search_provider = extract_search_provider(soup, url)
    if search_provider:
        return region, collect_university_links_from_api(search_provider)

    links = set()
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        full_url = normalize_url(urljoin(BASE_URL, href))

        if re.search(r"/vuz/\d{2}/[^/]+/?$", full_url):
            links.add(full_url)

    return region, links


def parse_university_page(url: str, region: str | None) -> University | None:
    soup = get_soup(url)

    title = clean_text(soup.title.text if soup.title else None)
    name = title.split("|")[0].strip() if title else None

    h1 = soup.find("h1")
    if not name and h1:
        name = clean_text(h1.get_text(" "))

    if not name:
        return None

    page_text = clean_text(soup.get_text(" ")) or ""

    city = extract_city(page_text)
    short_name = extract_short_name(name)

    return University(
        name=name,
        short_name=short_name,
        city=city,
        region=region,
        url=url,
    )


def save_json(items: list[University], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(x) for x in items], f, ensure_ascii=False, indent=2)


def save_csv(items: list[University], path: str) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "short_name", "city", "region", "url"],
        )
        writer.writeheader()
        for item in items:
            writer.writerow(asdict(item))


def main() -> None:
    all_links: dict[str, str | None] = {}

    print("Collecting university links...")

    for code in REGION_CODES:
        try:
            region, links = collect_university_links(code)
            print(f"{code}: {region or '-'} - {len(links)} links")

            for link in links:
                all_links[link] = region

            time.sleep(0.5)

        except Exception as e:
            print(f"Failed region {code}: {e}")

    print(f"Total unique links: {len(all_links)}")

    universities: list[University] = []

    for i, (url, region) in enumerate(all_links.items(), start=1):
        try:
            item = parse_university_page(url, region)
            if item:
                universities.append(item)
                print(f"[{i}/{len(all_links)}] {item.name}")

            time.sleep(0.5)

        except Exception as e:
            print(f"Failed university {url}: {e}")

    unique = {}
    for item in universities:
        key = (item.name.lower(), item.city or "", item.region or "")
        unique[key] = item

    result = list(unique.values())

    save_json(result, "universities_russiaedu.json")
    save_csv(result, "universities_russiaedu.csv")

    print(f"Saved {len(result)} universities")
    print("universities_russiaedu.json")
    print("universities_russiaedu.csv")


if __name__ == "__main__":
    main()
