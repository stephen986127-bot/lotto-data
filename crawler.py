# crawler.py
import requests
from bs4 import BeautifulSoup
import json

URL = "https://cn.lottolyzer.com/history/malaysia/supreme-toto/page/1/per-page/50/summary-view"

def fetch_latest_draw():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(URL, headers=headers, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    row = soup.select_one("table tr:nth-of-type(2)")

    if not row:
        print("❌ No data found")
        return None

    cols = row.find_all("td")
    if len(cols) < 3:
        print("❌ Parse error")
        return None

    draw_no = cols[0].get_text(strip=True)
    date = cols[1].get_text(strip=True)

    raw_nums = cols[2].get_text(strip=True)
    numbers = [int(x.strip()) for x in raw_nums.split(",")]

    return {
        "draw_no": draw_no,
        "date": date,
        "n1": numbers[0],
        "n2": numbers[1],
        "n3": numbers[2],
        "n4": numbers[3],
        "n5": numbers[4],
        "n6": numbers[5],
    }

def update_json():
    try:
        with open("results.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    latest = fetch_latest_draw()
    if latest is None:
        return

    # ===== 关键修复：全表去重 =====
    existing_draw_nos = {item["draw_no"] for item in data}

    if latest["draw_no"] in existing_draw_nos:
        print("📦 Already latest:", latest["draw_no"])
    else:
        print("⬆️ New draw added:", latest["draw_no"])
        data.append(latest)

    # ===== 排序 + 去重保障 =====
    unique_map = {}
    for item in data:
        unique_map[item["draw_no"]] = item

    cleaned = list(unique_map.values())

    # 按 draw_no 数字排序（大到小）
    cleaned.sort(key=lambda x: int(x["draw_no"]), reverse=True)

    with open("results.json", "w") as f:
        json.dump(cleaned, f, indent=2)

if __name__ == "__main__":
    update_json()
