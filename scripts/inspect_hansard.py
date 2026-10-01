import requests
from bs4 import BeautifulSoup


url = "https://sencanada.ca/en/content/sen/chamber/451/debates/086db_2026-06-18-e"


response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")


print("Searching page text...\n")


text = soup.get_text("\n", strip=True)

lines = text.split("\n")


# Look for possible speaker/debate markers

for i, line in enumerate(lines):

    if (
        "Hon." in line
        or "Senator" in line
        or "The Speaker" in line
        or "Honourable" in line
    ):

        print("FOUND POSSIBLE SPEAKER:")
        print("Line number:", i)
        print(line)

        print("\nContext:")
        
        for context_line in lines[i:i+5]:
            print(context_line)

        print("--------------------")