import ttfr_fastlog
from .utils import info
import time

# ==========================================================
#   GLOBAL SINGLETON
# ==========================================================
_ENGINE = None


def get_engine():
    """
    Returns a global TTFR_Engine instance.
    Required by benchmark_phase_c.py.
    """
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = TTFR_Engine()
    return _ENGINE


# ==========================================================
#   MAIN ENGINE
# ==========================================================
class TTFR_Engine:
    def __init__(self, buffer_mb=512):
        info(f"Allocating optimized zero-copy buffer: {buffer_mb} MB")
        self.buffer = ttfr_fastlog.RingBuffer(buffer_mb * 1024 * 1024)
        self.events = []  # Keep original JSON form for MITRE replay

    # ------------------------------------------------------
    #   INGEST
    # ------------------------------------------------------
    def ingest(self, msg: bytes):
        """
        Ingest raw event bytes into RingBuffer
        and store decoded event for replay.
        """
        ts = int(time.time_ns())
        text = msg.decode("utf-8", errors="ignore")

        # Store in ring buffer
        self.buffer.push(msg)

        # Store structured event for batch compression
        self.events.append({"ts": ts, "msg": text})

    # ------------------------------------------------------
    #   SNAPSHOT
    # ------------------------------------------------------
    def dump_snapshot(self):
        """
        Returns a compressed FASTLOG blob containing structured JSON events.
        Exactly what benchmark_phase_c expects.
        """
        if not self.events:
            return b""

        blob = ttfr_fastlog.compress_json(self.events)
        return blob

