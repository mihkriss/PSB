import re
import requests
from bs4 import BeautifulSoup
import ujson
from pymongo import MongoClient
import time
import threading

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

URL_TEMPLATE = "https://www.banki.ru/services/responses/bank/promsvyazbank/?page={page_index}&is_countable=on"

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["comments_database"]
collection = db["comments_1"]

def clean_comment_text(text: str) -> str:
    return re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9\s.,?!\-:;()]+', '', text)


def get_comments(page_index: int):
    url = URL_TEMPLATE.format(page_index=page_index)

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_index}: {e}")
        return []

    # Parse the HTML page
    soup = BeautifulSoup(response.text, "html.parser")

    # Look for the JSON data embedded in a script tag
    script_tag = soup.find("script", {"type": "application/ld+json"})

    if script_tag:
        try:
            data = script_tag.string.strip().replace('&quot;', '').replace('&lt;p&gt;', '').replace('&lt;/p&gt;',
                                                                                                    '').replace(
                '\u00A0', '')
            data = re.sub(r'\\[^"\\/bfnrtu]', '', data)
            data = ujson.loads(data)

            reviews = data.get('review', [])
            if not reviews:
                print(f"No reviews found on page {page_index}.")
                return []

            # Extract the required fields
            result = []
            for record in reviews:
                comment = clean_comment_text(record.get('description', ''))
                name = clean_comment_text(record.get('name', ''))
                date_published = record.get('datePublished', 'N/A')
                best_rating = record.get('reviewRating', {}).get('ratingValue', 'N/A')
                result.append({
                    "name": name,
                    "text_comment": comment,
                    "date": date_published,
                    "marks": best_rating
                })

            return result

        except (ujson.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON on page {page_index}: {e}")
            return []
    else:
        print(f"Script tag with JSON not found on page {page_index}.")
        return []

def save_comments_to_db(comments):
    if comments:
        for comment in comments:
            if not collection.find_one({"text_comment": comment["text_comment"], "date": comment["date"], "name": comment["name"]}):
                collection.insert_one(comment)
        print(f"Inserted comments into the database.")

def scrape_and_update():
    page_index = 1
    while True:
        comments = get_comments(page_index)
        if not comments:
            break
        save_comments_to_db(comments)
        page_index += 1
    print("Database updated successfully.")

def schedule_task(interval_minutes):
    while True:
        print("Starting scraping task...")
        scrape_and_update()
        print(f"Task completed. Waiting for {interval_minutes} minutes.")
        time.sleep(interval_minutes * 60)
def main():
    interval_minutes = 10
    threading.Thread(target=schedule_task, args=(interval_minutes,), daemon=True).start()
    print(f"Scraper is running. Updates will happen every {interval_minutes} minutes.")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
