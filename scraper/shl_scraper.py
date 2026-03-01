from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time

def scrape_shl_catalog(output_file="../data/raw_assessments.json"):
    assessments = []
    
    print("Launching browser...")
    with sync_playwright() as p:
        # headless=False opens a visible browser. You can watch it work!
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        start_idx = 0
        
        while True:
            url = f"https://www.shl.com/products/product-catalog/?start={start_idx}&type=1"
            print(f"Scraping {url}...")
            
            try:
                # domcontentloaded is faster and less prone to timeout than networkidle
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # Hard wait to allow SHL's JavaScript to populate the tables
                time.sleep(5) 
            except Exception as e:
                print(f"Page load timed out or failed: {e}")
                break

            # Accept cookies on the very first page if the banner appears
            if start_idx == 0:
                try:
                    page.click("button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=2000)
                    print("Accepted cookies.")
                    time.sleep(2)
                except:
                    pass # Banner didn't appear, move on
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all table wrappers
            table_wrappers = soup.find_all('div', class_='custom__table-wrapper')
            
            target_table = None
            for wrapper in table_wrappers:
                header = wrapper.find('th', class_='custom__table-heading__title')
                if header and 'Individual Test Solutions' in header.text:
                    target_table = wrapper
                    break
            
            # Fallback if text varies
            if not target_table and table_wrappers:
                target_table = table_wrappers[-1]
                
            if not target_table:
                print("No valid tables found on this page. Reached the end.")
                break
                
            rows = target_table.find_all('tr')
            data_rows = rows[1:] # Skip the header row
            
            if len(data_rows) == 0:
                print("No more items found in the table.")
                break
                
            items_on_page = 0
            for row in data_rows:
                cells = row.find_all('td')
                if len(cells) < 4:
                    continue
                    
                title_td = cells[0]
                link_tag = title_td.find('a')
                if not link_tag:
                    continue
                    
                name = link_tag.text.strip()
                href = link_tag['href']
                item_url = "https://www.shl.com" + href if href.startswith('/') else href
                
                remote_td = cells[1]
                remote_support = "Yes" if remote_td.find('span', class_=lambda c: c and '-yes' in c) else "No"
                
                adaptive_td = cells[2]
                adaptive_support = "Yes" if adaptive_td.find('span', class_=lambda c: c and '-yes' in c) else "No"
                
                types_td = cells[3]
                type_spans = types_td.find_all('span', class_='product-catalogue__key')
                test_types = [span.text.strip() for span in type_spans]
                
                type_mapping = {
                    "A": "Ability & Aptitude",
                    "B": "Biodata & Situational Judgement",
                    "C": "Competencies",
                    "D": "Development & 360",
                    "E": "Assessment Exercises",
                    "K": "Knowledge & Skills",
                    "P": "Personality & Behavior",
                    "S": "Simulations"
                }
                full_test_types = [type_mapping.get(t, t) for t in test_types]
                
                assessment = {
                    "name": name,
                    "url": item_url,
                    "description": f"{name} is an assessment focusing on {', '.join(full_test_types)}.",
                    "duration": 30, 
                    "adaptive_support": adaptive_support,
                    "remote_support": remote_support,
                    "test_type": full_test_types
                }
                assessments.append(assessment)
                items_on_page += 1
                
            print(f"Found {items_on_page} items on this page. Total so far: {len(assessments)}")
            
            if items_on_page == 0:
                break
                
            start_idx += 12

        browser.close()

    print(f"\n--- SCRAPING COMPLETE ---")
    print(f"Successfully saved {len(assessments)} assessments to {output_file}.")
    
    with open(output_file, 'w') as f:
        json.dump(assessments, f, indent=4)

if __name__ == "__main__":
    scrape_shl_catalog()