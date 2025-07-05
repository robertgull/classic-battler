from playwright.sync_api import sync_playwright
import pandas as pd
import re


def extract_mop_battle_pets():
    data = []

    with sync_playwright() as p:
        for offset in range(0, 900, 100):
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.wowhead.com/mop-classic/battle-pets#petspecies;{offset}" if offset else "https://www.wowhead.com/mop-classic/battle-pets#petspecies"
            print(f"Scraping: {url}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("table.listview-mode-default")

            rows = page.query_selector_all("table.listview-mode-default tbody tr")

            for row in rows:
                cells = row.query_selector_all("td")
                if not cells or len(cells) < 11:
                    continue

                name_link = cells[1].query_selector("a")
                name = name_link.inner_text().strip() if name_link else ""
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

                data.append([
                    name, level, health, power, speed, breed,
                    abilities, source, _type, popularity, is_untameable
                ])

            browser.close()

    df = pd.DataFrame(data, columns=[
        "Name", "Level", "Health", "Power", "Speed", "Breed",
        "Abilities", "Source", "Type", "Popularity", "Untameable"
    ])
    df.to_csv(r"C:\Users\Rober\repos\classic-battler\data\mop_battle_pets.csv", index=False)

def extract_mop_battle_pet_abilities():
    ability_data = []

    with sync_playwright() as p:




        for offset in range(0, 900, 100):
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.wowhead.com/battle-pet-abilities#{offset}" if offset else "https://www.wowhead.com/battle-pet-abilities"
            print(f"Scraping: {url}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("table.listview-mode-default")

            rows = page.query_selector_all("table.listview-mode-default tbody tr")

            for row in rows:
                cells = row.query_selector_all("td")
                if not cells or len(cells) < 8:
                    continue

                name = cells[1].inner_text().strip()
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

                ability_data.append([
                    name, damage, healing, duration, cooldown, accuracy, _type, popularity
                ])
            browser.close()
    df = pd.DataFrame(ability_data, columns=[
        "Name", "Damage", "Healing", "Duration", "Cooldown", "Accuracy", "Type", "Popularity"
    ])
    df.to_csv(r"C:\Users\Rober\repos\classic-battler\data/mop_battle_pet_abilities.csv", index=False)
    print("Saved to mop_battle_pet_abilities.csv")



# Run the extraction function
if __name__ == "__main__":
    extract_mop_battle_pets()
    #extract_mop_battle_pet_abilities()