from typing import List

import requests

try:
    from .document import Document
except ImportError:
    from document import Document


DATASET_URL = (
    "https://datasets-server.huggingface.co/rows"
    "?dataset=AMSRNA%2FMusicSem&config=default&split=train"
)


def _format_description(row: dict) -> str:
    return "\n".join(
        [
            f"Descriptive: {row.get('descriptive', '')}",
            f"Artist: {row.get('artist', '')}",
            f"Song: {row.get('song', '')}",
            f"Contextual: {row.get('contextual', '')}",
            f"Atmospheric: {row.get('atmospheric', '')}",
            f"Metadata: {row.get('metadata', '')}",
            f"Pairs: {row.get('pairs', '')}",
        ]
    )


def fetch_documents(offset: int = 0, length: int = 100, timeout: int = 30) -> List[Document]:
    response = requests.get(
        f"{DATASET_URL}&offset={offset}&length={length}",
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()
    rows = data.get("rows", [])

    documents = []
    for index, item in enumerate(rows):
        row = item.get("row", {})
        doc_id = row.get("id", offset + index)
        metadata = {
            "artist": row.get("artist", ""),
            "song": row.get("song", ""),
            "contextual": row.get("contextual", ""),
            "atmospheric": row.get("atmospheric", ""),
            "metadata": row.get("metadata", ""),
            "pairs": row.get("pairs", ""),
        }
        documents.append(
            Document(
                id=str(doc_id),
                description=_format_description(row),
                metadata=metadata,
            )
        )

    return documents


try:
    document_list = fetch_documents()
except requests.RequestException:
    document_list = []
