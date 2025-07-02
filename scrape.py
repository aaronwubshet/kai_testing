import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime
import csv

# Base URL and search parameters
BASE_URL = "https://www.prosportstransactions.com/basketball/Search/SearchResults.php"
PARAMS = {
    "Player": "",
    "Team": "",
    "BeginDate": "2010-01-01",
    "EndDate": "2024-12-31",
    "ILChkBx": "yes",
    "InjuriesChkBx": "yes",
    "Injuries": "acl",
    "Submit": "Search",
    "sort": "0",
    "start": 0,
}

def extract_acl_injuries():
    injury_count_by_year = defaultdict(int)
    while True:
        print(f"Scraping entries starting from: {PARAMS['start']}")
        response = requests.get(BASE_URL, params=PARAMS)
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.select("table.datatable tr")[1:]
        if not rows:
            break

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 1:
                continue
            date_str = cols[0].get_text(strip=True)
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                injury_count_by_year[date_obj.year] += 1
            except ValueError:
                continue

        PARAMS["start"] += 25

    return dict(sorted(injury_count_by_year.items()))

def export_to_csv(data, filename="acl_injuries_by_year.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Year", "ACL Injuries"])
        for year, count in data.items():
            writer.writerow([year, count])
    print(f"Data exported to {filename}")

# Main execution
if __name__ == "__main__":
    acl_by_year = extract_acl_injuries()
    export_to_csv(acl_by_year)
