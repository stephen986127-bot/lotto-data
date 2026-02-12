# crawler.py
import requests
from bs4 import BeautifulSoup
import json

# 页面 URL（JSON 可扩展到多个 page）
URL = "https://cn.lottolyzer.com/history/malaysia/supreme-toto/page/1/per-page/50/summary-view"

def fetch_latest_draw():
    # 使用通用 UA 模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(URL, headers=headers, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # 定位第一行数据
    row = soup.select_one("table tr:nth-of-type(2)")

    if not row:
        print("❌ No data found")
        return None

    cols = row.find_all("td")
    if len(cols) < 3:
        print("❌ Parse error — not enough columns")
        return None

    draw_no = cols[0].get_text(strip=True)
    date     = cols[1].get_text(strip=True)

    # 中奖号码按英文逗号分隔
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

    # 检查是否为新一期
    if data and data[0]["draw_no"] == latest["draw_no"]:
        print("📦 Already latest:", latest["draw_no"])
    else:
        print("⬆️ New draw added:", latest["draw_no"])
        data.insert(0, latest)
        with open("results.json", "w") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    update_json()
