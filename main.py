import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# ✅ Discord Webhook 設定
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1382649011231658014/ZAD9IvmhqSSliqPnBzBP8J1l7GtxM7QL6iNoaHnU-HG56a3IuU2lxfGgPAdJ-QvM6Q-5'

# ✅ 加上 User-Agent headers，避開反爬蟲
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# ✅ 安全抓取頁面（自動 retry）
def safe_request(url, max_retries=3, sleep_sec=5):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code == 200:
                return resp
            else:
                print(f"⚠️ 第 {attempt+1} 次嘗試失敗，狀態碼: {resp.status_code}")
        except Exception as e:
            print(f"❗ 請求錯誤：{e}")
        time.sleep(sleep_sec)
    print(f"🚫 無法取得 {url}，已重試 {max_retries} 次")
    return None

# ✅ 傳送 Discord 訊息
def send_discord_message(content):
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
        if response.status_code != 204:
            print(f"❗ Discord 發送失敗，狀態碼: {response.status_code}")
            print("🔍 回傳內容：", response.text)
        else:
            print("✅ Discord 發送成功")
    except Exception as e:
        print("❗ 發送 Discord 失敗：", e)

# ✅ 抓取活動頁面中的所有演唱會連結
def get_all_activity_links():
    url = "https://tixcraft.com/activity"
    resp = safe_request(url)
    if not resp:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    events = soup.select("div.event-info a")
    links = []

    for event in events:
        name = event.text.strip()
        href = event.get("href")
        if href:
            links.append(("https://tixcraft.com" + href, name))
    return links

# ✅ 檢查各活動是否有票
def check_ticket_status(concert_url, concert_name):
    resp = safe_request(concert_url)
    if not resp:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    area_tags = soup.select("a.area-item")

    available = []
    for area in area_tags:
        text = area.get_text(strip=True)
        if "已售完" not in text:
            available.append(text)

    if available:
        return f"🎟️ {concert_name} 有票囉！\n👉 網址：{concert_url}\n🎯 可選區：\n" + "\n".join(available)
    return None

# ✅ 主邏輯：每 2 分鐘跑一次
def run_checker():
    send_discord_message("👀 Render 成功啟動，開始監控 TixCraft 活動票券狀態囉～")

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"⏰ [{now}] 開始抓取活動清單...")

        activity_list = get_all_activity_links()
        print(f"📌 共找到 {len(activity_list)} 筆活動")

        messages = []

        for url, name in activity_list:
            result = check_ticket_status(url, name)
            if result:
                messages.append(result)
            else:
                print(f"❌ [{now}] {name}：目前全部已售完")

        if messages:
            send_discord_message("\n\n".join(messages))

        print(f"🕒 [{now}] 休息 120 秒後再次檢查...\n")
        time.sleep(120)

# ✅ 程式啟動點
if __name__ == "__main__":
    run_checker()
