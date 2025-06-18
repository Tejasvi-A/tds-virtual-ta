import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import time, json
from datetime import datetime, timezone  # ✅ updated

CATEGORY_URL_TEMPLATE = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb.json?page={}"
TOPIC_JSON_URL = "https://discourse.onlinedegree.iitm.ac.in/t/{}.json"


START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
END_DATE   = datetime(2025, 4, 14, tzinfo=timezone.utc)

MAX_PAGES = 50  # ✅ Limit to first 50 pages

def is_within_range(date_str):
    dt = parser.parse(date_str)
    return START_DATE <= dt <= END_DATE

options = uc.ChromeOptions()
options.headless = False  # Let user manually login
driver = uc.Chrome(options=options)

# Prompt user to log in
print("Opening browser. Please log in to Discourse.")
driver.get("https://discourse.onlinedegree.iitm.ac.in")
input("After logging in, press Enter to continue...")

all_topics = []
page = 0

# 🌀 Paginate until empty page or max page
while page < MAX_PAGES:
    print(f"Fetching page {page}...")
    driver.get(CATEGORY_URL_TEMPLATE.format(page))
    try:
        pre = driver.find_element("tag name", "pre")
        category_data = json.loads(pre.text)
        topics = category_data["topic_list"]["topics"]
        if not topics:
            print("No more topics on this page.")
            break
        all_topics.extend(topics)
        page += 1
        time.sleep(0.5)
    except Exception as e:
        print("Failed to fetch or parse page:", e)
        break

print(f"✅ Total topics fetched (max {MAX_PAGES} pages): {len(all_topics)}")

# Filter + scrape topic content
filtered = []
for topic in all_topics:
    topic_id = topic["id"]
    driver.get(TOPIC_JSON_URL.format(topic_id))
    try:
        pre = driver.find_element("tag name", "pre")
        topic_data = json.loads(pre.text)
        created_at = topic_data["created_at"]
        print(f"{topic_id} | {topic_data['title']} | {created_at}")
        if is_within_range(created_at):
            posts = [BeautifulSoup(p["cooked"], "html.parser").get_text() for p in topic_data["post_stream"]["posts"]]
            filtered.append({
                "id": topic_id,
                "title": topic_data["title"],
                "created_at": created_at,
                "posts": posts
            })
        time.sleep(0.5)
    except Exception as e:
        print(f"Error fetching topic {topic_id}: {e}")
        continue

# Save
with open("tds_kb_topics_jan_to_apr_2025.json", "w", encoding="utf-8") as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print(f"🎉 Done! Saved {len(filtered)} topics between Jan 1 and Apr 14, 2025.")
try:
    driver.quit()
except:
    pass
