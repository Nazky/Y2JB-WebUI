import fnmatch
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename as werkzeug_secure_filename
import os
from src.SendPayload import send_payload
from src.delete_payload import handle_delete_payload
from src.download_payload import handle_url_download
from src.repo_manager import update_payloads, add_repo_entry, delete_repo_entry
from src.ps5_utils import auto_replace_download0, patch_blocker
import time
import threading
import requests
import socket
from src.ftp_manager import list_ftp_directory, delete_item, create_directory, rename_item, download_file_content, upload_file_content
import io
from flask import send_file
import uuid
from src.dns_server import DNSServer
from src.backpork.core import BackporkEngine
from src.features import setup_logging, run_startup_tasks

app = Flask(__name__)
app.secret_key = 'Nazky'
CORS(app)

dns_service = None

PAYLOAD_DIR = "payloads"
DAT_DIR = "payloads/dat"
CONFIG_DIR = "static/config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
PAYLOAD_CONFIG_FILE = os.path.join(CONFIG_DIR, "payload_config.json")
PAYLOAD_ORDER_FILE = os.path.join(CONFIG_DIR, "payload_order.json")
PAYLOAD_DELAYS_FILE = os.path.join(CONFIG_DIR, "payload_delays.json")
PAYLOAD_DELAY_FLAGS_FILE = os.path.join(CONFIG_DIR, "payload_delay_flags.json")
DNS_CONFIG_FILE = os.path.join(CONFIG_DIR, "dns_rules.json")
ALLOWED_EXTENSIONS = {'bin', 'elf', 'js', 'dat'}
url = "http://localhost:8000/send_payload"

os.makedirs(PAYLOAD_DIR, exist_ok=True)
os.makedirs(DAT_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs('templates', exist_ok=True)

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"ajb": "false", "ip": ""}, f)

