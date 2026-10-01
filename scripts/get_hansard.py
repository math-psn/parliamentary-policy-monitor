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
    "charity",
    "charities",
    "charitable",
    "volunteer",
    "volunteers",
    "voluntary",
    "NGO",
    "non-profit",
    "nonprofit",
    "not-for-profit",
    "non-governmental",
    "non gov",
    "donation",
    "donations",
    "community",
    "communities",
    "social"
]

print("Searching Hansard...\n")

results = []

for source in sources:

    print("Checking:", source["name"])

    response = requests.get(source["url"])

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    for word in keywords:

        if word.lower() in text.lower():

            print("FOUND:", word)

            position = text.lower().find(word.lower())

            start = max(0, position - 150)
            end = position + 250

            context = text[start:end]

            print(context)
            print("\n--------------------\n")

            results.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": source["name"],
                "keyword": word,
                "context": context
            })


df = pd.DataFrame(results)

df.to_csv("data/hansard_mentions.csv", index=False)

print("Saved results to data/hansard_mentions.csv")
print("Done")