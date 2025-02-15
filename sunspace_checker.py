import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SunspaceChecker:
    def __init__(self):
        self.base_url = "https://sunspace.ph/collections/yoga"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_page_content(self, page=1):
        """Fetch content from a specific page"""
        # First page is just the base URL, subsequent pages use the page parameter
        url = self.base_url if page == 1 else f"{self.base_url}?page={page}"
        try:
            logging.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching page {page}: {str(e)}")
            return None

    def parse_class_info(self, html_content):
        """Parse HTML content and extract available class information"""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        available_classes = []

        # Find all product items
        products = soup.find_all('div', {'class': 'grid__item'})
        

        breakpoint()

        logging.info(f"Found {len(products)} products on page")

        for product in products:
            # Skip if it's a gift card or sold out
            if 'Gift Card' in product.get_text():
                continue

            quick_add_button = product.find('button', attrs={'id': lambda x: x and 'quick-add-template' in x})
            if quick_add_button and quick_add_button.has_attr('disabled'):
                continue

            sold_out_badge = product.select_one('.card__badge .badge')
            if sold_out_badge and sold_out_badge.get_text(strip=True) == 'Sold out':
                continue

            # Extract class details
            title_elem = product.find('a', {'class': 'full-unstyled-link'})
            if not title_elem:
                continue

            title = title_elem.text.strip()
            
            # Extract price
            price_elem = product.find('span', {'class': 'price-item'})
            if not price_elem:
                continue
                
            price = price_elem.text.strip()
            
            # Parse date and class name
            try:
                parts = title.split('|')
                class_name = parts[0].strip()
                date_str = parts[1].strip()
                
                # Convert date format
                date_obj = datetime.strptime(date_str, '%b %d, %a')
                # Use current year since it's not in the original string
                date_obj = date_obj.replace(year=datetime.now().year)
                formatted_date = date_obj.strftime('[%A, %b %d]')
                
                # Format price to remove currency symbol and use P instead
                price = f"P{price.replace('₱', '').strip()}"
                
                formatted_class = f"{formatted_date} {class_name}, {price}"
                available_classes.append(formatted_class)
                logging.info(f"Found available class: {formatted_class}")
                
            except (ValueError, IndexError) as e:
                logging.error(f"Error parsing class info for {title}: {str(e)}")
                continue

        return available_classes

    def check_all_pages(self):
        """Check all pages for available classes"""
        all_available_classes = []
        page = 1
        
        while True:
            logging.info(f"Checking page {page}")
            content = self.get_page_content(page)
            
            if not content:
                break
                
            # Check if we've reached a page with no results
            soup = BeautifulSoup(content, 'html.parser')
            if "No products found" in soup.text:
                break
                
            available_classes = self.parse_class_info(content)
            if not available_classes:
                # Only break if we're past page 1 and found no classes
                if page > 1:
                    break
                
            all_available_classes.extend(available_classes)
            page += 1
            
            # Add a small delay between requests to be polite
            time.sleep(1)
            
        return all_available_classes

def main():
    checker = SunspaceChecker()
    available_classes = checker.check_all_pages()
    
    if available_classes:
        print("\nAvailable Classes:")
        for class_info in available_classes:
            print(class_info)
    else:
        print("No available classes found.")

if __name__ == "__main__":
    main() 