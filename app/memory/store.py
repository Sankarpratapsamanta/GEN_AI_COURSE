from typing import Any

conversation_store:dict[str, list[dict[str,Any]]] = {}


def get_messages(conversation_id: str):
    return conversation_store.get(conversation_id,[])

def add_message(conversation_id: str,role:str, content: str):
    if conversation_id not in conversation_store:
        conversation_store[conversation_id] = []

    conversation_store[conversation_id].append({
        "role":role,
        "content":content
    })


