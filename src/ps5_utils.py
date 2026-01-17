import os
import json
import sqlite3
from ftplib import FTP

DAT_FILE = "payloads/dat/download0.dat"
CACHE_DIR = "cache"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def ftp_connect(ip, port):
    ftp = FTP()
    ftp.connect(ip, int(port), timeout=10)
    ftp.login('anonymous', 'anonymous')
    return ftp

def auto_replace_download0(ip, port):
    try:
        if not os.path.exists(DAT_FILE):
            return False, "File not found! Please download 'download0.dat' using the Repo Manager first."
        
        ftp = ftp_connect(ip, port)
        remote_path = "/user/download/PPSA01650/download0.dat"
        
        try:
            ftp.delete(remote_path)
        except:
            pass 

        with open(DAT_FILE, 'rb') as f:
            ftp.storbinary(f'STOR {remote_path}', f)
        
        ftp.quit()
        return True, "download0.dat installed successfully on PS5"
    except Exception as e:
        return False, str(e)

def patch_blocker(ip, port):
    try:
        ensure_dir(CACHE_DIR)
        ftp = ftp_connect(ip, port)
        
        files_to_patch = [
            ("/system_data/priv/mms/appinfo.db", "appinfo.db"),
            ("/system_data/priv/mms/app.db", "app.db"),
            ("/user/appmeta/PPSA01650/param.json", "param.json")
        ]

        for remote, local in files_to_patch:
            local_path = os.path.join(CACHE_DIR, local)
            try:
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote}', f.write)
            except Exception as e:
                ftp.quit()
                return False, f"Failed to download {local} from PS5: {str(e)}"

        appinfo_path = os.path.join(CACHE_DIR, "appinfo.db")
        conn = sqlite3.connect(appinfo_path)
        cursor = conn.cursor()
        queries = [
            ("UPDATE tbl_appinfo SET val = ? WHERE titleId = ? AND key = 'CONTENT_VERSION'", ("99.999.999", "PPSA01650")),
            ("UPDATE tbl_appinfo SET val = ? WHERE titleId = ? AND key = 'VERSION_FILE_URI'", ("http://127.0.0.2", "PPSA01650"))
        ]
        for q, p in queries:
            cursor.execute(q, p)
        conn.commit()
        conn.close()

        app_db_path = os.path.join(CACHE_DIR, "app.db")
        conn = sqlite3.connect(app_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT AppInfoJson FROM tbl_contentinfo WHERE titleId = ?", ("PPSA01650",))
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            data['CONTENT_VERSION'] = "99.999.999"
            data['VERSION_FILE_URI'] = "http://127.0.0.2"
            new_json = json.dumps(data)
            cursor.execute("UPDATE tbl_contentinfo SET AppInfoJson = ? WHERE titleId = ?", (new_json, "PPSA01650"))
            conn.commit()
        conn.close()

        param_path = os.path.join(CACHE_DIR, "param.json")
        with open(param_path, 'r') as f:
            data = json.load(f)
        data['contentVersion'] = "99.999.999"
        data['versionFileUri'] = "http://127.0.0.2"
        with open(param_path, 'w') as f:
            json.dump(data, f, indent=4)

        upload_map = [
            ("appinfo.db", "/system_data/priv/mms/appinfo.db"),
            ("app.db", "/system_data/priv/mms/app.db"),
            ("param.json", "/system_data/priv/appmeta/PPSA01650/param.json"),
            ("param.json", "/user/appmeta/PPSA01650/param.json")
        ]

        for local, remote in upload_map:
            local_path = os.path.join(CACHE_DIR, local)
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote}', f)

        ftp.quit()
        return True, "Updates blocked successfully (Files patched)"

    except Exception as e:
        return False, str(e)