# GitHub MCP Server

This repository contains a GitHub MCP-compatible server implementation designed to work with the [Kagent](https://github.com/kagentai/kagent) framework. It enables GitHub automation workflows such as pull request creation, issue tracking, branch operations, and more exposed via an SSE-compatible MCP toolserver.


## Features

- SSE-based MCP server for GitHub operations  
- Supports:
  - Creating pull requests
  - Creating issues
  - Creating and pushing new branches
  - Cloning repositories
- Built-in FastAPI endpoints (for testing)
- Compatible with Kagent's `ToolServer` CRD
- Kubernetes-ready (Docker + Deployment manifests)

---


---

## How to Use

### Local Testing

1. Set the GitHub token as an environment variable:
   ```bash
   export GITHUB_TOKEN=ghp_XXXX

2. Run the server locally
   python app.py

3. Test endpoint:
curl -X POST http://localhost:8000/create_pr


### Deploy on Kubernetes with Kagent
## Build and push the Docker image:

docker build -t your-registry/github-mcp-server .
docker push your-registry/github-mcp-server

Apply the kagent-resources
kubectl apply -f kagent-resources/


