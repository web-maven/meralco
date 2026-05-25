import json
from datetime import datetime, timezone

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": "https://company.meralco.com.ph/news-and-advisories/maintenance-schedule",
    "items": [
        {
            "title": "Test Meralco Maintenance Schedule",
            "date": "Sample date",
            "location": "Sample location",
            "url": "https://company.meralco.com.ph/news-and-advisories/maintenance-schedule"
        }
    ]
}

with open("maintenance.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)
