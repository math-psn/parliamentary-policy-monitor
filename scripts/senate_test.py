import requests
from bs4 import BeautifulSoup

url = "https://sencanada.ca/en/in-the-chamber/debates/"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

print("Searching for debate links...\n")

links = soup.find_all("a")

count = 0

for link in links:

    text = link.get_text(" ", strip=True)
    href = link.get("href")

    if href and ("debates" in href.lower() or "hansard" in href.lower()):

        print(text)
        print(href)
        print("--------------------")

        count += 1

print("\nTotal possible debate links:", count)