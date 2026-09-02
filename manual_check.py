import sys
import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def send_google_chat_notification(message):
    if WEBHOOK_URL:
        payload = {"text": message}
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print("Google Chat notification sent. Status:", response.status_code)
    else:
        print("Webhook URL not found. Skipping notification.")

def check_availability(target_date="20"):
    target_url = "https://cenacolovinciano.vivaticket.it/en/event/cenacolo-vinciano/151991?idt=2547"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Navigating to page (Checking Date: {target_date})...")
        page.goto(target_url, wait_until="networkidle", timeout=60000)
        page.wait_for_selector(".date-cal", timeout=15000)

        # 指定日付の要素を判定
        is_available = page.evaluate(f'''() => {{
            const listItems = Array.from(document.querySelectorAll('.date-cal li'));
            for (const li of listItems) {{
                const text = li.innerText.trim();
                if (text === "{target_date}") {{
                    const hasLink = li.querySelector('a') !== null;
                    const isInactive = li.classList.contains('inactive');
                    if (!isInactive && hasLink) {{
                        return true;
                    }}
                }}
            }}
            return false;
        }}''')

        status_str = "Available (Green)" if is_available else "Not available"
        print(f"Status for day {target_date}: {status_str}")

        if is_available:
            msg = f"🟢 *【朗報】「最後の晩餐」{target_date}日の予約枠が空いています！*\n今すぐ予約サイトを確認してください：\n{target_url}"
            send_google_chat_notification(msg)
        else:
            # 手動チェック時に空いていなかった場合もログや通知でわかりやすくする
            print(f"Day {target_date} is currently not available.")

        browser.close()

if __name__ == "__main__":
    # コマンドライン引数があればその日付を使用し、なければデフォルトで "20"
    day_to_check = sys.argv[1] if len(sys.argv) > 1 else "20"
    check_availability(day_to_check)
