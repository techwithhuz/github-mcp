import requests
import base64
import os
import subprocess

class GitHubAgent:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_repo_info(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else {"error": response.json()}

    def create_issue(self, owner, repo, title, body=None):
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        data = {"title": title}
        if body:
            data["body"] = body
        response = requests.post(url, json=data, headers=self.headers)
        return response.json() if response.status_code == 201 else {"error": response.json()}

    def create_pull_request(self, owner, repo, title, head_branch, base_branch, body=None):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "head": head_branch,
            "base": base_branch,
        }
        if body:
            data["body"] = body
        response = requests.post(url, json=data, headers=self.headers)
        return response.json() if response.status_code == 201 else {"error": response.json()}

    def create_branch(self, owner, repo, new_branch, base_branch="main"):
        ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{base_branch}"
        ref_response = requests.get(ref_url, headers=self.headers)
        if ref_response.status_code != 200:
            return {"error": ref_response.json()}
        sha = ref_response.json()["object"]["sha"]

        new_ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{new_branch}",
            "sha": sha
        }
        response = requests.post(new_ref_url, json=data, headers=self.headers)
        return response.json() if response.status_code in [201, 200] else {"error": response.json()}

    def push_file(self, owner, repo, file_path, branch, content, commit_message):
        get_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        get_resp = requests.get(get_url, headers=self.headers)
        sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        data = {
            "message": commit_message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch
        }
        if sha:
            data["sha"] = sha

        response = requests.put(url, json=data, headers=self.headers)
        return response.json() if response.status_code in [200, 201] else {"error": response.json()}

    def git_clone(self, repo_url, clone_dir):
        try:
            subprocess.check_output(["git", "clone", repo_url, clone_dir])
            return {"success": True, "message": f"Repository cloned to {clone_dir}"}
        except subprocess.CalledProcessError as e:
            return {"error": str(e)}
