import time
from typing import List, Optional

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
            f"Spotify Link: {row.get('spotify_link', '')}",
            f"Contextual: {row.get('contextual', '')}",
            f"Atmospheric: {row.get('atmospheric', '')}",
            f"Metadata: {row.get('metadata', '')}",
            f"Pairs: {row.get('pairs', '')}",
        ]
    )


def fetch_documents(
    offset: int = 0,
    length: int = 100,
    timeout: int = 30,
    retries: int = 3,
    retry_delay: float = 1.5,
) -> List[Document]:
    last_error = None

    for attempt in range(retries):
        try:
            response = requests.get(
                f"{DATASET_URL}&offset={offset}&length={length}",
                timeout=timeout,
            )
            response.raise_for_status()
            break
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries - 1:
                raise
            time.sleep(retry_delay * (attempt + 1))

    if last_error and "response" not in locals():
        raise last_error

    data = response.json()
    rows = data.get("rows", [])

    documents = []
    for index, item in enumerate(rows):
        row = item.get("row", {})
        doc_id = row.get("id", offset + index)
        metadata = {
            "artist": row.get("artist", ""),
            "song": row.get("song", ""),
            "spotify_link": row.get("spotify_link", ""),
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


def fetch_all_documents(
    start_offset: int = 0,
    batch_size: int = 100,
    timeout: int = 30,
    retries: int = 3,
    retry_delay: float = 1.5,
    max_documents: Optional[int] = None,
) -> List[Document]:
    all_documents: List[Document] = []
    offset = start_offset

    while True:
        current_batch_size = batch_size
        if max_documents is not None:
            remaining = max_documents - len(all_documents)
            if remaining <= 0:
                break
            current_batch_size = min(batch_size, remaining)

        batch = fetch_documents(
            offset=offset,
            length=current_batch_size,
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
        )

        if not batch:
            break

        all_documents.extend(batch)
        offset += len(batch)

        if len(batch) < current_batch_size:
            break

    return all_documents


# Removed eager loading to avoid rate limits on import
# document_list = fetch_all_documents()
