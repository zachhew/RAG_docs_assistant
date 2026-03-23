from langchain_core.documents import Document


def build_prompt(question: str, documents: list[Document]) -> str:
    context_blocks = []

    for i, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown")
        title = doc.metadata.get("title", "unknown")
        content = doc.page_content.strip()

        context_blocks.append(
            f"[Document {i}]\n"
            f"Title: {title}\n"
            f"Source: {source}\n"
            f"Content:\n{content}"
        )

    context = "\n\n".join(context_blocks)

    return f"""
    You are a helpful documentation assistant.
    
    Answer the user's question using ONLY the provided context.
    If the answer is not present in the context, say clearly that you do not know based on the available documentation.
    Do not invent APIs, parameters, behaviors, or file names.
    Be concise but useful.
    
    User question:
    {question}
    
    Context:
    {context}
    """.strip()