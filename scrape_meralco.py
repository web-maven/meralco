import json
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://company.meralco.com.ph"
LIST_URL = "https://company.meralco.com.ph/news-and-advisories/maintenance-schedule"

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(LIST_URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

items = []
seen = set()

for link in soup.find_all("a", href=True):
    href = link["href"]

    if "/news-and-advisories/maintenance-schedule/" not in href:
        continue

    url = urljoin(BASE_URL, href)

    if url in seen:
        continue

    title = link.get_text(" ", strip=True)

    if not title or title.lower() == "read more":
        continue

    seen.add(url)

    detail = requests.get(url, headers=headers, timeout=30)
    detail.raise_for_status()

    detail_soup = BeautifulSoup(detail.text, "html.parser")
    text = detail_soup.get_text("\n", strip=True)

    location = ""
    h3 = detail_soup.find("h3")
    if h3:
        title = h3.get_text(" ", strip=True)
        next_text = h3.find_next(string=True)
        if next_text:
            location = str(next_text).strip()

    items.append({
        "title": title,
        "date": title.split(" - ")[0] if " - " in title else "",
        "location": location,
        "details": text,
        "url": url
    })

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": LIST_URL,
    "items": items[:20]
}

with open("maintenance.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print(f"Saved {len(items[:20])} schedules.")
