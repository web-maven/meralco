import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://company.meralco.com.ph"
LIST_URL = "https://company.meralco.com.ph/news-and-advisories/maintenance-schedule"


def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def scrape_list():
    items = []
    seen_urls = set()

    for page in range(0, 5):
        url = f"{LIST_URL}?date_range_filter=&field_service_maintenance_loc_target_id=All&page={page}"
        html = get_page(url)
        soup = BeautifulSoup(html, "html.parser")

        links = soup.find_all("a", href=True)

        for link in links:
            href = link["href"]

            if "/news-and-advisories/maintenance-schedule/" not in href:
                continue

            full_url = urljoin(BASE_URL, href)

            if full_url in seen_urls:
                continue

            title = clean_text(link.get_text())

            if not title or title.lower() in ["read more", "view all maintenance schedules"]:
                continue

            seen_urls.add(full_url)

            items.append({
                "title": title,
                "url": full_url
            })

    return items


def scrape_detail(item):
    html = get_page(item["url"])
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h3")
    title = clean_text(title_tag.get_text()) if title_tag else item["title"]

    text = clean_text(soup.get_text(" "))

    location = ""
    time_text = ""
    areas = ""
    reason = ""

    if title:
        date = title.split(" - ")[0]
    else:
        date = ""

    title_index = text.find(title)
    detail_text = text[title_index + len(title):] if title_index != -1 else text

    reason_match = re.search(r"REASON:\s*(.*?)(View all Maintenance Schedules|Thanks for staying connected|$)", detail_text, re.I)
    if reason_match:
        reason = clean_text(reason_match.group(1))

    time_match = re.search(r"(BETWEEN .*?)(?=REASON:|View all Maintenance Schedules|$)", detail_text, re.I)
    if time_match:
        full_details = clean_text(time_match.group(1))

        parts = re.split(r"\s{2,}", full_details)
        time_text = full_details

        if "REASON:" in time_text:
            time_text = time_text.split("REASON:")[0].strip()

        areas = time_text

    location_match = re.search(rf"{re.escape(title)}\s+([A-Za-z ]+?)\s+Facebook", text)
    if location_match:
        location = clean_text(location_match.group(1))

    return {
        "title": title,
        "date": date,
        "location": location,
        "details": areas,
        "reason": reason,
        "url": item["url"]
    }


def main():
    list_items = scrape_list()
    detailed_items = []

    for item in list_items[:30]:
        try:
            detailed_items.append(scrape_detail(item))
        except Exception as error:
            print(f"Skipped {item['url']}: {error}")

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": LIST_URL,
        "items": detailed_items
    }

    with open("maintenance.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print(f"Saved {len(detailed_items)} Meralco maintenance schedules.")


if __name__ == "__main__":
    main()
