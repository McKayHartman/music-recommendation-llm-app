from database.db import retrieve


def run_rag(query: str, n_results: int = 5, dataset_length: int = 100):
    return retrieve(
        query=query,
        n_results=n_results,
        dataset_length=dataset_length,
    )


if __name__ == "__main__":
    results = run_rag("Heavy metal yet calming", n_results=3)
    print(results)
