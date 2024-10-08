Script Overview
Part 1: Google Scraping
Initializes Selenium WebDriver to scrape job listings from a list of Google search URLs.
Extracts company names and addresses from the search results.
Part 2: Yellow Pages Lookup
For each scraped company, constructs a URL to search for additional information on Yellow Pages.
Extracts the company name and contact phone number from Yellow Pages.
Part 3: Google WoPH Lookup
Constructs a search URL for Google to find additional company information.
Scrapes the Google search results for contact details.
Part 4: Airtable Integration
After gathering all the data, connects to Airtable and uploads the scraped data into the specified table.
Example Data Structure
The script organizes the scraped data into a structured format with the following fields:

CompanyName: Name of the company
Address: Address of the company
Yellow Page Company Name: Company name retrieved from Yellow Pages
Yellow Page Contact: Phone number retrieved from Yellow Pages
Google WoPH Company Name: Company name retrieved from Google WoPH
Google WoPH Contact: Phone number retrieved from Google WoPH
Company to Yellow Match %: Match percentage between Google and Yellow Pages company names
Company to Google Match %: Match percentage between Google company names
Contact: Final contact field
