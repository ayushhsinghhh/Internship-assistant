import pandas as pd
import time
from playwright.sync_api import sync_playwright

INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"

def wait_and_click(page, selector, timeout=5000):
    page.wait_for_selector(selector, timeout=timeout)
    page.click(selector)

def scrape_apollo():
    df = pd.read_csv(INPUT_FILE)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Open Apollo.io and login manually (first run only)
        page.goto("https://app.apollo.io/#/login")
        print("🚪 Please log in manually in the opened browser window...")
        input("✅ Press ENTER after you're logged in.")

        for idx, row in df.iterrows():
            company = str(row['company'])
            founder = str(row['founder'])
            search_term = f"{founder} {company}"

            print(f"🔍 Searching: {search_term}")
            page.goto("https://app.apollo.io/#/people-search")

            try:
                # Wait for search bar and enter query
                page.wait_for_selector("input[placeholder='Search by name, title, company, etc.']", timeout=10000)
                search_input = page.query_selector("input[placeholder='Search by name, title, company, etc.']")
                search_input.fill(search_term)
                search_input.press("Enter")

                # Wait for search results
                page.wait_for_selector(".search-results", timeout=10000)
                time.sleep(3)  # Let results load

                # Try grabbing the first visible email
                email = None
                email_element = page.query_selector("div.contact-info__email")  # Adjust selector as needed
                if email_element:
                    email = email_element.inner_text().strip()

                results.append({
                    "company": company,
                    "founder": founder,
                    "email": email if email else "Not found"
                })

            except Exception as e:
                print(f"⚠️ Error with {search_term}: {e}")
                results.append({
                    "company": company,
                    "founder": founder,
                    "email": "Error"
                })

        # Save results
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        print(f"\n✅ Saved {len(results)} results to {OUTPUT_FILE}")

        browser.close()

if __name__ == "__main__":
    scrape_apollo()
