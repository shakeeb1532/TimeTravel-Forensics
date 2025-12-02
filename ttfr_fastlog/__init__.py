# ============================================================
#  FASTLOG – TTFR PYTHON LAYER (Stable Build)
# ============================================================

try:
    # Fast PyO3 backend (Rust)
    from fastlog_py import compress_json, decompress_json
    FASTLOG_BACKEND = "rust"
except Exception:
    # Pure-Python fallback
    FASTLOG_BACKEND = "python"
    import json
    import lz4.block as lz4b

    def compress_json(data):
        """
        Pure-python fallback JSON → LZ4-compressed bytes.
        """
        try:
            raw = json.dumps(data).encode("utf-8")
            return lz4b.compress(raw)
        except Exception as e:
            raise RuntimeError(f"compress_json failed: {e}")

    def decompress_json(blob):
        """
        Pure-python fallback LZ4-decompress → JSON.
        """
        try:
            dec = lz4b.decompress(blob)
            return json.loads(dec.decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"decompress_json failed: {e}")


# ============================================================
#  RingBuffer (TTFR Compatible)
# ============================================================

class RingBuffer:
    """
    High-speed Python fallback ring buffer.

    Provides full compatibility with TTFR CLI engine:

        ingest()
        push()
        write()
        snapshot()
        clear()

    Stores raw bytes while maintaining event list for snapshot().
    """

    def __init__(self, capacity_bytes: int):
        self.capacity = capacity_bytes
        self.buffer = bytearray(capacity_bytes)
        self.write_pos = 0
        self.full = False
        self.events = []      # logical event list

    # ---------------------------------------------------------
    # Ingest core function
    # ---------------------------------------------------------
    def ingest(self, raw: bytes):
        """
        Write raw bytes into circular buffer + store logical event.
        """
        n = len(raw)

        # Wrap
        if self.write_pos + n > self.capacity:
            self.write_pos = 0
            self.full = True

        # Write into memory ring
        self.buffer[self.write_pos : self.write_pos + n] = raw
        self.write_pos += n

        # Store logical event
        self.events.append(raw)

    # ---------------------------------------------------------
    # TTFR compatibility methods
    # ---------------------------------------------------------
    def push(self, raw: bytes):
        """Alias used by TTFR engine."""
        self.ingest(raw)

    def write(self, raw: bytes):
        """Alias used in older TTFR versions."""
        self.ingest(raw)

    # ---------------------------------------------------------
    # Snapshot (returns LZ4-compressed JSON list)
    # ---------------------------------------------------------
    def snapshot(self):
        """
        Export all stored events into compressed JSON.
        """
        try:
            decoded = [
                e.decode("utf-8", errors="ignore") for e in self.events
            ]
            structured = [{"event": d} for d in decoded]
            return compress_json(structured)
        except Exception as e:
            raise RuntimeError(f"snapshot failed: {e}")

    # ---------------------------------------------------------
    # Clear events + reset buffer
    # ---------------------------------------------------------
    def clear(self):
        self.write_pos = 0
        self.full = False
        self.events.clear()


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "compress_json",
    "decompress_json",
    "RingBuffer",
    "FASTLOG_BACKEND",
]

