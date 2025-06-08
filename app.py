import click
import httpx
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
import uvicorn
import os
from githubmcp import GitHubAgent

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github_agent = GitHubAgent(GITHUB_TOKEN)

@click.command()
@click.option("--port", default=8080, help="Port to listen on for SSE")
def main(port: int) -> int:
    app = Server("github-mcp-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "create_pr":
            return [
                types.TextContent(
                    type="text",
                    text=str(github_agent.create_pull_request(
                        owner=arguments["owner"],
                        repo=arguments["repo"],
                        title=arguments["title"],
                        head_branch=arguments["head_branch"],
                        base_branch=arguments["base_branch"],
                        body=arguments.get("body")
                    ))
                )
            ]
        elif name == "create_branch":
            return [
                types.TextContent(
                    type="text",
                    text=str(github_agent.create_branch(
                        owner=arguments["owner"],
                        repo=arguments["repo"],
                        new_branch=arguments["new_branch"],
                        base_branch=arguments["base_branch"]
                    ))
                )
            ]
        elif name == "push_file":
            return [
                types.TextContent(
                    type="text",
                    text=str(github_agent.push_file(
                        owner=arguments["owner"],
                        repo=arguments["repo"],
                        branch=arguments["branch"],
                        file_path=arguments["file_path"],
                        content=arguments["content"],
                        commit_message=arguments["commit_message"]
                    ))
                )
            ]
        elif name == "git_clone":
            return [
                types.TextContent(
                    type="text",
                    text=str(github_agent.git_clone(
                        clone_url=arguments["clone_url"],
                        clone_path=arguments["clone_path"]
                    ))
                )
            ]
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="create_pr",
                description="Create a GitHub Pull Request",
                inputSchema={
                    "type": "object",
                    "required": ["owner", "repo", "title", "head_branch", "base_branch"],
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "title": {"type": "string"},
                        "head_branch": {"type": "string"},
                        "base_branch": {"type": "string"},
                        "body": {"type": "string"},
                    },
                },
            ),
            types.Tool(
                name="create_branch",
                description="Create a new GitHub branch",
                inputSchema={
                    "type": "object",
                    "required": ["owner", "repo", "new_branch", "base_branch"],
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "new_branch": {"type": "string"},
                        "base_branch": {"type": "string"},
                    },
                },
            ),
            types.Tool(
                name="push_file",
                description="Push a new file to GitHub",
                inputSchema={
                    "type": "object",
                    "required": ["owner", "repo", "branch", "file_path", "content", "commit_message"],
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "branch": {"type": "string"},
                        "file_path": {"type": "string"},
                        "content": {"type": "string"},
                        "commit_message": {"type": "string"},
                    },
                },
            ),
            types.Tool(
                name="git_clone",
                description="Clone a GitHub repository",
                inputSchema={
                    "type": "object",
                    "required": ["clone_url", "clone_path"],
                    "properties": {
                        "clone_url": {"type": "string"},
                        "clone_path": {"type": "string"},
                    },
                },
            )
        ]

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    return 0


if __name__ == "__main__":
    main()
