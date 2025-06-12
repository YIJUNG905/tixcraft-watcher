import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# ✅ 請貼上你的 Discord Webhook URL（不要漏掉開頭和結尾）
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1382649011231658014/ZAD9IvmhqSSliqPnBzBP8J1l7GtxM7QL6iNoaHnU-HG56a3IuU2lxfGgPAdJ-QvM6Q-5'

# ✅ 傳送 Discord 訊息
def send_discord_message(content):
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
        if response.status_code != 204:
            print(f"❗ Discord 發送失敗，狀態碼: {response.status_code}")
        else:
            print("✅ Discord 發送成功")
    except Exception as e:
        print("❗ 傳送失敗：", e)

# ✅ 抓取所有活動連結
def get_all_activity_links():
    url = "https://tixcraft.com/activity"
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        events = soup.select("div.event-info a")
        links = []
        for event in events:
            name = event.text.strip()
            href = event.get("href")
            if href:
                links.append(("https://tixcraft.com" + href, name))
        return links
    except Exception as e:
        print("⚠️ 抓取活動失敗：", e)
        return []

# ✅ 檢查票券狀態
def check_ticket_status(concert_url, concert_name):
    try:
        resp = requests.get(concert_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        area_tags = soup.select("a.area-item")

        available = []
        for area in area_tags:
            text = area.get_text(strip=True)
            if "已售完" not in text:
                available.append(text)

        if available:
            return f"🎟️ {concert_name} 有票囉！\n網址：{concert_url}\n可選區：\n" + "\n".join(available)
    except Exception as e:
        print(f"⚠️ 無法檢查 {concert_name}：{e}")
    return None

# ✅ 主迴圈：每 60 秒檢查一次
def run_checker():
    send_discord_message("✅ 測試訊息：Render 已成功啟動並開始監控票券！")

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"🔍 [{now}] 正在抓取全部活動...")

        activity_list = get_all_activity_links()
        print(f"🎫 找到 {len(activity_list)} 筆活動")

        messages = []

        for url, name in activity_list:
            result = check_ticket_status(url, name)
            if result:
                messages.append(result)
            else:
                print(f"[{now}] {name}：全部已售完")

        if messages:
            send_discord_message("\n\n".join(messages))

        print(f"⏳ [{now}] 60 秒後再次檢查...\n")
        time.sleep(60)

# ✅ 程式啟動點
if __name__ == "__main__":
    run_checker()
