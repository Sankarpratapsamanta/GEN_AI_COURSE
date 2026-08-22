from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Engineering MCP SERVER")


@mcp.tool(description="""Get the deployment status of an application

Supported applications:
-company-api
-company api
-company
-frontend
-mobile-api
""")
def get_deployment_status(application: str):

    print(application)
    deployments = {
        "company-api":"Company Api deployment is healthy",
        "frontend":"Frontend deployment is healthy",
        "mobile-api":"Mobile Api deployment is healthy"
    }

    return deployments.get(application,
                         f"No deployment found for"
                         f"{application}"
                         )

@mcp.tool(description="Get the current service version")
def get_service_version(service:str):
    versions={
        "company-api":"v2.3.1",
        "frontend":"v1.0.0",
        "mobile-api":"v1.8.0"
    }

    return versions.get(service,f"No service found for {service}")


if __name__ == "__main__":
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = 8002
    mcp.run(transport="streamable-http")