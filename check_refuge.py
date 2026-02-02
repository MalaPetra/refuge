import requests
from bs4 import BeautifulSoup

URL = "https://rifugiolagazuoi.com/EN/disponibilita.php?prm=4&chm=-1"
CHECK_DAY = "27"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0 Safari/537.36"
    )
}

def check_status():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for cell in soup.find_all("td"):
        # Look for a link whose text is exactly "27"
        link = cell.find("a", string=CHECK_DAY)

        if link:
            return "AVAILABLE"

        # If the cell contains just "27" with no link
        if cell.get_text(strip=True) == CHECK_DAY:
            return "NOT AVAILABLE"

    return "DAY NOT FOUND"


if __name__ == "__main__":
    print("March 27 status:", check_status())
