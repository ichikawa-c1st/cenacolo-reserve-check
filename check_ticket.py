import os
import requests
from playwright.sync_api import sync_playwright

# GitHub Secrets に登録した Webhook URL
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # 名称はそのままでOK

def send_google_chat_notification(message):
    if WEBHOOK_URL:
        # Google Chat 用の JSON データ構造 ({ "text": "メッセージ" })
        payload = {"text": message}
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print("Google Chat notification sent. Status:", response.status_code)
    else:
        print("Webhook URL not found. Skipping notification.")

def check_availability():
    target_url = "https://cenacolovinciano.vivaticket.it/en/event/cenacolo-vinciano/151991?idt=2547"
    target_date = "20"  # 9/20の「20」

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("Navigating to page...")
        page.goto(target_url, wait_until="networkidle", timeout=60000)
        page.wait_for_selector(".date-cal", timeout=15000)

        # 9/20の要素（inactiveが外れて<a>タグがあるか）を判定
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

        print(f"Status for September {target_date}: {'Available (Green)' if is_available else 'Not available'}")

        if is_available:
            msg = f"🟢 *【朗報】「最後の晩餐」9/20の予約枠が空きました！*\n今すぐ予約サイトを確認してください：\n{target_url}"
            send_google_chat_notification(msg)

        browser.close()

if __name__ == "__main__":
    check_availability()
