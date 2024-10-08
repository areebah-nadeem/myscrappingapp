import pandas as pd
from airtable import Airtable
import time

import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote

# Part 1: Google Scraping - List of URLs to scrape from Google (you can add more URLs if needed)
# List of URLs to scrape
url_list = [
    'https://www.google.com/search?sca_esv=90bdcdfe264c115d&rlz=1C1UEAD_enCA1053CA1053&udm=8&sxsrf=ADLYWIKaV7D8n_W9GDCduxW8Rl4X0yptjA:1728262942930&q=google+job+for+apprenticeship+in+ontario&spell=1&sa=X&ved=2ahUKEwinw6qWifuIAxXLpokEHXorMRcQBSgAegQICRAB&biw=1536&bih=695&dpr=1.25&jbr=sep:0',
    'https://www.google.com/search?q=google%20job%20for%20apprenticeship%20near%20manitoba&sca_esv=90bdcdfe264c115d&rlz=1C1UEAD_enCA1053CA1053&sxsrf=ADLYWILOmJdrWKb6tUNWG_BZ4QmjaPPzLw%3A1728262831418&ei=rzIDZ9qgGbDIptQPp4K90QI&ved=2ahUKEwj3zpfjiPuIAxWnm4kEHXsbF_QQ3L8LegQIGxAN&uact=5&oq=google%20job%20for%20apprenticeship%20near%20manitoba&gs_lp=Egxnd3Mtd2l6LXNlcnAiK2dvb2dsZSBqb2IgZm9yIGFwcHJlbnRpY2VzaGlwIG5lYXIgbWFuaXRvYmEyBRAhGKABMgUQIRigATIFECEYnwVI0RZQ-gpYgRRwAngBkAEDmAG1AaABlgiqAQM0LjS4AQPIAQD4AQGYAgegApAEwgIKEAAYsAMY1gQYR8ICBxAhGKABGAqYAwCIBgGQBgiSBwM2LjGgB4Y8&sclient=gws-wiz-serp&jbr=sep:0&udm=8',
    'https://www.google.com/search?q=google+job+for+apprenticeship+near+british+columbia&sca_esv=90bdcdfe264c115d&rlz=1C1UEAD_enCA1053CA1053&udm=8&sxsrf=ADLYWILS5XIw9q-wXgXKnJ81S30usC7xOQ%3A1728262840181&ei=uDIDZ5XoCtmFw8cP1N7JuAI&oq=google+job+for+apprenticeship+near+british+colum&gs_lp=Egxnd3Mtd2l6LXNlcnAiMGdvb2dsZSBqb2IgZm9yIGFwcHJlbnRpY2VzaGlwIG5lYXIgYnJpdGlzaCBjb2x1bSoCCAAyBRAhGKABMgUQIRigATIFECEYoAFIqjFQ4gVYvR1wAngBkAEAmAGIAaABiwqqAQM4LjW4AQHIAQD4AQGYAg-gArEKwgIKEAAYsAMY1gQYR8ICBRAhGJ8FwgIEECEYFcICBxAhGKABGArCAgQQIRgKmAMAiAYBkAYEkgcDOS42oAe4QQ&sclient=gws-wiz-serp&jbr=sep:0'
]


# Set up Selenium WebDriver with Service
service = Service(ChromeDriverManager().install())

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)

# Initialize set to keep track of existing companies (to avoid duplicates)
existing_companies = set()

# List to store all scraped company data (without URL)
scraped_data_list = []

