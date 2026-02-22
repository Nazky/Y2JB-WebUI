import json
import os
import logging
import time
import requests

logger = logging.getLogger("Y2JB.UpdateChecker")

REPO_OWNER = "Nazky"
REPO_NAME = "Y2JB-WebUI"
BRANCH = "main"
REMOTE_VERSION_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/version.json"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
LOCAL_VERSION_FILE = "version.json"

_cache = {
    "last_check": 0,
    "result": None,
    "ttl": 300  # 5 minutes
}


def _read_local_version():
    try:
        with open(LOCAL_VERSION_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not read local version.json: {e}")
        return None


def _fetch_remote_version():
    try:
        response = requests.get(REMOTE_VERSION_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Could not fetch remote version.json: {e}")
        return None


def _compare_versions(local_ver, remote_ver):
    try:
        local_parts = [int(x) for x in local_ver.split('.')]
        remote_parts = [int(x) for x in remote_ver.split('.')]
        
        for l, r in zip(local_parts, remote_parts):
            if l < r:
                return -1
            if l > r:
                return 1
        
        if len(local_parts) < len(remote_parts):
            return -1
        if len(local_parts) > len(remote_parts):
            return 1
        
        return 0
    except Exception:
        return 0


def check_for_updates(force=False):
    now = time.time()

    if not force and _cache["result"] is not None and (now - _cache["last_check"]) < _cache["ttl"]:
        return _cache["result"]

    local = _read_local_version()
    remote = _fetch_remote_version()

    result = {
        "local_version": local.get("version") if local else None,
        "local_branch": local.get("branch") if local else None,
        "local_date": local.get("date") if local else None,
        "local_description": local.get("description") if local else None,
        "remote_version": remote.get("version") if remote else None,
        "remote_branch": remote.get("branch") if remote else None,
        "remote_date": remote.get("date") if remote else None,
        "remote_description": remote.get("description") if remote else None,
        "up_to_date": None,
        "repo_url": REPO_URL,
        "error": None
    }

    if not local or not local.get("version"):
        result["error"] = "Local version.json not found or invalid"
    elif not remote or not remote.get("version"):
        result["error"] = "Could not reach GitHub to check for updates"
    else:
        cmp = _compare_versions(local["version"], remote["version"])
        if cmp >= 0:
            result["up_to_date"] = True
        else:
            result["up_to_date"] = False

    _cache["result"] = result
    _cache["last_check"] = now

    if result["up_to_date"] is False:
        logger.info(f"Update available! Local: v{result['local_version']} -> Remote: v{result['remote_version']}")
    elif result["up_to_date"] is True:
        logger.info(f"Codebase is up to date (v{result['local_version']})")

    return result
