import requests

url = "https://sencanada.ca/en/in-the-chamber/debates/"

response = requests.get(url)

html = response.text

print("HTML length:", len(html))

print("\nSearching for Hansard references...\n")

terms = [
    "2026",
    "June",
    "Debate",
    "Hansard",
    "45-1"
]

for term in terms:
    if term.lower() in html.lower():
        print("FOUND:", term)
    else:
        print("NOT FOUND:", term)