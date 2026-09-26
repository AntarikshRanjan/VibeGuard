import os
import github
from github import Github
from github import Auth

class GithubIntegration:
    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN must be provided or set in environment variables")
        self.auth = Auth.Token(self.token)
        self.client = Github(auth=self.auth)

    def get_repo(self, repo_name: str):
        return self.client.get_repo(repo_name)

    def create_branch(self, repo_name: str, branch_name: str, base_sha: str):
        repo = self.get_repo(repo_name)
        ref = f"refs/heads/{branch_name}"
        repo.create_git_ref(ref=ref, sha=base_sha)
        return True

    def commit_files(self, repo_name: str, branch_name: str, commit_message: str, files: dict):
        """
        files is a dict mapping file path to content string
        """
        repo = self.get_repo(repo_name)
        
        # Get the latest commit tree of the branch
        ref = repo.get_git_ref(f"heads/{branch_name}")
        base_commit = repo.get_git_commit(ref.object.sha)
        base_tree = repo.get_git_tree(base_commit.tree.sha)

        # Create tree elements
        elements = []
        for path, content in files.items():
            blob = repo.create_git_blob(content, "utf-8")
            element = github.InputGitTreeElement(path=path, mode="100644", type="blob", sha=blob.sha)
            elements.append(element)
            
        # Create tree and commit
        new_tree = repo.create_git_tree(elements, base_tree)
        new_commit = repo.create_git_commit(message=commit_message, tree=new_tree, parents=[base_commit])
        
        # Update branch ref
        ref.edit(sha=new_commit.sha)
        return new_commit.sha

    def open_draft_pull_request(self, repo_name: str, title: str, body: str, head_branch: str, base_branch: str = "main"):
        repo = self.get_repo(repo_name)
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch,
            draft=True
        )
        return pr.html_url

    def merge_pull_request(self, repo_name: str, pr_number: int):
        repo = self.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        status = pr.merge()
        return status.merged
