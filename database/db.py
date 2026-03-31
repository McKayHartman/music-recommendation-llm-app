import chromadb
from api import document_list
from chromadb.utils import embedding_functions

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
	model_name="all-MiniLM-L6-v2"
)

chroma_client = chromadb.Client(
	chromadb.config.Settings(
		persist_directory="./chroma_db"
	)
)

# switch \`create_collection\` to \`get_or_create_collection\` to avoid creating a new collection every time
collection = chroma_client.get_or_create_collection(
	name="my_collection",
	embedding_function=embedding_function
)

# switch \`add\` to \`upsert\` to avoid adding the same documents every time
collection.upsert(
	documents=[doc.get_description() for doc in document_list], # list of documents to add
	ids=[str(doc.get_id()) for doc in document_list] # list of IDs for the documents)
)
# chroma_client.persist() *** DEPRICATED 

results = collection.query(
    query_texts=["piano background acoustic"], # Chroma will embed this for you
    n_results=1 # how many results to return
)

print(results)