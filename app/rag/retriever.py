from app.rag.vector import vectorstore
from langchain_core.tools import tool

retriever = vectorstore.as_retriever(search_kwargs={
     "k":2
})


@tool
def search_company_documents(query:str):
    """
    Search the company knowledge base.
    Use this for company policies,leave policy,remote work,insurance,working hours and other company information
    """

    documents = retriever.invoke(query)

    if not documents:
        return "No relevant documents found"

    results=[]

    for document in documents:
        results.append(
            f"Content: "
            f"{document.page_content}\n"
            f"Metadata: "
            f"{document.metadata}"
        )

    return "\n\n".join(results)