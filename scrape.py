import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json


# Selenium setup for headless mode
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


# Base URL for Texas Speed website
base_url = "https://www.texas-speed.com/"

# Shared data list
product_data = []


# Function to scrape product details from a product page
def scrape_product_page(product_url):
    driver = create_driver()
    try:
        driver.get(product_url)
        time.sleep(1)  # Wait for the page to load

        # Extract product name
        try:
            product_name = driver.find_element(By.CSS_SELECTOR, "div.product > h1").text.strip()
        except Exception:
            product_name = "Unavailable"

        # Extract product number
        try:
            product_number = driver.find_element(By.CSS_SELECTOR, "div.product-number").text.strip()
        except Exception:
            product_number = "Unavailable"

        # Extract price from JSON-LD script
        try:
            script_element = driver.find_element(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
            json_data = json.loads(script_element.get_attribute("innerHTML"))
            product_price = json_data["offers"]["price"].rstrip("0").rstrip(".")  # Remove trailing zeros
        except Exception:
            product_price = "Unavailable"

        return {
            "Product Name": product_name,
            "Product Number": product_number,
            "Price": product_price

        }
    finally:
        driver.quit()


# Function to scrape products from a page (subcategory or category without subcategories)
def scrape_products_from_page(page_url):
    driver = create_driver()
    try:
        driver.get(page_url)
        print(f"Scraping products from: {page_url}")

        # Locate all product links
        products = driver.find_elements(By.CSS_SELECTOR, "ul.product-listing li a")
        for product in products:
            try:
                product_url = product.get_attribute("href").strip()
                product_details = scrape_product_page(product_url)
                product_data.append(product_details)
                print(f"Scraped product: {product_details}")
            except Exception as e:
                print(f"Error scraping product: {e}")
    finally:
        driver.quit()


# Function to scrape subcategories or products directly if no subcategories exist
def scrape_subcategories_or_products(category_url):
    driver = create_driver()
    try:
        driver.get(category_url)
        time.sleep(1)  # Wait for the page to load

        # Locate subcategories
        subcategories = driver.find_elements(By.CSS_SELECTOR, "ul.subcategory-listing li a")
        if subcategories:
            print(f"Found subcategories in: {category_url}")
            for subcategory in subcategories:
                try:
                    subcategory_url = subcategory.get_attribute("href").strip()
                    print(f"Accessing subcategory: {subcategory_url}")
                    scrape_products_from_page(subcategory_url)
                except Exception as e:
                    print(f"Error scraping subcategory: {e}")
        else:
            print(f"No subcategories found. Scraping products directly from: {category_url}")
            scrape_products_from_page(category_url)
    finally:
        driver.quit()


# Main scraping logic
print("Starting scraping...")

# Step 1: Scrape category links
def scrape_category_links():
    driver = create_driver()
    try:
        driver.get(base_url)
        time.sleep(1)  # Wait for the page to load

        # Locate the "Shop By Category" menu
        categories = driver.find_elements(By.CSS_SELECTOR, 'ul.main-menu li div.submenu ul li a')
        category_links = []

        for category in categories:
            try:
                category_url = category.get_attribute("href").strip()
                category_links.append(category_url)
                print(f"Found category URL: {category_url}")
            except Exception as e:
                print(f"Error extracting category URL: {e}")

        return category_links
    finally:
        driver.quit()


# Step 2: Scrape products and subcategories
category_urls = scrape_category_links()
if not category_urls:
    print("No categories found. Exiting.")
    exit()

for category_url in category_urls:
    scrape_subcategories_or_products(category_url)

# Step 3: Save the scraped data to a CSV file
csv_file = "texas_speed_products.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Product Name", "Product Number", "Price"])
    writer.writeheader()
    writer.writerows(product_data)

print(f"Scraped data saved to {csv_file}")
