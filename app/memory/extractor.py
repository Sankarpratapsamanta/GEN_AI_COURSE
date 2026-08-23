from langchain_core.messages import HumanMessage

MEMORY_EXTRACTION_PROMPT="""
You are a memory extraction system.

Analyze the conversation and determine weather there is any durable information about the user that would be
useful in future conversations.

Only extract information that is:
-about the user
-likely to remain useful
-explicit or strongly supported

DO NOT extract:
-temorary requests
-general knowledge
-questions
-one-time tasks
-information about unrelated people

if there is useful memory,return it as a short plain-text statement

if there is no useful memory, return exactly:
NO_MEMORY
"""

async def extract_memory(llm,user_message:str,assistant_message:str):
    prompt=f"""
    {MEMORY_EXTRACTION_PROMPT}
    
    User message: {user_message}
    
    Assistant message: {assistant_message}
"""
    res = await llm.ainvoke([HumanMessage(content=prompt)])

    content = res.content.strip()

    if content == "NO_MEMORY":
        return None
    return content

