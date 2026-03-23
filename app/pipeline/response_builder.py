from app.api.schemes.ask import Citation


def build_citations(documents) -> list[Citation]:
    citations = []

    for doc in documents:
        citations.append(
            Citation(
                chunk_id=doc.metadata["chunk_id"],
                source=doc.metadata["source"],
                title=doc.metadata["title"],
                url=doc.metadata.get("url"),
                score=doc.metadata.get("score"),
            )
        )

    return citations