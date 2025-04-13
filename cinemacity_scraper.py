from playwright.sync_api import sync_playwright, TimeoutError
from datetime import datetime
import json
import time

def scrape_today_movies():
    today = datetime.today().strftime("%Y-%m-%d")
    url = f"https://www.cinema-city.pl/kina/bemowo/1061#/buy-tickets-by-cinema?in-cinema=1061&at={today}&view-mode=list"

    movies = []

    print(f"🌐 Navigating to {url}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        
        print("⏳ Waiting for movie blocks to appear...")
        # Retry logic in case JS loads slowly
        for attempt in range(10):
            try:
                page.wait_for_selector(".qb-movie-details", timeout=3000)
                print(f"✅ Found movie blocks (on attempt {attempt + 1})")
                break
            except TimeoutError:
                print(f"⌛ Still waiting... attempt {attempt + 1}/10")
                time.sleep(2)
        else:
            print("❌ Failed to find movie blocks after 10 attempts.")
            browser.close()
            return

        movie_blocks = page.locator(".qb-movie-details")
        count = movie_blocks.count()
        print(f"🎬 Found {count} movie blocks")

        for i in range(count):
            block = movie_blocks.nth(i)
            try:
                print(f"🔍 Scraping movie {i + 1}/{count}")
                title = block.locator(".qb-movie-name").text_content().strip()

                genre_line = block.locator(".qb-movie-rating-info").text_content().strip()
                if "|" in genre_line:
                    genre, length = genre_line.split("|")
                else:
                    genre, length = genre_line, ""

                try:
                    movie_type = block.locator(".qb-screening-attributes").text_content().strip()
                except:
                    movie_type = ""

                try:
                    showtime_tags = block.locator("a.btn").all()
                    showtimes = [tag.text_content().strip() for tag in showtime_tags]
                except:
                    showtimes = []

                try:
                    image_url = block.locator("img").get_attribute("src")
                except:
                    image_url = ""

                try:
                    language = block.locator(".qb-movie-attributes").text_content().strip()
                except:
                    language = ""

                movies.append({
                    "title": title,
                    "genre": genre.strip(),
                    "length": length.strip(),
                    "type": movie_type,
                    "showtimes": showtimes,
                    "image_url": image_url,
                    "language": language,
                    "date": today
                })

            except Exception as e:
                print(f"⚠️ Error parsing movie block {i}: {e}")

        browser.close()

    # Save to JSON
    with open("cinema_bemowo_movies_today.json", "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(movies)} movies for {today}. Data saved to cinema_bemowo_movies_today.json")

if __name__ == "__main__":
    scrape_today_movies()

