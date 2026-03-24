import requests
import json

# API GET to get the database
response = requests.get("https://datasets-server.huggingface.co/rows?dataset=AMSRNA%2FMusicSem&config=default&split=train&offset=0&length=1")
data = response.json()
filtered_data = data.
readable = json.dumps(data, indent=4)
print(readable)