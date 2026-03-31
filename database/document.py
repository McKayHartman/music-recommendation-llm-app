#  document value = hf descriptive
#  metadata value = dict hf artist name, song name, contextual, atmospheric, metadata, pairs
#  id value = hf unique identifier for the document


class Document:
	def __init__(self, id, description):
		self.id = id
		self.description = description



	# Getters
	def get_id(self):
		return self.id
	
	def get_description(self):
		return self.description


	# Setters
	def set_id(self, id):
		self.id = id

	def set_description(self, description):
		self.description = description
