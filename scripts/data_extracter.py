import csv
import os

from playwright.sync_api import sync_playwright
import pandas as pd
import re
from bs4 import BeautifulSoup

def extract_mop_battle_pets(csv_path=r"../data/mop_battle_pets.csv"):
    if not os.path.exists(csv_path):
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Name", "Level", "Health", "Power", "Speed", "Breed",
                "Abilities", "Source", "Type", "Popularity", "Untameable"
            ])
    with sync_playwright() as p:
        for offset in range(0, 900, 100):
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(200000)
            url = f"https://www.wowhead.com/mop-classic/battle-pets#petspecies;{offset}" if offset else "https://www.wowhead.com/mop-classic/battle-pets#petspecies"
            print(f"Scraping: {url}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("table.listview-mode-default")
            rows = page.query_selector_all("table.listview-mode-default tbody tr")

            for row in rows:
                cells = row.query_selector_all("td")
                if not cells or len(cells) < 11:
                    continue

                name_cell = cells[1]
                name_link = name_cell.query_selector("a")
                name = name_link.inner_text().strip() if name_link else ""
                pet_id = None
                if name_link:
                    href = name_link.get_attribute("href")
                    match = re.search(r"npc=(\d+)", href or "")
                    if match:
                        pet_id = int(match.group(1))
                print(f"Processing pet: {name} (ID: {pet_id})")
                is_untameable = "untameable" in cells[1].inner_text().lower()
                level = cells[2].inner_text().strip()
                health = cells[3].inner_text().strip()
                power = cells[4].inner_text().strip()
                speed = cells[5].inner_text().strip()
                breed = cells[6].inner_text().strip()

                ability_links = cells[7].query_selector_all("a")
                abilities = []
                for link in ability_links:
                    href = link.get_attribute("href")
                    if href and "pet-ability=" in href:
                        match = re.search(r"pet-ability=(\d+)", href)
                        if match:
                            ability_id = int(match.group(1))
                            abilities.append(ability_id)
                source = cells[8].inner_text().strip().replace("\n", "-").strip()
                _type = cells[9].inner_text().strip()

                popularity_span = cells[10].query_selector("span")
                class_attr = popularity_span.get_attribute("class") if popularity_span else ""
                match = re.search(r"popularity-(\d+)", class_attr)
                popularity = int(match.group(1)) if match else None

                row = [
                    pet_id, name, level, health, power, speed, breed,
                    abilities, source, _type, popularity, is_untameable
                ]
                with open(csv_path, "a",
                          encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(row)

            browser.close()

def read_description(url, page):
    """Helper function to read the description from a pet or ability page."""
    try:
        print(f"🔗 Visiting: {url}")
        page.goto(url, wait_until="domcontentloaded")
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"]
    except Exception as e:
        print(f"⚠️ Failed to read description: {e}")
    return ""

def extract_mop_battle_pet_abilities(csv_path=r"../data/mop_battle_pet_abilities.csv"):
    if not os.path.exists(csv_path):
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Name", "Damage", "Healing", "Duration", "Cooldown",
                "Accuracy", "Type", "Popularity", "Description"
            ])

    with sync_playwright() as p:
        for offset in range(400, 900, 100):
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            detail_page = browser.new_page()
            page.set_default_timeout(200000)
            url = f"https://www.wowhead.com/battle-pet-abilities#{offset}" if offset else "https://www.wowhead.com/battle-pet-abilities"
            print(f"Scraping: {url}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("table.listview-mode-default")

            rows = page.query_selector_all("table.listview-mode-default tbody tr")

            for row in rows:
                cells = row.query_selector_all("td")
                if not cells or len(cells) < 8:
                    continue

                name_cell = cells[1]
                link = name_cell.query_selector("a")

                name = name_cell.inner_text().strip()
                ability_id = None
                if link:
                    href = link.get_attribute("href")
                    match = re.search(r"pet-ability=(\d+)", href or "")
                    if match:
                        ability_id = int(match.group(1))
                ability_url = href if href.startswith("http") else f"https://www.wowhead.com{href}"
                description = read_description(ability_url, detail_page)

                print(f"Processing ability: {name} (ID: {ability_id})")
                damage = cells[2].inner_text().strip()
                healing = cells[3].inner_text().strip()
                duration = cells[4].inner_text().strip()
                cooldown = cells[5].inner_text().strip()
                accuracy = cells[6].inner_text().strip()
                _type = cells[7].inner_text().strip()

                # Popularity via span class
                pop_span = cells[8].query_selector("span")
                popularity = None
                if pop_span:
                    class_attr = pop_span.get_attribute("class")
                    match = re.search(r"popularity-(\d+)", class_attr or "")
                    if match:
                        popularity = int(match.group(1))

                row = [
                    ability_id, name, damage, healing, duration, cooldown, accuracy, _type, popularity, description
                ]
                with open(csv_path, "a",
                          encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
            browser.close()
    print("Saved to mop_battle_pet_abilities.csv")



def extract_pet_descriptions():
    descriptions = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        list_page = browser.new_page()
        detail_page = browser.new_page()
        list_page.goto("https://www.wowhead.com/mop-classic/battle-pets#petspecies", wait_until="networkidle")
        list_page.wait_for_selector("table.listview-mode-default")

        rows = list_page.query_selector_all("table.listview-mode-default tbody tr")
        for i, row in enumerate(rows):
            cells = row.query_selector_all("td")
            if not cells or len(cells) < 2:
                continue

            name_cell = cells[1]
            link = name_cell.query_selector("a")
            name = link.inner_text().strip() if link else ""
            href = link.get_attribute("href") if link else ""
            pet_url = href if href.startswith("http") else f"https://www.wowhead.com{href}"
            description = ""

            try:
                print(f"🔗 Visiting: {pet_url}")
                detail_page.goto(pet_url, wait_until="domcontentloaded")
                html = detail_page.content()
                soup = BeautifulSoup(html, "html.parser")
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    description = meta_desc["content"]
                print(f"{name}: {description}")
            except Exception as e:
                print(f"⚠️ Failed for {name}: {e}")

            descriptions.append({"Name": name, "Description": description})

        browser.close()

    # Optional: Save to CSV
    df = pd.DataFrame(descriptions)
    df.to_csv("pet_descriptions.csv", index=False)
    print("✅ Saved to pet_descriptions.csv")

def extract_ability_descriptions():
    ability_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        list_page = browser.new_page()
        detail_page = browser.new_page()

        # Handle pagination by increasing the offset if needed
        for offset in range(0, 900, 100):  # Adjust if there are more/less abilities
            url = f"https://www.wowhead.com/battle-pet-abilities#{offset}" if offset else "https://www.wowhead.com/battle-pet-abilities"
            print(f"Scraping: {url}")
            list_page.goto(url, wait_until="networkidle")
            list_page.wait_for_selector("table.listview-mode-default")

            rows = list_page.query_selector_all("table.listview-mode-default tbody tr")
            for row in rows:
                cells = row.query_selector_all("td")
                if not cells or len(cells) < 2:
                    continue

                name_cell = cells[1]
                link = name_cell.query_selector("a")

                name = link.inner_text().strip() if link else ""
                href = link.get_attribute("href") if link else ""
                ability_url = href if href.startswith("http") else f"https://www.wowhead.com{href}"
                ability_id = None
                match = re.search(r"pet-ability=(\d+)", href or "")
                if match:
                    ability_id = int(match.group(1))

                description = ""
                try:
                    print(f"🔗 Visiting: {ability_url}")
                    detail_page.goto(ability_url, wait_until="domcontentloaded")
                    html = detail_page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc and meta_desc.get("content"):
                        description = meta_desc["content"]
                    print(f"{name}: {description}")
                except Exception as e:
                    print(f"⚠️ Failed for {name}: {e}")

                ability_data.append({
                    "ID": ability_id,
                    "Name": name,
                    "Description": description,
                    "URL": ability_url,
                })

        browser.close()

    # Save to CSV
    df = pd.DataFrame(ability_data)
    df.to_csv("ability_descriptions.csv", index=False)
    print("✅ Saved to ability_descriptions.csv")

# Run the extraction function
if __name__ == "__main__":
    extract_mop_battle_pets(r"../data/mop_battle_pets_test.csv")
    #extract_mop_battle_pet_abilities(r"../data/mop_battle_pet_abilities_test.csv")


