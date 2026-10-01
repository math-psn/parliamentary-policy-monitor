import requests

url = "https://sencanada.ca/en/in-the-chamber/debates/"

response = requests.get(url)

print("Status code:", response.status_code)

print(response.text[:500])