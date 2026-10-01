import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


BASE_URL = "https://sencanada.ca"


KEYWORDS = [
    "charity",
    "charities",
    "charitable",
    "nonprofit",
    "non-profit",
    "not-for-profit",
    "NGO",
    "volunteer",
    "donation",
    "community organization",
    "civil society",
    "funding",
    "grant"
]


def get_debate_links():

    url = "https://sencanada.ca/en/in-the-chamber/debates/"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for link in soup.find_all("a"):

        href = link.get("href")

        if href and ("debates" in href.lower() or "hansard" in href.lower()):

            if href.startswith("/"):
                href = BASE_URL + href

            if href not in links:
                links.append(href)

    return links



def extract_date(url):

    match = re.search(r"(\d{4}-\d{2}-\d{2})", url)

    if match:
        return match.group(1)

    return ""



def search_page(url):

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    results = []

    for keyword in KEYWORDS:

        if keyword.lower() in text.lower():

            matches = re.findall(
                r".{0,120}" + keyword + r".{0,120}",
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                results.append({
                    "date": extract_date(url),
                    "chamber": "Senate",
                    "keyword": keyword,
                    "context": match,
                    "url": url
                })

    return results



print("Finding Senate debates...")

links = get_debate_links()

print(f"Found {len(links)} debate pages")


all_results = []


for i, link in enumerate(links):

    print(f"Scanning {i+1}/{len(links)}")

    results = search_page(link)

    all_results.extend(results)



df = pd.DataFrame(all_results)


df.to_csv(
    "data/senate_mentions.csv",
    index=False
)


print("Finished!")
print(f"Found {len(df)} mentions")