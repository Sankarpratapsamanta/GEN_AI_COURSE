from app.rag.vector import vectorstore

retriever = vectorstore.as_retriever(search_kwargs={
    "k":2
})