# Part 1: Google Scraping - Function to collect data from Google search results
def scrape_page(soup):
    companies = soup.find_all("div", class_="wHYlTd MKCbgd a3jPc")
    addresses = soup.find_all("div", class_="wHYlTd FqK3wc MKCbgd")

    for company, address in zip(companies, addresses):
        company_name = company.text.strip().replace('.', '')
        if '(' in address.text:
            address_text = address.text.split('(')[0].strip()  # Remove everything after '('
        else:
            address_text = address.text.split('•')[0].strip()  # Remove everything after '•'

        if company_name not in existing_companies:
            # Add company name and address to the main list for further processing
            scraped_data_list.append({
                'CompanyName': company_name,        # Part 1: Scraped Google company name
                'Address': address_text,            # Part 1: Scraped Google address
                'Yellow Page Company Name': '',     # Part 2: Placeholder for Yellow Pages data
                'Yellow Page Contact': '',          # Part 2: Placeholder for Yellow Pages data
                'Google WoPH Company Name': '',     # Part 3: Placeholder for Google WoPH data
                'Google WoPH Contact': '',          # Part 3: Placeholder for Google WoPH data
                'Company to Yellow Match %': 0,     # Part 4: Match % between Google and Yellow Page names
                'Company to Google Match %': 0,     # Part 4: Match % between Google names
                'Contact': ''                       # Part 4: Final contact field
            })
            existing_companies.add(company_name)
            print(f"Company: {company_name}, Address: {address_text}")

# Part 1: Google Scraping - Loop through each URL and scrape data from Google
for url in url_list:
    driver.get(url)
    
    while True:  # Continue scraping until no more jobs/pages are found
        try:
            # Wait for the companies and addresses to be present
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "wHYlTd"))
            )
            
            # Scroll down the page continuously until no more content loads
            previous_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                time.sleep(5)  # Give time for the page to load

                # Calculate new scroll height after scrolling
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == previous_height:
                    break  # If no more content is loaded, break the loop
                previous_height = new_height

            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            scrape_page(soup)

            # Try to find the "Next" button and click it to go to the next page
            try:
                next_button = driver.find_element(By.XPATH, "//a[@id='pnnext']")
                if next_button:
                    next_button.click()
                    time.sleep(5)  # Wait longer for the next page to load
                else:
                    print("No more pages.")
                    break
            except:
                print("Next button not found or no more pages.")
                break

        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            break

    time.sleep(10)  # Extra time between processing different URLs

# Close the browser after scraping is complete
driver.quit()

# Part 2: Yellow Pages Lookup - Function to clean and format the company name and address
def format_text(text):
    return text.strip()

# Part 2: Yellow Pages Lookup - Function to extract and clean phone number from Yellow Pages
def extract_phone_number(soup):
    phone_tag = soup.find('ul', class_='mlr__submenu')
    if phone_tag:
        phone_number_tag = phone_tag.find('h4')
        if phone_number_tag:
            raw_phone_number = phone_number_tag.get_text(strip=True).split('\n')[0]
            # Remove spaces, brackets, hyphens, periods, etc., using regex
            clean_phone_number = re.sub(r'[^\d]', '', raw_phone_number)
            return clean_phone_number
    return ''

# Part 2: Yellow Pages Lookup - Function to get company name from Yellow Pages
def get_company_name_from_title(soup):
    title_tag = soup.find('a', class_='listing__name--link')
    if title_tag and 'title' in title_tag.attrs:
        return title_tag['title'].split('See detailed information for ')[-1]
    return ''

