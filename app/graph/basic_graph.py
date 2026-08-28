from typing import TypedDict
from langgraph.graph import (StateGraph,START,END)


# State
class AgentState(TypedDict):
    messages:str
    processed_message:str
    response:str



def getting_node(state:AgentState):
    return {
        "message":f"My name is John"
    }

def process_message(state:AgentState):
    processed = state["messages"]
    return {
        "processed_message":processed
    }

def generate_response(state:AgentState):
    return{
        "response":f"You Said : {state['processed_message']}"
    }

def route_question(state:AgentState):
    if "Rahul" in state["processed_message"]:
        return "rag"
    return "direct"

def rag_fun(state:AgentState):
    return {
        "response":f"Rag tool should be called"
    }

def direct_fun(state:AgentState):
    return {
        "response":f"Direct LLM should be called"
    }

builder = StateGraph(AgentState)

# Node
builder.add_node("greeting",getting_node)
builder.add_node("process",process_message)
# builder.add_node("generate",generate_response)
builder.add_node("rag",rag_fun)
builder.add_node("direct",direct_fun)

#Edge

builder.add_edge(START,"greeting")
builder.add_edge("greeting","process")
builder.add_conditional_edges(
    "process",
    route_question,
    {
        "rag":"rag",
        "direct":"direct"
    }
)
builder.add_edge("rag",END)
builder.add_edge("direct",END)

graph = builder.compile()

if __name__ == "__main__":
    res = graph.invoke({
        "message":"My name is AMIT",
        "response":""
    })

    print(res)

