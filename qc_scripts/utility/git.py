"""
git.py
Holds methods for getting information about the commit and repo from Github
"""

from pathlib import Path
import subprocess
import inspect
    
def get_git_info_from_path(path: Path):
    """
    Extracts Git information given a path (helper function)
    """
    path = Path(path).resolve()

    # Walk up to find the repo
    current = path
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists():
            repo_root = current
            break
        current = current.parent
    else:
        return {"error": "Not in a git repo"}
    try:
    # Get commit hash
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root
        ).decode().strip()
    except subprocess.CalledProcessError:
        commit_hash = "unknown"
    
    try:
    # Get remote URL (if available)
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=repo_root
        ).decode().strip()
    except subprocess.CalledProcessError:
        remote_url = "no remote"

    return {
        "repo_root": str(repo_root),
        "script_path_in_repo": str(path.relative_to(repo_root)),
        "commit_hash": commit_hash,
        "remote_url": remote_url,
    }

def get_pipeline_origin_path(exclude_dir="qc_scripts"):
    """
    Used for Pipelines if the pipeline is in the same repo other scripts (git, logger, stream)
    Traverses the call stack to find the first file that is not main and is not in qc_scripts, 
    then uses GitPython to extract git info from that file's repository.
    """
    for frame_info in reversed(inspect.stack()):
        filepath = Path(frame_info.filename).resolve()
        if exclude_dir not in filepath.parts and "main.py" != filepath.name:
            return get_git_info_from_path(filepath)
    return {"error": "No caller found outside qc_scripts folder"}

def get_git_info_from_caller_script(abstraction_repo_name="qc_utility"):
    """
    Used for Pipelines
    Traverses the call stack to find the first file that isn't part of 
    the abstraction repo, uses GitPython to extract git info from that 
    file's repository.
    """
    for frame_info in inspect.stack():
        file_path = Path(frame_info.filename).resolve()

        if abstraction_repo_name not in str(file_path):
            # Found the first frame outside of the abstraction repo
            return get_git_info_from_path(file_path)

    return {"error": "No caller found outside abstraction repo"}

def get_git_info_from_node(node_func):
    """
    Used for Nodes
    Get git info for the file where the given class/function 
    from the Node is defined
    """
    file_path = Path(inspect.getfile(node_func)).resolve()
    return get_git_info_from_path(file_path)
