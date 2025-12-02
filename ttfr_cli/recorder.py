import threading
import time
from .engine import get_engine
from .utils import info

running = False
thread_handle = None

def _recorder_loop():
    global running
    engine = get_engine()
    info("Recorder loop active.")

    while running:
        fake_event = b"cpu=5%, net=12kb/s, msg=heartbeat"
        engine.ingest(fake_event)
        time.sleep(0.1)

    info("Recorder loop ended.")

def start():
    global running, thread_handle
    if running:
        info("Recorder already running.")
        return

    running = True
    thread_handle = threading.Thread(target=_recorder_loop, daemon=True)
    thread_handle.start()
    info("Recorder started.")

def stop():
    global running
    running = False
    info("Recorder stopped.")

def status():
    return running

