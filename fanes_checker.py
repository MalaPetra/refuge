import os
import random
import string
import requests

PROPERTY_ID = "13308"
SOURCE_ID = "98"
CHECK_DATE = "2026-06-11”         # Change this to your target date (YYYY-MM-DD)
GUEST_COUNT = 2                    # Number of guests

BOOKING_URL = "https://www.rifugiofanes.com/en/booking"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0 Safari/537.36"
    ),
    "Origin": "https://www.rifugiofanes.com",
    "Referer": "https://www.rifugiofanes.com/",
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


def make_correlation_id(length: int = 23) -> str:
    """Generate a random correlation ID matching the site's format."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def check_date(check_in: str) -> str:
    """
    Returns "AVAILABLE", "NOT AVAILABLE", or raises on error.
    check_in format: YYYY-MM-DD. check_out is always the next day.
    """
    # Build check-out date (arrival + 1 night)
    from datetime import date, timedelta
    d = date.fromisoformat(check_in)
    check_out = str(d + timedelta(days=1))

    # Build guests param: list of [age, age] pairs, all adults (18)
    guests_param = "[" + ",".join(["[18,18]"] * (GUEST_COUNT // 2)) + "]"
    if GUEST_COUNT % 2:
        guests_param = guests_param[:-1] + ",[18]]"  # add a lone adult if odd

    url = (
        f"https://api.widgets.bookingsuedtirol.com/v6/properties/{PROPERTY_ID}/offers"
        f"?correlationId={make_correlation_id()}"
        f"&from={check_in}"
        f"&guestCount={GUEST_COUNT}"
        f"&guests={requests.utils.quote(guests_param)}"
        f"&lang=en"
        f"&maxAdults=5"
        f"&maxChildren=4"
        f"&sourceId={SOURCE_ID}"
        f"&to={check_out}"
    )

    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()

    # The API returns a list of room offers when available, empty list when not
    rooms = data.get("rooms", [])
    if any(room.get("room_free", 0) > 0 for room in rooms):
        return "AVAILABLE"
    return "NOT AVAILABLE"


if __name__ == "__main__":
    try:
        status = check_date(CHECK_DATE)
        print(f"{CHECK_DATE} status: {status}")
        if status == "AVAILABLE":
            send_telegram(
                f"🚨 ALERT: Rifugio Fanes available on {CHECK_DATE}! "
                f"Book now: {BOOKING_URL}"
            )
    except Exception as exc:
        print("Error checking status:", exc)
        send_telegram(f"⚠️ Error: Rifugio Fanes scout script failed: {exc}")
