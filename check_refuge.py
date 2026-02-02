import os
import requests
from bs4 import BeautifulSoup

URL = "https://rifugiolagazuoi.com/EN/disponibilita.php?prm=5&chm=1"
CHECK_DAY = "23"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0 Safari/537.36"
    )
}

def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram token or chat id not set; skipping notification.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print("Failed to send Telegram message:", e)

def check_status():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for cell in soup.find_all("td"):
        link = cell.find("a", string=CHECK_DAY)

        if link:
            return "AVAILABLE"

        if cell.get_text(strip=True) == CHECK_DAY:
            return "NOT AVAILABLE"

    return "DAY NOT FOUND"

if __name__ == "__main__":
    try:
        status = check_status()
        print("June 23 status:", status)

        if status == "AVAILABLE":
            send_telegram(f"Refuge available on {CHECK_DAY}! {URL}")
    except Exception as exc:
        print("Error checking status:", exc)
        send_telegram(f"Error checking refuge availability: {exc}")
