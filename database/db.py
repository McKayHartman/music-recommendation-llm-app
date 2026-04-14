from pathlib import Path
from typing import Iterable, Optional

import chromadb
import requests
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions

try:
    from .api import fetch_all_documents, fetch_documents
    from .document import Document
except ImportError:
    from api import fetch_all_documents, fetch_documents
    from document import Document


DEFAULT_COLLECTION_NAME = "music_sem"
DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "chroma_db"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL):
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)


def get_client(persist_directory: Optional[Path] = None) -> chromadb.PersistentClient:
    db_path = Path(persist_directory or DEFAULT_DB_PATH)
    db_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(db_path))


def get_collection(
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_directory: Optional[Path] = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> Collection:
    client = get_client(persist_directory=persist_directory)
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=get_embedding_function(model_name=model_name),
    )


def upsert_documents(collection: Collection, documents: Iterable[Document]) -> int:
    docs = list(documents)
    if not docs:
        return 0

    collection.upsert(
        ids=[doc.get_id() for doc in docs],
        documents=[doc.get_description() for doc in docs],
        metadatas=[doc.get_metadata() for doc in docs],
    )
    return len(docs)


def build_database(
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_directory: Optional[Path] = None,
    dataset_offset: int = 0,
    dataset_length: Optional[int] = None,
    batch_size: int = 100,
) -> Collection:
    collection = get_collection(
        collection_name=collection_name,
        persist_directory=persist_directory,
    )

    try:
        if dataset_length is None:
            documents = fetch_all_documents(
                start_offset=dataset_offset,
                batch_size=batch_size,
            )
        else:
            documents = fetch_documents(offset=dataset_offset, length=dataset_length)
        upsert_documents(collection, documents)
    except requests.RequestException as exc:
        if collection.count() == 0:
            raise RuntimeError(
                "Could not fetch the MusicSem dataset from Hugging Face, and no local "
                "Chroma cache is available yet."
            ) from exc

    return collection


def query_database(
    query: str,
    n_results: int = 5,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_directory: Optional[Path] = None,
    include: Optional[list[str]] = None,
):
    collection = get_collection(
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    return collection.query(
        query_texts=[query],
        n_results=n_results,
        include=include or ["documents", "metadatas", "distances"],
    )


def retrieve(
    query: str,
    n_results: int = 5,
    dataset_length: Optional[int] = None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_directory: Optional[Path] = None,
):
    collection = build_database(
        collection_name=collection_name,
        persist_directory=persist_directory,
        dataset_length=dataset_length,
    )
    return collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )


if __name__ == "__main__":
    results = retrieve(query="Heavy metal yet calming", n_results=3)
    print(results)
