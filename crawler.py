# crawler.py — FIXED VERSION

import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://cn.lottolyzer.com/history/malaysia/supreme-toto/page/1/per-page/50/summary-view"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

FILE = "results.json"


# ============================================================
# 抓取页面所有结果（不是只抓一个）
# ============================================================

def fetch_all_draws():

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("table tbody tr")

    results = []

    for row in rows:

        cols = row.find_all("td")

        if len(cols) < 3:
            continue

        draw_no = cols[0].get_text(strip=True)
        date = cols[1].get_text(strip=True)

        numbers = [
            int(x.strip())
            for x in cols[2].get_text(strip=True).split(",")
        ]

        if len(numbers) != 6:
            continue

        results.append({
            "draw_no": draw_no,
            "date": date,
            "n1": numbers[0],
            "n2": numbers[1],
            "n3": numbers[2],
            "n4": numbers[3],
            "n5": numbers[4],
            "n6": numbers[5],
        })

    return results


# ============================================================
# 读取已有数据
# ============================================================

def load_existing():

    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        return json.load(f)


# ============================================================
# 保存数据
# ============================================================

def save(data):

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
# 更新 JSON
# ============================================================

def update():

    existing = load_existing()

    existing_map = {x["draw_no"]: x for x in existing}

    new_draws = fetch_all_draws()

    added = 0

    for draw in new_draws:

        if draw["draw_no"] not in existing_map:

            existing_map[draw["draw_no"]] = draw
            added += 1

    # 转 list
    updated = list(existing_map.values())

    # 排序：最新在前
    updated.sort(
        key=lambda x: int(x["draw_no"]),
        reverse=True
    )

    save(updated)

    print("Added:", added)
    print("Total:", len(updated))


# ============================================================

if __name__ == "__main__":
    update()
