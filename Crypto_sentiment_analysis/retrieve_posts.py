import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# === Configuration ===
THREADS = {
    203: "Wall Observer BTC/USD",
    2969: "BTC Escrow Service",
    178336: "DirectBet Sportsbook",
    1152261: "Bitcointalk Collectibles"
}
NUM_PAGES = 4  # pages to fetch per thread

# === Setup Selenium headless browser ===
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# === Scrape one thread ===
def scrape_thread(driver, thread_id, title, num_pages=1):
    posts = []
    for page in range(num_pages):
        url = f"https://bitcointalk.org/index.php?topic={thread_id}.{page * 20}"
        print(f"Scraping: {url}")
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        authors = soup.select("td.poster_info b")
        posts_data = soup.select("td.td_headerandpost")

        print(f"  Found {len(posts_data)} posts")

        for i, post_cell in enumerate(posts_data):
            try:
                author = authors[i].text.strip() if i < len(authors) else "unknown"

                # Timestamp
                timestamp_tag = post_cell.select_one("div.smalltext")
                timestamp = timestamp_tag.text.strip() if timestamp_tag else ""

                # Message
                message_tag = post_cell.select_one("div.post")
                message = message_tag.get_text(separator=" ").strip() if message_tag else ""

                posts.append({
                    "thread_id": thread_id,
                    "thread_title": title,
                    "author": author,
                    "timestamp": timestamp,
                    "message": message
                })
            except Exception as e:
                print(f"    Error parsing post {i}: {e}")
                continue

    return posts

# === Main logic ===
if __name__ == "__main__":
    driver = create_driver()
    all_posts = []

    for thread_id, title in THREADS.items():
        try:
            thread_posts = scrape_thread(driver, thread_id, title, NUM_PAGES)
            all_posts.extend(thread_posts)
        except Exception as e:
            print(f"Failed to scrape thread {thread_id}: {e}")

    driver.quit()

    # === Save to JSON ===
    output_file = "bitcointalk_posts.json"
    with open(output_file, "w") as f:
        json.dump(all_posts, f, indent=2)

    print(f"\nSaved {len(all_posts)} posts to {output_file}")

