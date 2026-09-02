import sys
import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# 監視対象のURLリスト（追加したいURLをここに並べます）
TARGET_URLS = [
    "https://cenacolovinciano.vivaticket.it/en/event/cenacolo-vinciano/151991?idt=2547",
    "追加したいURLをここに記述（例: https://cenacolovinciano.vivaticket.it/en/event/...）"
]

def send_google_chat_notification(message):
    if WEBHOOK_URL:
        payload = {"text": message}
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print("Google Chat notification sent. Status:", response.status_code)
    else:
        print("Webhook URL not found. Skipping notification.")

def check_single_url(page, target_url, target_date):
    print(f"\n--- Navigating to: {target_url} (Checking Date: {target_date}) ---")
    
    try:
        page.goto(target_url, wait_until="networkidle", timeout=60000)
        page.wait_for_selector(".date-cal", timeout=15000)

        # 判定処理
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
        print(f"Status for September {target_date}: {status_str}")

        if is_available:
            msg = f"🟢 *【朗報】「最後の晩餐」9/{target_date}の予約枠が空いています！*\n確認はこちら：\n{target_url}"
            send_google_chat_notification(msg)

    except Exception as e:
        print(f"Error checking {target_url}: {e}")

def main():
    # 引数があればその日付、なければデフォルトで "20"
    target_date = sys.argv[1] if len(sys.argv) > 1 else "20"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 設定されたすべてのURLを順番にチェック
        for url in TARGET_URLS:
            check_single_url(page, url, target_date)

        browser.close()

if __name__ == "__main__":
    main()