# Part 2: Yellow Pages Lookup - Loop through the scraped companies to gather Yellow Pages information
for company in scraped_data_list:
    formatted_company_name = format_text(company['CompanyName'])
    formatted_address = format_text(company['Address'])
    updated_url = f'https://www.yellowpages.ca/search/si/1/{quote(formatted_company_name)}/{quote(formatted_address)}'

    print(f"Processing Yellow Pages for company: {formatted_company_name}")

    try:
        response = requests.get(updated_url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the company name from the page title
        yellow_page_company_name = get_company_name_from_title(soup)
        print(f"Yellow Page company name: {yellow_page_company_name}")

        # Extract and clean the phone number
        phone_number = extract_phone_number(soup)
        print(f"Found phone number: {phone_number}")

        # Update the company info with Yellow Pages data, leave empty if not found
        company['Yellow Page Company Name'] = yellow_page_company_name if yellow_page_company_name else ''
        company['Yellow Page Contact'] = phone_number if phone_number else ''

    except requests.RequestException as e:
        print(f"Request failed for URL {updated_url}: {e}")
        company['Yellow Page Company Name'] = ''  # Leave empty
        company['Yellow Page Contact'] = ''  # Leave empty

# Part 3: Google WoPH Scraping - Function to restructure the URL for Google search
def restructure_url(company_name, address):
    company_name = company_name.replace(" ", "+").replace("&", "%26").replace("-", "+").replace(".", "")
    address = address.replace(" ", "+").replace(",", "+")
    search_url = f"https://www.google.com/search?q={company_name}+{address}"
    return search_url

# Part 3: Google WoPH Scraping - Function to get company info from Google search
def get_google_info(soup):
    company_name_selectors = [
        {'class': 'qrShPb', 'data-attrid': 'title'},
        {'class': 'PZPZlf', 'data-attrid': 'title', 'role': 'heading'},
        {'class': 'PZPZlf ssJ7i xgAzOe', 'data-attrid': 'title', 'role': 'heading'},
        {'data-attrid': 'title', 'role': 'heading'}
    ]
    
    google_company_name = None
    for selector in company_name_selectors:
        company_element = soup.find(['h2', 'div'], selector)
        if company_element:
            google_company_name = company_element.text.strip()
            break

    # Get phone number from Google search
    phone_div = soup.find('div', {'class': 'zloOqf PZPZlf', 'data-local-attribute': 'd3ph'})
    if phone_div:
        phone_span = phone_div.find('span', {'class': 'LrzXr zdqRlf kno-fv'})
        google_contact = phone_span.text.strip() if phone_span else None
    else:
        google_contact = None

    # Clean the Google WoPH contact number (remove spaces, brackets, hyphens, periods)
    if google_contact:
        google_contact = re.sub(r'[^\d]', '', google_contact)  # Clean number

    return google_company_name, google_contact

# Part 3: Google WoPH Scraping - Function to scrape Google for company info
def scrape_google_info(company_name, address):
    url = restructure_url(company_name, address)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            google_company_name, google_contact = get_google_info(soup)
            print(f"Info found for search '{company_name}': Google WoPH Name: {google_company_name}, WoPH Contact: {google_contact}")
            return google_company_name, google_contact
        else:
            print(f"Failed to retrieve data for {company_name}. HTTP Status code: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None

# Helper function to calculate match percentage between two company names
def calculate_match_percentage(name1, name2):
    if not name1 or not name2:
        return 0
    match_count = sum(1 for a, b in zip(name1, name2) if a == b)
    return (match_count / len(name1)) * 100 if len(name1) > 0 else 0

# Part 3: Google WoPH Scraping - Loop through the scraped companies to gather Google WoPH information
for company in scraped_data_list:
    company_name = company['CompanyName']
    address = company['Address']
    
    print(f"Processing {company_name} on Google WoPH...")
    google_company_name, google_contact = scrape_google_info(company_name, address)
    
    # Update the dictionary with Google WoPH information
    company['Google WoPH Company Name'] = google_company_name if google_company_name else ''
    company['Google WoPH Contact'] = google_contact if google_contact else ''
    
    # Calculate match percentage for Yellow and Google
    yellow_match_percentage = calculate_match_percentage(company_name, company['Yellow Page Company Name'])
    google_match_percentage = calculate_match_percentage(company_name, company['Google WoPH Company Name'])
    
    company['Company to Yellow Match %'] = yellow_match_percentage
    company['Company to Google Match %'] = google_match_percentage
    
    # Updated logic for choosing the contact number
    if yellow_match_percentage <= 0 and google_match_percentage <= 0:
        company['Contact'] = ''  # No match
    elif yellow_match_percentage > google_match_percentage:
        company['Contact'] = company['Yellow Page Contact'] if company['Yellow Page Contact'] else company['Google WoPH Contact']
    else:
        company['Contact'] = company['Google WoPH Contact'] if company['Google WoPH Contact'] else company['Yellow Page Contact']
    
    # Add a delay to avoid hitting Google's rate limits
    time.sleep(2)  # Adjust this delay if needed

# Part 4: Convert the list of dictionaries to a DataFrame and save to Excel
# df = pd.DataFrame(scraped_data_list)

# # Define the path to save the Excel file
# output_excel_file = 'scraped_data_output.xlsx'

# # Save the DataFrame to Excel (make sure to use openpyxl as the engine)
# df.to_excel(output_excel_file, index=False, engine='openpyxl')

# print(f"Data successfully saved to {output_excel_file}")



# Part 5: Data Cleansing
def clean_data(scraped_data_list):
    # Step 1: Remove entries with 'Contact' starting with '1800'
    # cleaned_data = [entry for entry in scraped_data_list if not entry['Contact'].startswith('1800')]
    cleaned_data = [entry for entry in scraped_data_list if entry['Contact'] and not entry['Contact'].startswith('1800')]


    # Step 2: Keep only 'Company Name', 'Address', and 'Contact' in the cleaned dictionary
    final_cleaned_data = [{'CompanyName': entry['CompanyName'], 'Address': entry['Address'], 'Contact': entry['Contact']} for entry in cleaned_data]

    print("Cleaned Data:")
    for entry in final_cleaned_data:
        print(entry)

    return final_cleaned_data

# Call the cleaning function on scraped_data_list
cleaned_data = clean_data(scraped_data_list)

# Part 6: Upload Cleaned Data to Airtable

# Airtable API setup (ensure you replace these with your actual Airtable credentials)
# Airtable API setup
# AIRTABLE_API_KEY = 'patF55CtWdPT4xLGM.cc78d8b02df5e87cf80307e305118bb1ce94b36da8a699fbb0452849ea4cd503'
# BASE_ID = 'appls71BBO4hL6cBx'
# TABLE_NAME = 'Data'
# airtable = Airtable(BASE_ID, TABLE_NAME, AIRTABLE_API_KEY)

# # Function to upload a single row to Airtable
# def upload_to_airtable(row):
#     company_name = row['Company Name']
    
#     try:
#         # Search for existing records by 'Company Name' to avoid duplicates
#         existing_records = airtable.search('Company Name', company_name)
        
#         if len(existing_records) == 0:  # No existing record, insert new one
#             record = {
#                 'Company Name': row['Company Name'],
#                 'Address': row['Address'],
#                 'Contact': row['Contact']
#             }
#             airtable.insert(record)
#             print(f"Inserted: {company_name}")
#         else:
#             print(f"Duplicate found: {company_name} - skipping.")
    
#     except Exception as e:
#         print(f"Error uploading {company_name}: {e}")

# # Iterate over the cleaned data and upload each row to Airtable with a delay
# for entry in cleaned_data:
#     upload_to_airtable(entry)
#     time.sleep(0.2)  # Add a 200ms delay between requests to limit to 5 requests per second

# print("Data upload complete.")





###############################         PART 6 UPDATED
# Airtable API setup (ensure you replace these with your actual Airtable credentials)
# AIRTABLE_API_KEY = 'patF55CtWdPT4xLGM.cc78d8b02df5e87cf80307e305118bb1ce94b36da8a699fbb0452849ea4cd503'
# BASE_ID = 'appls71BBO4hL6cBx'
# TABLE_NAME = 'Data'
# airtable = Airtable(BASE_ID, TABLE_NAME, AIRTABLE_API_KEY)

# # Function to upload a single row to Airtable
# def upload_to_airtable(row):
#     company_name = row['CompanyName']  # Use the correct key from the cleaned data
    
#     try:
#         # Search for existing records in Airtable by 'Company Name' to avoid duplicates
#         existing_records = airtable.search('Company Name', company_name)
        
#         if len(existing_records) == 0:  # No existing record, insert new one
#             record = {
#                 'Company Name': row['CompanyName'],  # Map to 'Company Name' in Airtable
#                 'Address': row['Address'],
#                 'Contact': row['Contact']
#             }
#             airtable.insert(record)
#             print(f"Inserted: {company_name}")
#         else:
#             print(f"Duplicate found: {company_name} - skipping.")
    
#     except Exception as e:
#         print(f"Error uploading {company_name}: {e}")

# # Iterate over the cleaned data and upload each row to Airtable with a delay
# for entry in cleaned_data:
#     upload_to_airtable(entry)
#     time.sleep(0.2)  # Add a 200ms delay between requests to limit to 5 requests per second

# print("Data upload complete.")
