import os
import fnmatch
import time
from flask import jsonify

def sending_payload(data, utils):
    try:
        host = data.get("IP")
        payload = data.get("payload")

        if not host:
            return jsonify({"error": "Missing IP parameter"}), 400
        if not payload:
            print("--- Starting Auto-Jailbreak Sequence ---")

            config = utils['get_payload_config']()

            print(f"[SEND] lapse.js -> {host}:50000")
            result = utils['send_payload'](file_path='payloads/js/lapse.js', host=host, port=50000)
            time.sleep(10)

            if result:
                global_config = utils['get_config']()
                kstuff_enabled = global_config.get("kstuff", "true") == "true"
                kstuff_result = True

                if kstuff_enabled:
                    kstuff_path = os.path.join(utils['ELF_DIR'], 'kstuff.elf')
                    if not os.path.exists(kstuff_path):
                        kstuff_path = 'payloads/kstuff.elf'

                    print(f"[SEND] kstuff.elf -> {host}:9021")
                    kstuff_result = utils['send_payload'](file_path=kstuff_path, host=host, port=9021)
                    time.sleep(10)
                else:
                    print("[SKIP] kstuff.elf (Disabled in Settings)")

                if kstuff_result:
                    files = []
                    for root, _, filenames in os.walk(utils['PAYLOAD_DIR']):
                        for f in filenames:
                            rel_path = os.path.relpath(os.path.join(root, f), utils['PAYLOAD_DIR']).replace("\\", "/")
                            files.append(rel_path)

                    try:
                        order = utils['get_payload_order']()
                        weights = {name: i for i, name in enumerate(order)}
                        files.sort(key=lambda x: weights.get(x, 9999))
                    except Exception as e:
                        print(f"[SORT] Error sorting payloads: {e}")

                    active_payloads = []
                    for f in files:
                        if (config.get(f, True) and config.get(os.path.basename(f), True)):
                            active_payloads.append(f)

                    print(f"--- Active Payloads in Queue: {len(active_payloads)} ---")
                    for p in active_payloads:
                        print(f"  • {p}")
                    print("-----------------------------------")

                    delay_flags = utils['get_payload_delay_flags']()
                    global_config = utils['get_config']()
                    try:
                        delay_time = float(global_config.get("global_delay", "5"))
                    except:
                        delay_time = 5.0

                    for filename in files:
                        if not config.get(filename, True) or not config.get(os.path.basename(filename), True):
                            continue

                        if (fnmatch.fnmatch(filename, '*.bin') or fnmatch.fnmatch(filename, '*.elf')) and 'kstuff.elf' not in filename:
                            print(f"[SEND] {filename} -> {host}:9021")
                            result = utils['send_payload'](file_path=os.path.join(utils['PAYLOAD_DIR'],filename), host=host, port=9021)

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
            result = utils['send_payload'](file_path=payload, host=host, port=port)

            if result:
                return jsonify({"success": True, "message": "Custom payload sent"})
            else:
                return jsonify({"error": "Failed to send custom payload"}), 500

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500
