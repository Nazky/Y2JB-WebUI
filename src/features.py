import logging
import threading
import sys
from collections import deque
from datetime import datetime
from src.repo_manager import update_payloads
from src.update_checker import check_for_updates

LOG_BUFFER = deque(maxlen=2000)

class ListHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            LOG_BUFFER.append(msg)
        except Exception:
            self.handleError(record)

class StdoutCapture:
    def __init__(self, stream):
        self.stream = stream
        self.encoding = stream.encoding

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        
        if data.strip(): 
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
            LOG_BUFFER.append(f"{timestamp} [STDOUT] {data.strip()}")

    def flush(self):
        self.stream.flush()

def setup_logging(config):
    level = logging.DEBUG if config.get("debug_mode") == "true" else logging.INFO
    
    list_handler = ListHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    list_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            list_handler
        ],
        force=True
    )
    
    if not isinstance(sys.stdout, StdoutCapture):
        sys.stdout = StdoutCapture(sys.stdout)

    logger = logging.getLogger("Y2JB")
    logger.info(f"Logging initialized at {'DEBUG' if level == logging.DEBUG else 'INFO'} level")

def run_startup_tasks(config):
    if config.get("auto_update_repos", "true") == "true":
        print("[STARTUP] Auto-updating repositories...")
        threading.Thread(target=lambda: update_payloads(['all']), daemon=True).start()
    
    print("[STARTUP] Checking for codebase updates...")
    threading.Thread(target=check_for_updates, daemon=True).start()

def get_logs():
    return list(LOG_BUFFER)