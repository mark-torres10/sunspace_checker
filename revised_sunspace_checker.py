import requests
from bs4 import BeautifulSoup
from datetime import datetime


class RevisedSunspaceChecker:
    def __init__(self):
        self.base_url = "https://sunspace.ph/collections/yoga"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_page_content(self, page=1):
        """Fetch content from a specific page."""
        url = self.base_url if page == 1 else f"{self.base_url}?page={page}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching page {page}: {str(e)}")
            return None

    def get_class_cards(self, html_content):
        """
        Isolate all class card components.
        Each card contains the classes "card", "card--standard", and "card--media".
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all("div", class_=lambda c: c and "card--standard" in c and "card--media" in c)
        return cards

    def parse_class_card(self, card):
        """
        Extract information from a single class card.
        Expected format:
        [Day, Month Date] <Class name> : SOLD OUT / OPEN, P<Price>
        """
        title_elem = card.find("a", class_="full-unstyled-link")
        if not title_elem:
            return None

        full_title = title_elem.get_text(strip=True)
        parts = full_title.split('|')
        if len(parts) < 2:
            class_name = full_title
            date_part = ""
        else:
            class_name = parts[0].strip()
            date_part = parts[1].strip()

        # Parse and format the date
        formatted_date = "[Unknown]"
        if date_part:
            try:
                # Expected format e.g., 'Feb 17, Mon'
                date_obj = datetime.strptime(date_part, '%b %d, %a')
                date_obj = date_obj.replace(year=datetime.now().year)
                formatted_date = date_obj.strftime('[%A, %b %d]')
            except Exception as e:
                formatted_date = f"[{date_part}]"

        # Check sold out status by badge text
        badge_elem = card.select_one("div.card__badge span.badge")
        if badge_elem and "sold out" in badge_elem.get_text(strip=True).lower():
            status = "SOLD OUT"
        else:
            status = "OPEN"

        # Extract price
        price_elem = card.select_one("div.price span.price-item--regular")
        price = price_elem.get_text(strip=True) if price_elem else ""
        if price and not price.startswith("P"):
            price = "P" + price.replace("₱", "").strip()

        return f"{formatted_date} {class_name} : {status}, {price}"

    def parse_all_classes(self, html_content):
        """
        Process all class cards from the HTML content.
        Returns a list of strings with each class's information.
        """
        cards = self.get_class_cards(html_content)
        classes = []
        for card in cards:
            result = self.parse_class_card(card)
            if result:
                classes.append(result)
        return classes

    def check_all_pages(self):
        """
        Iterate over multiple pages to check for classes.
        Stops when no more content or no cards found on subsequent pages.
        """
        all_classes = []
        page = 1
        while True:
            html = self.get_page_content(page)
            if not html:
                break
            classes = self.parse_all_classes(html)
            if not classes and page > 1:
                break
            all_classes.extend(classes)
            page += 1
        return all_classes


def main():
    checker = RevisedSunspaceChecker()
    classes = checker.check_all_pages()
    if classes:
        print("Available classes:")
        for cls in classes:
            print(cls)
    else:
        print("No classes found.")


if __name__ == "__main__":
    main() 