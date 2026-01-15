import fnmatch
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from src.SendPayload import send_payload
from src.delete_payload import handle_delete_payload
from src.download_payload import handle_url_download
import time
import threading
import requests

app = Flask(__name__)
app.secret_key = 'Nazky'
CORS(app)

PAYLOAD_DIR = "payloads"
CONFIG_DIR = "static/config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
ALLOWED_EXTENSIONS = {'bin', 'elf'}
url = "http://localhost:8000/send_payload"

os.makedirs(PAYLOAD_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs('templates', exist_ok=True)

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

            print("Auto-Jailbreak:", ajb_content)

            if ajb_content == "true":
                ip_address = config.get("ip", "").strip()

                if not ip_address:
                    print("Empty IP in settings")
                else:
                    print("IP:", ip_address)

                    response = requests.post(url, json={
                        "IP": ip_address,
                        "payload": ""
                    })

                    if response.status_code == 200:
                        print("Payload sent successfully")
                    else:
                        print("Error sending payload:", response.text)

        except Exception as e:
            print("Error:", str(e))

        finally:
            time.sleep(5)

@app.route("/")
def home():
    return render_template('index.html')

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
    try:
        files = [f for f in os.listdir(folder)
                if f.lower().endswith(('.bin', '.elf'))]
        return jsonify(files)
    except:
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
        response, status_code = handle_url_download(url, PAYLOAD_DIR, ALLOWED_EXTENSIONS)
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
            result = send_payload(file_path='payloads/js/lapse.js', host=host, port=50000)
            time.sleep(1)
            if result:
                result = send_payload(file_path='payloads/kstuff.elf', host=host, port=9021)
                time.sleep(1)
                if result:
                    for filename in os.listdir(PAYLOAD_DIR):
                        if (fnmatch.fnmatch(filename, '*.bin') or fnmatch.fnmatch(filename, '*.elf')) and filename != 'kstuff.elf':
                            result = send_payload(file_path=os.path.join(PAYLOAD_DIR,filename), host=host, port=9021)
                            time.sleep(1)
                            if not result:
                                return jsonify({"error": f"Failed to send {filename}"}), 500
                    return jsonify({"success": True, "message": "All payloads sent successfully"})
                else:
                    return jsonify({"error": "Failed to send kstuff.elf"}), 500
            else:
                return jsonify({"error": "Failed to send lapse.js"}), 500
        else:
            result = send_payload(file_path=payload, host=host, port=9021)
            if result:
                return jsonify({"success": True, "message": "Custom payload sent"})
            else:
                return jsonify({"error": "Failed to send custom payload"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_payload', methods=['POST'])
def delete_payload():
    try:
        data = request.get_json()
        response, status_code = handle_delete_payload(data, PAYLOAD_DIR, ALLOWED_EXTENSIONS)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to delete file'
        }), 500

@app.route('/update_y2jb', methods=['POST'])
def update_y2jb():
    try:
        url = "https://raw.githubusercontent.com/Gezine/Y2JB/main/payloads/lapse.js"
        print(f"Fetching update from: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            target_dir = os.path.join(PAYLOAD_DIR, 'js')
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, 'lapse.js')
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return jsonify({"success": True, "message": "Updated lapse.js successfully!"})
        else:
            return jsonify({"error": f"GitHub Error: {response.status_code}"}), 500
    except Exception as e:
        print(f"Update Failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    threading.Thread(target=check_ajb, daemon=True).start()
    app.run(host="0.0.0.0", port=8000 ,debug=False)