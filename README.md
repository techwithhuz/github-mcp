# GitHub MCP Server for KAgent

This repository contains the code and Kubernetes resources for running a GitHub-compatible [MCP](https://github.com/docker/mcp) server. It is designed to integrate with [KAgent](https://github.com/kubeframe/kagent), enabling AI agents to interact with GitHub and perform developer automation tasks like creating pull requests.

---

## Features

- SSE-based communication with KAgent.
- Tools implemented:
  - `create_pr`: Create GitHub pull requests.
  - `create_branch`: Create a new branch in the repository.
  - `push_file`: Push Terraform files or any file to a repo.
  - `clone_repo`: Clone and inspect the repository.
- Secure authentication via GitHub personal access token.
- Packaged as a container and deployed on Kubernetes.

---

## Terraform Agent (GCP)

This project is extended by a **Terraform AI Agent** that connects to this GitHub MCP server and automates Terraform-based GCP infrastructure provisioning. The agent:

- Creates `.tf` files for GCP using best practices.
- Automatically commits and opens a pull request to [this repo](https://github.com/techwithhuz/gcp-terraform).
- Responds only with the **GitHub PR URL**, without any extra output.
- Handles creation of:
  - VPCs, subnets
  - e2-micro VM instances in `us-central1-a`
  - SSH firewall rules
  - Required API enablement
  - Resource labels (`creator = gcp-terraform-agent`)

This agent works by calling the `create_branch`, `push_file`, and `create_pr` tools exposed by the MCP server.


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


