from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

documents = [
     Document(
         page_content="Employees receive 20 paid leave days per year",
         metadata={
             "category":"leave",
             "department":"hr"
         }
     ),
     Document(
         page_content="The company provides health insurance to all full-time employees",
         metadata={
             "category":"insurance",
             "department":"hr"
         }
     ),
     Document(
         page_content="The company working hours are form 9 AM TO 6 Pm",
         metadata={
             "category":"working-hours",
             "department":"hr"
         }
     ),
 ]


vectorstore = Chroma.from_documents(
     documents=documents,
     embedding=embeddings,
     collection_name="company_documents"
)

