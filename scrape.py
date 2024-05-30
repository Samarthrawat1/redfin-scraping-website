import requests
from bs4 import BeautifulSoup
import re
import time

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0'}
# response = requests.get(url, headers=headers)
def scrape_redfin_data(url, retries=3, delay=5):  
    """Scrapes property data from a Redfin URL, with retry logic for 202 responses.

    Args:
        url (str): The URL of the Redfin property listing.
        retries (int): The maximum number of retries if a 202 response is received.
        delay (int): The initial delay between retries in seconds.

    Returns:
        dict: A dictionary containing the scraped data, or None if scraping fails.
    """

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=headers)
            
            # Check for 202 Accepted directly from Redfin
            if response.status_code == 202:  
                if attempt < retries:
                    print(f"Received 202 from Redfin for {url}, retrying in {delay} seconds...")
                    time.sleep(delay)  # Wait and retry
                    delay *= 2  # Increase delay for subsequent retries (optional)
                    continue  # Retry the request
                else:
                    print(f"Max retries reached for {url}. Redfin still processing.")
                    return None  # Return None to signal failure

            data = {
    'Street Address': '',
    'City': '',
    'State': '',
    'Postal Code': '',
    'Price': '',
    'Bed Room': '',
    'Bath Room': '',
    'Sq.Ft.': '',
    'House type': '',
    'Built Year': '',
    'Area': '',
    'Price/Sq.Ft': '',
    'Car Parking': '',
    'AC': '',
    'Agent Name': '',
    'Brokerage': '',
    'MLS ID': '',
    'Time on Redfin': '',
    "Buyer's Agent Commission": '',
    "Agent License": '',
    'Contact': ''
}
            response.raise_for_status()  
            soup = BeautifulSoup(response.content, 'html.parser')
            # Address and Location
            full_address_elem = soup.find('h1', class_='full-address')
            if full_address_elem:
                address_lines = full_address_elem.find_all('div')
                data['Street Address'] = address_lines[0].text.strip()
                address_parts = address_lines[1].text.split()
                data['City'] = address_parts[0].replace(',', '')
                data['State'] = address_parts[1]
                data['Postal Code'] = address_parts[2]

            # Basic Stats
            stats_elem = soup.find('div', class_='home-main-stats-variant')
            if stats_elem:
                for div in stats_elem.find_all('div'):
                    data_rf_test_id = div.get('data-rf-test-id')
                    if data_rf_test_id == 'abp-price':
                        data['Price'] = div.find('div').text.strip()
                    elif data_rf_test_id == 'abp-beds':
                        data['Bed Room'] = div.find('div').text.strip()
                    elif data_rf_test_id == 'abp-baths':
                        data['Bath Room'] = div.find('div').text.strip()
                    elif data_rf_test_id == 'abp-sqFt':
                        data['Sq.Ft.'] = div.find('span').text.replace('Sq.Ft.', '').strip()

            # ... (Continue extracting other data similarly, using find(), find_all(), get(), etc.)
            details_table = soup.find('div', class_='KeyDetailsTable')
            if details_table:
                for row in details_table.find_all('div', class_='keyDetails-row'):
                    icon_class = row.find('svg')['class']
                    value_div = row.find('div')  
                    value = value_div.text.strip()

                    if 'clock' in icon_class:
                        data['Time on Redfin'] = value.replace('\xa0on Redfin', '')
                    elif 'house' in icon_class:
                        data['House type'] = value.replace(' House type', '')
                    elif 'wrench' in icon_class:
                        data['Built Year'] = value.replace('Built in ', '')
                    elif 'fence' in icon_class:
                        data['Area'] = value
                    elif 'ruler' in icon_class:
                        data['Price/Sq.Ft'] = value.replace(' per sq ft', '')
                    elif 'car' in icon_class:
                        data['Car Parking'] = value
                    elif 'temperature' in icon_class:
                        data['AC'] = value
                    elif 'agent' in icon_class:
                        data['Buyer\'s Agent Commission'] = value.replace('\xa0buyer\'s agent fee', '')

            # Agent Info
            agent_info_elem = soup.find('div', class_='agent-info-item')
            if agent_info_elem:
                for span in agent_info_elem.find_all('span'):
                    if span.get('class') == ['agent-basic-details--heading']:
                        data['Agent Name'] = span.text.replace("Agent Name ", "").strip()
                    elif span.get('class') == ['agent-basic-details--broker']:
                        data['Brokerage'] = span.text.strip()
                    elif span.get('class') == ['agentLicenseDisplay']:
                        data['Agent License'] = span.text.strip()

            # Contact
            contact_section = soup.find('div', class_='listingContactSection')
            if contact_section:
                data['Contact'] = contact_section.text.replace("Contact: ", "").strip()

            # MLS ID
            mls_id_elem = soup.find('span', class_='ListingSource--mlsId')
            if mls_id_elem:
                data['MLS ID'] = mls_id_elem.text.replace("#", "").strip()

            for key, value in data.items():
            # Remove invalid characters
                data[key] = re.sub(r'[•\n\r]+|[^\x00-\x7F]+', ' ', value).strip()

            return data
        

        except requests.exceptions.RequestException as e:
            print(f"Request error for URL {url}: {e}")
            return None

        except AttributeError as e:
            print(f"Attribute error for URL {url}: {e}")
            return None

        except Exception as e:  # Catch any other unexpected errors
            print(f"Unexpected error for URL {url}: {e}")
            return None

# ... (Example usage)
if __name__ == '__main__':
    url = "https://www.redfin.com/CA/Los-Angeles/123-Main-St-90001/home/123456789"  # Replace with actual URL
    url = "https://www.redfin.com/CA/Upland/2530-Mountain-Dr-91784/home/3877330"
    property_data = scrape_redfin_data(url)
    if property_data:
        print(property_data)