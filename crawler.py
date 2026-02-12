# crawler.py
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import pytz

# 目标页面
URL = "https://cn.lottolyzer.com/history/malaysia/supreme-toto/page/1/per-page/50/summary-view"

# 马来西亚时区
TZ = pytz.timezone("Asia/Kuala_Lumpur")

# 只在 周三(2) 周六(5) 周日(6) 22:30 之后运行
ALLOWED_DAYS = [2, 5, 6]
ALLOWED_HOUR = 22
ALLOWED_MINUTE = 30


# ==========================================================
# 时间判断
# ==========================================================
def is_allowed_time():
    now = datetime.now(TZ)

    if now.weekday() not in ALLOWED_DAYS:
        print("⏰ Not allowed weekday:", now.weekday())
        return False

    if now.hour < ALLOWED_HOUR:
        print("⏰ Too early")
        return False

    if now.hour == ALLOWED_HOUR and now.minute < ALLOWED_MINUTE:
        print("⏰ Waiting until 22:30")
        return False

    return True


# ==========================================================
# 抓最新一期
# ==========================================================
def fetch_latest_draw():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # 找第一条数据行
    row = soup.select_one("table tbody tr")
    if not row:
        print("❌ No table row found")
        return None

    cols = row.find_all("td")
    if len(cols) < 3:
        print("❌ Not enough columns")
        return None

    draw_no = cols[0].get_text(strip=True)
    date = cols[1].get_text(strip=True)

    raw_nums = cols[2].get_text(strip=True)
    numbers = [int(x.strip()) for x in raw_nums.split(",")]

    if len(numbers) != 6:
        print("❌ Number count error")
        return None

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


# ==========================================================
# 更新 JSON
# ==========================================================
def update_json():
    if not is_allowed_time():
        return

    filename = "results.json"

    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
    else:
        data = []

    latest = fetch_latest_draw()
    if latest is None:
        return

    # 已经是最新
    if data and data[0]["draw_no"] == latest["draw_no"]:
        print("📦 Already latest:", latest["draw_no"])
        return

    print("⬆️ New draw:", latest["draw_no"])
    data.insert(0, latest)

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    update_json()
