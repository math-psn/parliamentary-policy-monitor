import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

sources = [
    {
        "name": "House of Commons",
        "url": "https://www.ourcommons.ca/DocumentViewer/en/house/latest/hansard"
    },
    {
        "name": "Senate",
        "url": "https://sencanada.ca/en/in-the-chamber/debates/"
    }
]

keywords = [
    # Core nonprofit terms
    "charity",
    "charities",
    "charitable",
    "volunteer",
    "volunteers",
    "voluntary",
    "NGO",
    "NGOs",
    "non-profit",
    "nonprofit",
    "not-for-profit",
    "non-governmental",
    "non gov",
    "donation",
    "donations",

    # Sector terminology
    "nonprofit sector",
    "non-profit sector",
    "not-for-profit sector",
    "charitable sector",
    "voluntary sector",
    "civil society",

    # Organization types
    "community organization",
    "community organizations",
    "community group",
    "community groups",
    "local organization",
    "local organizations",
    "faith group",
    "faith groups",
    "service provider",
    "service providers",
    "food bank",
    "food banks",
    "social enterprise",
    "social enterprises",

    # Government and funding language
    "grant recipient",
    "grant recipients",
    "beneficiary",
    "beneficiaries",
    "settlement services",
    "organizations delivering settlement services",

    # General terms
    "community",
    "communities",
    "social",
    "the sector"
]

print("Searching Hansard...\n")

results = []

for source in sources:

    print(f"Checking: {source['name']}")

    response = requests.get(source["url"])
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    print(f"Text length: {len(text)}")

    lower_text = text.lower()

    for word in keywords:

        start_search = 0

        while True:

            position = lower_text.find(word.lower(), start_search)

            if position == -1:
                break

            start = max(0, position - 150)
            end = position + len(word) + 250

            context = text[start:end]

            print(f"FOUND: {word}")
            print(context)
            print("\n--------------------\n")

            results.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": source["name"],
                "keyword": word,
                "context": context
            })

            start_search = position + len(word)

df = pd.DataFrame(results)

df.to_csv("data/hansard_mentions.csv", index=False)

print(f"\nFound {len(results)} total mentions.")
print("Saved results to data/hansard_mentions.csv")
print("Done")