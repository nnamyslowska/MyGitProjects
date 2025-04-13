import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup
url = "https://www.cinema-city.pl/kina/promenada/1068#/buy-tickets-by-cinema?in-cinema=1068&at=2025-04-14&view-mode=list"
today = datetime.today().strftime("%Y-%m-%d")

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)
time.sleep(5)

movies_data = []

# Locate all movie blocks
movie_blocks = driver.find_elements(By.CLASS_NAME, "row.movie-row")

for movie in movie_blocks:
    try:
        title = movie.find_element(By.CLASS_NAME, "qb-movie-name").text.strip()

        # Genre and length
        genre_info = movie.find_element(By.CLASS_NAME, "qb-movie-rating-info").text.strip().split("|")
        genre = genre_info[0].strip() if len(genre_info) > 0 else ""
        length = genre_info[1].strip() if len(genre_info) > 1 else ""

        # Get image URL properly from movie-poster-container img[src]
        try:
            img_tag = movie.find_element(By.CSS_SELECTOR, ".movie-poster-container img")
            img_url = img_tag.get_attribute("data-src") or img_tag.get_attribute("src")

            # Filter out placeholder
            if "film.placeholder.poster.jpg" in img_url:
                img_url = ""
        except:
            img_url = ""

        # Types (2D/3D/etc.)
        types = []
        type_elements = movie.find_elements(By.CLASS_NAME, "qb-screening-attributes")
        for t in type_elements:
            try:
                screening_type = t.find_element(By.TAG_NAME, "span").text.strip()
                if screening_type and screening_type not in types:
                    types.append(screening_type)
            except:
                continue

        # Showtimes
        showtimes = []
        presale_mode = False
        presale_buttons = movie.find_elements(By.CSS_SELECTOR, ".qb-movie-info-column a.btn.btn-primary")
        for btn in presale_buttons:
            t = btn.text.strip()
            if "\n" in t or any(month in t for month in ["APR", "MAY", "JUN", "LIP", "MAJ", "CZE"]):
                presale_mode = True
                lines = t.split("\n")
                showtimes.append(" ".join(lines).strip())
            else:
                showtimes.append(t)

        if presale_mode:
            types = []  # No types for presale entries

        # Language variants
        langs = []
        lang_blocks = movie.find_elements(By.CLASS_NAME, "qb-movie-attributes")
        for block in lang_blocks:
            line = block.text.strip()
            if line and line not in langs:
                langs.append(line)

        movies_data.append({
            "title": title,
            "genre": genre,
            "length": length,
            "type": types,
            "showtimes": showtimes,
            "image_url": img_url,
            "language": langs,
            "date": today
        })

    except Exception as e:
        print(f"[!] Error processing a movie block: {e}")

driver.quit()

# Save JSON output
with open("cinema_city_movies.json", "w", encoding="utf-8") as f:
    json.dump(movies_data, f, ensure_ascii=False, indent=2)

print("✅ Scraping complete. Data saved to 'cinema_city_movies.json'")
