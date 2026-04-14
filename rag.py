from typing import Optional

from database.db import retrieve


def run_rag(query: str, n_results: int = 5, dataset_length: Optional[int] = None):
    return retrieve(
        query=query,
        n_results=n_results,
        dataset_length=dataset_length,
    )


def get_recommendations(query: str, n_results: int = 5, dataset_length: Optional[int] = None):
    results = run_rag(query=query, n_results=n_results, dataset_length=dataset_length)

    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])
    distances = results.get("distances", [[]])
    ids = results.get("ids", [[]])

    recommendations = []
    for index, metadata in enumerate(metadatas[0] if metadatas else []):
        recommendations.append(
            {
                "id": ids[0][index] if ids and ids[0] and index < len(ids[0]) else None,
                "document": (
                    documents[0][index]
                    if documents and documents[0] and index < len(documents[0])
                    else ""
                ),
                "metadata": metadata or {},
                "distance": (
                    distances[0][index]
                    if distances and distances[0] and index < len(distances[0])
                    else None
                ),
            }
        )

    return recommendations


def format_recommendations_for_prompt(
    query: str,
    n_results: int = 5,
    dataset_length: Optional[int] = None,
) -> str:
    recommendations = get_recommendations(
        query=query,
        n_results=n_results,
        dataset_length=dataset_length,
    )

    if not recommendations:
        return "No matching songs were retrieved."

    sections = []
    for index, item in enumerate(recommendations, start=1):
        metadata = item.get("metadata", {})
        sections.append(
            "\n".join(
                [
                    f"Match {index}",
                    f"Artist: {metadata.get('artist', 'Unknown')}",
                    f"Song: {metadata.get('song', 'Unknown')}",
                    f"Why it may fit: {metadata.get('contextual', '')}",
                    f"Mood: {metadata.get('atmospheric', '')}",
                    f"Extra tags: {metadata.get('metadata', '')}",
                ]
            )
        )

    return "\n\n".join(sections)


if __name__ == "__main__":
    results = run_rag("Heavy metal yet calming", n_results=3)
    print(results)
