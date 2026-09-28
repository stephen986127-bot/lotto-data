# crawler.py

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random

URL = "https://cn.lottolyzer.com/history/malaysia/supreme-toto/page/1/per-page/50/summary-view"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

FILE = "results.json"


def fetch_all_draws():
    # 随机延迟，避免被识别为机器人
    time.sleep(random.uniform(2, 5))

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table tbody tr")

    if not rows:
        raise ValueError(f"No rows found — page may have changed. Status: {r.status_code}")

    results = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        draw_no = cols[0].get_text(strip=True)
        date    = cols[1].get_text(strip=True)
        numbers = [
            int(x.strip())
            for x in cols[2].get_text(strip=True).split(",")
        ]

        if len(numbers) != 6:
            continue

        results.append({
            "draw_no": draw_no,
            "date":    date,
            "n1": numbers[0],
            "n2": numbers[1],
            "n3": numbers[2],
            "n4": numbers[3],
            "n5": numbers[4],
            "n6": numbers[5],
        })

    return results


def load_existing():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)


def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def update():
    existing     = load_existing()
    existing_map = {x["draw_no"]: x for x in existing}

    new_draws = fetch_all_draws()
    added = 0

    for draw in new_draws:
        if draw["draw_no"] not in existing_map:
            existing_map[draw["draw_no"]] = draw
            added += 1

    updated = sorted(
        existing_map.values(),
        key=lambda x: int(x["draw_no"]),
        reverse=True
    )

    save(updated)
    print(f"Added: {added}")
    print(f"Total: {len(updated)}")

    if added == 0:
        print("No new draws — data is up to date")


if __name__ == "__main__":
    update()
