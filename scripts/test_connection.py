import requests

url = "https://www.ourcommons.ca/"

response = requests.get(url)

print(response.status_code)