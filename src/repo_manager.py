import os
import json
import requests
import fnmatch

CONFIG_FILE = os.path.join("static", "config", "repos.json")

def get_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def add_repo_entry(name, entry_data):
    config = get_config()
    config[name] = entry_data
    save_config(config)

def delete_repo_entry(name):
    config = get_config()
    if name in config:
        del config[name]
        save_config(config)
        return True
    return False

def download_file(url, save_path):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        print(f"    Downloading {url}...")
        r = requests.get(url, stream=True, timeout=15)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"    Saved to {save_path}")
        return True
    except Exception as e:
        print(f"    [!] Error downloading: {e}")
        return False

def get_latest_release_asset(repo, pattern):
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for asset in data.get("assets", []):
            if fnmatch.fnmatch(asset["name"], pattern):
                return asset["browser_download_url"]
        return None
    except Exception as e:
        print(f"    [!] GitHub API Error for {repo}: {e}")
        return None

def update_payloads(targets=None):
    config = get_config()
    if not config:
        return {"success": False, "message": "repos.json empty or not found"}

    updated_files = []
    errors = []

    for name, data in config.items():
        if targets and "all" not in targets and name not in targets:
            continue

        print(f"[*] Processing {name}...")
        download_url = None
        save_path = data.get("save_path")
        
        if data.get("type") == "direct":
            download_url = data.get("url")
            
        elif data.get("type") == "release":
            repo = data.get("repo")
            pattern = data.get("asset_pattern")
            download_url = get_latest_release_asset(repo, pattern)
            if not download_url:
                errors.append(f"Could not find asset '{pattern}' in {repo} releases")
                continue

        if download_url:
            if download_file(download_url, save_path):
                updated_files.append(name)
            else:
                errors.append(f"Failed to download {name}")
        else:
            errors.append(f"Invalid configuration for {name}")

    return {
        "success": True,
        "updated": updated_files,
        "errors": errors
    }

if __name__ == "__main__":
    update_payloads()