def get_payload_config():
    if not os.path.exists(PAYLOAD_CONFIG_FILE):
        return {}
    try:
        with open(PAYLOAD_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_payload_order():
    if not os.path.exists(PAYLOAD_ORDER_FILE):
        return []
    try:
        with open(PAYLOAD_ORDER_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_payload_order(order):
    with open(PAYLOAD_ORDER_FILE, 'w') as f:
        json.dump(order, f, indent=4)

def get_payload_delays():
    if not os.path.exists(PAYLOAD_DELAYS_FILE):
        return {}
    try:
        with open(PAYLOAD_DELAYS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_payload_delays(data):
    with open(PAYLOAD_DELAYS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def save_payload_config(config):
    with open(PAYLOAD_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_config():
    if not os.path.exists(CONFIG_FILE):
        return {"ajb": "false", "ip": ""}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"ajb": "false", "ip": ""}

def update_config(key, value):
    config = get_config()
    config[key] = str(value)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_dns_rules():
    if not os.path.exists(DNS_CONFIG_FILE):
        return []
    try:
        with open(DNS_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_dns_rules(rules):
    with open(DNS_CONFIG_FILE, 'w') as f:
        json.dump(rules, f, indent=4)
    if dns_service:
        dns_service.load_rules()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    import re
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

def check_ajb():
    while True:
        try:
            config = get_config()
            ajb_content = config.get("ajb", "false").lower()


            if ajb_content == "true":
                ip_address = config.get("ip", "").strip()

                if not ip_address:
                    print("[AJB] Enabled but IP missing")
                else:

                    response = requests.post(url, json={
                        "IP": ip_address,
                        "payload": ""
                    })

                    if response.status_code == 200:
                        print("[AJB] Sequence completed successfully")
                    else:
                        print(f"[AJB] Error: {response.text}")

        except Exception as e:
            print("[AJB] Error:", str(e))

        finally:
            time.sleep(5)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/api/payload_config', methods=['GET'])
def get_payload_config_route():
    return jsonify(get_payload_config())

@app.route('/api/payload_config/toggle', methods=['POST'])
def toggle_payload_config():
    try:
        data = request.json
        filename = data.get('filename')
        enabled = data.get('enabled')
        
        if not filename:
            return jsonify({"error": "Missing filename"}), 400
            
        config = get_payload_config()
        config[filename] = enabled
        save_payload_config(config)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payload_order', methods=['GET', 'POST'])
def handle_payload_order():
    if request.method == 'GET':
        return jsonify(get_payload_order())
    
    if request.method == 'POST':
        try:
            order = request.json.get('order', [])
            save_payload_order(order)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/payload_delay', methods=['GET', 'POST'])
def handle_payload_delay():
    if request.method == 'GET':
        return jsonify(get_payload_delays())
    
    if request.method == 'POST':
        try:
            data = request.json
            filename = data.get('filename')
            delay = data.get('delay')
            
            if not filename:
                return jsonify({"error": "Missing filename"}), 400
            
            delays = get_payload_delays()
            if delay is None or delay == "":
                if filename in delays:
                    del delays[filename]
            else:
                delays[filename] = int(delay)
                
            save_payload_delays(delays)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def get_payload_delay_flags():
    if not os.path.exists(PAYLOAD_DELAY_FLAGS_FILE):
        return {}
    try:
        with open(PAYLOAD_DELAY_FLAGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_payload_delay_flags(flags):
    with open(PAYLOAD_DELAY_FLAGS_FILE, 'w') as f:
        json.dump(flags, f, indent=4)

@app.route('/api/payload_delays', methods=['GET'])
def get_payload_delays_route():
    return jsonify(get_payload_delay_flags())

@app.route('/api/payload_delays/toggle', methods=['POST'])
def toggle_payload_delay_flag():
    try:
        data = request.json
        filename = data.get('filename')
        enabled = data.get('enabled')
        
        if not filename:
            return jsonify({"error": "Missing filename"}), 400
            
        flags = get_payload_delay_flags()
        flags[filename] = enabled
        save_payload_delay_flags(flags)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit_ajb', methods=['POST'])
def edit_ajb():
    new_content = request.json.get('content')
    update_config("ajb", new_content)
    return "Settings updated!"

@app.route('/edit_ip', methods=['POST'])
def edit_ip():
    new_content = request.json.get('content')
    update_config("ip", new_content)
    return "Settings updated!"

@app.route('/list_payloads')
def list_files():
    folder = "payloads"
    payload_files = []
    try:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(('.bin', '.elf', '.js', '.dat')):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, folder)
                    rel_path = rel_path.replace("\\", "/") 
                    payload_files.append(rel_path)
        
        order = get_payload_order()
        weights = {name: i for i, name in enumerate(order)}
        payload_files.sort(key=lambda x: weights.get(x, 9999))
        
        return jsonify(payload_files)
    except Exception as e:
        return jsonify({"error": "Folder not found"}), 404

@app.route('/upload_payload', methods=['POST'])
def upload_payload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(PAYLOAD_DIR, filename)

        try:
            file.save(save_path)
            print(f"[UPLOAD] Saved {filename}")
            return jsonify({
                'success': True,
                'filename': filename,
                'path': save_path
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download_payload_url', methods=['POST'])
def download_payload_url():
    try:
        data = request.get_json()
        url = data.get('url')
        print(f"[DOWNLOAD] Fetching from {url}...")
        response, status_code = handle_url_download(url, PAYLOAD_DIR, ALLOWED_EXTENSIONS)
        
        if status_code == 200:
            filename = response.get('filename')
            if filename:
                entry = {
                    "type": "direct",
                    "url": url,
                    "save_path": f"payloads/{filename}"
                }
                add_repo_entry(filename, entry)
        
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/send_payload", methods=["POST"])
def sending_payload():
    try:
        data = request.get_json()
        host = data.get("IP")
        payload = data.get("payload")

        if not host:
            return jsonify({"error": "Missing IP parameter"}), 400
        if not payload:
            print("--- Starting Auto-Jailbreak Sequence ---")
            
            config = get_payload_config()

            print(f"[SEND] lapse.js -> {host}:50000")
            result = send_payload(file_path='payloads/js/lapse.js', host=host, port=50000)
            time.sleep(10)
            
            if result:
                global_config = get_config()
                kstuff_enabled = global_config.get("kstuff", "true") == "true"
                kstuff_result = True 

                if kstuff_enabled:
                    print(f"[SEND] kstuff.elf -> {host}:9021")
                    kstuff_result = send_payload(file_path='payloads/kstuff.elf', host=host, port=9021)
                    time.sleep(10)
                else:
                    print("[SKIP] kstuff.elf (Disabled in Settings)")
                
                if kstuff_result:
                    files = os.listdir(PAYLOAD_DIR)
                    try:
                        order = get_payload_order()
                        weights = {name: i for i, name in enumerate(order)}
                        files.sort(key=lambda x: weights.get(x, 9999))
                    except Exception as e:
                        print(f"[SORT] Error sorting payloads: {e}")

                    delay_flags = get_payload_delay_flags()
                    global_config = get_config()
                    try:
                        delay_time = float(global_config.get("global_delay", "5"))
                    except:
                        delay_time = 5.0

                    for filename in files:
                        if not config.get(filename, True):
                            print(f"[SKIP] {filename} (Disabled in settings)")
                            continue

                        if (fnmatch.fnmatch(filename, '*.bin') or fnmatch.fnmatch(filename, '*.elf')) and filename != 'kstuff.elf':
                            print(f"[SEND] {filename} -> {host}:9021")
                            result = send_payload(file_path=os.path.join(PAYLOAD_DIR,filename), host=host, port=9021)
                            
                            if delay_flags.get(filename, False):
                                print(f"[WAIT] Sleeping {delay_time}s for {filename}...")
                                time.sleep(delay_time)
                            else:
                                time.sleep(0.5)
                            
                            if not result:
                                print(f"[FAIL] Could not send {filename}")
                                return jsonify({"error": f"Failed to send {filename}"}), 500
                    
                    print("--- Auto-Jailbreak Sequence Complete ---")
                    return jsonify({"success": True, "message": "All payloads sent successfully"})
                else:
                    return jsonify({"error": "Failed to send kstuff.elf"}), 500
            else:
                return jsonify({"error": "Failed to send lapse.js"}), 500
        else:
            port = 9021
            if payload.lower().endswith('.js'):
                port = 50000
            
            print(f"[MANUAL] Sending {payload} -> {host}:{port}")
            result = send_payload(file_path=payload, host=host, port=port)
            
            if result:
                return jsonify({"success": True, "message": "Custom payload sent"})
            else:
                return jsonify({"error": "Failed to send custom payload"}), 500

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_payload', methods=['POST'])
def delete_payload():
    try:
        data = request.get_json()
        print(f"[DELETE] Request: {data}")
        response, status_code = handle_delete_payload(data, PAYLOAD_DIR, ALLOWED_EXTENSIONS)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to delete file'
        }), 500

@app.route('/list_repos')
def list_repos():
    try:
        repo_file = os.path.join("static", "config", "repos.json")
        with open(repo_file, 'r') as f:
            repos = json.load(f)
        return jsonify(list(repos.keys()))
    except:
        return jsonify([])

@app.route('/update_repos', methods=['POST'])
def update_repos():
    try:
        data = request.get_json() or {}
        targets = data.get('targets', ['all'])
        print(f"[REPO] Updating targets: {targets}")
        result = update_payloads(targets)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/settings/repos')
def repo_manager_ui():
    return render_template('repos.html')

@app.route('/api/repos/list')
def get_repo_list():
    try:
        with open(os.path.join("static", "config", "repos.json"), 'r') as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

@app.route('/api/repos/add', methods=['POST'])
def add_new_repo():
    try:
        data = request.json
        name = data.get('name')
        old_name = data.get('old_name')

        if not name: 
            return jsonify({"error": "Missing name"}), 400
        
        if old_name and old_name != name:
            delete_repo_entry(old_name)

        config_data = {k:v for k,v in data.items() if k not in ['name', 'old_name']}
        add_repo_entry(name, config_data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/repos/delete', methods=['POST'])
def remove_repo():
    try:
        data = request.json
        name = data.get('name')
        delete_repo_entry(name)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit_ftp_port', methods=['POST'])
def edit_ftp_port():
    new_content = request.json.get('content')
    update_config("ftp_port", new_content)
    return "Settings updated!"

@app.route('/tools/update_download0', methods=['POST'])
def run_update_download0():
    config = get_config()
    ip = config.get("ip")
    port = config.get("ftp_port", "1337")
    
    if not ip:
        return jsonify({"success": False, "message": "IP Address not set"}), 400

    print(f"[TOOL] Installing download0.dat to {ip}...")
    success, message = auto_replace_download0(ip, port)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 500

@app.route('/tools/block_updates', methods=['POST'])
def run_block_updates():
    config = get_config()
    ip = config.get("ip")
    port = config.get("ftp_port", "1337")
    
    if not ip:
        return jsonify({"success": False, "message": "IP Address not set"}), 400

    print(f"[TOOL] Blocking updates on {ip}...")
    success, message = patch_blocker(ip, port)
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 500

@app.route('/credits')
def credits_page():
    return render_template('credits.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'GET':
        return jsonify(get_config())
    
    if request.method == 'POST':
        try:
            new_settings = request.get_json()
            current_config = get_config()
            
            valid_keys = [
                'ip', 'ajb', 'ftp_port', 'global_delay', 
                'ui_animations', 'kstuff', 'debug_mode', 
                'auto_update_repos', 'dns_auto_start', 'compact_mode'
            ]
            for key in valid_keys:
                if key in new_settings:
                    current_config[key] = str(new_settings[key])
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(current_config, f, indent=4)
                
            return jsonify({"success": True, "message": "Settings saved successfully"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/network_info')
def network_info():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip = s.getsockname()[0]
        s.close()
    except:
        server_ip = "Unknown"
    
    client_ip = request.remote_addr
    
    return jsonify({
        "server_ip": server_ip,
        "client_ip": client_ip
    })

@app.route('/ftp')
def ftp_page():
    return render_template('ftp.html')

@app.route('/api/ftp/list', methods=['POST'])
def api_ftp_list():
    config = get_config()
    ip = config.get("ip")
    port = config.get("ftp_port", "1337")
    path = request.json.get('path', '/')
    
    if not ip:
        return jsonify({"success": False, "error": "IP not configured"}), 400
        
    result = list_ftp_directory(ip, port, path)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/ftp/download_file', methods=['POST'])
def api_ftp_download():
    config = get_config()
    ip = config.get("ip")
    port = config.get("ftp_port", "1337")
    path = request.json.get('path')
    
    result = download_file_content(ip, port, path)
    if result['success']:
        if request.json.get('as_text'):
            try:
                return jsonify({"success": True, "content": result['content'].decode('utf-8')})
            except:
                return jsonify({"success": False, "error": "Could not decode file as text"})
        
        filename = os.path.basename(path)
        return send_file(
            io.BytesIO(result['content']),
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    return jsonify(result), 500

@app.route('/api/ftp/upload_file', methods=['POST'])
def api_ftp_upload():
    config = get_config()
    ip = config.get("ip")
    port = config.get("ftp_port", "1337")
    
    path = request.form.get('path')
    file = request.files.get('file')
    
    text_content = request.form.get('content')
    
    if text_content is not None:
        result = upload_file_content(ip, port, path, text_content.encode('utf-8'))
        return jsonify(result)

    if file:
        file_content = file.read()
        filename = secure_filename(file.filename)
        full_path = f"{path.rstrip('/')}/{filename}"
        result = upload_file_content(ip, port, full_path, file_content)
        return jsonify(result)
        
    return jsonify({"success": False, "error": "No data provided"}), 400

@app.route('/api/ftp/action', methods=['POST'])
def api_ftp_action():
    config = get_config()
    ip = config.get("ip")
    port = config.get("ftp_port", "1337")
    
    data = request.json
    action = data.get('action')
    path = data.get('path')
    
    if action == 'delete':
        return jsonify(delete_item(ip, port, path, data.get('is_dir', False)))
    elif action == 'mkdir':
        return jsonify(create_directory(ip, port, path))
    elif action == 'rename':
        return jsonify(rename_item(ip, port, path, data.get('new_path')))
        
    return jsonify({"success": False, "error": "Invalid action"}), 400

@app.route('/dns')
def dns_page():
    return render_template('dns.html')

@app.route('/api/dns/list')
def api_dns_list():
    return jsonify(get_dns_rules())

@app.route('/api/dns/add', methods=['POST'])
def api_dns_add():
    try:
        data = request.json
        name = data.get('name')
        domain = data.get('domain')
        target = data.get('target', '0.0.0.0')

        if not name or not domain:
            return jsonify({"error": "Name and Domain are required"}), 400

        rules = get_dns_rules()
        new_rule = {
            "id": str(uuid.uuid4()),
            "name": name,
            "domain": domain,
            "target": target
        }
        rules.append(new_rule)
        save_dns_rules(rules)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dns/delete', methods=['POST'])
def api_dns_delete():
    try:
        rule_id = request.json.get('id')
        rules = get_dns_rules()
        rules = [r for r in rules if r.get('id') != rule_id]
        save_dns_rules(rules)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/backpork')
def backpork_page():
    pairs = [{"id": i, "label": f"Pair {i}"} for i in range(1, 11)] 
    return render_template('backpork.html', sdk_pairs=pairs)

@app.route("/api/backpork/settings", methods=['GET', 'POST'])
def handle_backpork_settings():
    if request.method == 'GET':
        return jsonify(BackporkEngine.load_config())
    if request.method == 'POST':
        BackporkEngine.save_config(request.json)
        return jsonify({"success": True})

@app.route("/api/backpork/run", methods=['POST'])
def run_backpork_process():
    data = request.json
    return Response(BackporkEngine.run_process(data), mimetype='text/event-stream')

if __name__ == "__main__":
    config = get_config()
    
    setup_logging(config)
    
    run_startup_tasks(config)

    threading.Thread(target=check_ajb, daemon=True).start()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    if config.get("dns_auto_start", "true") == "true":
        print(f"--- Initializing DNS Server on {local_ip} ---")
        dns_service = DNSServer(config_file=DNS_CONFIG_FILE, host_ip=local_ip)
        threading.Thread(target=dns_service.start, daemon=True).start()
    else:
        print("[STARTUP] DNS Server disabled by settings")

    app.run(host="0.0.0.0", port=8000, debug=(config.get("debug_mode") == "true"))