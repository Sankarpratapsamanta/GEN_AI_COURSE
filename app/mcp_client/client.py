from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_client = MultiServerMCPClient(
    {
        "hr":{
            "transport":"streamable_http",
            "url":"http://127.0.0.1:8001/mcp",
        },
        "engineering":{
            "transport":"streamable_http",
            "url":"http://127.0.0.1:8002/mcp",
        }
    }
)

async def get_mcp_tools():
    tools = await mcp_client.get_tools()

    return tools