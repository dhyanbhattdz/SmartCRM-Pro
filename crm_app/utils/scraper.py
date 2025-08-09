import requests
from bs4 import BeautifulSoup
import random
import time

# Mock company database
mock_companies = [
    "Tata Consultancy Services",
    "Infosys Technologies",
    "Wipro Ltd.",
    "HCL Tech",
    "Capgemini India",
    "Google India",
    "Microsoft Corporation",
    "Cognizant",
    "Tech Mahindra",
    "IBM India"
]

def get_company_info(name):
    """
    Simulates fetching a company name based on customer name using mock scraping logic.
    """
    time.sleep(1)  # Simulate delay
    print(f"[Scraper] Getting company info for '{name}'...")

    # Simulate a company match using name similarity logic
    lowercase_name = name.lower()
    for company in mock_companies:
        if lowercase_name.split()[0] in company.lower():
            return company

    # Fallback: Return a random company
    return random.choice(mock_companies)
