import requests
import json

from document import Document

url = "https://datasets-server.huggingface.co/rows?dataset=AMSRNA%2FMusicSem&config=default&split=train&offset=0&length=100"

response = requests.get(url)


if response.status_code == 200:
	data = response.json()
	row_count = len(data['rows'])

	document_list = []
	for i in range(row_count):
		json_item = data['rows'][i]["row"]
		document = Document(
			id=i, 
			description=f"""
			Descriptive: {json_item["descriptive"]},
			Artist: {json_item["artist"]},
			Song: {json_item["song"]},
			Contextual: {json_item["contextual"]},
			Atmospheric: {json_item["atmospheric"]},
			Metadata: {json_item["metadata"]},
			Pairs: {json_item["pairs"]}	
			"""	
		)
		document_list.append(document)
	
	# print(document_list[99].get_metadata())
	
else:
	print(f"Failure Status code: {response.status_code}. Response: {response.text}")